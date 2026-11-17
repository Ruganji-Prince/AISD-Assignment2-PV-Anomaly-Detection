# Model selection and beginning of deployment

## Scope and evidence status

**REPRODUCED:** original LR F6, RF E4 and LightGBM E4 TEST predictions; all 21 sensor-ablation block-13 validation scores; original TRAIN imputer statistics; fitted-model hashes; fixed-threshold block-14 counts. No training, parameter search, threshold search or new scientific experiment was performed during recovery. Original outputs were retained; verification outputs are separate.

**Critical limitation:** the historical TEST partition had already been inspected before the revised protocol. Revised model/sensor selection used block 13 and threshold selection used block 14, with frozen receipts before revised TEST evaluation, but prior human knowledge cannot be ruled out. These are retrospective estimates, not pristine independent or prospective generalization measurements. No model passed all predeclared engineering criteria.

The integration starts from public preprocessing commit `b7a1f634bc529784f6cf9ec0041c4c76d9f356e6`, preserving the ten intervening preprocessing commits after `59db34fefee55aea48fd3a8d4adbf9042e9d96e5`. Original scientific code/evidence was recovered from `cf5d0ac4b66a98ddbc2fc03653cb8b90f4a9980b`; model bytes were checked against the preserved pre-compliance hash record. Original models are distinct from later reconstructed noise-study models.

## Dataset and partition protocol

The clayton-h-costa/pv_fault_dataset release associated with Lazzaretti et al. (2020) contains 1,373,798 observations, six continuous predictors and nominal target `f_nv`. Labels: 0 normal, 1 short circuit, 2 resistive degradation, 3 open circuit, 4 natural building shade. Class 4 is environmental, not hardware failure. Source/source-license links remain in the [raw-data guide](../data/raw/README.md).

| Partition | Half-open source positions | N | Purpose |
| --- | --- | --- | --- |
| TRAIN | [0,1006129) | 1,006,129 | Fit quality-compatible median, scaling and classifiers |
| VALIDATION | [1056990,1173967) | 116,977 | Reserved validation range |
| VALIDATION block 13 | [1056990,1089790) | 32,800 | Model settings, sensor comparisons and explanations |
| VALIDATION block 14 | [1140571,1173967) | 33,396 | Hardware-alert threshold selection |
| TEST | [1227337,1373798) | 146,461 | Frozen retrospective reporting |

The remaining positions inside the full validation range are not used to select models or thresholds. Excluded split separator gaps total 104,231 positions. Sixteen signal-defined blocks are not verified days, sessions or hours. Released files lack timestamps; source order does not establish uninterrupted one-second spacing. No random repartitioning occurred. TRAIN, validation and TEST indices are disjoint.

The 62 paired irradiance/temperature zeros remain observed, not declared missing. The small negative irradiance reading follows the existing [-1,0) clamp convention. No automatic outlier removal/capping or source population filtering was added. Training class counts are 844805, 1226, 5695, 1204 and 153199 (0?4). Class weights are N/(5*N_class), fixed from TRAIN. All class orders are [0,1,2,3,4]. Target and row/block metadata are excluded from model features.

## Candidates and fitting provenance

| Model | Frozen principal parameters | Preprocessing |
| --- | --- | --- |
| LR F6 | C=1, lbfgs, max_iter=2000, seed 42, TRAIN-balanced class weights | Six raw channels, TRAIN median, StandardScaler, six missing indicators: 12 inputs |
| RF E4 | 100 trees, max_depth=10, min_samples_leaf=20, max_features=sqrt, n_jobs=2, seed 42, TRAIN-balanced weights | Four electrical channels, TRAIN median, native scale, four missing indicators: 8 inputs |
| LightGBM E4 | 150 trees, learning_rate=.05, max_depth=6, num_leaves=31, min_child_samples=50, max_bin=127, reg_lambda=1, deterministic, n_jobs=2, seed 42, TRAIN-balanced weights | Four channels, TRAIN median, five physical derived features and four indicators: 13 inputs |

Saved fit counts and source-index digests match the complete frozen TRAIN population. All 21 saved imputers match independently computed TRAIN medians. The reproduction command also checks LR training means/variances, class weights, classes and metadata exclusion. Historical training is supported by code/guards and stored metadata; the binary itself is not cryptographic proof of every historical execution step. Original dependency versions are pinned in the [archived lock](../phase2_implementation/stage1/requirements-stage1-lock.txt).

## VALIDATION comparison ? model selection only

| Model | Physical / mathematical inputs | Macro precision | Macro recall | Macro-F1 | Macro AP |
| --- | --- | --- | --- | --- | --- |
| LR__F6 | 6 / 12 | 0.872022940 | 0.927024112 | 0.893869804 | 0.942431868 |
| RF__E4 | 4 / 8 | 0.955450596 | 0.962811690 | 0.956297122 | 0.989740014 |
| LightGBM__E4 | 4 / 13 | 0.908327034 | 0.866445735 | 0.855657128 | 0.991518322 |

