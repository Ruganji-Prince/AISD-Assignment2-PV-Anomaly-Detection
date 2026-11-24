# Student learning guide

The five fixed historical demo references originate in the previously inspected TEST partition. They are parity/reproducibility examples, not independent accuracy evidence; [exact source positions](Submission_Readiness.md#exact-provenance-of-the-five-fixed-references) are documented. No new prediction-based example search is performed.

Study physical/data foundations, then split integrity, models/evaluation, errors and software. Each concept includes a simple explanation, mathematics or contract, project relevance, actual source, measured result and an examination question/answer. The [walkthrough](Evaluation_Walkthrough.md) prepares a repository demonstration; the [mock examination](Mock_Technical_Examination.md) supports independent practice.

The assessment remains **91/100**, not an official grade. Original models/results, reconstructed experiments and production behavior are distinct. Historical TEST is not pristine. No independent-site validity, calibrated production confidence or physical-simulator validation is claimed.

## End-to-end architecture

```mermaid
flowchart LR
  A[Four electrical measurements] --> B[Strict API schema and body validation]
  B --> C[Trusted cached RF pipeline]
  C --> D[Fitted median and four indicators]
  D --> E[Original forest]
  E --> F[Nominal class and actual label]
```

The same model is used by the local CLI and API. The target and source/block metadata are not inputs; calibration alternatives are separate experiments. The diagram describes inference, not model training or a live sensor acquisition system.

## Variables and labels

| Variable | Meaning | Unit / type | Production input |
| --- | --- | --- | --- |
| vdc1,vdc2 | String1/string2 DC RMS voltage | V, continuous | Yes |
| idc1,idc2 | String1/string2 DC RMS current | A, continuous | Yes |
| irr | Reported average plane-of-array irradiance | W/m², continuous | No |
| pvt | Reported average aggregate module temperature | °C, continuous | No |
| f_nv | Experimental operating-state label | Nominal target | Never |

Mapping:0 normal;1 short circuit;2 resistive degradation;3 open circuit;4 natural building shade. Timestamps are absent. Exported-channel counts do not necessarily equal the total source probe count, particularly for aggregate temperature.

## Data engineering and feature screening

### 1.1 Observation and every variable

One prediction classifies one source-position observation. vdc1/vdc2 are the two strings' DC RMS voltages; idc1/idc2 their DC RMS currents. irr is reported plane-of-array irradiance; pvt aggregates module temperature probes. f_nv is an unordered experimental operating-state label.

**Mathematics or contract:** `X has six continuous columns; Y belongs to {0,1,2,3,4}.`

**Why it matters:** Production uses four electrical channels, not irradiance/temperature. An aggregate exported column is not a complete physical probe inventory.

**Implementation:** [src/preprocessing/study.py :: PreprocessingStudy.load_data](../../src/preprocessing/study.py#L25).

**Actual result:** N=1,373,798; P=7. Units V, A, W/m^2 and degrees C. Labels0 normal,1 short circuit,2 degradation,3 open circuit,4 natural building shade. [Evidence](../../phase1_strategy/Variable_Inventory.csv).

**Likely question:** What is the prediction unit, and is f_nv regression?

**Defensible answer:** The unit is an exported source-position observation; integer codes are nominal identities, not continuous severity. There are no reconstructed timestamps.

### 1.2 Dataset provenance

A dataset reference must identify the actual release and conversion, not merely cite a similar paper. Source ordering and hashes preserve traceability.

**Mathematics or contract:** `SHA256 identifies a specific byte sequence.`

**Why it matters:** The release is clayton-h-costa/pv_fault_dataset, associated with Lazzaretti et al.(2020); paper and exported populations are not silently equated.

**Implementation:** [src/preprocessing/study.py :: PreprocessingStudy.load_data](../../src/preprocessing/study.py#L25).

**Actual result:** Raw CSV SHA717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a; pinned upstream commit is in README. [Evidence](../../data/raw/README.md).

**Likely question:** Why retain low-irradiance rows if a filtered population matches literature counts?

**Defensible answer:** The paper does not explicitly establish that exact filtering operation. Rows are retained instead of changing the population to force agreement.

### 1.3 MCAR, MAR and MNAR

MCAR missingness is independent of measurements. MAR may depend on observed values; MNAR additionally depends on unobserved values. MAR does not mean arbitrary independent random disappearance.

**Mathematics or contract:** `MCAR: P(M|X)=P(M). MAR: P(M|X)=P(M|X_obs). MNAR retains X_mis dependence.`

**Why it matters:** An imputation argument must state assumptions. No exported missingness patterns exist from which to identify a mechanism.

**Implementation:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Actual result:** Zero NaNs/infinities and zero incomplete rows. The62 paired irr/pvt zeros remain suspicious observations, not confirmed missingness. [Evidence](../../technical_evaluation/evidence/rubric1/missingness.json).

**Likely question:** Does zero missingness establish MCAR?

**Defensible answer:** No. It describes the released export, not unobserved acquisition failures or the missingness mechanism.

### 1.4 Little MCAR and missingness Cramer V

Little's test needs estimable incomplete-data patterns. Missingness-versus-target Cramer V needs both contingency dimensions to vary.

**Mathematics or contract:** `V=sqrt(chi_squared/[n*min(r-1,c-1)]); a constant missingness category makes the denominator zero.`

**Why it matters:** Statistical software cannot create information absent from the data. Non-applicability needs explicit justification.

**Implementation:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Actual result:** Both tests are NOT APPLICABLE; no statistic or p-value was fabricated. [Evidence](../../technical_evaluation/evidence/rubric1/missingness.json).

**Likely question:** Why omit the named formal tests?

**Defensible answer:** Their applicability conditions fail. Executable evidence verifies constant indicators; it does not support a claim of MCAR/MAR/MNAR.

### 1.5 IQR outlier fences

Quartiles describe the central half of a distribution. Fences flag statistical unusualness rather than establish sensor errors.

**Mathematics or contract:** `IQR=Q3-Q1; lower=Q1-1.5*IQR; upper=Q3+1.5*IQR.`

**Why it matters:** Bounds must be TRAIN-derived. Genuine fault extremes should not automatically disappear from the learning problem.

**Implementation:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Actual result:** TRAIN quartiles, bounds and flagged counts are provided per channel; no automatic removal selected. [Evidence](../../technical_evaluation/evidence/rubric1/training_outliers.csv).

**Likely question:** Would an IQR flag justify deleting a fault observation?

**Defensible answer:** No. Physical validity and experimental context must be assessed separately; a genuine fault can be statistically extreme.

### 1.6 Z-score, skewness and robust MAD

Z-score standardizes distance from a mean. MAD uses distance from a median and resists extreme values. Skewness describes asymmetry.

**Mathematics or contract:** `z=(x-mean)/SD; modified_z=.67448975*(x-median)/MAD.`

**Why it matters:** Mixed operating states are not necessarily one Gaussian population. Dependent rows invalidate naive independent normality interpretation.

**Implementation:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Actual result:** Absolute Z>3 and modified Z>3.5 counts, TRAIN skewness and a bounded normality diagnostic are recorded. [Evidence](../../technical_evaluation/evidence/rubric1/training_outliers.csv).

**Likely question:** Why not remove every absolute Z>3 reading?

**Defensible answer:** That could remove the target fault signatures and imposes an unjustified distributional assumption.

### 1.7 Median imputation and alternatives

A median replacement is learned from training values. Means are sensitive to skew/extremes; mode suits categories; KNN requires meaningful neighbors; interpolation requires justified sequence/timing assumptions.

**Mathematics or contract:** `Missing x_j is replaced by median(x_j in TRAIN).`

**Why it matters:** The export is complete; imputation is a contingency. The62 zeros are not replaced or declared missing.

**Implementation:** [src/phase2_stage2/models.py :: build_preprocessor](../../src/phase2_stage2/models.py#L28).

**Actual result:** Fitted TRAIN medians were independently verified; missing public API inputs are rejected. [Evidence](../../reports/model_verification.json).

**Likely question:** Why have an imputer with zero exported NaNs?

**Defensible answer:** It defines a consistent bounded offline missing-channel policy. It does not prove persistent outage reliability or justify synthetic missingness claims.

### 1.8 Clipping versus retaining values

Clipping caps values at fitted bounds without removing rows. Its effect must be evaluated on unchanged development observations.

**Mathematics or contract:** `Alternative bounds: TRAIN IQR fences or q0.005/q0.995; never validation-fitted quantiles.`

**Why it matters:** Fault signatures can be suppressed by capping. A statistically tidy distribution is not the objective.

**Implementation:** [technical_evaluation/experiments.py :: TrainingClipper](../../technical_evaluation/experiments.py#L15).

**Actual result:** Block13 F1 none=.956297122, IQR=.956297122, quantile=.956041296; original no-clipping policy retained. [Evidence](../../technical_evaluation/evidence/rubric1/clipping_comparison.json).

**Likely question:** Why was clipping rejected?

**Defensible answer:** IQR did not improve validation and quantile clipping slightly degraded it. No automatic winsorization of faults was justified.

### 1.9 Pearson correlation

Pearson measures linear co-variation between numeric measurements. It is not an appropriate interpretation of arbitrary nominal label-code distances.

**Mathematics or contract:** `r=Cov(X,Y)/(SD(X)*SD(Y)).`

**Why it matters:** Strong correlation screens redundancy, not causality or an automatic deletion decision.

**Implementation:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Actual result:** Five TRAIN pairs exceed the absolute.85 screen in the preprocessing evidence. [Evidence](../../technical_evaluation/evidence/rubric1/Pearson.csv).

**Likely question:** Why not correlate voltage with integer f_nv as a continuous outcome?

**Defensible answer:** Renumbering unordered labels would change that quantity. Nominal-target association uses methods such as MI instead.

### 1.10 Spearman correlation

Spearman correlates ranks and can detect monotonic relationships that are nonlinear on the original scale. Ties and dependence still matter.

**Mathematics or contract:** `rho_s=Corr(rank(X),rank(Y)).`

**Why it matters:** It is a sensitivity comparison for skewed/mixed-regime continuous channels.

**Implementation:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Actual result:** Full TRAIN matrix and threshold-screened pairs are published. [Evidence](../../technical_evaluation/evidence/rubric1/Spearman.csv).

**Likely question:** Does Pearson/Spearman agreement prove physical causality?

**Defensible answer:** No. Shared conditions and acquisition design can cause association without establishing a causal intervention.

### 1.11 Variance Inflation Factor

VIF measures how much a predictor is explained by the others, which can destabilize linear coefficient interpretation.

**Mathematics or contract:** `VIF_j=1/(1-R_j_squared).`

**Why it matters:** The threshold>10 is a screen; regularized LR and nonlinear RF still require ablation/physical reasoning rather than blind deletion.

**Implementation:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Actual result:** TRAIN VIF vdc1~52.168, vdc2~56.346, idc1~31.496. [Evidence](../../technical_evaluation/evidence/rubric1/feature_screening.json).

**Likely question:** Why retain high-VIF predictors?

**Defensible answer:** Physical dependencies, regularization and validation ablation support retention. Independent causal coefficient interpretations are not claimed.

### 1.12 Mutual information

MI estimates statistical dependence, including nonlinear association, between a continuous predictor and nominal target. It is not a causal explanation of a fitted forest.

**Mathematics or contract:** `I(X;Y)=sum p(x,y)*log[p(x,y)/(p(x)*p(y))], with continuous estimation in software.`

**Why it matters:** The nominal target needs a label-order-invariant association strategy.

**Implementation:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Actual result:** Seed42 natural-prevalence TRAIN sample50000; diagnostic MI values in nats. [Evidence](../../technical_evaluation/evidence/rubric1/feature_screening.json).

**Likely question:** Is high MI equivalent to trained-model importance?

**Defensible answer:** No. MI describes data association; permutation and SHAP assess specific fitted model behavior.

### 1.13 Principal Component Analysis

PCA rotates standardized measurements into orthogonal directions ranked by variance. Explained variance is not predictive sufficiency.

**Mathematics or contract:** `Z=X_scaled*W; component variance ratio=lambda_j/sum(lambda).`

**Why it matters:** Components need their physical parent inputs. Mathematical dimensionality reduction is not physical sensor reduction.

**Implementation:** [technical_evaluation/data_audit.py :: main](../../technical_evaluation/data_audit.py#L15).

**Actual result:** About95.17% TRAIN variance in two components in original preprocessing; PCA not deployed. [Evidence](../../technical_evaluation/evidence/rubric1/feature_screening.json).

**Likely question:** Why not replace four sensors with two PCs?

**Defensible answer:** PCs still require their source measurements. Explicit sensor-channel ablation addresses acquisition requirements.

### 1.14 Shortcuts and engineering costs

Explicit target/index/block proxies are forbidden, but hidden acquisition dependence cannot be excluded by schema alone. Costs distinguish missed faults from false inspection and environmental shade.

**Mathematics or contract:** `Allowed inference fields are four electrical channels; illustrative risk=sum C_ij*P(Y=i,pred=j).`

**Why it matters:** Hypothetical costs are not stakeholder-approved money and are not optimized on TEST.

**Implementation:** [technical_evaluation/metrics.py :: hypothetical_cost](../../technical_evaluation/metrics.py#L27).

**Actual result:** Hardware-miss weights2/5/10/20 were considered; original10ms/10MiB targets unchanged. [Evidence](../../technical_evaluation/evidence/rubric1/hypothetical_costs.json).

**Likely question:** Can accuracy alone justify an operational decision?

**Defensible answer:** No. Class-specific consequences, physical validity and independent evidence are required; no monetary utility or safety certification is invented.

## Split integrity and leakage prevention

### 2.1 Why ordered rather than random splits

Nearby source positions can share regimes and acquisition conditions. Random stratification can preserve class balance while mixing dependent signals.

**Mathematics or contract:** `Source sets are disjoint; iid independence is not asserted.`

**Why it matters:** The approved ordered split and separators reduce obvious adjacency leakage without fabricating sessions.

**Implementation:** [src/preprocessing/study.py :: PreprocessingStudy.split_data](../../src/preprocessing/study.py#L33).

**Actual result:** TRAIN1006129, VAL116977, TEST146461; no random repartitioning. [Evidence](../../technical_evaluation/evidence/rubric2/leakage.json).

**Likely question:** Would stratified random splitting solve dependence?

**Defensible answer:** No. Balancing labels is different from separating acquisition regimes.

### 2.2 Blocks and separator construction

Irradiance below100 W/m^2 for at least3600 consecutive source positions identifies separators. Sixteen signal-defined blocks have12/2/2 allocation.

**Mathematics or contract:** `Run rule: irr<100 and length>=3600 positions.`

**Why it matters:** No timestamps/day/session identifiers verify elapsed spacing. Nominal1Hz and a16-day study do not turn positions into hours.

**Implementation:** [phase1_strategy/verify_phase1.py :: main](../../phase1_strategy/verify_phase1.py#L19).

**Actual result:** 104231 excluded split-gap positions; blocks are not verified days, sessions or hours. [Evidence](../../phase1_strategy/Phase1_Split_Manifest.json).

**Likely question:** Why not call3600 positions an hour?

**Defensible answer:** Uninterrupted one-second spacing cannot be reconstructed from the released vectors.

### 2.3 Frozen intervals and validation roles

Half-open bounds include the first index and exclude the endpoint. Different development choices use declared populations.

**Mathematics or contract:** `TRAIN[0,1006129), VAL[1056990,1173967), TEST[1227337,1373798).`

**Why it matters:** Block13 chooses settings; block14 originally chooses hardware threshold and later supports separate calibration experiments.

**Implementation:** [src/phase2_stage3/common.py :: load_part](../../src/phase2_stage3/common.py#L20).

**Actual result:** Block13 N32800; block14 N33396; selection is not all116977 validation positions. [Evidence](../../reports/Model_Selection_and_Deployment.md).

**Likely question:** Were all validation rows used for model selection?

**Defensible answer:** No. The reserved range includes background positions; model-selection tables specifically use block13.

### 2.4 Exact vector overlap and conflicts

Canonical physical vectors are hashed and candidate equalities are independently checked. Repeated within-partition states are not automatically erroneous.

**Mathematics or contract:** `BLAKE2b-128 over float64 vectors, followed by numeric equality verification.`

**Why it matters:** No target or metadata is included in the compared inference features.

**Implementation:** [technical_evaluation/data_audit.py :: vector_hash](../../technical_evaluation/data_audit.py#L11).

**Actual result:** Zero cross-partition exact matches for four/six channels; zero conflicting-label duplicate vectors. [Evidence](../../technical_evaluation/evidence/rubric2/leakage.json).

**Likely question:** Does a hash alone establish no leakage?

**Defensible answer:** No. Vector construction, equality, source/block isolation and learned-transform fitting all matter.

### 2.5 Near-duplicate analysis

Nearest neighbors measure similarity after TRAIN-fitted standardization; close values need not hash equally.

**Mathematics or contract:** `Euclidean distance<=.001; exact cKDTree eps0 search.`

**Why it matters:** No legitimate similar measurement is removed merely to manufacture independence.

**Implementation:** [technical_evaluation/refinement/experiments.py :: near](../../technical_evaluation/refinement/experiments.py#L15).

**Actual result:** All TRAIN references and later queries; E4 near counts37313VAL/62917TEST; F6 counts1290/1125; exact distances0. [Evidence](../../technical_evaluation/refinement/results/full_near_duplicates.json).

**Likely question:** Are close states proof of target leakage?

**Defensible answer:** No. They limit independence/transfer claims and may reflect legitimate repeated operating states. The fixed split is retained.

### 2.6 Pipeline and ColumnTransformer isolation

Pipeline fits transformations in sequence; ColumnTransformer routes approved columns and drops the rest. These classes do not repair a scaler previously fitted on all data.

**Mathematics or contract:** `Fit learned parameters on TRAIN, then transform VAL/TEST.`

**Why it matters:** The same learned median/scaler/indicator transform must be reused at inference.

**Implementation:** [src/phase2_stage2/models.py :: build_preprocessor](../../src/phase2_stage2/models.py#L28).

**Actual result:** TRAIN medians and LR means/variances checked; remainder=drop and retained schema explicit. [Evidence](../../reports/model_verification.json).

**Likely question:** Can a global scaler followed by Pipeline prevent leakage?

**Defensible answer:** No. Later-partition information has already entered the scaler; fitting must be isolated before evaluation.

### 2.7 Fold-specific fitting and class weights

Every grouped fold independently fits preprocessing and classifier. Weights use that fit fold's available classes and counts.

**Mathematics or contract:** `w_k=N_fit/(K_observed*n_k_fit).`

**Why it matters:** A group-aware index split is insufficient if preprocessing or weighting learns evaluation statistics.

**Implementation:** [technical_evaluation/experiments.py :: fit_one](../../technical_evaluation/experiments.py#L46).

**Actual result:** Nine independent fits, three families times three nonshuffled TRAIN folds; digests and supports retained. [Evidence](../../technical_evaluation/evidence/rubric2/grouped_validation.json).

**Likely question:** Which code verifies preprocessing isolation?

**Defensible answer:** assert_fit_isolated rejects overlap; fit_one checks learned medians, scaler means and clipping fit-index digest against the actual fitting rows.

### 2.8 Historical TEST exposure

Implementation leakage prevention and an independent prospective holdout are different claims. Human knowledge of prior TEST cannot be erased.

**Mathematics or contract:** `No rerun or resampling formula creates a pristine holdout.`

**Why it matters:** New experimental choices are frozen before retrospective TEST diagnostics, but external generalization still requires new data.

**Implementation:** [technical_evaluation/refinement/experiments.py :: freeze](../../technical_evaluation/refinement/experiments.py#L14).

**Actual result:** Prior TEST exposure is prominent; no new TEST-guided model/feature/calibration/threshold choice. [Evidence](../../technical_evaluation/refinement/Protocol.json).

**Likely question:** How can leakage prevention be claimed after TEST inspection?

**Defensible answer:** No identified unaddressed target/preprocessing leak is claimed. Pristine holdout independence is explicitly not claimed; historical design exposure remains a limitation.

## Machine learning and evaluation

### 3.1 Multiclass Logistic Regression

LR models class log-odds as linear functions of transformed inputs. Regularization limits coefficients; scaling makes penalty geometry more comparable across units.

**Mathematics or contract:** `p_k=exp(w_k^T*x+b_k)/sum_j exp(w_j^T*x+b_j).`

**Why it matters:** It is an interpretable functional baseline, not a claim that nominal labels have numeric distances.

**Implementation:** [src/phase2_stage1/models.py :: F6Model](../../src/phase2_stage1/models.py#L14).

**Actual result:** Original LR F6 block13 F1=.893870 and historical TEST=.898389; E4 same-input comparison is separate. [Evidence](../../technical_evaluation/evidence/rubric3/model_comparison.json).

**Likely question:** Why scale LR but not treat f_nv as a continuous target?

**Defensible answer:** Scaling concerns predictor geometry; the likelihood still models unordered class identities.

### 3.2 Random Forest

RF averages class distributions across randomized trees fitted to bootstrapped data. Threshold trees model nonlinear interactions without requiring standardization.

**Mathematics or contract:** `p_k(x)=mean_t p_tk(x); prediction=argmax_k p_k.`

**Why it matters:** The original E4 forest remains the deployed research artifact. Depth/leaf limits do not guarantee external transfer.

**Implementation:** [src/phase2_stage1/models.py :: F6Model](../../src/phase2_stage1/models.py#L14).

**Actual result:** 100 trees, depth10, minimum leaf20, max_features=sqrt, seed42, TRAIN-balanced weights. [Evidence](../../technical_evaluation/evidence/rubric3/original_model_parameters.json).

**Likely question:** What prevents overfitting at a new PV installation?

**Defensible answer:** Development validation and capacity restrictions help, but independent-site transfer is unverified and cannot be guaranteed from this study.

### 3.3 LightGBM

Boosting adds trees sequentially to reduce loss. Leaf-wise growth captures interactions; leaf/depth constraints limit capacity.

**Mathematics or contract:** `F_m=F_(m-1)+learning_rate*h_m, followed by multiclass probability mapping.`

**Why it matters:** It is compared with LR/RF and computes explicit physical derivatives only when parent channels are retained.

**Implementation:** [src/phase2_stage1/models.py :: F6Model](../../src/phase2_stage1/models.py#L14).

**Actual result:** Selected family settings include150 trees, learning rate.05, depth6 and31 leaves; original E4 TEST F1=.902137. [Evidence](../../technical_evaluation/evidence/rubric3/original_model_parameters.json).

**Likely question:** Why not select LightGBM from hardware AP alone?

**Defensible answer:** Hardware ranking can conceal subtype failure: archived short-circuit recall is approximately.499365. Selection and error interpretation must be class-specific.

### 3.4 Most-frequent and class-prior baselines

Most-frequent predicts the largest TRAIN class. Prior supplies the full TRAIN prevalence vector; the two can share argmax outputs but differ in probability quality.

**Mathematics or contract:** `Prior p_k=n_k_TRAIN/N_TRAIN.`

**Why it matters:** Performance must exceed prevalence-driven behavior rather than rely on majority-class accuracy.

**Implementation:** [technical_evaluation/experiments.py :: model_metrics](../../technical_evaluation/experiments.py#L93).

**Actual result:** Both Dummy argmax F1 values: block13 .144269; TEST .183800. Calculations were reproduced. [Evidence](../../technical_evaluation/refinement/results/baseline_reverification.json).

**Likely question:** Why report both if F1 is identical?

**Defensible answer:** Their probability distributions and proper scoring rules differ, even though their classifications coincide.

### 3.5 Distinct physical-rule baselines

The historical score standardizes current/voltage discrepancies against normal TRAIN statistics. The audit later adds a separate TRAIN-q99 current-imbalance reference. Neither is a five-class diagnosis.

**Mathematics or contract:** `Audit imbalance=abs(idc1-idc2)/(abs(idc1)+abs(idc2)+1e-12); threshold=TRAIN q99.`

**Why it matters:** A simple physics-motivated reference anchors evaluation without claiming detailed fault identification.

**Implementation:** [src/phase2_stage1/models.py :: EngineeringReference](../../src/phase2_stage1/models.py#L44).

**Actual result:** The audit rule reports binary hardware AP/recall and normal/shade FPR; the historical two-discrepancy score is separately documented. [Evidence](../../technical_evaluation/evidence/rubric3/model_comparison.json).

**Likely question:** Are these two rule baselines the same implementation?

**Defensible answer:** No. The normal-referenced two-discrepancy score and q99 current-only rule are distinct and should not be conflated.

### 3.6 Class imbalance and weighting

Rare classes receive larger loss weights. Weighting changes the objective; it neither adds independent examples nor teaches an absent class.

**Mathematics or contract:** `Complete TRAIN weights w_k=N/(5*n_k); fold weights use observed fit classes.`

**Why it matters:** Normal TRAIN count844805 greatly exceeds short-circuit1226 and open-circuit1204. No SMOTE was used.

**Implementation:** [src/phase2_stage1/contracts.py :: weights](../../src/phase2_stage1/contracts.py#L39).

**Actual result:** TRAIN class counts844805,1226,5695,1204,153199; explicit balanced dictionary verified. [Evidence](../../phase2_implementation/stage1/evidence/class_weights.json).

**Likely question:** Can a high weight repair zero class support?

**Defensible answer:** No. No observations exist from which to learn that class; support limitations must be reported.

### 3.7 Bounded hyperparameter search

A declared development search avoids unlimited experimentation until TEST looks favorable. Stage2 freezes family settings while varying channels.

**Mathematics or contract:** `Stage1 budget16: LR C .1/1; RF depth6/10; GB leaves/depth15/4 or31/6; declared weighting/feature policies.`

**Why it matters:** Seed, budget, tie-breaks and selection population make provenance inspectable.

**Implementation:** [src/phase2_stage1/run.py :: trial_specs](../../src/phase2_stage1/run.py#L25).

**Actual result:** Block13 macro-F1 selected per-family settings; block14/TEST were not Stage1 scoring populations. [Evidence](../../phase2_implementation/stage1/evidence/experiment_configuration.json).

**Likely question:** Are21 sensor comparisons another21-setting hyperparameter search?

**Defensible answer:** No. They compare seven channel groups across three families using frozen family settings.

### 3.8 Sensor ablation and mathematical features

Ablation refits using only retained channels. Mathematical indicators/derivatives must not be counted as extra acquired sensors.

**Mathematics or contract:** `RF E4=4raw+4indicators=8; GB E4=4raw+5derived+4indicators=13; LR F6=6raw+6indicators=12.`

**Why it matters:** Derived power requires its voltage/current parent channels. A temperature aggregate can require several source probes.

**Implementation:** [src/phase2_stage2/models.py :: AblationModel](../../src/phase2_stage2/models.py#L38).

**Actual result:** Seven groups times three families; production accepts exactly vdc1,vdc2,idc1,idc2. [Evidence](../../phase2_implementation/stage2/evidence/sensor_ablation_validation.csv).

**Likely question:** Why are four physical measurements sufficient?

**Defensible answer:** They meet the selected rule among evaluated alternatives; no globally minimum hardware inventory or PCA equivalence is claimed.

### 3.9 Selection versus full engineering acceptance

The sensing/performance candidate is distinct from a resource-qualified candidate. A null resource result must remain null.

**Mathematics or contract:** `Validation: F1>=.80; each hardware recall>=.90; F6 degradation<=.05; channels<=4. Separate latency<=10ms and size<=10MiB.`

**Why it matters:** A research demonstrator can be selected while still failing resource targets.

**Implementation:** [src/phase2_stage2/selection.py :: select](../../src/phase2_stage2/selection.py#L11).

**Actual result:** RF E4 alone passed the four sensing/performance constraints; resource/performance candidate was null. [Evidence](../../reports/Model_Selection_and_Deployment.md).

**Likely question:** Why select a model larger than10MiB?

**Defensible answer:** The prototype passed a different declared validation rule. It was never relabeled as satisfying full engineering acceptance.

### 3.10 Confusion matrices

Rows are true classes; columns are predictions. Offline evidence retains a separate abstention column rather than hiding unsupported predictions.

**Mathematics or contract:** `Confusion count C_ij=sum 1[Y=i,pred=j].`

**Why it matters:** Counts reveal which errors an aggregate score conceals, including environmental versus hardware confusions.

**Implementation:** [technical_evaluation/metrics.py :: evaluate](../../technical_evaluation/metrics.py#L18).

**Actual result:** RF historical TEST has6604 true-normal observations predicted shade. [Evidence](../../technical_evaluation/evidence/rubric3/model_comparison.json).

**Likely question:** Can a diagonal-looking matrix be judged without supports?

**Defensible answer:** No. Row/class counts and error consequences matter, especially for rare hardware states.

### 3.11 Precision, recall and F1

Precision measures correctness among predicted class members; recall measures recovered true members. F1 combines both and is not a simple average of accuracy.

**Mathematics or contract:** `P=TP/(TP+FP); R=TP/(TP+FN); F1=2PR/(P+R).`

**Why it matters:** A high recall can coexist with low precision when many normal observations are falsely assigned the class.

**Implementation:** [technical_evaluation/metrics.py :: evaluate](../../technical_evaluation/metrics.py#L18).

**Actual result:** Shade precision .691081 and recall .991146. [Evidence](../../technical_evaluation/evidence/rubric4/normal_shade_errors.json).

**Likely question:** Does near-perfect shade recall prove good shade discrimination?

**Defensible answer:** No. Normal-to-shade errors lower precision; both directions and their denominators must be examined.

### 3.12 Macro versus weighted F1 and balanced accuracy

Macro averages class F1 equally. Weighted F1 uses supports. Balanced accuracy averages supported-class recall; absent-class conventions must be explicit.

**Mathematics or contract:** `MacroF1=mean_k F1_k; weightedF1=sum n_k*F1_k/N; BA=mean_k recall_k.`

**Why it matters:** Rare faults deserve attention that majority-dominated accuracy can hide. Supported-class and fixed-five averages are not interchangeable.

**Implementation:** [technical_evaluation/metrics.py :: evaluate](../../technical_evaluation/metrics.py#L18).

**Actual result:** Original RF validation F1=.956297 and historical TEST=.950481; full per-class/base-rate metrics are available. [Evidence](../../technical_evaluation/evidence/rubric3/model_comparison.json).

**Likely question:** Why not MAE between integer target codes?

**Defensible answer:** Unordered code distances have no physical or validated utility meaning; a cost function needs separately stated costs.

### 3.13 Average precision, PR-AUC and inspection budgets

AP accumulates precision at recall increments in ranking order. Trapezoidal PR-AUC uses a different interpolation. Precision at k concerns an explicit inspection budget.

**Mathematics or contract:** `AP=sum_n (R_n-R_(n-1))*P_n; top1% uses k=ceil(.01N).`

**Why it matters:** Rare-event metrics require prevalence and exact definitions; ranking quality is not subtype correctness.

**Implementation:** [technical_evaluation/metrics.py :: evaluate](../../technical_evaluation/metrics.py#L18).

**Actual result:** Original RF historical TEST hardware AP~.993354. Macro AP is one-vs-rest average precision, not trapezoidal area. [Evidence](../../technical_evaluation/evidence/rubric3/model_comparison.json).

**Likely question:** Can excellent hardware AP coexist with poor short-circuit diagnosis?

**Defensible answer:** Yes. Classes1/2/3 are combined for hardware ranking; subtype confusion can remain severe.

### 3.14 Hardware threshold and false-alarm denominators

Hardware score sums only classes1/2/3. Shade is excluded. A binary alert is different from multiclass argmax and needs a declared negative population.

**Mathematics or contract:** `s=p1+p2+p3; alert if s>=tau; combined FPR denominator is true{0,4}.`

**Why it matters:** Normal-only, shade-only and combined FPR answer different operational questions.

**Implementation:** [src/phase2_stage3/common.py :: select_threshold](../../src/phase2_stage3/common.py#L39).

**Actual result:** Original tau=.5913558658757772; maximize block14 hardware recall subject to combined FPR<=.01 with exact-score enumeration/tie-breaks. [Evidence](../../phase2_implementation/stage3/evidence/final_candidate_comparison.csv).

**Likely question:** Does the production API apply this threshold?

**Defensible answer:** No. hardware_fault_class reflects the argmax nominal prediction. Archived binary-alert evaluation is a separate policy.

### 3.15 Calibration fit/evaluation isolation

Sigmoid maps each class probability through a logistic function; isotonic fits a monotone map. Separate calibration does not create an independent deployment guarantee.

**Mathematics or contract:** `q_k=g_k(p_k)/sum_j g_j(p_j), after clipping at1e-12.`

**Why it matters:** Maps fit block14 only; four256-position tile folds purge64 neighboring positions. Tiles are not independent sessions.

**Implementation:** [technical_evaluation/experiments.py :: ProbabilityMap](../../technical_evaluation/experiments.py#L56).

**Actual result:** Minimum positives50 sigmoid/100 isotonic and100 negatives passed. Sigmoid selected using block14 OOF logloss before retrospectiveTEST. [Evidence](../../technical_evaluation/refinement/results/probability_normalization.json).

**Likely question:** Why was calibration not deployed?

**Defensible answer:** One historical block is insufficient justification for changing operational probability/threshold policy. No calibrated confidence or calibrated alert threshold was deployed.

### 3.16 Brier score, log loss and ECE

Brier penalizes squared probability error; log loss penalizes confident wrong predictions; ECE compares binned confidence with frequency and depends on binning.

**Mathematics or contract:** `Brier=mean_i sum_k(p_ik-onehot_ik)^2; logloss=-mean log(p_true); ECE=sum_b(n_b/N)*abs(conf_b-acc_b).`

**Why it matters:** Proper scoring rules complement class predictions. This multiclass Brier is not divided by the number of classes.

**Implementation:** [technical_evaluation/metrics.py :: probability_metrics](../../technical_evaluation/metrics.py#L12).

**Actual result:** Original Brier/logloss/ECE .079293/.151089/.023762; sigmoid .051306/.089088/.014281; isotonic .053112/.092305/.011333. [Evidence](../../technical_evaluation/refinement/results/calibration/calibration_TEST_retrospective.json).

**Likely question:** Why prefer sigmoid when isotonic has lower TEST ECE?

**Defensible answer:** The frozen selection criterion is block14 OOF logloss, not TEST ECE. Post-hoc criterion switching would undermine selection provenance.

### 3.17 Reliability diagrams

Each bin compares mean predicted probability with observed event frequency. Empty bins provide no evidence; bin counts and population definition matter.

**Mathematics or contract:** `Perfect calibration would follow observed_frequency=mean_probability, subject to uncertainty.`

**Why it matters:** Top-label, per-class and hardware reliability are different targets and none certifies external-site reliability.

**Implementation:** [technical_evaluation/metrics.py :: reliability](../../technical_evaluation/metrics.py#L4).

**Actual result:** Ten equal-width bins; reproduced Brier/logloss/ECE match prior values within1e-12. [Evidence](../../technical_evaluation/refinement/figures/reproduced_reliability.png).

**Likely question:** Is a visually diagonal diagram enough to display calibrated confidence?

**Defensible answer:** No. The specific deployed map/population/policy needs independent validation; the existing UI intentionally displays no confidence percentage.

### 3.18 Grouped CV and unsupported classes

Three nonshuffled folds hold out whole TRAIN operating blocks and independently fit each family. The population excludes background rows, unlike the full original split.

**Mathematics or contract:** `Three folds over12 TRAIN operating blocks; no shuffled row CV.`

**Why it matters:** Class1 appears only in block12; holding it out makes class1 unlearnable. Class3 is also concentrated there.

**Implementation:** [technical_evaluation/experiments.py :: training_experiments](../../technical_evaluation/experiments.py#L124).

**Actual result:** RF supported-class F1 approximately.512135/.913322/.897464; original TEST .950481 is a different protocol/population. [Evidence](../../technical_evaluation/evidence/rubric2/grouped_validation.json).

**Likely question:** Why is grouped validation worse than original TEST performance?

**Defensible answer:** It exposes acquisition transfer and absent fit-class support. These scores are not interchangeable unbiased estimates of one population.

### 3.19 Block-bootstrap uncertainty

Whole block confusion matrices are resampled to preserve within-block dependence. The procedure does not prove blocks themselves are independent.

**Mathematics or contract:** `1000 draws of12 TRAIN grouped-OOF block matrices with replacement; seed42.`

**Why it matters:** Class-support conditioning changes the resampling population; supported-class averaging changes its class set.

**Implementation:** [technical_evaluation/refinement/experiments.py :: uncertainty](../../technical_evaluation/refinement/experiments.py#L34).

**Actual result:** 671 all-five-supported draws; conditional F1 range.495205-.623462; unconditional fixed-five convention .373881-.721550. [Evidence](../../technical_evaluation/refinement/results/bootstrap_sensitivity.json).

**Likely question:** Are these intervals around deployed TEST F1 .950481?

**Defensible answer:** No. They summarize preserved TRAIN grouped-OOF outcomes under stated conventions, not independent deployed TEST or external-site coverage.

## Robustness and explainability

### 4.1 Subgroup/regime analysis

Global averages can hide errors concentrated at particular irradiance, temperature, output or imbalance ranges. Every slice needs supports and fixed boundaries.

**Mathematics or contract:** `Output=vdc1*idc1+vdc2*idc2; imbalance=abs(a-b)/(abs(a)+abs(b)+1e-12).`

**Why it matters:** Physical irradiance cutoffs100/400/800 and TRAIN quartiles avoid TEST-selected subgroup boundaries.

**Implementation:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Actual result:** TRAIN/VAL/TEST and source blocks reported separately; N<100 and class support<50 flagged. [Evidence](../../technical_evaluation/evidence/rubric4/subgroups.json).

**Likely question:** Can a slice with no hardware examples establish zero miss rate?

**Defensible answer:** No. Hardware recall is undefined without positive opportunities; absent support is not safety evidence.

### 4.2 Cohort shift

Features and class prevalence can differ across cohorts without known timestamps. The appropriate term here is source-cohort shift, not verified calendar-time drift.

**Mathematics or contract:** `Reference bins/scaling are fitted on TRAIN, then later cohorts are compared.`

**Why it matters:** Prevalence affects precision/AP, while acquisition differences may limit transfer.

**Implementation:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Actual result:** Substantial current-channel shifts are measured; operating/background mixture also differs. [Evidence](../../technical_evaluation/evidence/rubric4/shift.json).

**Likely question:** How would an entirely new photovoltaic installation behave?

**Defensible answer:** Behavior is unverified. Hardware, sensor calibration and operating regimes may shift; independent prospective site evidence is necessary.

### 4.3 Population Stability Index

PSI compares histogram proportions. Values depend on binning and epsilon choices; no validated operational alarm is inferred.

**Mathematics or contract:** `PSI=sum_b(q_b-p_b)*log(q_b/p_b).`

**Why it matters:** TRAIN decile bins and epsilon1e-6 make the comparison explicit and reproducible.

**Implementation:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Actual result:** TEST idc1 PSI~4.627 and idc2~3.682. [Evidence](../../technical_evaluation/evidence/rubric4/shift.json).

**Likely question:** Does a large PSI prove a hardware malfunction?

**Defensible answer:** No. It describes distribution difference under selected bins; a cause or operational alarm requires additional evidence.

### 4.4 KS effect size

KS is the largest separation between empirical cumulative distribution functions. A large dependent dataset does not justify naive iid significance claims.

**Mathematics or contract:** `D_KS=sup_x abs(F(x)-G(x)).`

**Why it matters:** Effect sizes are emphasized instead of tiny p-values driven by sample size and dependence.

**Implementation:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Actual result:** TEST idc1 KS~.431; iid p-values are not interpreted. [Evidence](../../technical_evaluation/evidence/rubric4/shift.json).

**Likely question:** Why not use a tiny KS p-value as independent proof?

**Defensible answer:** Rows are dependent. A p-value under the wrong sampling assumptions would exaggerate the conclusion.

### 4.5 Wasserstein distance

One-dimensional Wasserstein measures the area between CDFs and retains the sensor unit, unlike a dimensionless KS statistic.

**Mathematics or contract:** `W1=integral abs(F(x)-G(x)) dx.`

**Why it matters:** TRAIN-IQR-normalized values permit scale-aware comparisons but remain descriptive.

**Implementation:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Actual result:** Distances are published in original units and relative to TRAIN IQR for each channel/cohort. [Evidence](../../technical_evaluation/evidence/rubric4/shift.json).

**Likely question:** Why report both absolute and normalized distance?

**Defensible answer:** Absolute distance preserves engineering units; normalization describes change relative to reference variability. Neither alone establishes causality.

### 4.6 Noise and systematic bias

Noise is random perturbation; bias is a systematic offset. The percentage requires a defined scale, not an unexplained fraction of a reading.

**Mathematics or contract:** `Noise SD=a*TRAIN_IQR, a=.01/.02/.05/.10; bias +/- .05/.10 TRAIN_IQR; negatives clamped to0.`

**Why it matters:** The frozen model is stressed using fixed block13 examples and seeds, not retuned to TEST. Source labels are retained as an assumption.

**Implementation:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Actual result:** N12000; seeds42/43/44. F1 at5% noise .796863-.798149; at10% .645450-.655924. [Evidence](../../technical_evaluation/evidence/rubric4/stress.json).

**Likely question:** Are these measured field sensor failures?

**Defensible answer:** No. They are simulated perturbations; extreme changes can violate photovoltaic relationships and label persistence is not independently validated.

### 4.7 Dropout versus bounded imputation

Offline eligibility permits at most one unavailable channel and a missing run of at most two consecutive source positions. Sparse sample gaps reset the rule.

**Mathematics or contract:** `Eligible=(missing_channels<=1) AND (maximum_run<=2).`

**Why it matters:** Isolated-missing coverage must not be mislabeled as sustained outage tolerance.

**Implementation:** [src/phase2_stage1/features.py :: eligible](../../src/phase2_stage1/features.py#L44).

**Actual result:** Contiguous block13 outage leaves2/32800 eligible; two missing channels give zero coverage. Missing public inputs are rejected. [Evidence](../../technical_evaluation/evidence/rubric4/contiguous_dropout.json).

**Likely question:** What happens during persistent dropout?

**Defensible answer:** The offline policy abstains after two positions; the API rejects missing measurements instead of promising reliable persistent imputation.

### 4.8 Saturation and OOD

Saturation fixes a sensor to a bound; OOD means insufficient support under the reference distribution. A finite nonnegative vector need not obey joint PV physics.

**Mathematics or contract:** `Saturation uses TRAIN q05/q95; finite OOD uses TRAIN maximum+IQR.`

**Why it matters:** Observed-range warnings are not certified safety limits or a multivariate OOD detector.

**Implementation:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Actual result:** Finite OOD stress F1~.144341. The API warns on observed-range exceedance without silent clipping. [Evidence](../../technical_evaluation/evidence/rubric4/stress.json).

**Likely question:** Can range checks reject every physically dangerous input?

**Defensible answer:** No. Joint relationships and certified operating envelopes require additional domain validation.

### 4.9 Permutation importance

A raw channel is shuffled while the full downstream feature pipeline is recomputed. Score loss describes model dependence on that channel/sample.

**Mathematics or contract:** `Importance=baseline_score-permuted_score.`

**Why it matters:** Shuffling only an engineered derivative would not model loss of its physical parent. Correlated channels can share importance.

**Implementation:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Actual result:** RF-specific sample1000 balanced rows,200/class, seed42, three repeats; archived family permutation also reproduced. [Evidence](../../technical_evaluation/evidence/rubric4/RF_raw_channel_permutation.json).

**Likely question:** Does importance establish which sensor causes the fault?

**Defensible answer:** No. Predictive dependence under permutation is not a causal physical intervention.

### 4.10 LightGBM Tree SHAP

Native contributions decompose raw class scores relative to a base value. Additivity verifies algebraic consistency, not causal correctness.

**Mathematics or contract:** `Raw_score_k=base_k+sum_j contribution_jk.`

**Why it matters:** These explanations belong to LightGBM; they must not be relabeled RF SHAP or probability percentage points.

**Implementation:** [src/evaluation/verify_explanations.py :: main](../../src/evaluation/verify_explanations.py#L10).

**Actual result:** Native LightGBM additivity and mean absolute contributions match archived references; RF has separate permutation evidence. [Evidence](../../technical_evaluation/evidence/rubric4/archived_explanations_reverification.json).

**Likely question:** Is the UI explanatory text local RF SHAP?

**Defensible answer:** No. It describes the actual predicted class; no feature contributions are fabricated.

### 4.11 Normal versus shade confusion

High shade recall can coexist with poor precision when normal observations are also predicted shade. Environmental classification errors are not hardware alerts by definition.

**Mathematics or contract:** `Precision_shade=TP_shade/(TP_shade+FP_shade).`

**Why it matters:** Conditional sensor medians describe measured association, not a causal explanation for the errors.

**Implementation:** [technical_evaluation/robustness.py :: main](../../technical_evaluation/robustness.py#L11).

**Actual result:** 6604 normal-to-shade errors; shade precision .691081 and recall .991146. [Evidence](../../technical_evaluation/evidence/rubric4/normal_shade_errors.json).

**Likely question:** Why not count class4 as a broken-hardware detection?

**Defensible answer:** Its source label is natural building shade, an environmental condition; changing the definition would misrepresent the task.

### 4.12 Synthetic versus historical demonstration

Historical references, original hand-designed synthetic intents and new TRAIN-derived empirical perturbations are distinct sources. None should borrow another source's validity claim.

**Mathematics or contract:** `Ten complete TRAIN rows/class/seed for five seeds; shared voltage gain exp(N(0,.002)) and current gain exp(N(0,.01)).`

**Why it matters:** No generated candidate is rejected because the prediction disagrees. Shared gains preserve pair ratios, not full photovoltaic dynamics.

**Implementation:** [technical_evaluation/refinement/experiments.py :: synthetic](../../technical_evaluation/refinement/experiments.py#L25).

**Actual result:** Original presets all predictshade. Fixed250 empirical cases have249 conditioning agreements; parents were used in model fitting. [Evidence](../../technical_evaluation/refinement/results/empirical_scenarios.json).

**Likely question:** Does249/250 prove generalization, or why do all old presets predictshade?

**Defensible answer:** It does not prove generalization: parents are TRAIN observations. Old intuitive marginal values need not follow learned joint regimes; neither generator is a validated fault simulator.

## Software engineering and deployment

### 5.1 Repository architecture and execution modes

Data/provenance, preprocessing, original modeling/evaluation, inference/web and technical evidence have separate roles. Quick verification is different from expensive reproduction.

**Mathematics or contract:** `The software contract is explicit entry points and versioned artifacts.`

**Why it matters:** A professor needs direct source/result/command navigation without confusing historical snapshots with current evidence.

**Implementation:** [technical_evaluation/refinement/verify.py :: main](../../technical_evaluation/refinement/verify.py#L18).

**Actual result:** Quick audit runs30 tests and protected/hash/link checks, with no fitting/cloud calls or tracked-receipt rewrites. [Evidence](../../technical_evaluation/refinement/results/clean_clone_quick_audit.json).

**Likely question:** Will the quick command retrain production?

**Defensible answer:** No. New fits require an explicit separate reconstruction command and remain outside the production model path.

### 5.2 Serialization and trusted SHA

Pickle stores Python object state, including fitted medians and trees, but loading arbitrary pickle objects can execute code. Identity is not inherently safety.

**Mathematics or contract:** `SHA256(model_bytes) must equal the fixed trusted digest before pickle.loads.`

**Why it matters:** The application accepts only its fixed trusted model, not user-uploaded serialized objects.

**Implementation:** [src/inference/cli.py :: load_model](../../src/inference/cli.py#L35).

**Actual result:** Original model SHA55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb remains verified. [Evidence](../../models/rf_e4/provenance.json).

**Likely question:** Would hashing any uploaded pickle make it safe?

**Defensible answer:** No. The reference must itself be trusted. This service has no arbitrary model-upload endpoint.

### 5.3 FastAPI lifecycle

A prediction request passes content/body/schema validation, local capacity, cached trusted loading, fitted preprocessing/forest and actual-class response. Middleware adds security/timing headers.

**Mathematics or contract:** `422 validation;503 unavailable/busy;504 response deadline;408 body deadline.`

**Why it matters:** The response comes from four measurements, not the scenario button or true-label metadata.

**Implementation:** [web/app.py :: predict_measurements](../../web/app.py#L114).

**Actual result:** Five predetermined cases match CLI/API; invalid input and timing headers were checked. [Evidence](../../technical_evaluation/refinement/results/final_preview_verification.json).

**Likely question:** Does the backend read a scenario label to return the desired result?

**Defensible answer:** No. Target/index/scenario metadata is forbidden in the inference schema.

### 5.4 Frontend/backend communication

Four client-side panels preserve measurements, source/scenario, chart and prediction state. Requests use the same-origin API and stale results clear after input edits.

**Mathematics or contract:** `One visible panel and preserved state are interface invariants, not model accuracy measures.`

**Why it matters:** Keyboard, reduced-motion and responsive behavior support a reliable demonstration without changing scientific behavior.

**Implementation:** [web/static/app.js](../../web/static/app.js).

**Actual result:** Smoke tests passed desktop1366/1920, tablet820 and mobile390/320 widths, navigation and error paths. [Evidence](../../technical_evaluation/refinement/results/production_browser.json).

**Likely question:** Are animated input bars a live PV installation feed?

**Defensible answer:** No. They visualize entered/example measurements; hosting does not establish live acquisition or real-time operational monitoring.

### 5.5 Input schema and physical validity

Exactly four finite nonnegative numeric fields are accepted. Strings, booleans, duplicate/extra keys and nonfinite JSON are rejected. Range warnings do not certify physics.

**Mathematics or contract:** `Schema={vdc1,vdc2,idc1,idc2}; body<=2048 bytes.`

**Why it matters:** Strict contracts prevent accidental target/metadata leakage and silent defaults, while joint physical validity remains a limitation.

**Implementation:** [src/inference/cli.py :: validate](../../src/inference/cli.py#L18).

**Actual result:** Malformed, duplicate, oversize, missing, extra, nonnumeric, negative and nonfinite cases are tested. [Evidence](../../web/tests/test_api.py).

**Likely question:** Why not silently cap400V to a TRAIN bound?

**Defensible answer:** That would alter evidence without validation. The value is preserved with a warning; observed ranges are not safety limits.

### 5.6 Docker architecture

A container packages an inference runtime, not a newly trained model. Its image size includes Python/dependencies and is distinct from model-artifact size.

**Mathematics or contract:** `Default Python3.14.10; tested3.14.2 alternative; hash-locked installation; nonroot user; read-only execution test.`

**Why it matters:** A Dockerfile alone is not execution evidence. Local Windows Docker/WSL is unavailable.

**Implementation:** [Dockerfile](../../Dockerfile).

**Actual result:** Both actual Linux patch images ran, passed five references and200 TRAIN probability comparisons within1e-12. [Evidence](../../technical_evaluation/refinement/results/container_final_runtime.json).

**Likely question:** Is Docker verified locally?

**Defensible answer:** No. Actual builds/runs used standard free public GitHub Linux runners, with their environment and timings recorded.

### 5.7 GitHub Actions

The workflow builds/starts/verifies the exact container for both tested patch versions. Checkout is SHA-pinned and repository permissions are read-only.

**Mathematics or contract:** `Standard ubuntu-latest matrix; no paid/large runner or model-registry publication.`

**Why it matters:** Workflow success is evidence for its tested revision, not a guarantee for unknown future platforms.

**Implementation:** [.github/workflows/container-verification.yml](../../.github/workflows/container-verification.yml).

**Actual result:** Published application revision869a0a5 passed both Linux jobs. Stabilization changes no application files. [Evidence](../../technical_evaluation/refinement/results/container_final_runtime.json).

**Likely question:** Must documentation stabilization retrain or rebuild every model?

**Defensible answer:** No. Unchanged runtime hashes preserve the scope of successful application CI; documentation and the new demo receive separate checks.

### 5.8 Vercel deployment and runtime compatibility

The same FastAPI app runs on Vercel and caches a model per process. READY build status does not prove successful runtime installation or valid predictions.

**Mathematics or contract:** `Explicit allowed patches3.14.2/.7/.8/.10; unknown patches fail rather than silently load unverified objects.`

**Why it matters:** An earlier preview exposed a provider patch mismatch; compatibility was verified before allowance, without altering scientific package pins.

**Implementation:** [pyproject.toml](../../pyproject.toml).

**Actual result:** Both Linux runtimes and live reference parity passed; the existing project/URL and Hobby plan were preserved. [Evidence](../../technical_evaluation/refinement/results/runtime3142_preallow.json).

**Likely question:** Does READY establish classification validity?

**Defensible answer:** No. Schema, actual endpoint calls, trusted model identity and prediction parity require independent checks.

### 5.9 Dependency locking and numerical determinism

Exact versions and hashes reduce environment drift. Seed control alone does not fix iterative numerical differences from BLAS/thread settings.

**Mathematics or contract:** `Public reconstruction restores threadpool_limits(2); runtime closure is uv.lock plus web/requirements.lock.`

**Why it matters:** Three initial LR differences were retained and investigated, not deleted as unfavorable results.

**Implementation:** [technical_evaluation/reconstruct.py :: main](../../technical_evaluation/reconstruct.py#L13).

**Actual result:** All21 fits executed; restoring original two-thread control made LR E5/F6/S4 validation F1 exactly match references. [Evidence](../../technical_evaluation/refinement/results/LR_thread_sensitivity.json).

**Likely question:** Does matching F1 prove identical reconstructed bytes?

**Defensible answer:** No. These are separately reconstructed objects, not recovered original binaries; metric equality is not serialization identity.

### 5.10 Latency components and targets

Validation/frame creation, preprocessing, forest computation, server wall time and network response time measure different parts of the system. None directly measures billedCPU.

**Mathematics or contract:** `Sequential production p95: forest6.743ms; preprocess5.868ms; server16.988ms; network638.937ms.`

**Why it matters:** Favorable inner-component latency does not meet a complete-path target or establish behavior under all concurrency.

**Implementation:** [technical_evaluation/refinement/cloud_benchmark.py :: benchmark](../../technical_evaluation/refinement/cloud_benchmark.py#L6).

**Actual result:** 42/42 requests passed; concurrent forest p95~10.703ms. Original artifact11.665MiB and archived p95=36.808295ms remain unchanged. [Evidence](../../technical_evaluation/refinement/results/cloud_production_profile.json).

**Likely question:** Why can the forest be below10ms while full inference fails the target?

**Defensible answer:** Preprocessing/validation/server overhead adds time. Even forest concurrency p95 exceeds10ms; blanket compliance is not claimed.

### 5.11 Model initialization and cold starts

A new process can load its model cache. Platform/module startup can precede application timing, and a readiness call may warm the process.

**Mathematics or contract:** `X-PV-Initialized marks a model-cache load, not the entire platform cold start.`

**Why it matters:** A first observed request must not automatically be labeled a confirmed cold start.

**Implementation:** [web/app.py :: model_with_timing](../../web/app.py#L34).

**Actual result:** One observed production model initialization was~2079.525ms during concurrency; full platform cold-start time unmeasured. [Evidence](../../technical_evaluation/refinement/results/cloud_production_profile.json).

**Likely question:** Can that number be called total Vercel cold-start latency?

**Defensible answer:** No. It excludes platform/module work outside the measured interval and differs from network latency.

### 5.12 Security, deadlines and capacity

Strict2KB bodies,5s body/15s response deadlines, safe errors, CSP and trusted loading reduce concrete risks. A guard permits two active inferences per process.

**Mathematics or contract:** `A response timeout does not kill the Python worker; its capacity slot is released when the worker finishes.`

**Why it matters:** Local capacity is not distributed IP/user rate limiting across serverless instances. No paid/metered protection was activated.

**Implementation:** [web/app.py :: guarded_inference](../../web/app.py#L59).

**Actual result:** Timeout/capacity tests pass; known-advisory and heuristic secret scans found no matches within their stated scopes. [Evidence](../../technical_evaluation/refinement/Rate_Limit_Review.json).

**Likely question:** Is the service fully abuse-proof or operationally certified?

**Defensible answer:** No. Distributed rate limits, monitoring and safety qualification remain outstanding; heuristic/advisory scans are not absolute security guarantees.

### 5.13 Cloud cost assumptions

Scenarios must state active CPU time, memory allocation, in-flight duration and requests. Actual invoices/remaining shared quota are separate evidence.

**Mathematics or contract:** `CPU_hours=N*t_CPU/3600; GB_hours=N*GB*t_inflight/3600.`

**Why it matters:** Network time includes transport/waiting and cannot be multiplied by CPU pricing to infer a bill.

**Implementation:** [technical_evaluation/cloud.py :: main](../../technical_evaluation/cloud.py#L6).

**Actual result:** Assumed40ms CPU/request gives1.111 CPU-hours at100k requests and11.111 at1million; no purchase or actual-charge claim. [Evidence](../../technical_evaluation/evidence/rubric5/cost.json).

**Likely question:** What additional evidence is needed before real-world operation?

**Defensible answer:** Independent PV sites/timestamps, prospective calibration/evaluation, stakeholder costs, sensor contracts, rate limits, monitoring, resource qualification and safety review.

## Scaling, encoding and transformation recap

All predictor columns are continuous, so no categorical predictor one-hot encoding is required. Target integers remain nominal labels and are never scaled. LR StandardScaler learns TRAIN mean/SD and applies `z=(x-mean_TRAIN)/SD_TRAIN`; RF uses native measurements. RobustScaler/MinMaxScaler and PCA are descriptive alternatives in the preprocessing study, not newly selected deployment policies. The LightGBM derivatives require their physical parent channels. No automatic raw logarithm is introduced for zeros/negative Celsius values.

## Archived guards versus deployable inference

The historical `AblationModel.predict_proba` method restricts source positions to its stage-specific development population. Production [predict](../../src/inference/cli.py) intentionally calls the already fitted `model.pipeline` after validating four raw measurements; it does not ask for acquisition index, true target or block identifiers. This is not a refit or a change to learned transformations. [FrozenPredictor](../../src/phase2_stage3/common.py) separately authorizes declared retrospective evaluation ranges. The API/CLI and full-partition parity checks validate the preserved learned behavior.

## Independent study method

Derive each formula or contract, open the named implementation, interpret the result, and identify an unresolved assumption without reading the answer. Separate code guarantees from statistical claims. Practice quick verification and fixed examples; reserve expensive fitting for a separate disposable reproduction exercise, never the live evaluation.
