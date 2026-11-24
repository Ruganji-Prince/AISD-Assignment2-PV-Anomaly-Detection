# Mock technical examination

The five fixed historical demo references originate in the previously inspected TEST partition. They are parity/reproducibility examples, not independent accuracy evidence; [exact source positions](Submission_Readiness.md#exact-provenance-of-the-five-fixed-references) are documented. No new prediction-based example search is performed.

**66 questions** under the five official rubrics. Attempt answers with the actual repository before reading the model answers. Explain the mechanism, evidence and limitation. Concepts, mathematics, source inspection, methodology, trade-offs, deployment and validity challenges are covered.

## Rubric 1: Data engineering and feature screening

### Q1. What is the prediction unit, and is f_nv regression?

**Model answer:** The unit is an exported source-position observation; integer codes are nominal identities, not continuous severity. There are no reconstructed timestamps. One prediction classifies one source-position observation. vdc1/vdc2 are the two strings' DC RMS voltages; idc1/idc2 their DC RMS currents. irr is reported plane-of-array irradiance; pvt aggregates module temperature probes. f_nv is an unordered experimental operating-state label.

**Code to inspect:** [src/preprocessing/study.py :: PreprocessingStudy.load_data](../../src/preprocessing/study.py#L25).

**Measured evidence:** N=1,373,798; P=7. Units V, A, W/m^2 and degrees C. Labels0 normal,1 short circuit,2 degradation,3 open circuit,4 natural building shade. [Evidence](../../phase1_strategy/Variable_Inventory.csv).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q2. Why retain low-irradiance rows if a filtered population matches literature counts?

**Model answer:** The paper does not explicitly establish that exact filtering operation. Rows are retained instead of changing the population to force agreement. A dataset reference must identify the actual release and conversion, not merely cite a similar paper. Source ordering and hashes preserve traceability.

**Code to inspect:** [src/preprocessing/study.py :: PreprocessingStudy.load_data](../../src/preprocessing/study.py#L25).

**Measured evidence:** Raw CSV SHA717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a; pinned upstream commit is in README. [Evidence](../../data/raw/README.md).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q3. Does zero missingness establish MCAR?

**Model answer:** No. It describes the released export, not unobserved acquisition failures or the missingness mechanism. MCAR missingness is independent of measurements. MAR may depend on observed values; MNAR additionally depends on unobserved values. MAR does not mean arbitrary independent random disappearance.

**Code to inspect:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Measured evidence:** Zero NaNs/infinities and zero incomplete rows. The62 paired irr/pvt zeros remain suspicious observations, not confirmed missingness. [Evidence](../../technical_evaluation/evidence/rubric1/missingness.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q4. Why omit the named formal tests?

**Model answer:** Their applicability conditions fail. Executable evidence verifies constant indicators; it does not support a claim of MCAR/MAR/MNAR. Little's test needs estimable incomplete-data patterns. Missingness-versus-target Cramer V needs both contingency dimensions to vary.

**Code to inspect:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Measured evidence:** Both tests are NOT APPLICABLE; no statistic or p-value was fabricated. [Evidence](../../technical_evaluation/evidence/rubric1/missingness.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q5. Would an IQR flag justify deleting a fault observation?

**Model answer:** No. Physical validity and experimental context must be assessed separately; a genuine fault can be statistically extreme. Quartiles describe the central half of a distribution. Fences flag statistical unusualness rather than establish sensor errors.

**Code to inspect:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Measured evidence:** TRAIN quartiles, bounds and flagged counts are provided per channel; no automatic removal selected. [Evidence](../../technical_evaluation/evidence/rubric1/training_outliers.csv).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q6. Why not remove every absolute Z>3 reading?

**Model answer:** That could remove the target fault signatures and imposes an unjustified distributional assumption. Z-score standardizes distance from a mean. MAD uses distance from a median and resists extreme values. Skewness describes asymmetry.

**Code to inspect:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Measured evidence:** Absolute Z>3 and modified Z>3.5 counts, TRAIN skewness and a bounded normality diagnostic are recorded. [Evidence](../../technical_evaluation/evidence/rubric1/training_outliers.csv).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q7. Why have an imputer with zero exported NaNs?

**Model answer:** It defines a consistent bounded offline missing-channel policy. It does not prove persistent outage reliability or justify synthetic missingness claims. A median replacement is learned from training values. Means are sensitive to skew/extremes; mode suits categories; KNN requires meaningful neighbors; interpolation requires justified sequence/timing assumptions.

**Code to inspect:** [src/phase2_stage2/models.py :: build_preprocessor](../../src/phase2_stage2/models.py#L28).

**Measured evidence:** Fitted TRAIN medians were independently verified; missing public API inputs are rejected. [Evidence](../../reports/model_verification.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q8. Why was clipping rejected?

**Model answer:** IQR did not improve validation and quantile clipping slightly degraded it. No automatic winsorization of faults was justified. Clipping caps values at fitted bounds without removing rows. Its effect must be evaluated on unchanged development observations.

**Code to inspect:** [technical_evaluation/experiments.py :: TrainingClipper](../../technical_evaluation/experiments.py#L15).

**Measured evidence:** Block13 F1 none=.956297122, IQR=.956297122, quantile=.956041296; original no-clipping policy retained. [Evidence](../../technical_evaluation/evidence/rubric1/clipping_comparison.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q9. Why not correlate voltage with integer f_nv as a continuous outcome?

**Model answer:** Renumbering unordered labels would change that quantity. Nominal-target association uses methods such as MI instead. Pearson measures linear co-variation between numeric measurements. It is not an appropriate interpretation of arbitrary nominal label-code distances.

**Code to inspect:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Measured evidence:** Five TRAIN pairs exceed the absolute.85 screen in the preprocessing evidence. [Evidence](../../technical_evaluation/evidence/rubric1/Pearson.csv).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q10. Does Pearson/Spearman agreement prove physical causality?

**Model answer:** No. Shared conditions and acquisition design can cause association without establishing a causal intervention. Spearman correlates ranks and can detect monotonic relationships that are nonlinear on the original scale. Ties and dependence still matter.

**Code to inspect:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Measured evidence:** Full TRAIN matrix and threshold-screened pairs are published. [Evidence](../../technical_evaluation/evidence/rubric1/Spearman.csv).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q11. Why retain high-VIF predictors?

**Model answer:** Physical dependencies, regularization and validation ablation support retention. Independent causal coefficient interpretations are not claimed. VIF measures how much a predictor is explained by the others, which can destabilize linear coefficient interpretation.

**Code to inspect:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Measured evidence:** TRAIN VIF vdc1~52.168, vdc2~56.346, idc1~31.496. [Evidence](../../technical_evaluation/evidence/rubric1/feature_screening.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q12. Is high MI equivalent to trained-model importance?

**Model answer:** No. MI describes data association; permutation and SHAP assess specific fitted model behavior. MI estimates statistical dependence, including nonlinear association, between a continuous predictor and nominal target. It is not a causal explanation of a fitted forest.

**Code to inspect:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Measured evidence:** Seed42 natural-prevalence TRAIN sample50000; diagnostic MI values in nats. [Evidence](../../technical_evaluation/evidence/rubric1/feature_screening.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q13. Why not replace four sensors with two PCs?

**Model answer:** PCs still require their source measurements. Explicit sensor-channel ablation addresses acquisition requirements. PCA rotates standardized measurements into orthogonal directions ranked by variance. Explained variance is not predictive sufficiency.

**Code to inspect:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Measured evidence:** About95.17% TRAIN variance in two components in original preprocessing; PCA not deployed. [Evidence](../../technical_evaluation/evidence/rubric1/feature_screening.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q14. Can accuracy alone justify an operational decision?

**Model answer:** No. Class-specific consequences, physical validity and independent evidence are required; no monetary utility or safety certification is invented. Explicit target/index/block proxies are forbidden, but hidden acquisition dependence cannot be excluded by schema alone. Costs distinguish missed faults from false inspection and environmental shade.

**Code to inspect:** [technical_evaluation/metrics.py :: hypothetical_cost](../../technical_evaluation/metrics.py#L27).

**Measured evidence:** Hardware-miss weights2/5/10/20 were considered; original10ms/10MiB targets unchanged. [Evidence](../../technical_evaluation/evidence/rubric1/hypothetical_costs.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

## Rubric 2: Split integrity and leakage prevention

### Q15. Would stratified random splitting solve dependence?

**Model answer:** No. Balancing labels is different from separating acquisition regimes. Nearby source positions can share regimes and acquisition conditions. Random stratification can preserve class balance while mixing dependent signals.

**Code to inspect:** [src/preprocessing/study.py :: PreprocessingStudy.split_data](../../src/preprocessing/study.py#L33).

**Measured evidence:** TRAIN1006129, VAL116977, TEST146461; no random repartitioning. [Evidence](../../technical_evaluation/evidence/rubric2/leakage.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q16. Why not call3600 positions an hour?

**Model answer:** Uninterrupted one-second spacing cannot be reconstructed from the released vectors. Irradiance below100 W/m^2 for at least3600 consecutive source positions identifies separators. Sixteen signal-defined blocks have12/2/2 allocation.

**Code to inspect:** [phase1_strategy/verify_phase1.py :: main](../../phase1_strategy/verify_phase1.py#L19).

**Measured evidence:** 104231 excluded split-gap positions; blocks are not verified days, sessions or hours. [Evidence](../../phase1_strategy/Phase1_Split_Manifest.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q17. Were all validation rows used for model selection?

**Model answer:** No. The reserved range includes background positions; model-selection tables specifically use block13. Half-open bounds include the first index and exclude the endpoint. Different development choices use declared populations.

**Code to inspect:** [src/phase2_stage3/common.py :: load_part](../../src/phase2_stage3/common.py#L20).

**Measured evidence:** Block13 N32800; block14 N33396; selection is not all116977 validation positions. [Evidence](../../reports/Model_Selection_and_Deployment.md).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q18. Does a hash alone establish no leakage?

**Model answer:** No. Vector construction, equality, source/block isolation and learned-transform fitting all matter. Canonical physical vectors are hashed and candidate equalities are independently checked. Repeated within-partition states are not automatically erroneous.

**Code to inspect:** [technical_evaluation/data_audit.py :: vector_hash](../../technical_evaluation/data_audit.py#L11).

**Measured evidence:** Zero cross-partition exact matches for four/six channels; zero conflicting-label duplicate vectors. [Evidence](../../technical_evaluation/evidence/rubric2/leakage.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q19. Are close states proof of target leakage?

**Model answer:** No. They limit independence/transfer claims and may reflect legitimate repeated operating states. The fixed split is retained. Nearest neighbors measure similarity after TRAIN-fitted standardization; close values need not hash equally.

**Code to inspect:** [technical_evaluation/refinement/experiments.py :: near](../../technical_evaluation/refinement/experiments.py#L15).

**Measured evidence:** All TRAIN references and later queries; E4 near counts37313VAL/62917TEST; F6 counts1290/1125; exact distances0. [Evidence](../../technical_evaluation/refinement/results/full_near_duplicates.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q20. Can a global scaler followed by Pipeline prevent leakage?

**Model answer:** No. Later-partition information has already entered the scaler; fitting must be isolated before evaluation. Pipeline fits transformations in sequence; ColumnTransformer routes approved columns and drops the rest. These classes do not repair a scaler previously fitted on all data.

**Code to inspect:** [src/phase2_stage2/models.py :: build_preprocessor](../../src/phase2_stage2/models.py#L28).

**Measured evidence:** TRAIN medians and LR means/variances checked; remainder=drop and retained schema explicit. [Evidence](../../reports/model_verification.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q21. Which code verifies preprocessing isolation?

**Model answer:** assert_fit_isolated rejects overlap; fit_one checks learned medians, scaler means and clipping fit-index digest against the actual fitting rows. Every grouped fold independently fits preprocessing and classifier. Weights use that fit fold's available classes and counts.

**Code to inspect:** [technical_evaluation/experiments.py :: fit_one](../../technical_evaluation/experiments.py#L46).

**Measured evidence:** Nine independent fits, three families times three nonshuffled TRAIN folds; digests and supports retained. [Evidence](../../technical_evaluation/evidence/rubric2/grouped_validation.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q22. How can leakage prevention be claimed after TEST inspection?

**Model answer:** No identified unaddressed target/preprocessing leak is claimed. Pristine holdout independence is explicitly not claimed; historical design exposure remains a limitation. Implementation leakage prevention and an independent prospective holdout are different claims. Human knowledge of prior TEST cannot be erased.

**Code to inspect:** [technical_evaluation/refinement/experiments.py :: freeze](../../technical_evaluation/refinement/experiments.py#L14).

**Measured evidence:** Prior TEST exposure is prominent; no new TEST-guided model/feature/calibration/threshold choice. [Evidence](../../technical_evaluation/refinement/Protocol.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

## Rubric 3: Machine learning and evaluation

### Q23. Why scale LR but not treat f_nv as a continuous target?

**Model answer:** Scaling concerns predictor geometry; the likelihood still models unordered class identities. LR models class log-odds as linear functions of transformed inputs. Regularization limits coefficients; scaling makes penalty geometry more comparable across units.

**Code to inspect:** [src/phase2_stage1/models.py :: F6Model](../../src/phase2_stage1/models.py#L14).

**Measured evidence:** Original LR F6 block13 F1=.893870 and historical TEST=.898389; E4 same-input comparison is separate. [Evidence](../../technical_evaluation/evidence/rubric3/model_comparison.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q24. What prevents overfitting at a new PV installation?

**Model answer:** Development validation and capacity restrictions help, but independent-site transfer is unverified and cannot be guaranteed from this study. RF averages class distributions across randomized trees fitted to bootstrapped data. Threshold trees model nonlinear interactions without requiring standardization.

**Code to inspect:** [src/phase2_stage1/models.py :: F6Model](../../src/phase2_stage1/models.py#L14).

**Measured evidence:** 100 trees, depth10, minimum leaf20, max_features=sqrt, seed42, TRAIN-balanced weights. [Evidence](../../technical_evaluation/evidence/rubric3/original_model_parameters.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q25. Why not select LightGBM from hardware AP alone?

**Model answer:** Hardware ranking can conceal subtype failure: archived short-circuit recall is approximately.499365. Selection and error interpretation must be class-specific. Boosting adds trees sequentially to reduce loss. Leaf-wise growth captures interactions; leaf/depth constraints limit capacity.

**Code to inspect:** [src/phase2_stage1/models.py :: F6Model](../../src/phase2_stage1/models.py#L14).

**Measured evidence:** Selected family settings include150 trees, learning rate.05, depth6 and31 leaves; original E4 TEST F1=.902137. [Evidence](../../technical_evaluation/evidence/rubric3/original_model_parameters.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q26. Why report both if F1 is identical?

**Model answer:** Their probability distributions and proper scoring rules differ, even though their classifications coincide. Most-frequent predicts the largest TRAIN class. Prior supplies the full TRAIN prevalence vector; the two can share argmax outputs but differ in probability quality.

**Code to inspect:** [technical_evaluation/experiments.py :: model_metrics](../../technical_evaluation/experiments.py#L93).

**Measured evidence:** Both Dummy argmax F1 values: block13 .144269; TEST .183800. Calculations were reproduced. [Evidence](../../technical_evaluation/refinement/results/baseline_reverification.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q27. Are these two rule baselines the same implementation?

**Model answer:** No. The normal-referenced two-discrepancy score and q99 current-only rule are distinct and should not be conflated. The historical score standardizes current/voltage discrepancies against normal TRAIN statistics. The audit later adds a separate TRAIN-q99 current-imbalance reference. Neither is a five-class diagnosis.

**Code to inspect:** [src/phase2_stage1/models.py :: EngineeringReference](../../src/phase2_stage1/models.py#L44).

**Measured evidence:** The audit rule reports binary hardware AP/recall and normal/shade FPR; the historical two-discrepancy score is separately documented. [Evidence](../../technical_evaluation/evidence/rubric3/model_comparison.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q28. Can a high weight repair zero class support?

**Model answer:** No. No observations exist from which to learn that class; support limitations must be reported. Rare classes receive larger loss weights. Weighting changes the objective; it neither adds independent examples nor teaches an absent class.

**Code to inspect:** [src/phase2_stage1/contracts.py :: weights](../../src/phase2_stage1/contracts.py#L39).

**Measured evidence:** TRAIN class counts844805,1226,5695,1204,153199; explicit balanced dictionary verified. [Evidence](../../phase2_implementation/stage1/evidence/class_weights.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q29. Are21 sensor comparisons another21-setting hyperparameter search?

**Model answer:** No. They compare seven channel groups across three families using frozen family settings. A declared development search avoids unlimited experimentation until TEST looks favorable. Stage2 freezes family settings while varying channels.

**Code to inspect:** [src/phase2_stage1/run.py :: trial_specs](../../src/phase2_stage1/run.py#L25).

**Measured evidence:** Block13 macro-F1 selected per-family settings; block14/TEST were not Stage1 scoring populations. [Evidence](../../phase2_implementation/stage1/evidence/experiment_configuration.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q30. Why are four physical measurements sufficient?

**Model answer:** They meet the selected rule among evaluated alternatives; no globally minimum hardware inventory or PCA equivalence is claimed. Ablation refits using only retained channels. Mathematical indicators/derivatives must not be counted as extra acquired sensors.

**Code to inspect:** [src/phase2_stage2/models.py :: AblationModel](../../src/phase2_stage2/models.py#L38).

**Measured evidence:** Seven groups times three families; production accepts exactly vdc1,vdc2,idc1,idc2. [Evidence](../../phase2_implementation/stage2/evidence/sensor_ablation_validation.csv).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q31. Why select a model larger than10MiB?

**Model answer:** The prototype passed a different declared validation rule. It was never relabeled as satisfying full engineering acceptance. The sensing/performance candidate is distinct from a resource-qualified candidate. A null resource result must remain null.

**Code to inspect:** [src/phase2_stage2/selection.py :: select](../../src/phase2_stage2/selection.py#L11).

**Measured evidence:** RF E4 alone passed the four sensing/performance constraints; resource/performance candidate was null. [Evidence](../../reports/Model_Selection_and_Deployment.md).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q32. Can a diagonal-looking matrix be judged without supports?

**Model answer:** No. Row/class counts and error consequences matter, especially for rare hardware states. Rows are true classes; columns are predictions. Offline evidence retains a separate abstention column rather than hiding unsupported predictions.

**Code to inspect:** [technical_evaluation/metrics.py :: evaluate](../../technical_evaluation/metrics.py#L18).

**Measured evidence:** RF historical TEST has6604 true-normal observations predicted shade. [Evidence](../../technical_evaluation/evidence/rubric3/model_comparison.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q33. Does near-perfect shade recall prove good shade discrimination?

**Model answer:** No. Normal-to-shade errors lower precision; both directions and their denominators must be examined. Precision measures correctness among predicted class members; recall measures recovered true members. F1 combines both and is not a simple average of accuracy.

**Code to inspect:** [technical_evaluation/metrics.py :: evaluate](../../technical_evaluation/metrics.py#L18).

**Measured evidence:** Shade precision .691081 and recall .991146. [Evidence](../../technical_evaluation/evidence/rubric4/normal_shade_errors.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q34. Why not MAE between integer target codes?

**Model answer:** Unordered code distances have no physical or validated utility meaning; a cost function needs separately stated costs. Macro averages class F1 equally. Weighted F1 uses supports. Balanced accuracy averages supported-class recall; absent-class conventions must be explicit.

**Code to inspect:** [technical_evaluation/metrics.py :: evaluate](../../technical_evaluation/metrics.py#L18).

**Measured evidence:** Original RF validation F1=.956297 and historical TEST=.950481; full per-class/base-rate metrics are available. [Evidence](../../technical_evaluation/evidence/rubric3/model_comparison.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q35. Can excellent hardware AP coexist with poor short-circuit diagnosis?

**Model answer:** Yes. Classes1/2/3 are combined for hardware ranking; subtype confusion can remain severe. AP accumulates precision at recall increments in ranking order. Trapezoidal PR-AUC uses a different interpolation. Precision at k concerns an explicit inspection budget.

**Code to inspect:** [technical_evaluation/metrics.py :: evaluate](../../technical_evaluation/metrics.py#L18).

**Measured evidence:** Original RF historical TEST hardware AP~.993354. Macro AP is one-vs-rest average precision, not trapezoidal area. [Evidence](../../technical_evaluation/evidence/rubric3/model_comparison.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q36. Does the production API apply this threshold?

**Model answer:** No. hardware_fault_class reflects the argmax nominal prediction. Archived binary-alert evaluation is a separate policy. Hardware score sums only classes1/2/3. Shade is excluded. A binary alert is different from multiclass argmax and needs a declared negative population.

**Code to inspect:** [src/phase2_stage3/common.py :: select_threshold](../../src/phase2_stage3/common.py#L39).

**Measured evidence:** Original tau=.5913558658757772; maximize block14 hardware recall subject to combined FPR<=.01 with exact-score enumeration/tie-breaks. [Evidence](../../phase2_implementation/stage3/evidence/final_candidate_comparison.csv).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q37. Why was calibration not deployed?

**Model answer:** One historical block is insufficient justification for changing operational probability/threshold policy. No calibrated confidence or calibrated alert threshold was deployed. Sigmoid maps each class probability through a logistic function; isotonic fits a monotone map. Separate calibration does not create an independent deployment guarantee.

**Code to inspect:** [technical_evaluation/experiments.py :: ProbabilityMap](../../technical_evaluation/experiments.py#L56).

**Measured evidence:** Minimum positives50 sigmoid/100 isotonic and100 negatives passed. Sigmoid selected using block14 OOF logloss before retrospectiveTEST. [Evidence](../../technical_evaluation/refinement/results/probability_normalization.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q38. Why prefer sigmoid when isotonic has lower TEST ECE?

**Model answer:** The frozen selection criterion is block14 OOF logloss, not TEST ECE. Post-hoc criterion switching would undermine selection provenance. Brier penalizes squared probability error; log loss penalizes confident wrong predictions; ECE compares binned confidence with frequency and depends on binning.

**Code to inspect:** [technical_evaluation/metrics.py :: probability_metrics](../../technical_evaluation/metrics.py#L12).

**Measured evidence:** Original Brier/logloss/ECE .079293/.151089/.023762; sigmoid .051306/.089088/.014281; isotonic .053112/.092305/.011333. [Evidence](../../technical_evaluation/refinement/results/calibration/calibration_TEST_retrospective.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q39. Is a visually diagonal diagram enough to display calibrated confidence?

**Model answer:** No. The specific deployed map/population/policy needs independent validation; the existing UI intentionally displays no confidence percentage. Each bin compares mean predicted probability with observed event frequency. Empty bins provide no evidence; bin counts and population definition matter.

**Code to inspect:** [technical_evaluation/metrics.py :: reliability](../../technical_evaluation/metrics.py#L4).

**Measured evidence:** Ten equal-width bins; reproduced Brier/logloss/ECE match prior values within1e-12. [Evidence](../../technical_evaluation/refinement/figures/reproduced_reliability.png).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q40. Why is grouped validation worse than original TEST performance?

**Model answer:** It exposes acquisition transfer and absent fit-class support. These scores are not interchangeable unbiased estimates of one population. Three nonshuffled folds hold out whole TRAIN operating blocks and independently fit each family. The population excludes background rows, unlike the full original split.

**Code to inspect:** [technical_evaluation/experiments.py :: training_experiments](../../technical_evaluation/experiments.py#L124).

**Measured evidence:** RF supported-class F1 approximately.512135/.913322/.897464; original TEST .950481 is a different protocol/population. [Evidence](../../technical_evaluation/evidence/rubric2/grouped_validation.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q41. Are these intervals around deployed TEST F1 .950481?

**Model answer:** No. They summarize preserved TRAIN grouped-OOF outcomes under stated conventions, not independent deployed TEST or external-site coverage. Whole block confusion matrices are resampled to preserve within-block dependence. The procedure does not prove blocks themselves are independent.

**Code to inspect:** [technical_evaluation/refinement/experiments.py :: uncertainty](../../technical_evaluation/refinement/experiments.py#L34).

**Measured evidence:** 671 all-five-supported draws; conditional F1 range.495205-.623462; unconditional fixed-five convention .373881-.721550. [Evidence](../../technical_evaluation/refinement/results/bootstrap_sensitivity.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

## Rubric 4: Robustness and explainability

### Q42. Can a slice with no hardware examples establish zero miss rate?

**Model answer:** No. Hardware recall is undefined without positive opportunities; absent support is not safety evidence. Global averages can hide errors concentrated at particular irradiance, temperature, output or imbalance ranges. Every slice needs supports and fixed boundaries.

**Code to inspect:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Measured evidence:** TRAIN/VAL/TEST and source blocks reported separately; N<100 and class support<50 flagged. [Evidence](../../technical_evaluation/evidence/rubric4/subgroups.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q43. How would an entirely new photovoltaic installation behave?

**Model answer:** Behavior is unverified. Hardware, sensor calibration and operating regimes may shift; independent prospective site evidence is necessary. Features and class prevalence can differ across cohorts without known timestamps. The appropriate term here is source-cohort shift, not verified calendar-time drift.

**Code to inspect:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Measured evidence:** Substantial current-channel shifts are measured; operating/background mixture also differs. [Evidence](../../technical_evaluation/evidence/rubric4/shift.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q44. Does a large PSI prove a hardware malfunction?

**Model answer:** No. It describes distribution difference under selected bins; a cause or operational alarm requires additional evidence. PSI compares histogram proportions. Values depend on binning and epsilon choices; no validated operational alarm is inferred.

**Code to inspect:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Measured evidence:** TEST idc1 PSI~4.627 and idc2~3.682. [Evidence](../../technical_evaluation/evidence/rubric4/shift.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q45. Why not use a tiny KS p-value as independent proof?

**Model answer:** Rows are dependent. A p-value under the wrong sampling assumptions would exaggerate the conclusion. KS is the largest separation between empirical cumulative distribution functions. A large dependent dataset does not justify naive iid significance claims.

**Code to inspect:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Measured evidence:** TEST idc1 KS~.431; iid p-values are not interpreted. [Evidence](../../technical_evaluation/evidence/rubric4/shift.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q46. Why report both absolute and normalized distance?

**Model answer:** Absolute distance preserves engineering units; normalization describes change relative to reference variability. Neither alone establishes causality. One-dimensional Wasserstein measures the area between CDFs and retains the sensor unit, unlike a dimensionless KS statistic.

**Code to inspect:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Measured evidence:** Distances are published in original units and relative to TRAIN IQR for each channel/cohort. [Evidence](../../technical_evaluation/evidence/rubric4/shift.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q47. Are these measured field sensor failures?

**Model answer:** No. They are simulated perturbations; extreme changes can violate photovoltaic relationships and label persistence is not independently validated. Noise is random perturbation; bias is a systematic offset. The percentage requires a defined scale, not an unexplained fraction of a reading.

**Code to inspect:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Measured evidence:** N12000; seeds42/43/44. F1 at5% noise .796863-.798149; at10% .645450-.655924. [Evidence](../../technical_evaluation/evidence/rubric4/stress.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q48. What happens during persistent dropout?

**Model answer:** The offline policy abstains after two positions; the API rejects missing measurements instead of promising reliable persistent imputation. Offline eligibility permits at most one unavailable channel and a missing run of at most two consecutive source positions. Sparse sample gaps reset the rule.

**Code to inspect:** [src/phase2_stage1/features.py :: eligible](../../src/phase2_stage1/features.py#L44).

**Measured evidence:** Contiguous block13 outage leaves2/32800 eligible; two missing channels give zero coverage. Missing public inputs are rejected. [Evidence](../../technical_evaluation/evidence/rubric4/contiguous_dropout.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q49. Can range checks reject every physically dangerous input?

**Model answer:** No. Joint relationships and certified operating envelopes require additional domain validation. Saturation fixes a sensor to a bound; OOD means insufficient support under the reference distribution. A finite nonnegative vector need not obey joint PV physics.

**Code to inspect:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Measured evidence:** Finite OOD stress F1~.144341. The API warns on observed-range exceedance without silent clipping. [Evidence](../../technical_evaluation/evidence/rubric4/stress.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q50. Does importance establish which sensor causes the fault?

**Model answer:** No. Predictive dependence under permutation is not a causal physical intervention. A raw channel is shuffled while the full downstream feature pipeline is recomputed. Score loss describes model dependence on that channel/sample.

**Code to inspect:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Measured evidence:** RF-specific sample1000 balanced rows,200/class, seed42, three repeats; archived family permutation also reproduced. [Evidence](../../technical_evaluation/evidence/rubric4/RF_raw_channel_permutation.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q51. Is the UI explanatory text local RF SHAP?

**Model answer:** No. It describes the actual predicted class; no feature contributions are fabricated. Native contributions decompose raw class scores relative to a base value. Additivity verifies algebraic consistency, not causal correctness.

**Code to inspect:** [src/evaluation/verify_explanations.py :: main](../../src/evaluation/verify_explanations.py#L10).

**Measured evidence:** Native LightGBM additivity and mean absolute contributions match archived references; RF has separate permutation evidence. [Evidence](../../technical_evaluation/evidence/rubric4/archived_explanations_reverification.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q52. Why not count class4 as a broken-hardware detection?

**Model answer:** Its source label is natural building shade, an environmental condition; changing the definition would misrepresent the task. High shade recall can coexist with poor precision when normal observations are also predicted shade. Environmental classification errors are not hardware alerts by definition.

**Code to inspect:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Measured evidence:** 6604 normal-to-shade errors; shade precision .691081 and recall .991146. [Evidence](../../technical_evaluation/evidence/rubric4/normal_shade_errors.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q53. Does249/250 prove generalization, or why do all old presets predictshade?

**Model answer:** It does not prove generalization: parents are TRAIN observations. Old intuitive marginal values need not follow learned joint regimes; neither generator is a validated fault simulator. Historical references, original hand-designed synthetic intents and new TRAIN-derived empirical perturbations are distinct sources. None should borrow another source's validity claim.

**Code to inspect:** [technical_evaluation/refinement/experiments.py :: synthetic](../../technical_evaluation/refinement/experiments.py#L25).

**Measured evidence:** Original presets all predictshade. Fixed250 empirical cases have249 conditioning agreements; parents were used in model fitting. [Evidence](../../technical_evaluation/refinement/results/empirical_scenarios.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

## Rubric 5: Software engineering and deployment

### Q54. Will the quick command retrain production?

**Model answer:** No. New fits require an explicit separate reconstruction command and remain outside the production model path. Data/provenance, preprocessing, original modeling/evaluation, inference/web and technical evidence have separate roles. Quick verification is different from expensive reproduction.

**Code to inspect:** [technical_evaluation/refinement/verify.py :: main](../../technical_evaluation/refinement/verify.py#L18).

**Measured evidence:** Quick audit runs30 tests and protected/hash/link checks, with no fitting/cloud calls or tracked-receipt rewrites. [Evidence](../../technical_evaluation/refinement/results/clean_clone_quick_audit.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q55. Would hashing any uploaded pickle make it safe?

**Model answer:** No. The reference must itself be trusted. This service has no arbitrary model-upload endpoint. Pickle stores Python object state, including fitted medians and trees, but loading arbitrary pickle objects can execute code. Identity is not inherently safety.

**Code to inspect:** [src/inference/cli.py :: load_model](../../src/inference/cli.py#L35).

**Measured evidence:** Original model SHA55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb remains verified. [Evidence](../../models/rf_e4/provenance.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q56. Does the backend read a scenario label to return the desired result?

**Model answer:** No. Target/index/scenario metadata is forbidden in the inference schema. A prediction request passes content/body/schema validation, local capacity, cached trusted loading, fitted preprocessing/forest and actual-class response. Middleware adds security/timing headers.

**Code to inspect:** [web/app.py :: predict_measurements](../../web/app.py#L114).

**Measured evidence:** Five predetermined cases match CLI/API; invalid input and timing headers were checked. [Evidence](../../technical_evaluation/refinement/results/final_preview_verification.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q57. Are animated input bars a live PV installation feed?

**Model answer:** No. They visualize entered/example measurements; hosting does not establish live acquisition or real-time operational monitoring. Four client-side panels preserve measurements, source/scenario, chart and prediction state. Requests use the same-origin API and stale results clear after input edits.

**Code to inspect:** [web/static/app.js](../../web/static/app.js).

**Measured evidence:** Smoke tests passed desktop1366/1920, tablet820 and mobile390/320 widths, navigation and error paths. [Evidence](../../technical_evaluation/refinement/results/production_browser.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q58. Why not silently cap400V to a TRAIN bound?

**Model answer:** That would alter evidence without validation. The value is preserved with a warning; observed ranges are not safety limits. Exactly four finite nonnegative numeric fields are accepted. Strings, booleans, duplicate/extra keys and nonfinite JSON are rejected. Range warnings do not certify physics.

**Code to inspect:** [src/inference/cli.py :: validate](../../src/inference/cli.py#L18).

**Measured evidence:** Malformed, duplicate, oversize, missing, extra, nonnumeric, negative and nonfinite cases are tested. [Evidence](../../web/tests/test_api.py).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q59. Is Docker verified locally?

**Model answer:** No. Actual builds/runs used standard free public GitHub Linux runners, with their environment and timings recorded. A container packages an inference runtime, not a newly trained model. Its image size includes Python/dependencies and is distinct from model-artifact size.

**Code to inspect:** [Dockerfile](../../Dockerfile).

**Measured evidence:** Both actual Linux patch images ran, passed five references and200 TRAIN probability comparisons within1e-12. [Evidence](../../technical_evaluation/refinement/results/container_final_runtime.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q60. Must documentation stabilization retrain or rebuild every model?

**Model answer:** No. Unchanged runtime hashes preserve the scope of successful application CI; documentation and the new demo receive separate checks. The workflow builds/starts/verifies the exact container for both tested patch versions. Checkout is SHA-pinned and repository permissions are read-only.

**Code to inspect:** [.github/workflows/container-verification.yml](../../.github/workflows/container-verification.yml).

**Measured evidence:** Published application revision869a0a5 passed both Linux jobs. Stabilization changes no application files. [Evidence](../../technical_evaluation/refinement/results/container_final_runtime.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q61. Does READY establish classification validity?

**Model answer:** No. Schema, actual endpoint calls, trusted model identity and prediction parity require independent checks. The same FastAPI app runs on Vercel and caches a model per process. READY build status does not prove successful runtime installation or valid predictions.

**Code to inspect:** [pyproject.toml](../../pyproject.toml).

**Measured evidence:** Both Linux runtimes and live reference parity passed; the existing project/URL and Hobby plan were preserved. [Evidence](../../technical_evaluation/refinement/results/runtime3142_preallow.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q62. Does matching F1 prove identical reconstructed bytes?

**Model answer:** No. These are separately reconstructed objects, not recovered original binaries; metric equality is not serialization identity. Exact versions and hashes reduce environment drift. Seed control alone does not fix iterative numerical differences from BLAS/thread settings.

**Code to inspect:** [technical_evaluation/reconstruct.py :: main](../../technical_evaluation/reconstruct.py#L13).

**Measured evidence:** All21 fits executed; restoring original two-thread control made LR E5/F6/S4 validation F1 exactly match references. [Evidence](../../technical_evaluation/refinement/results/LR_thread_sensitivity.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q63. Why can the forest be below10ms while full inference fails the target?

**Model answer:** Preprocessing/validation/server overhead adds time. Even forest concurrency p95 exceeds10ms; blanket compliance is not claimed. Validation/frame creation, preprocessing, forest computation, server wall time and network response time measure different parts of the system. None directly measures billedCPU.

**Code to inspect:** [technical_evaluation/refinement/cloud_benchmark.py :: benchmark](../../technical_evaluation/refinement/cloud_benchmark.py#L6).

**Measured evidence:** 42/42 requests passed; concurrent forest p95~10.703ms. Original artifact11.665MiB and archived p95=36.808295ms remain unchanged. [Evidence](../../technical_evaluation/refinement/results/cloud_production_profile.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q64. Can that number be called total Vercel cold-start latency?

**Model answer:** No. It excludes platform/module work outside the measured interval and differs from network latency. A new process can load its model cache. Platform/module startup can precede application timing, and a readiness call may warm the process.

**Code to inspect:** [web/app.py :: model_with_timing](../../web/app.py#L34).

**Measured evidence:** One observed production model initialization was~2079.525ms during concurrency; full platform cold-start time unmeasured. [Evidence](../../technical_evaluation/refinement/results/cloud_production_profile.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q65. Is the service fully abuse-proof or operationally certified?

**Model answer:** No. Distributed rate limits, monitoring and safety qualification remain outstanding; heuristic/advisory scans are not absolute security guarantees. Strict2KB bodies,5s body/15s response deadlines, safe errors, CSP and trusted loading reduce concrete risks. A guard permits two active inferences per process.

**Code to inspect:** [web/app.py :: guarded_inference](../../web/app.py#L59).

**Measured evidence:** Timeout/capacity tests pass; known-advisory and heuristic secret scans found no matches within their stated scopes. [Evidence](../../technical_evaluation/refinement/Rate_Limit_Review.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.

### Q66. What additional evidence is needed before real-world operation?

**Model answer:** Independent PV sites/timestamps, prospective calibration/evaluation, stakeholder costs, sensor contracts, rate limits, monitoring, resource qualification and safety review. Scenarios must state active CPU time, memory allocation, in-flight duration and requests. Actual invoices/remaining shared quota are separate evidence.

**Code to inspect:** [technical_evaluation/cloud.py :: main](../../technical_evaluation/cloud.py#L6).

**Measured evidence:** Assumed40ms CPU/request gives1.111 CPU-hours at100k requests and11.111 at1million; no purchase or actual-charge claim. [Evidence](../../technical_evaluation/evidence/rubric5/cost.json).

**Further challenge:** State the assumptions, a possible failure case, and the independent evidence needed to strengthen the conclusion.
