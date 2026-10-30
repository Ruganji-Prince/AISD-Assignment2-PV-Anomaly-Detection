# Controlled Reconstruction Study

Models are reconstructed RF E4 and reconstructed LightGBM E4, never recovered originals.

Source commit: `34ab15ed18abb29defc0f30baa284f189fc05aef`. Exact recorded Python and model dependencies verified before fitting. Immutable raw CSV and TRAIN/VALIDATION/TEST counts verified. Full parameters, partition bounds, class weights and dependency versions are in `Reconstruction_Verification.json`.

The original Stage 2 constructor depends on a missing Stage 1 estimator cache. The reconstruction explicitly replaces that cache-cloning step with an unfitted estimator constructed from the complete frozen parameter projection, then clones it. It uses the unchanged original `build_preprocessor` factory and `AblationModel.fit` method. No original source is edited; no F6 selection or threshold selection is rerun. This adaptation is recorded, rather than treating a new model as an original binary.

The original fit method restricts fitting to all 1,006,129 TRAIN rows and verifies label counts, estimator parameters and feature dimension. FrozenPredictor is used for authorized clean TEST prediction. All newly fitted models and prediction arrays are isolated under the local-only reconstruction workspace.

Exact confusion-count agreement is the primary clean reproduction check. Aggregate confusion counts cannot establish the actual number of per-observation changed predictions when historical row-level predictions are unavailable; half the confusion L1 difference is only a lower bound on necessary changed classifications. A zero bound does not prove identical row-level predictions.

Binary identity with the lost originals is NOT ESTABLISHED, irrespective of behavioral classification. The existing artifact-gate and recovery records are preserved.

## Behavioral gate completed

| Reconstruction | Gate | Macro-F1 difference | Recall differences: short/degradation/open | Max confusion-cell difference | Hardware-alert AP difference |
| --- | --- | --- | --- | --- | --- |
| Reconstructed RF E4 | B | 0.000000000000 | 0.000000000000/0.000000000000/0.000000000000 | 0 | -0.000000089591 |
| Reconstructed LightGBM E4 | A | 0.000000000000 | 0.000000000000/0.000000000000/0.000000000000 | 0 | 0.000000000000 |

Both gates passed. The noise study uses these behaviorally verified reconstructed models exclusively; original results and artifacts are not replaced.

## Local reproduction and public package scope

The historical fitted artifacts were not recovered. Reconstruction used the exact recorded environment, frozen TRAIN data/settings, unchanged preprocessing factory and fit method. The constructor adaptation and behavioral gates are recorded above. Binary identity with the historical artifacts is NOT ESTABLISHED. All fitting was TRAIN-only; preprocessing and thresholds were frozen during clean TEST and noisy evaluation.

The public package contains source and completed evidence, not fitted models, a dependency environment, or original per-row prediction arrays. Choose an ignored/external local workspace. First ensure the source commit `34ab15ed18abb29defc0f30baa284f189fc05aef` is available in local Git history. Use Python 3.14.7 and the exact model dependencies recorded in `Reconstruction_Verification.json`; the original complete lock remains at `phase2_implementation/stage1/requirements-stage1-lock.txt` in the frozen commit.

With `LOCAL_WORKSPACE` replaced by a new local directory, the explicit commands are:

```text
python phase2_implementation/noise_robustness/prepare_reconstruction_workspace.py --work-dir LOCAL_WORKSPACE
python phase2_implementation/noise_robustness/reconstruct_models.py --work-dir LOCAL_WORKSPACE
python phase2_implementation/noise_robustness/run_noise_robustness.py --work-dir LOCAL_WORKSPACE
python phase2_implementation/noise_robustness/render_noise_results.py
```

Use a separate fresh repository copy for a new execution: these entry points write new analysis outputs and must not overwrite reviewed evidence. Reconstruction refuses to overwrite an existing fitted artifact, and the noise runner requires both behavioral gates to pass. These are documented future reproduction commands; none was run for publication. Presentation rendering alone reads completed CSVs and does not fit or predict. Reconstructed models remain private/local in the selected workspace's `models/` subdirectory.

The four response plots and three tables now visibly include shared coverage (100.0000%, 92.1941 ± 0.0737%, 84.4133 ± 0.0997%, 74.7809 ± 0.1046%, 69.5123 ± 0.1124%). Coverage decreases because unchanged input-quality rules can convert noise-induced negative electrical readings to missing values and trigger abstention. Interpret the results as end-to-end pipeline robustness under Gaussian sensor noise, including existing input-quality/abstention rules. Building Shade remains environmental. No universal robustness or binary-identity claim is made. No evaluated configuration satisfied all predeclared engineering criteria.
