"""Deterministic descriptive electrical ranges, frozen TRAIN only; no model fitting.

From repository root:
    python -B -m technical_evaluation.class_measurement_ranges
    python -B -m technical_evaluation.class_measurement_ranges --check
"""
import argparse
import hashlib
import io
from itertools import combinations
from pathlib import Path
import platform

import numpy as np
import pandas as pd

from src.preprocessing.common import TRAIN
from src.phase2_stage1.contracts import TRAIN_COUNTS
from src.transformers import RetainedQuality

ROOT = Path(__file__).resolve().parents[1]
CHANNELS = ['vdc1', 'vdc2', 'idc1', 'idc2']
LABELS = ['Normal operation', 'Short circuit', 'Resistive degradation',
          'Open circuit', 'Natural building shade']
RAW_SHA = '717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a'
MODEL_SHA = '55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb'
STAT_KEYS = ['min', 'p05', 'p25', 'median', 'p75', 'p95', 'max', 'mean', 'std_sample']


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()


def summary(values):
    a = np.asarray(values, dtype=np.float64)
    assert len(a) > 1 and np.isfinite(a).all()
    q = np.quantile(a, [0, .05, .25, .5, .75, .95, 1], method='linear')
    return dict(zip(STAT_KEYS, [*map(float, q), float(a.mean()), float(a.std(ddof=1))]))


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '| ' + ' | '.join(['---'] * len(headers)) + ' |',
                      *['| ' + ' | '.join(map(str, r)) + ' |' for r in rows]])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Recalculate and compare both outputs without writing.')
    args = parser.parse_args()
    assert TRAIN == (0, 1006129), 'Frozen TRAIN changed'
    path = ROOT / 'data/raw/pv_fault_dataset.csv'
    assert sha(path) == RAW_SHA, 'Original CSV hash mismatch'
    assert sha(ROOT / 'models/rf_e4/model.pkl') == MODEL_SHA, 'Original model hash mismatch'
    # Only TRAIN measurements are parsed; whole-file hashing above checks byte integrity only.
    train = pd.read_csv(path, nrows=TRAIN[1], float_precision='round_trip')
    assert len(train) == TRAIN[1] and list(train) == CHANNELS + ['irr', 'pvt', 'f_nv']
    counts = {int(k): int(v) for k, v in train.f_nv.value_counts().sort_index().items()}
    assert counts == TRAIN_COUNTS
    electrical = train[CHANNELS]
    clean = RetainedQuality(CHANNELS).transform(electrical)
    assert np.isfinite(electrical.to_numpy()).all() and (electrical.to_numpy() >= 0).all()
    assert np.array_equal(clean.to_numpy(), electrical.to_numpy()), 'Quality changed electrical data; review before describing raw distributions'
    assert clean.isna().sum().sum() == 0
    rows, derived_rows, joint_rows, regimes = [], [], [], []
    stats, difference_stats = {}, {}
    for k, label in enumerate(LABELS):
        x = clean.loc[train.f_nv == k]
        for channel in CHANNELS:
            s = summary(x[channel])
            stats[k, channel] = s
            rows.append({'class': k, 'class_label': label, 'channel': channel,
                         'unit': 'V' if channel.startswith('vdc') else 'A',
                         'n_observations': len(x), **s})
        dv, di = x.vdc1 - x.vdc2, x.idc1 - x.idc2
        for name, unit, values in [('vdc1-vdc2', 'V', dv), ('abs(vdc1-vdc2)', 'V', abs(dv)),
                                   ('idc1-idc2', 'A', di), ('abs(idc1-idc2)', 'A', abs(di))]:
            s = summary(values)
            difference_stats[k, name] = s
            derived_rows.append([k, name, unit, len(x), *[f'{s[z]:.4f}' for z in STAT_KEYS]])
        joint_rows.append([k, len(x), *[f'{a.corr(b, method=method):.6f}'
                            for a, b in [(x.vdc1, x.vdc2), (x.idc1, x.idc2), (dv, di)]
                            for method in ['pearson', 'spearman']]])
        low = int((train.loc[train.f_nv == k, 'irr'] < 100).sum())
        regimes.append([k, label, len(x), low, f'{100 * low / len(x):.4f}%'])
    df = pd.DataFrame(rows)
    csv = df.to_csv(index=False, float_format='%.17g', lineterminator='\n')
    # In-memory CSV round-trip catches lost columns/values at published precision.
    back = pd.read_csv(io.StringIO(csv), float_precision='round_trip')
    assert len(back) == 20 and list(back) == list(df)
    np.testing.assert_array_equal(back[STAT_KEYS].to_numpy(), df[STAT_KEYS].to_numpy())
    overlap_rows = []
    full_overlaps = {c: 0 for c in CHANNELS}
    for a, b in combinations(range(5), 2):
        for channel in CHANNELS:
            sa, sb = stats[a, channel], stats[b, channel]
            full_overlaps[channel] += int(max(sa['min'], sb['min']) <= min(sa['max'], sb['max']))
            lo, hi = max(sa['p05'], sb['p05']), min(sa['p95'], sb['p95'])
            fractions = []
            for k in [a, b]:
                v = clean.loc[train.f_nv == k, channel]
                fractions.append(f'{100 * ((v >= lo) & (v <= hi)).mean():.4f}%' if lo <= hi else '0.0000%')
            overlap_rows.append([f'{a} / {b}', channel, 'V' if channel.startswith('vdc') else 'A',
                                 f'[{lo:.4f}, {hi:.4f}]' if lo <= hi else 'None', *fractions])
    heads = ['Class', 'Channel', 'Unit', 'N', 'Min', 'P5', 'P25', 'Median', 'P75', 'P95', 'Max', 'Mean', 'Sample SD']
    physical_rows = [[r['class'], r['channel'], r['unit'], r['n_observations'], *[f'{r[z]:.4f}' for z in STAT_KEYS]] for r in rows]
    oc = clean.loc[train.f_nv == 3]
    oc_voltage_positive = int((oc.vdc1 > oc.vdc2).sum())
    oc_voltage_negative = int((oc.vdc1 < oc.vdc2).sum())
    report = f'''# PV class measurement ranges — frozen TRAIN only

## Scope and provenance

Source: [original CSV](../data/raw/pv_fault_dataset.csv), SHA-256 `{RAW_SHA}`. Dataset attribution: [source repository](https://github.com/clayton-h-costa/pv_fault_dataset), [Lazzaretti et al. (2020)](https://doi.org/10.3390/s20174688); preserved [source documentation](../phase1_strategy/PRIMARY_SOURCE_README.md).

The prediction unit is one exported observation. Only source positions **[0, 1006129)**, N=1,006,129, are analyzed. VALIDATION and TEST measurements are not loaded or used for summaries, interpretation-based selection or threshold design. Whole-CSV hashing verifies immutable bytes, not held-out measurement statistics. The complete frozen TRAIN interval is retained, including its background/low-irradiance observations; no operating-state or eligibility filtering, random resampling, class balancing or block deletion is applied. Labels are nominal, not ordinal. Class 4 is an environmental condition, not a hardware fault. Source order is not a verified timestamp, day, session or hour.

The existing [RetainedQuality convention](../src/transformers.py) is applied to the four electrical channels: nonfinite and negative electrical inputs would become NaN. TRAIN has **zero** such electrical inputs; quality output equals original electrical measurements exactly. Therefore no imputation, scaling, clipping, winsorization or outlier deletion is needed or applied for these physical-unit summaries. Medians are not fitted separately by class for inference. No model is loaded, fitted or queried. Original model SHA-256 is verified as `{MODEL_SHA}`; no model bytes change.

## Calculation definitions and reproduction

- N is the number of TRAIN rows carrying the given class label; all four electrical channels have N valid observations, with no missing-value denominator change.
- Min/max are observed extrema, not physical validity limits or guaranteed classification thresholds.
- P5/P25/median/P75/P95 use NumPy `quantile(method="linear")`: for sorted x and q, h=(N−1)q, interpolate linearly between floor(h) and ceil(h). Median is q=.5.
- Mean is sum(x)/N; sample SD is sqrt(sum((x−mean)²)/(N−1)), `ddof=1`. SD is descriptive; dependent acquisition rows do not constitute N independent replicates or justify iid confidence intervals.
- Signed differences use the same row: ΔV=vdc1−vdc2 and ΔI=idc1−idc2. Absolute differences retain magnitude without direction. No voltage/current ratio with a near-zero denominator is introduced.
- Correlations are within-class Pearson and average-rank Spearman, computed pairwise on complete TRAIN electrical values. Descriptive association is not causal evidence or a hypothesis test.
- The overlap screen intersects each pair of classes' marginal [P5,P95] intervals. Fractions count each class's actual readings inclusively inside that intersection. These are interval-occupancy summaries, not density-overlap coefficients, classifier error rates or new decision thresholds.
- Tables round to four decimals (correlations six); [CSV](PV_Class_Measurement_Ranges.csv) uses 17 significant digits for all 20 physical-channel summaries. Derived/overlap tables are regenerated directly from the unrounded arrays, not rounded table entries.

Deterministic script: [class_measurement_ranges.py](class_measurement_ranges.py). No sampling, RNG, network access, model fitting, timestamps or environment-specific absolute paths are used. Verified runtime: Python {platform.python_version()}, NumPy {np.__version__}, pandas {pd.__version__}. Existing installation: `uv venv --python 3.14.10 .venv`, then `uv pip install --python .venv -r technical_evaluation/requirements.txt`.

From the repository root, using that environment:

```sh
python -B -m technical_evaluation.class_measurement_ranges
python -B -m technical_evaluation.class_measurement_ranges --check
```

The first command writes only this new Markdown report and its CSV. `--check` recomputes both and verifies byte-identical output without writing. Raw CSV/model hashes, split constants, frozen class counts, unchanged quality values and lossless CSV round-trip are checked on every run. Scientific reports, historical results and frontend files are not modified.

## Class support and existing irradiance regime

{table(['Class', 'Label', 'N', 'irr <100 W/m²: N', 'Fraction of class'], regimes)}

The 100 W/m² boundary is the existing project regime/separator boundary, used only to describe support here. The rule does not become an electrical classification threshold and does not filter these summaries. Mixed operating regimes can make class extrema and means misleading without quantiles and joint relationships.

## Observed physical-channel distributions

{table(heads, physical_rows)}

## Joint electrical differences

{table(heads, derived_rows)}

Signed values distinguish which channel is larger; absolute values quantify imbalance. These are same-observation relationships, not differences of independently sampled class averages. Marginal quantile boxes do not recover a full four-dimensional joint distribution.

{table(['Class', 'N', 'V pair Pearson', 'V pair Spearman', 'I pair Pearson', 'I pair Spearman', 'ΔV/ΔI Pearson', 'ΔV/ΔI Spearman'], joint_rows)}

## Distribution overlap

Number of class pairs with intersecting full observed min–max ranges (out of 10 pairs per channel): {', '.join(f'{c}={v}/10' for c, v in full_overlaps.items())}. Extrema can be driven by a few unusual observations; central intervals give a different, still descriptive view.

{table(['Classes A / B', 'Channel', 'Unit', 'Intersection of P5–P95 intervals', 'A observations inside', 'B observations inside'], overlap_rows)}

“None” means only that the two **central marginal intervals** do not intersect. Tails can still overlap, and absence of overlap in one marginal summary does not certify a separator, fault mechanism or generalization to another acquisition regime. Conversely, overlapping central intervals do not imply identical multivariate distributions. Interval intersections across different channels need not describe the same observations.

## Class-specific descriptive findings

- **Normal operation:** 615,051/844,805 observations (72.8039%) have irradiance below the existing 100 W/m² regime boundary. The vdc1 median is {stats[0, 'vdc1']['median']:.4f} V but the mean is {stats[0, 'vdc1']['mean']:.4f} V and P75 is {stats[0, 'vdc1']['p75']:.4f} V. This marked regime mixture makes a single “normal voltage band” misleading. Median absolute voltage/current differences are {difference_stats[0, 'abs(vdc1-vdc2)']['median']:.4f} V / {difference_stats[0, 'abs(idc1-idc2)']['median']:.4f} A.
- **Short circuit:** the median signed voltage difference is {difference_stats[1, 'vdc1-vdc2']['median']:.4f} V, compared with {difference_stats[2, 'vdc1-vdc2']['median']:.4f} V for resistive degradation. However, the classes' vdc1 central intervals intersect at [{max(stats[1, 'vdc1']['p05'], stats[2, 'vdc1']['p05']):.4f}, {min(stats[1, 'vdc1']['p95'], stats[2, 'vdc1']['p95']):.4f}] V and their current distributions also overlap. These contrasts describe sampled operating states, not a diagnostic cutoff.
- **Resistive degradation:** median absolute current difference is {difference_stats[2, 'abs(idc1-idc2)']['median']:.4f} A. Its vdc2 extrema [{stats[2, 'vdc2']['min']:.4f}, {stats[2, 'vdc2']['max']:.4f}] V are much broader than its central interval [{stats[2, 'vdc2']['p05']:.4f}, {stats[2, 'vdc2']['p95']:.4f}] V, demonstrating why extrema alone are poor representative ranges. No unusual observation is deleted here.
- **Open circuit:** {oc_voltage_positive} observations have vdc1>vdc2 and {oc_voltage_negative} have vdc1<vdc2. Median absolute differences are {difference_stats[3, 'abs(vdc1-vdc2)']['median']:.4f} V and {difference_stats[3, 'abs(idc1-idc2)']['median']:.4f} A, despite signed means of only {difference_stats[3, 'vdc1-vdc2']['mean']:.4f} V and {difference_stats[3, 'idc1-idc2']['mean']:.4f} A. Opposite difference directions cancel in the signed means; the absolute values and near-perfect negative pairwise Pearson correlations expose the paired structure. The labels alone do not establish the physical cause of each individual observation.
- **Natural building shade:** median absolute voltage/current differences are {difference_stats[4, 'abs(vdc1-vdc2)']['median']:.4f} V / {difference_stats[4, 'abs(idc1-idc2)']['median']:.4f} A. Its vdc1 central interval intersects normal at [{max(stats[0, 'vdc1']['p05'], stats[4, 'vdc1']['p05']):.4f}, {min(stats[0, 'vdc1']['p95'], stats[4, 'vdc1']['p95']):.4f}] V; all four normal/shade central marginal intervals overlap. Shade remains environmental, and electrical overlap prevents a guaranteed class-specific UI input range.

## Interpretation boundary

The tables describe observed **P(measurements | class, TRAIN)**, not the reverse classification probability or the Random Forest decision boundaries. A forest combines learned feature splits across trees, fitted TRAIN preprocessing and class weighting; its boundaries cannot be inferred from class-specific min/max, medians or percentile intervals. Normal and shade can overlap in electrical space, and relative channel relationships must be considered alongside marginal distributions. Any visual range illustration must remain descriptive and must not promise a returned class for arbitrary values inside a range.

No new classifier rule, confidence estimate, feature selection, threshold optimization or deployment change is proposed. Existing TEST-exposure and lack-of-independent-session limitations remain unchanged. These summaries are not a held-out evaluation, a safety envelope, physical causality or field-validated fault limits. Frontend implementation is intentionally deferred until review of the actual distributions.
'''
    outputs = {'PV_Class_Measurement_Ranges.csv': csv, 'PV_Class_Measurement_Ranges.md': report}
    for name, content in outputs.items():
        dest = ROOT / 'technical_evaluation' / name
        expected = content.encode('utf8')
        if args.check:
            assert dest.read_bytes() == expected, f'Output differs: {name}'
        else:
            dest.write_bytes(expected)
    print('PASS: frozen TRAIN; 20 physical summaries; 20 difference summaries; 40 pair/channel overlap checks; ' + ('byte-identical outputs' if args.check else 'two outputs written'))
    print(df.to_string(index=False, float_format=lambda x: f'{x:.4f}'))


if __name__ == '__main__':
    main()
