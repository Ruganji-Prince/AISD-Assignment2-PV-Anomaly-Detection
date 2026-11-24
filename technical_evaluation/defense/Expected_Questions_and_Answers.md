# Expected questions and evidence-based answers

## Why was Random Forest selected?

The archived block 13 rule balanced sensing reduction and class-specific validation performance across 21 alternatives. RF E4 validation macro-F1 is.956297 and historical TEST F1.950481. Separate10ms/10MiB constraints were not met. [Evidence](../../reports/Model_Selection_and_Deployment.md).

## Why are four physical sensors sufficient?

Four electrical channels satisfy the selected rule among evaluated configurations. This is conditional on those alternatives and data, not a global minimum or external-site guarantee. [Evidence](../evidence/rubric3/original_model_parameters.json).

## Why are there eight mathematical inputs?

Four raw retained measurements plus four missingness indicators produce eight inputs. Indicators do not add physical sensors. [Evidence](../../src/phase2_stage2/models.py).

## Why was a random split avoided?

Ordered, locally dependent source readings and induced experimental blocks could leak regime information through row shuffling. The ordered split and separator gaps were frozen. [Evidence](../../phase1_strategy/Phase1_Split_Manifest.json).

## How was leakage prevented?

Learned transformations and weights fit TRAIN or fold-specific training rows. Source/block/exact-vector overlap is zero; full near-neighbor similarity remains disclosed rather than erased. Target/index/block metadata never enters inference. [Evidence](../refinement/results/full_near_duplicates.json).

## Why are formal missingness tests not applicable?

Every exported missingness indicator is constant zero. Little MCAR lacks incomplete patterns; a missingness-versus-target CramerV denominator has a zero dimension. No mechanism/p-value can be identified. [Evidence](../evidence/rubric1/missingness.json).

## Why retain extreme observations?

Extreme electrical values may represent genuine fault signatures. Statistical unusualness is not evidence of an erroneous fault observation. Physical quality rules remain separate from statistical fences. [Evidence](../evidence/rubric1/training_outliers.csv).

## Why reject clipping?

TRAIN-fitted IQR clipping did not improve block 13 F1, while quantile clipping reduced it from.956297 to.956041. No-clipping remains the original deployed policy. [Evidence](../evidence/rubric1/clipping_comparison.json).

## Why was PCA not deployed?

PCA needs its physical parent channels and does not reduce their acquisition requirements. Components complicate physical interpretation; explicit sensor ablation addresses the resource objective. [Evidence](../evidence/rubric1/feature_screening.json).

## Why macro-F1?

Rare hardware classes would be dominated by normal observations under accuracy alone. Macro-F1 weights class F1 equally; per-class supports, weighted F1, balanced accuracy and AP complement it. [Evidence](../evidence/rubric3/model_comparison.json).

## Why is grouped validation worse?

Class1 occurs only in TRAIN block 12, with class 3 heavily concentrated there. Withholding that block creates an unseen-class problem. Other folds have different class support; supported-class and fixed-five scores must remain distinct. [Evidence](../evidence/rubric2/grouped_validation.json).

## How were probabilities calibrated?

The frozen original model supplies block 14 probabilities; purged fourfold source-tile cross-fitting evaluates classwise sigmoid/isotonic mappings with positive/negative support guards and row normalization. Selection uses OOF logloss, not TEST. Nothing calibrated is deployed. [Evidence](../refinement/results/calibration/calibration_selection_freeze.json).

## How was the hardware threshold selected?

The original block 14 distinct-score enumeration maximized hardware recall subject to combined true{0,4} FPR<=.01, with fixed tie-breaks. The score is p1+p2+p3. API argmax classification is a separate policy. [Evidence](../../src/phase2_stage3/common.py).

## Why are intervals conditional?

Bootstrap units are 12 available TRAIN signal blocks, and some draws omit a class. Conditioning on all-five support changes the resampling population; neither conditional nor unconditional summaries establishes external/deployed-TEST coverage. [Evidence](../refinement/results/bootstrap_sensitivity.json).

## Why is shade not hardware failure?

Class4 labels natural building shade, an environmental condition. Hardware score and hardware-class flags include only classes1/2/3. [Evidence](../../src/inference/cli.py).

## Why can synthetic intent disagree with predictions?

Hand-designed values need not match learned joint regimes. Original presets all predictshade. A once-frozen TRAIN-derived joint perturbation agrees249/250 with source conditioning, without prediction-based search; that is not physical simulator validation or independent accuracy because parent rows were used for model fitting. [Evidence](../refinement/results/empirical_scenarios.json).

## What happens during persistent dropout?

The offline policy abstains after two consecutive unavailable source positions, and two simultaneous missing channels are ineligible. The public API rejects missing measurements rather than pretending persistent imputation is reliable. [Evidence](../evidence/rubric4/contiguous_dropout.json).

## What happens under shift?

Measured feature/prevalence/cohort differences can change error rates. TRAIN-bin PSI/KS/Wasserstein and subgroup tables expose this risk; no validated drift alarm or automatic retraining is deployed. [Evidence](../evidence/rubric4/shift.json).

## Why were resource targets not achieved?

The unchanged original model is 11.665MiB and archived local p95 is 36.808295ms. Sequential execution removes scheduling overhead, but preprocessing/server/network time remains; forest-only p95 below10ms does not meet an end-to-end target. [Evidence](../refinement/results/cloud_preview_profile.json).

## How does cloud inference work?

The four-step frontend sends four measurements to a FastAPI Vercel function. A per-process cached hash-verified pipeline predicts the nominal class; no target, fitted calibration or true-label lookup enters inference. Platform and application wall-clock timings are distinct. [Evidence](../../web/app.py).

## Why did LR reconstruction initially differ?

The public entry point omitted the archived two-thread BLAS control. Restoring threadpool_limits(2) made all three differing validation scores match. Both passes are retained; metric equality is not byte identity. [Evidence](../refinement/results/LR_thread_sensitivity.json).

## What is needed for real-world deployment?

Independent-site/time-identified data, prospective validation, stakeholder costs, sensor-quality contracts, operational rate limits/monitoring, sustained-outage policies, resource qualification and safety review are still required. [Evidence](../refinement/Final_Report.md).
