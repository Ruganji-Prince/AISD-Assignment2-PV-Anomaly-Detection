# Diverse historical PV replay — selection and verification

## Scope and immutable source

Baseline analysis commit: `b597ffa13a0de541ce20edc964f44dde618c7cce`. Frozen TRAIN positions **[0,1,006,129)** only. Source CSV SHA-256 `717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a`; original RF E4 SHA-256 `55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb`. All 592 existing tracked files at the baseline remain byte-identical. No original scientific evidence, model, split, preprocessing, frontend or cloud setting changes. Source attribution: [original dataset documentation](../data/raw/README.md). Class4 is natural building shade, an environmental condition rather than hardware failure.

The new [class distributions](PV_Class_Measurement_Ranges.md) are descriptive context. No independent channel intervals are sampled and no interpolation is performed. Every four-channel vector is copied from one complete original TRAIN row. The existing stateless electrical quality convention leaves all TRAIN electrical values unchanged; no scaling/imputation/clipping is applied to published measurements.

## Deterministic selection, before predictions

1. Seed42. For each source class, form a six-coordinate descriptive space from vdc1,vdc2,idc1,idc2,absolute voltage difference and absolute current difference. Each coordinate becomes its **within-class empirical average rank divided by class N**. This handles different units and represents lower/middle/upper observed portions without assuming Gaussian shapes. Correlated inputs and derived differences are intentionally all represented; this geometry is a diversity heuristic, not a statistically optimal sampling design or a model boundary.
2. Normal: select15 actual rows with irradiance<100W/m² and15 with irradiance>=100W/m², using the existing project regime boundary. Open circuit: select15 withvdc1>vdc2 and15 withvdc1<vdc2. Other classes: select30 from the complete class. These are demonstration quotas, not natural frequencies or new classification thresholds.
3. Within each stratum, draw a pool of up to6,000 original rows without replacement, using NumPy SeedSequence([42,class_id,stratum_id]). Add actual rank-coordinate extrema as candidate rows, sort unique source positions, apply a seeded permutation for deterministic tie order, and remove duplicate joint four-input vectors. No classifier is accessed during this stage.
4. Choose the candidate nearest the six-coordinate median point(.5,...,.5), then repeatedly choose the candidate maximizing its minimum squared Euclidean rank-space distance to already selected rows. Coordinates/centers are selection geometry only: no generated physical measurement is displayed. This is a bounded candidate-pool farthest-first heuristic, not a global coverage optimum. The normal/open strata are interleaved.
5. Freeze all150source indices and hash the class-index lists **before loading the model**: `00df25b5f43f0ab0c6b18a6af8a51112f09d5ac6b8cab8c8f4cfe5a00dc402ec`. Do not reject, replace or resample any selected row after seeing a prediction.
6. Build30cycles, each containing all five source classes in a seeded permutation (sequence RNGseed10042). Rotate a cycle order if needed to avoid matching the preceding cycle's final class. If the final class equals the first, swap the last two observations, retaining the final cycle's class balance. Every cycle advances to the next distinct observation for each class; no fixed one-row-per-class loop. The sequence has150unique electrical vectors and149adjacent source-class changes. Wrap-around source class change: **True**.
7. Run existing `src.inference.cli.predict` for every selected vector using the hash-verified original fitted RF E4. Only the four electrical measurements enter inference. A sequential joblib context matches the existing production execution strategy without changing forest parameters or fitted preprocessing. Record all outputs, including disagreements, in [verification evidence](PV_Replay_Verification.json).

## Agreement — selected TRAIN demonstration only

| Source class | Label | N | Agreements | Disagreements | Agreement |
| --- | --- | --- | --- | --- | --- |
| 0 | Normal operation | 30 | 24 | 6 | 80.00% |
| 1 | Short circuit | 30 | 30 | 0 | 100.00% |
| 2 | Resistive degradation | 30 | 27 | 3 | 90.00% |
| 3 | Open circuit | 30 | 30 | 0 | 100.00% |
| 4 | Natural building shade | 30 | 26 | 4 | 86.67% |

Overall: **137/150=91.33%**. This is agreement on a diversity-selected TRAIN subset, **not independent model accuracy**, held-out validation or a confidence guarantee. Source labels and predicted classes remain distinct even when equal. Deliberately balanced and coverage-seeking selection is not representative of natural class prevalence or a continuous PV operating trajectory. No correctly predicted examples were favored after inference.

## Measured diversity

Rank coverage below is [minimum,maximum] of selected observations' empirical ranks within their complete source class. Full coverage and per-coordinate lower/middle/upper-third counts are in the JSON evidence. The third boundaries describe sampling coverage only, not diagnosis thresholds.

| Class | irr<100 N | irr>=100 N | vdc1>vdc2 N | vdc1<vdc2 N | vdc1=vdc2 N | vdc1 rank | idc1 rank | abs ΔV rank | abs ΔI rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 15 | 15 | 18 | 11 | 1 | 0.037–0.997 | 0.000–0.991 | 0.000–1.000 | 0.003–0.988 |
| 1 | 0 | 30 | 30 | 0 | 0 | 0.002–0.999 | 0.003–0.996 | 0.006–1.000 | 0.002–0.996 |
| 2 | 0 | 30 | 27 | 3 | 0 | 0.001–0.998 | 0.000–1.000 | 0.033–1.000 | 0.001–1.000 |
| 3 | 0 | 30 | 15 | 15 | 0 | 0.001–1.000 | 0.017–1.000 | 0.007–0.982 | 0.002–1.000 |
| 4 | 1 | 29 | 16 | 14 | 0 | 0.001–0.995 | 0.001–1.000 | 0.002–1.000 | 0.003–1.000 |

The pool and farthest-first procedure generally favors unusual states as well as central ones. This can change agreement relative to a random TRAIN sample. No guarantee of field-representative operating regimes, independent sessions or complete joint support is implied. Source positions are not timestamps or verified days/hours.

## First scheduled example per source class

| Source class | TRAIN row index | Vdc1(V) | Vdc2(V) | Idc1(A) | Idc2(A) | RF class | Agrees |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 696020 | 1.7618 | 2.4247 | 0.0996 | 0.0385 | 0 | True |
| 1 | 991164 | 263.3410 | 204.2860 | 9.2173 | 8.9151 | 1 | True |
| 2 | 816818 | 254.5840 | 236.1210 | 8.9037 | 8.3712 | 2 | True |
| 3 | 992843 | 265.3300 | 2.1770 | 9.0215 | 0.0478 | 3 | True |
| 4 | 657590 | 277.6830 | 300.5190 | 4.6586 | 2.5762 | 4 | True |

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
