# Technical defense guide

## Problem and immutable foundation

The task predicts one of five nominal conditions from a source-position observation. The CSV contains 1,373,798 observations, six physical predictors and f_nv. Class4 is natural building shade, an environmental condition rather than hardware failure. Voltage/current quantities follow the original source terminology. The public inference endpoint requires four finite nonnegative electrical values in V/A and rejects target, index and metadata inputs.

The original RF artifact and fitted preprocessing remain byte-identical. The model hash is 55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb. The [model provenance](../../models/rf_e4/provenance.json), [protected baseline](../refinement/Baseline.json) and [source inventory](../../phase1_strategy/Variable_Inventory.csv) establish the foundation.

## Rubric1: hygiene and dependencies

Zero conventional NaNs/infinities does not prove MCAR or uninterrupted monitoring. Constant missingness indicators make Little MCAR and missingness CramerV unidentifiable. The62 paired irradiance/temperature zeros remain suspicious observations; the slight negative irradiance receives the original quality convention, and valid negative Celsius values are retained.

TRAIN-only IQR/Z/MAD, correlations, VIF, MI and PCA are in [feature evidence](../evidence/rubric1). IQR clipping did not improve validation macro-F1; quantile clipping slightly reduced it. Fault extremes may encode the target condition. No automatic deletion or winsorization was introduced. Correlated sensors are retained according to physical dependencies and ablation evidence; PCA is mathematical, not physical sensor reduction.

## Rubric2: split and leakage

TRAIN[0,1006129), VAL[1056990,1173967), TEST[1227337,1373798), with 104231 excluded positions. Sixteen signal-defined blocks are not dates/sessions/hours. Block13 selects model/settings; block 14 originally selects hardware threshold. Pipeline transformations/weights fit TRAIN or each training fold only. [Exact overlap](../evidence/rubric2/leakage.json) is zero. [Full near-duplicate checks](../refinement/results/full_near_duplicates.json) query every later-partition row against every TRAIN row using TRAIN scaling; similar sensor states remain and are not silently removed.

Grouped folds expose a structural support problem: class 1 appears only in TRAIN block 12. A fold withholding that block cannot learn class 1; the RF fold's supported-class F1 is approximately.512. This is a limitation of available experimental support, not a reason to randomize rows or fabricate sessions. Historical TEST exposure remains disclosed; no independent generalization estimate is claimed.

## Rubric3: models, metrics and calibration

RF E4 was selected by the original validation sensing/performance rule among21 evaluated alternatives. It uses four physical channels and eight mathematical features, the extra four being missingness indicators. This is not a globally minimal sensor proof. Compare E4 families separately from F6 references. [All21 public reconstructions](../refinement/results/public_reconstruction.json) are new fits. Three first-pass LR differences disappeared after restoring the original two-thread BLAS control; [both passes remain](../refinement/results/LR_thread_sensitivity.json). Matching validation F1 does not establish model byte identity.

Macro-F1 balances classes; weighted F1 reflects prevalence; AP is not trapezoidal PR area. Hardware score p1+p2+p3 excludes shade. The archived threshold is.5913558658757772, selected on block 14 with a nonhardware-FPR constraint. Public API classification is multiclass argmax and does not deploy that binary alert policy.

Classwise sigmoid/isotonic calibration uses only block 14, four purged source-tile cross-fitting folds and support guards, then probability renormalization. Sigmoid selection uses OOF logloss before retrospective TEST diagnostics. Maps remain experimental, with no calibrated UI confidence or calibrated threshold. [Reproduced calibration](../refinement/results/calibration/calibration_TEST_retrospective.json) matches previous Brier/logloss/ECE within 1e-12. A source tile is not an independent session.

The [1000-resample sensitivity](../refinement/results/bootstrap_sensitivity.json) compares fixed-five, supported-class and all-five-supported conditional summaries over12 TRAIN grouped-OOF block confusions. None is a confidence interval for deployed TEST F1 or established independent-site coverage.

## Rubric4: errors and stress

TEST has 6604 normal-to-shade errors and shade precision.691081. Subgroups and TRAIN-decile PSI/KS/Wasserstein identify measured cohort differences, not causal mechanisms or verified temporal drift. Noise/bias/dropout/saturation/OOD tests are simulated, and label preservation under extreme perturbation is an assumption. A contiguous missing-channel sequence leaves only the first two positions eligible; sparse sampled gaps reset that eligibility, so86.42% sampled coverage is not outage tolerance.

Archived raw-channel permutation and LightGBM SHAP were reproduced; additional RF permutation evaluates raw physical channel dependencies through the full fitted pipeline. Importance is not causality. The fixed [TRAIN empirical generator](../refinement/results/empirical_scenarios.json) samples whole class-conditional rows and shared voltage/current gains without rejection.249/250 conditioning agreement is a demonstration statistic, not validated fault-simulator accuracy.

## Rubric5: execution and cloud

The four-step HTML/CSS/JS frontend calls FastAPI `/api/predict`. The fixed model is SHA256 checked before unpickling; arbitrary serialized uploads are impossible. The [runtime lock](../../web/requirements.lock) pins the complete inference closure with hashes; original scientific versions are unchanged. [Container evidence](../refinement/results/container_matrix.json) records actual Linux image builds, nonroot/read-only execution, API/CLI/Vercel fixture parity and 200 TRAIN probability comparisons. Standard public GitHub runners are free; no image registry/artifact storage or paid runner is used.

`Server-Timing` separates body/validation, frame construction, preprocessing, forest execution, initialization and middleware-to-response-header wall time. A process identifier and initialization marker distinguish observed model-cache initialization from warm calls. Full platform startup/network/billedCPU are not inferred from those measurements. Thread-local joblib sequential execution avoids single-observation dispatch overhead without changing estimator parameters/fitted state or argmax policy. Original10ms/10MiB targets remain unmet for the complete application/model; forest-only timing is a different quantity.

API safeguards include2KB bodies,5s body deadline,15s inference-response deadline and two-active-inferences/process. Worker completion releases capacity even if the response deadline expires. These are local safeguards, not distributed IP/user rate limits. [Rate-limit review](../refinement/Rate_Limit_Review.json) documents the provider option and unactivated pricing review. No paid service or firewall/billing setting was changed.