TRAIN predictive scores are not reported; no training-score estimates were invented. Validation tables refer specifically to block 13, not all 116,977 reserved validation positions.

RF E4 is the only one of 21 evaluated configurations meeting the four archived validation constraints: macro-F1 >= .80; each hardware-class recall >= .90; same-family F6 macro-F1 degradation <= .05; at most four physical channels. This validation rule selects the prototype, independently of the later revised TEST table. ?Minimum currently passing? means within these seven evaluated channel groups and three families; it does not establish globally minimum sensing. The separate resource/performance candidate was null.

## TEST comparison ? retrospective, prior exposure disclosed

| Model | Physical / mathematical inputs | Macro precision | Macro recall | Macro-F1 | Macro AP |
| --- | --- | --- | --- | --- | --- |
| LR__F6 | 6 / 12 | 0.889885493 | 0.912349415 | 0.898389062 | 0.917422666 |
| RF__E4 | 4 / 8 | 0.926440050 | 0.985651058 | 0.950481150 | 0.976218899 |
| LightGBM__E4 | 4 / 13 | 0.940383125 | 0.896340685 | 0.902137434 | 0.993577665 |

Macro precision, recall and F1 are unweighted means across five nominal classes. Macro AP is mean one-vs-rest average precision, not trapezoidal PR-AUC. Argmax classification and thresholded hardware alerts are distinct tasks. The saved matrices include an abstention column; recall counts abstentions as misses and AP assigns zero score. Complete per-class precision/recall/F1/support/AP and confusion counts are in [reproduced evidence](model_verification.json) and [archived class metrics](../phase2_implementation/stage3/evidence/final_test_class_metrics.csv).

| TEST model | Short-circuit recall | Degradation recall | Open-circuit recall |
| --- | --- | --- | --- |
| LR F6 | 1.000000000 | .997797357 | .851867220 |
| RF E4 | .999576451 | .990748899 | 1.000000000 |
| LightGBM E4 | .499364676 | .992951542 | .999170124 |

LightGBM misclassifies 729 short-circuit observations as shade and 453 as degradation; high aggregate hardware-alert recall does not repair poor hardware-subtype recall. LR assigns 357 open-circuit observations to short circuit. RF assigns 6,604 normal observations to shade; environmental classification is not hardware false alarming.

[RF confusion matrix](../phase2_implementation/stage3/figures/test_confusion_RF__E4.png) ? [All-candidate confusion figure](../phase2_implementation/stage4/figures/final_candidate_confusion_matrices.png) ? [Class metrics figure](../phase2_implementation/stage3/figures/test_per_class_metrics.png)

### Fixed hardware-alert thresholds

Thresholds were frozen from block 14: LR .4193821086840833, RF .5913558658757772, LightGBM .13860002397413157. The archived rule maximizes hardware recall subject to combined nonhardware FPR <= .01, then lower FPR and higher threshold. Recovery only evaluates these frozen values; no threshold search was repeated. The freeze receipt predates revised TEST access. Hardware score is p1+p2+p3; class 4 is excluded.

| TEST model | Alert recall | Normal FPR | Shade FPR | Combined nonhardware FPR |
| --- | --- | --- | --- | --- |
| LR F6 | 1.000000000 | .001084233 | .011738664 | .002223497 |
| RF E4 | .995455191 | .000160627 | .006439496 | .000832018 |
| LightGBM E4 | .996875444 | .000088345 | .007110276 | .000839191 |

Normal FPR denominator is all true class-0 rows; shade FPR is all true class-4 rows; combined FPR is all true {0,4} rows. Alert recall denominator is all true {1,2,3} rows, including abstentions as misses. These are row-level retrospective rates, not alerts per hour. [Full alert counts and metrics](../phase2_implementation/stage3/evidence/final_hardware_alert_metrics.csv).

## Resource trade-offs

| Candidate | Archived validation p50 / p95 (ms) | Original pickle size (MiB) | Principal limitation |
| --- | --- | --- | --- |
| LR F6 | 12.79435 / 14.716925 | .003742218 | Open-circuit recall and latency |
| RF E4 | 31.32045 / 36.808295 | 11.665363312 | Latency >10 ms and artifact >10 MiB |
| LightGBM E4 | 3.79575 / 6.12476 | 1.569196701 | Short-circuit classification recall |

Timings are **ARCHIVED-MEASURED**, not rebenchmarked during recovery: 100 warmups and 2,000 single-observation calls, Windows 11 Intel Core host, 16 physical/22 logical cores, approximately 33.8 GB RAM, Python 3.14.7 and two-thread policy. Full environment/protocol are in [stage-3 protocol](../phase2_implementation/stage3/evidence/stage3_protocol.json). Artifact sizes were rechecked on original bytes. No measured cloud/network/streaming latency is claimed. All engineering acceptance flags remain false in [criteria](../phase2_implementation/stage3/evidence/final_engineering_criteria.csv).

