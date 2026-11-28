"""Select real TRAIN rows before inference; generate/check historical replay evidence.

python -B -m technical_evaluation.prepare_pv_replay [--check] [--tests]
Git must be on PATH. No network, fitting, deployment or frontend changes.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from joblib import parallel_backend
import numpy as np
import pandas as pd

from technical_evaluation.class_measurement_ranges import CHANNELS, LABELS, RAW_SHA, sha
from src.preprocessing.common import TRAIN
from src.phase2_stage1.contracts import TRAIN_COUNTS
from src.transformers import RetainedQuality
from src.inference.cli import load_model, predict, SHA256

ROOT = Path(__file__).resolve().parents[1]
BASELINE = 'b597ffa13a0de541ce20edc964f44dde618c7cce'
SEED = 42
RANK_FEATURES = CHANNELS + ['abs_voltage_difference', 'abs_current_difference']
PUBLIC = 'web/data/pv_historical_replay.json'
EVIDENCE = 'technical_evaluation/PV_Replay_Verification.json'
METHOD = 'technical_evaluation/PV_Replay_Selection_Method.md'


def dumps(x):
    return json.dumps(x, indent=2, ensure_ascii=True, allow_nan=False) + '\n'


def protected():
    git = shutil.which('git')
    if not git:
        raise RuntimeError('Git must be installed and on PATH for protected-file verification.')
    tree = subprocess.check_output([git, 'ls-tree', '-r', BASELINE], cwd=ROOT, text=True).splitlines()
    hashes = {}
    for line in tree:
        meta, name = line.split('\t')
        content = (ROOT / name).read_bytes()
        oid = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        if oid != meta.split()[2]:
            raise ValueError('Protected existing file changed: ' + name)
        hashes[name] = hashlib.sha256(content).hexdigest()
    return hashes


def stratum_selection(x, ranks, mask, count, class_id, stratum_id):
    """Seeded pool, distinct joint vectors, median-nearest then farthest-first."""
    available = x.index[np.asarray(mask)]
    rng = np.random.default_rng(np.random.SeedSequence([SEED, class_id, stratum_id]))
    pool = rng.choice(available.to_numpy(), size=min(6000, len(available)), replace=False)
    # Retain real extrema as candidates; selection still depends only on measurements.
    extra = []
    local = ranks.loc[available]
    for col in RANK_FEATURES:
        extra.extend([int(local[col].idxmin()), int(local[col].idxmax())])
    pool = np.unique(np.r_[pool, extra])
    pool = rng.permutation(pool)  # Stable seeded tie order, no classifier access.
    candidates = x.loc[pool, CHANNELS].drop_duplicates(keep='first').index.to_numpy()
    if len(candidates) < count:
        raise ValueError('Insufficient distinct real measurements in a required stratum.')
    z = ranks.loc[candidates].to_numpy()
    first = int(np.argmin(np.square(z - .5).sum(axis=1)))
    chosen = [first]
    distances = np.square(z - z[first]).sum(axis=1)
    distances[first] = -np.inf
    while len(chosen) < count:
        i = int(np.argmax(distances))
        chosen.append(i)
        distances = np.minimum(distances, np.square(z - z[i]).sum(axis=1))
        distances[chosen] = -np.inf
    return [int(candidates[i]) for i in chosen], {
        'available_rows': len(available), 'distinct_pool_rows': len(candidates),
        'requested_rows': count, 'selected_rows': count,
        'seed_sequence': [SEED, class_id, stratum_id]}


def markdown_table(head, rows):
    return '\n'.join(['| ' + ' | '.join(head) + ' |', '| ' + ' | '.join(['---']*len(head)) + ' |',
                      *['| ' + ' | '.join(map(str, row)) + ' |' for row in rows]])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Recompute and compare outputs without writing.')
    parser.add_argument('--tests', action='store_true', help='Run the existing 50 relevant regression tests.')
    args = parser.parse_args()
    original_hashes = protected()
    assert TRAIN == (0, 1006129)
    assert sha(ROOT / 'data/raw/pv_fault_dataset.csv') == RAW_SHA
    assert sha(ROOT / 'models/rf_e4/model.pkl') == SHA256
    # The returned DataFrame contains no VALIDATION or TEST observations.
    data = pd.read_csv(ROOT / 'data/raw/pv_fault_dataset.csv', nrows=TRAIN[1], float_precision='round_trip')
    assert {int(k): int(v) for k,v in data.f_nv.value_counts().items()} == TRAIN_COUNTS
    x = data[CHANNELS]
    assert np.array_equal(RetainedQuality(CHANNELS).transform(x).to_numpy(), x.to_numpy())
    assert np.isfinite(x.to_numpy()).all() and (x.to_numpy() >= 0).all()
    x = x.copy()
    x['abs_voltage_difference'] = abs(x.vdc1-x.vdc2)
    x['abs_current_difference'] = abs(x.idc1-x.idc2)
    selected, selection_ledger, rank_frames = {}, {}, {}
    for k in range(5):
        frame = x.loc[data.f_nv == k]
        ranks = frame[RANK_FEATURES].rank(method='average', pct=True)
        rank_frames[k] = ranks
        if k == 0:
            low = data.loc[frame.index, 'irr'] < 100
            strata = [('irr_below_100', low, 15), ('irr_at_least_100', ~low, 15)]
        elif k == 3:
            positive = frame.vdc1 > frame.vdc2
            negative = frame.vdc1 < frame.vdc2
            assert (positive | negative).all()
            strata = [('vdc1_greater_than_vdc2', positive, 15), ('vdc1_less_than_vdc2', negative, 15)]
        else:
            strata = [('complete_class', np.ones(len(frame), dtype=bool), 30)]
        blocks = []
        ledger = {}
        for j, (name, mask, n) in enumerate(strata):
            indices, info = stratum_selection(frame, ranks, mask, n, k, j)
            blocks.append(indices)
            ledger[name] = {**info, 'selected_source_positions': indices}
        # Interleave the two normal/open strata, rather than exhausting one first.
        selected[k] = [v for pair in zip(*blocks) for v in pair] if len(blocks)==2 else blocks[0]
        selection_ledger[str(k)] = ledger
        assert len(selected[k]) == 30
    all_indices = [v for indices in selected.values() for v in indices]
    assert len(all_indices) == len(set(all_indices)) == 150
    assert len(x.loc[all_indices, CHANNELS].drop_duplicates()) == 150
    assert all(0 <= i < TRAIN[1] for i in all_indices)
    # Freeze selected positions before loading/calling the classifier.
    selection_sha = hashlib.sha256(dumps(selected).encode()).hexdigest()
    rng = np.random.default_rng(SEED + 10000)
    schedule, last = [], None
    for cycle in range(30):
        order = rng.permutation(5)
        if int(order[0]) == last:
            order = np.roll(order, -1)
        for k in order:
            schedule.append((int(k), selected[int(k)][cycle]))
        last = int(order[-1])
    if schedule[-1][0] == schedule[0][0]:
        schedule[-2], schedule[-1] = schedule[-1], schedule[-2]
    assert all(schedule[i][0] != schedule[i-1][0] for i in range(1,150))
    assert schedule[-1][0] != schedule[0][0]
    model = load_model()
    observations, records = [], []
    with parallel_backend('sequential'):
        for position, (k, index) in enumerate(schedule, 1):
            measurements = {c: float(data.at[index, c]) for c in CHANNELS}
            output = predict(measurements, model)
            # Source label is evidence only; inference receives exactly four physical fields.
            assert set(measurements) == set(CHANNELS)
            observations.append({'source_class': k, 'measurements': measurements})
            records.append({'replay_position': position, 'train_source_row_index': index,
                            'ground_truth_class': k, **measurements,
                            'rf_e4_predicted_class': output['predicted_class'],
                            'agrees_with_source': output['predicted_class'] == k,
                            'abs_voltage_difference_V': abs(measurements['vdc1']-measurements['vdc2']),
                            'abs_current_difference_A': abs(measurements['idc1']-measurements['idc2']),
                            'source_irradiance_W_m2': float(data.at[index,'irr'])})
    assert hashlib.sha256(dumps(selected).encode()).hexdigest() == selection_sha
    assert all(Counter(k for k,_ in schedule[i:i+5]) == Counter(range(5)) for i in range(0,150,5))
    public = {'schema_version': 1, 'source': 'historical TRAIN observations',
              'suggested_interval_ms': 5000, 'observations': observations}
    public_text = dumps(public)
    parsed = json.loads(public_text)
    for sample, record in zip(parsed['observations'], records):
        index = record['train_source_row_index']
        assert sample['source_class'] == int(data.at[index,'f_nv'])
        assert all(sample['measurements'][c] == float(data.at[index,c]) for c in CHANNELS)
    agreement, diversity = {}, {}
    for k in range(5):
        group = [r for r in records if r['ground_truth_class']==k]
        indices = [r['train_source_row_index'] for r in group]
        correct = sum(r['agrees_with_source'] for r in group)
        agreement[str(k)] = {'source_label': LABELS[k], 'N':30, 'agreements':correct,
                             'disagreements':30-correct, 'agreement_rate':correct/30,
                             'predicted_class_counts':dict(sorted(Counter(r['rf_e4_predicted_class'] for r in group).items()))}
        diversity[str(k)] = {
            'source_row_index_min':min(indices), 'source_row_index_max':max(indices),
            'irr_below_100_N':sum(r['source_irradiance_W_m2']<100 for r in group),
            'vdc1_greater_than_vdc2_N':sum(r['vdc1']>r['vdc2'] for r in group),
            'vdc1_less_than_vdc2_N':sum(r['vdc1']<r['vdc2'] for r in group),
            'vdc1_equals_vdc2_N':sum(r['vdc1']==r['vdc2'] for r in group),
            'channel_ranges':{c:{'min':float(data.loc[indices,c].min()),'max':float(data.loc[indices,c].max())} for c in CHANNELS},
            'within_class_rank_coverage':{c:{'min':float(rank_frames[k].loc[indices,c].min()),
                                           'max':float(rank_frames[k].loc[indices,c].max()),
                                           'lower_third_N':int((rank_frames[k].loc[indices,c] <= 1/3).sum()),
                                           'middle_third_N':int(((rank_frames[k].loc[indices,c]>1/3)&(rank_frames[k].loc[indices,c]<=2/3)).sum()),
                                           'upper_third_N':int((rank_frames[k].loc[indices,c]>2/3).sum())} for c in RANK_FEATURES}}
    total_correct = sum(r['agrees_with_source'] for r in records)
    assert protected() == original_hashes
    report = {
        'status':'PASS', 'baseline_analysis_commit':BASELINE,
        'raw_csv_sha256':RAW_SHA, 'model_sha256':SHA256, 'seed':SEED,
        'frozen_TRAIN':[0,1006129], 'observation_N':150, 'unique_joint_vectors':150,
        'selection_completed_before_inference':True, 'selection_source_indices_sha256':selection_sha,
        'public_json_sha256':hashlib.sha256(public_text.encode()).hexdigest(),
        'selection_ledger':selection_ledger, 'per_class_agreement':agreement,
        'total_agreement':{'N':150,'agreements':total_correct,'disagreements':150-total_correct,'agreement_rate':total_correct/150},
        'diversity':diversity, 'sequence':{'cycles':30,'observations_per_cycle':5,'every_cycle_all_five_source_classes':True,
                                        'adjacent_source_class_changes':149,'wrap_changes_source_class':schedule[-1][0]!=schedule[0][0],
                                        'all_measurement_vectors_distinct':True,'suggested_display_interval_ms':5000,
                                        'interpretation':'Reordered historical observations; not continuous or real-time acquisition. 30 cycles use30 distinct observations per source class.'},
        'verification':{'exactly_150':True,'each_source_class_30':True,'TRAIN_only':True,
                        'source_measurements_exact_after_JSON_round_trip':True,'no_interpolation_or_synthetic_values':True,
                        'all_predictions_original_model':True,'source_and_predicted_classes_separate':True,
                        'no_timestamps':True,'no_frontend_or_cloud_changes':True,
                        'protected_existing_files_unchanged':len(original_hashes),'model_hash_unchanged':True},
        'regression_verification':{'command':'python -B -m technical_evaluation.prepare_pv_replay --check --tests',
                                   'existing_test_count':50,
                                   'scope':'Regression results are printed by --tests after artifact checks; PASS here certifies data/integrity checks, not a claim that regressions run without --tests.'},
        'protected_sha256':original_hashes,
        'runtime':{'numpy':np.__version__,'pandas':pd.__version__,'python':sys.version.split()[0],
                   'inference':'Existing src.inference.cli.predict and original fitted artifact; sequential joblib context as production, no estimator parameter changes.'},
        'limitations':['Selected TRAIN agreement is not independent model accuracy.',
                       'Balanced diverse sample is not natural prevalence, unbiased random sampling or a continuous physical trace.',
                       'Ground-truth labels are source annotations, not a guarantee of physical causality.',
                       'Selected rows include training observations; the replay cannot validate generalization.',
                       'No selection or replacement is based on model agreement.',
                       'Public JSON omits stored predictions; a future frontend must call Azure and display source_class separately.',
                       'Existing frontend/static build allowlist is unchanged and does not yet serve this new replay JSON.',
                       'Display scheduling, no-overlap request handling, pause/resume and failure behavior remain future frontend work.'],
        'observations':records}
    agreement_rows = [[k,LABELS[k],30,agreement[str(k)]['agreements'],agreement[str(k)]['disagreements'],f"{100*agreement[str(k)]['agreement_rate']:.2f}%"] for k in range(5)]
    diversity_rows = []
    for k in range(5):
        d=diversity[str(k)]
        coverage=d['within_class_rank_coverage']
        diversity_rows.append([k,d['irr_below_100_N'],30-d['irr_below_100_N'],d['vdc1_greater_than_vdc2_N'],d['vdc1_less_than_vdc2_N'],d['vdc1_equals_vdc2_N'],
                               *[f"{coverage[c]['min']:.3f}–{coverage[c]['max']:.3f}" for c in ['vdc1','idc1','abs_voltage_difference','abs_current_difference']]])
    examples = [next(r for r in records if r['ground_truth_class']==k) for k in range(5)]
    example_rows = [[r['ground_truth_class'],r['train_source_row_index'],*[f'{r[c]:.4f}' for c in CHANNELS],r['rf_e4_predicted_class'],r['agrees_with_source']] for r in examples]
    method = f'''# Diverse historical PV replay — selection and verification

## Scope and immutable source

Baseline analysis commit: `{BASELINE}`. Frozen TRAIN positions **[0,1,006,129)** only. Source CSV SHA-256 `{RAW_SHA}`; original RF E4 SHA-256 `{SHA256}`. All {len(original_hashes)} existing tracked files at the baseline remain byte-identical. No original scientific evidence, model, split, preprocessing, frontend or cloud setting changes. Source attribution: [original dataset documentation](../data/raw/README.md). Class4 is natural building shade, an environmental condition rather than hardware failure.

The new [class distributions](PV_Class_Measurement_Ranges.md) are descriptive context. No independent channel intervals are sampled and no interpolation is performed. Every four-channel vector is copied from one complete original TRAIN row. The existing stateless electrical quality convention leaves all TRAIN electrical values unchanged; no scaling/imputation/clipping is applied to published measurements.

## Deterministic selection, before predictions

1. Seed42. For each source class, form a six-coordinate descriptive space from vdc1,vdc2,idc1,idc2,absolute voltage difference and absolute current difference. Each coordinate becomes its **within-class empirical average rank divided by class N**. This handles different units and represents lower/middle/upper observed portions without assuming Gaussian shapes. Correlated inputs and derived differences are intentionally all represented; this geometry is a diversity heuristic, not a statistically optimal sampling design or a model boundary.
2. Normal: select15 actual rows with irradiance<100W/m² and15 with irradiance>=100W/m², using the existing project regime boundary. Open circuit: select15 withvdc1>vdc2 and15 withvdc1<vdc2. Other classes: select30 from the complete class. These are demonstration quotas, not natural frequencies or new classification thresholds.
3. Within each stratum, draw a pool of up to6,000 original rows without replacement, using NumPy SeedSequence([42,class_id,stratum_id]). Add actual rank-coordinate extrema as candidate rows, sort unique source positions, apply a seeded permutation for deterministic tie order, and remove duplicate joint four-input vectors. No classifier is accessed during this stage.
4. Choose the candidate nearest the six-coordinate median point(.5,...,.5), then repeatedly choose the candidate maximizing its minimum squared Euclidean rank-space distance to already selected rows. Coordinates/centers are selection geometry only: no generated physical measurement is displayed. This is a bounded candidate-pool farthest-first heuristic, not a global coverage optimum. The normal/open strata are interleaved.
5. Freeze all150source indices and hash the class-index lists **before loading the model**: `{selection_sha}`. Do not reject, replace or resample any selected row after seeing a prediction.
6. Build30cycles, each containing all five source classes in a seeded permutation (sequence RNGseed10042). Rotate a cycle order if needed to avoid matching the preceding cycle's final class. If the final class equals the first, swap the last two observations, retaining the final cycle's class balance. Every cycle advances to the next distinct observation for each class; no fixed one-row-per-class loop. The sequence has150unique electrical vectors and149adjacent source-class changes. Wrap-around source class change: **{schedule[-1][0]!=schedule[0][0]}**.
7. Run existing `src.inference.cli.predict` for every selected vector using the hash-verified original fitted RF E4. Only the four electrical measurements enter inference. A sequential joblib context matches the existing production execution strategy without changing forest parameters or fitted preprocessing. Record all outputs, including disagreements, in [verification evidence](PV_Replay_Verification.json).

## Agreement — selected TRAIN demonstration only

{markdown_table(['Source class','Label','N','Agreements','Disagreements','Agreement'],agreement_rows)}

Overall: **{total_correct}/150={100*total_correct/150:.2f}%**. This is agreement on a diversity-selected TRAIN subset, **not independent model accuracy**, held-out validation or a confidence guarantee. Source labels and predicted classes remain distinct even when equal. Deliberately balanced and coverage-seeking selection is not representative of natural class prevalence or a continuous PV operating trajectory. No correctly predicted examples were favored after inference.

## Measured diversity

Rank coverage below is [minimum,maximum] of selected observations' empirical ranks within their complete source class. Full coverage and per-coordinate lower/middle/upper-third counts are in the JSON evidence. The third boundaries describe sampling coverage only, not diagnosis thresholds.

{markdown_table(['Class','irr<100 N','irr>=100 N','vdc1>vdc2 N','vdc1<vdc2 N','vdc1=vdc2 N','vdc1 rank','idc1 rank','abs ΔV rank','abs ΔI rank'],diversity_rows)}

The pool and farthest-first procedure generally favors unusual states as well as central ones. This can change agreement relative to a random TRAIN sample. No guarantee of field-representative operating regimes, independent sessions or complete joint support is implied. Source positions are not timestamps or verified days/hours.

## First scheduled example per source class

{markdown_table(['Source class','TRAIN row index','Vdc1(V)','Vdc2(V)','Idc1(A)','Idc2(A)','RF class','Agrees'],example_rows)}

The example table is chosen by sequence position, not correctness. All150rows, irradiance provenance, absolute differences and predictions appear in the verification JSON.

## Public JSON contract and future integration boundary

[pv_historical_replay.json](../web/data/pv_historical_replay.json) contains only schema version, historical-TRAIN disclosure, suggested5000ms demonstration interval and150observations with `source_class` plus `measurements` containing exactly `vdc1,vdc2,idc1,idc2`. Voltage units areV; currents areA. It contains no source-row index, timestamps, cached model predictions, fabricated confidence, irradiance or target field inside the measurement payload. The suggested interval is a UI presentation cadence, **not recorded acquisition timing**.

The future UI must submit **only `observation.measurements`** to the existing Azure API and display source ground truth separately from the actual response's predicted class. The source label must never substitute for a response or be passed as a predictor. Cached verification outputs are not live inference. Retrying, duplicate-request prevention, pausing on failures, cadence/backpressure and separate labels remain unimplemented. At5000ms per observation,150scheduled presentations would nominally span750seconds, excluding waits/pauses; this is not an original recording duration.

The existing static builder explicitly allowlists current assets; this new JSON is **not yet served by the deployed frontend**. Any future bundling/route change requires the next reviewed implementation step. No builder, browser code, API contract, deployment, Azure resource, CORS or model changes occur here.

## Reproduction and checks

Script: [prepare_pv_replay.py](prepare_pv_replay.py). Use the existing pinned Python3.14.10 environment and `technical_evaluation/requirements.txt`; Git must be installed and on PATH. From repository root:

```sh
python -B -m technical_evaluation.prepare_pv_replay
python -B -m technical_evaluation.prepare_pv_replay --check --tests
```

Generation writes only the three new deliverables. `--check` recalculates selection, sequencing, all150original-model predictions and full source/protected-file checks, then demands byte-identical public JSON, evidence and method report without writing. `--tests` runs50existing relevant regressions across technical evaluation, local inference, webAPI, container context, Azure settings contracts and static frontend boundary. It performs no deployment or cloud mutation. Output hashing and frozen populations are verified on every run. Runtime versions and original-file hashes are preserved in evidence. All150selected positions are<1,006,129; VALIDATION/TEST rows are not used for selection or evaluation.
'''
    outputs={PUBLIC:public_text,EVIDENCE:dumps(report),METHOD:method}
    for name,text in outputs.items():
        path=ROOT/name
        if args.check:
            assert path.read_bytes()==text.encode('utf8'), 'Generated output differs: '+name
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(text.encode('utf8'))
    if args.tests:
        suites=[['technical_evaluation.tests','technical_evaluation.refinement.tests'],['discover','-s','tests'],['discover','-s','web/tests'],
                ['deployment.azure.test_context','deployment.azure.test_deployment','deployment.decoupled.test_backend','deployment.decoupled.test_frontend']]
        for suite in suites:
            subprocess.run([sys.executable,'-B','-m','unittest',*suite],cwd=ROOT,check=True)
    print(dumps({'status':'PASS','mode':'check' if args.check else 'generate','N':150,'agreement':report['total_agreement'],
                 'per_class':agreement,'examples':examples,'tests_passed':50 if args.tests else 'not requested'}))


if __name__=='__main__':
    main()