## Sparse sensing, explanations and robustness

Evaluated physical channel groups: F6 all six; E5 electrical plus irradiance; E4 both voltage/current pairs; C3 both currents plus irradiance; C2 both currents; S4 one voltage/current pair plus irradiance/temperature; S2 one voltage/current pair. [All 21 validation comparisons](../phase2_implementation/stage2/evidence/sensor_ablation_validation.csv) and [dependency definitions](../phase2_implementation/stage2/evidence/feature_availability_by_configuration.json) distinguish mathematical features from actual channels. Derived powers/differences require their parent physical channels; PCA is mathematical reduction, not physical sensor reduction. Electrical-only performance does not prove environmental sensors redundant under future conditions.

Archived model explanations use signed standardized LR coefficients, RF impurity importance, LightGBM gain, raw-channel permutation through the complete pipeline, and native LightGBM Tree SHAP raw-margin contributions. The fixed balanced block-13 sample contains 200 observations per class, seed 42, three permutations per channel. It is not prevalence-representative. Permuting one raw channel regenerates dependent features. vdc2 has the largest mean macro-F1 permutation loss for each frozen candidate. SHAP emphasizes P1, voltage difference and vdc2 for LightGBM class 1. Correlation disruption and nonunique dependent-feature attribution limit interpretation; predictive association is not causality. TRAIN mutual information remains descriptive, not a fitted-model explanation. [Explanation metadata](../phase2_implementation/stage3/evidence/explainability_metadata.json) and [channel permutation results](../phase2_implementation/stage3/evidence/physical_channel_permutation.csv) record the exact population and methods. RF SHAP was not performed.

Permutation results, native LightGBM SHAP contributions (including saved-array parity and additivity), and the fixed dropout outcomes were reproduced during recovery: [verification receipt](explanation_robustness_verification.json). The read-only reproduction command `python -B -m src.evaluation.verify_explanations` requires the private original model cache and checks the published explanation tables.

Archived isolated channel-dropout is **SIMULATED**, using 328 fixed block-13 positions (1%), one masked available channel per selected row. Macro-F1 losses: LR .01498559046, RF .00816308934, LightGBM .01063927235. This is not measured field dropout or proof of safety under sustained missing sensors. The inference prototype rejects missing channels. Noise-study reconstructed models remain outside this publication; their provenance differs from the recovered originals, and their results are not presented as validated here.

## Local deployment prototype

[CLI and installation](../deployment/README.md) loads only the original RF E4 artifact after fixed hash verification. Four electrical measurements enter the saved quality/median/indicator/forest pipeline. Schema and finite/nonnegative checks are applied; no target or source index enters inference. Output gives class, label, model provenance and separate hardware/environmental flags. No calibrated confidence is claimed. [Actual input](../deployment/example_input.json) and [actual output](../deployment/example_output.json) are included.

```text
python -B -m src.inference.cli --input deployment/example_input.json
python -B -m unittest discover -s tests -v
python -B -m src.evaluation.verify_recovery
python -B phase2_implementation/verify_submission.py
```

The first command requires the deployment environment; full preprocessing verification requires the preserved preprocessing/report dependencies. See the [existing reproduction guide](../phase2_implementation/Reproduction_Guide.md). The default model verifier reproduces public RF validation/TEST and frozen block-14 counts. `--all-originals` additionally requires the privately preserved 21 original Stage-2 artifacts and saved TEST NPZ references in the ignored `.cache` directories; only one fitted artifact is published. The [recovery manifest](Recovery_Manifest.json) records source, size, hash and purpose without local paths. Archived Stage 1?3 scripts are provenance, not a command to rerun training; original foundation manifests describe the historical tree and are not current-public-tree manifests.

## Limitations and next deployment steps

Validation selection already involves many comparisons on one operating-block pair. Prior TEST exposure, severe imbalance, one experimental setup, source-population mismatch with reported irradiance-qualified counts, absence of timestamps, sensor correlation and resource failures limit generalization. Sixteen blocks are not verified independent acquisition sessions. No prospective evaluation, probability calibration, cloud service, production deployment, monitoring, fail-safe protection, sustained missing-channel validation or cross-site external test has been completed. Future deployment requires a genuinely new external evaluation population, engineering acceptance review, measured target-hardware latency and operational input/failure handling; these steps were not simulated into completion.

## References

- Lazzaretti et al. (2020), photovoltaic fault-detection dataset/study, [Sensors 20, 4688](https://doi.org/10.3390/s20174688); [original release](https://github.com/clayton-h-costa/pv_fault_dataset).
- Breiman (2001), Random Forests, Machine Learning 45, 5?32, doi:10.1023/A:1010933404324.
- Ke et al. (2017), LightGBM: A Highly Efficient Gradient Boosting Decision Tree, NeurIPS.
- Lundberg and Lee (2017), A Unified Approach to Interpreting Model Predictions, NeurIPS; native implementation documented in the archived explanation metadata.
