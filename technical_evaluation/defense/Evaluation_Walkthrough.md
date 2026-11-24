# Evaluation walkthrough:10 and20 minutes

The five fixed historical demo references originate in the previously inspected TEST partition. They are parity/reproducibility examples, not independent accuracy evidence; [exact source positions](Submission_Readiness.md#exact-provenance-of-the-five-fixed-references) are documented. No new prediction-based example search is performed.

This is a planned repository/source/live-application demonstration, without slides. Install the environment beforehand. Do not run model training, a fresh notebook execution or repeated cloud benchmarks during the evaluation. Preflight readiness once; subsequent calls may be warm and must be labeled accordingly.

Both versions follow the same14 stages. The20-minute version doubles each time budget and adds code derivations/support checks. The10-minute version opens the listed location and states one measured result plus one limitation. Time budgets total600 and1200 seconds respectively.

| Stage |10-minute budget(seconds)|20-minute budget(seconds)|
| --- | ---: | ---: |
| 1. Problem definition and engineering motivation | 30 | 60 |
| 2. Dataset structure and provenance | 30 | 60 |
| 3. Data hygiene and preprocessing | 40 | 80 |
| 4. Feature screening and collinearity | 30 | 60 |
| 5. Split strategy and leakage prevention | 60 | 120 |
| 6. Training and baseline comparison | 45 | 90 |
| 7. Model selection and sensor reduction | 45 | 90 |
| 8. Metrics and class imbalance | 45 | 90 |
| 9. Calibration and threshold selection | 45 | 90 |
| 10. Error analysis and robustness | 50 | 100 |
| 11. Explainability | 30 | 60 |
| 12. Cloud architecture and deployment | 60 | 120 |
| 13. Reproducibility and security | 40 | 80 |
| 14. Limitations and future improvements | 50 | 100 |

## 1. Problem definition and engineering motivation

**Verbal explanation:** Define one nominal operating-state prediction, environmental shade versus hardware failure, sparse electrical acquisition and the separate resource constraints.

**Open:** [README.md](../../README.md).

**Code/section:** Project overview and archived results.

**Measured result:** Original10ms/10MiB targets; RF E4 selected under the sensing/performance rule.

**Command:** No execution needed: inspect the named source/evidence.

**Likely follow-up:** What cost is being minimized, and was it measured monetarily?

**20-minute extension:** Derive the relevant formula or contract, trace the actual function call, inspect class support or provenance, and distinguish a verified property from an unresolved assumption.

## 2. Dataset structure and provenance

**Verbal explanation:** Explain every variable/unit and source release, class codes and absent timestamps.

**Open:** [phase1_strategy/Variable_Inventory.csv](../../phase1_strategy/Variable_Inventory.csv).

**Code/section:** Entire inventory; source commit in data/raw/README.md.

**Measured result:** N=1373798,P=7; six continuous measurements and nominal f_nv.

**Command:** No execution needed: inspect the named source/evidence.

**Likely follow-up:** Why do nominal1Hz and16 study days not reconstruct timestamps?

**20-minute extension:** Derive the relevant formula or contract, trace the actual function call, inspect class support or provenance, and distinguish a verified property from an unresolved assumption.

## 3. Data hygiene and preprocessing

**Verbal explanation:** Explain zero conventional missingness, the62 paired zeros, retained extremes and training-only contingency median policy.

**Open:** [src/phase2_stage2/models.py](../../src/phase2_stage2/models.py).

**Code/section:** RetainedQuality.transform and build_preprocessor.

**Measured result:** NaNs/infinities0; pairedzeros62; slight negative irradiance retained in raw and quality-clamped in transformed data.

**Command:** No execution needed: inspect the named source/evidence.

**Likely follow-up:** Why are Little MCAR/CramerV unavailable, and why not delete Z-score extremes?

**20-minute extension:** Derive the relevant formula or contract, trace the actual function call, inspect class support or provenance, and distinguish a verified property from an unresolved assumption.

## 4. Feature screening and collinearity

**Verbal explanation:** Explain Pearson/Spearman, VIF, nominal-target MI, PCA and physical parent dependencies.

**Open:** [technical_evaluation/data_audit.py](../../technical_evaluation/data_audit.py).

**Code/section:** main: correlation/VIF/MI/PCA computation.

**Measured result:** Five high-correlation pairs; VIF vdc1~52.168; two PCs explain about95.17% in original preprocessing.

**Command:** No execution needed: inspect the named source/evidence.

**Likely follow-up:** Why retain high-VIF sensors, and why is PCA not sensor reduction?

**20-minute extension:** Derive the relevant formula or contract, trace the actual function call, inspect class support or provenance, and distinguish a verified property from an unresolved assumption.

## 5. Split strategy and leakage prevention

**Verbal explanation:** Show half-open bounds, purge gaps,16 signal blocks and12/2/2 allocation; distinguish code isolation from statistical independence.

**Open:** [src/preprocessing/study.py](../../src/preprocessing/study.py).

**Code/section:** split_data; then technical_evaluation/refinement/experiments.py::near.

**Measured result:** TRAIN1006129,VAL116977,TEST146461; gaps104231; exact overlaps0, close-state counts remain.

**Command:** `python -B -m technical_evaluation.refinement.verify --skip-tests` checks stored integrity/evidence; it does not rerun neighbor searches.

**Likely follow-up:** How can historical TEST exposure coexist with a no-preprocessing-leak claim?

**20-minute extension:** Derive the relevant formula or contract, trace the actual function call, inspect class support or provenance, and distinguish a verified property from an unresolved assumption.

## 6. Training and baseline comparison

**Verbal explanation:** Contrast LR linear softmax, RF bagging and LightGBM boosting, with class weights and bounded development search.

**Open:** [src/phase2_stage1/run.py](../../src/phase2_stage1/run.py).

**Code/section:** trial_specs; source model classes in src/phase2_stage1/models.py.

**Measured result:** Original16-trial budget; Dummy block13 F1 .144269;21 ablation configurations subsequently evaluated.

**Command:** No execution needed: inspect the named source/evidence.

**Likely follow-up:** What happens if a training fold contains no short-circuit observations?

**20-minute extension:** Derive the relevant formula or contract, trace the actual function call, inspect class support or provenance, and distinguish a verified property from an unresolved assumption.

## 7. Model selection and sensor reduction

**Verbal explanation:** Walk through pass_flags/select and explain the separate null full-resource candidate. Show original model versus new reconstructions.

**Open:** [src/phase2_stage2/selection.py](../../src/phase2_stage2/selection.py).

**Code/section:** pass_flags and select.

**Measured result:** RF E4 four raw+four indicators; validation F1 .956297; original artifact11.665MiB.

**Command:** No execution needed: inspect the named source/evidence.

**Likely follow-up:** Was the winning configuration chosen from TEST, and is four globally minimum?

**20-minute extension:** Derive the relevant formula or contract, trace the actual function call, inspect class support or provenance, and distinguish a verified property from an unresolved assumption.

## 8. Metrics and class imbalance

**Verbal explanation:** Derive precision/recall/F1, macro/weighted/BA and AP. Read one confusion matrix error without hiding support.

**Open:** [technical_evaluation/metrics.py](../../technical_evaluation/metrics.py).

**Code/section:** evaluate.

**Measured result:** Historical RF TEST F1 .950481;6604 normal-to-shade; shade precision .691081.

**Command:** No execution needed: inspect the named source/evidence.

**Likely follow-up:** Does high hardware AP prove good short-circuit subtype diagnosis?

**20-minute extension:** Derive the relevant formula or contract, trace the actual function call, inspect class support or provenance, and distinguish a verified property from an unresolved assumption.

## 9. Calibration and threshold selection

**Verbal explanation:** Separate original argmax, archived binary alert threshold and non-deployed calibration maps. Explain purged tile cross-fitting and conditional bootstrap.

**Open:** [src/phase2_stage3/common.py](../../src/phase2_stage3/common.py).

**Code/section:** select_threshold; then technical_evaluation/experiments.py::ProbabilityMap.

**Measured result:** tau=.5913558658757772; sigmoid TEST Brier .051306 versus original .079293; not production confidence.

**Command:** No execution needed: inspect the named source/evidence.

**Likely follow-up:** Why not deploy calibration, and are grouped-OOF intervals for deployedTEST?

**20-minute extension:** Derive the relevant formula or contract, trace the actual function call, inspect class support or provenance, and distinguish a verified property from an unresolved assumption.

## 10. Error analysis and robustness

**Verbal explanation:** Explain regime slicing, PSI/KS/Wasserstein and simulated noise/bias/dropout/saturation/OOD limits.

**Open:** [technical_evaluation/robustness.py](../../technical_evaluation/robustness.py).

**Code/section:** main and contiguous_dropout.

**Measured result:** 5%IQR noise F1~.797;10%~.65; persistent dropout leaves2/32800 eligible.

**Command:** No execution needed: inspect the named source/evidence.

**Likely follow-up:** Do simulated stresses or249/250 TRAIN-derived agreements demonstrate field reliability?

**20-minute extension:** Derive the relevant formula or contract, trace the actual function call, inspect class support or provenance, and distinguish a verified property from an unresolved assumption.

## 11. Explainability

**Verbal explanation:** Distinguish descriptive MI, full-channel permutation, LightGBM native SHAP and UI class text.

**Open:** [src/evaluation/verify_explanations.py](../../src/evaluation/verify_explanations.py).

**Code/section:** main; RF permutation in technical_evaluation/robustness.py.

**Measured result:** Archived SHAP additivity/magnitudes reproduced; RF balanced1000-row permutation sample.

**Command:** No execution needed: inspect the named source/evidence.

**Likely follow-up:** Are the explanations causal, RF-specific SHAP, or probability contributions?

**20-minute extension:** Derive the relevant formula or contract, trace the actual function call, inspect class support or provenance, and distinguish a verified property from an unresolved assumption.

## 12. Cloud architecture and deployment

**Verbal explanation:** Open the actual four-step app; run predetermined CLI/API parity; show timing headers and model SHA.

**Open:** [web/app.py](../../web/app.py).

**Code/section:** predict_measurements, inference, guarded_inference and security_headers.

**Measured result:** Five historical cases match; production sequential p95 forest6.74ms/server16.99ms/network638.94ms.

**Command:** `python -B -m technical_evaluation.defense.run_demo --url https://pv-anomaly-detection-prince-r-k.vercel.app` uses five fixed references plus invalid-input checks.

**Likely follow-up:** Why does an inner component below10ms not establish full target compliance?

**20-minute extension:** Derive the relevant formula or contract, trace the actual function call, inspect class support or provenance, and distinguish a verified property from an unresolved assumption.

## 13. Reproducibility and security

**Verbal explanation:** Show exact pins/hash guards, quick verification, actual Linux workflow and offline fallback.

**Open:** [src/inference/cli.py](../../src/inference/cli.py).

**Code/section:** load_model and validate; Dockerfile and .github/workflows/container-verification.yml.

**Measured result:** 30 tests; both Linux Python patches;200 TRAIN probabilities within1e-12; no arbitrary pickle upload.

**Command:** `python -B -m technical_evaluation.refinement.verify` runs30 tests and integrity/link checks; local fallback uses `python -m uvicorn web.app:app --host 127.0.0.1 --port 8000`.

**Likely follow-up:** Is a local capacity guard a distributed rate limiter?

**20-minute extension:** Derive the relevant formula or contract, trace the actual function call, inspect class support or provenance, and distinguish a verified property from an unresolved assumption.

## 14. Limitations and future improvements

**Verbal explanation:** State what software verifies and what requires new sites/timestamps/fault repetitions, prospective validation and operational review.

**Open:** [technical_evaluation/refinement/Final_Report.md](../../technical_evaluation/refinement/Final_Report.md).

**Code/section:** Limitations, mock assessment and actual production benchmark.

**Measured result:** 91/100 retained; originalresource targets unmet; independent generalization and full platform cold-start unverified.

**Command:** No execution needed: inspect the named source/evidence.

**Likely follow-up:** What evidence would be necessary before real-world deployment?

**20-minute extension:** Derive the relevant formula or contract, trace the actual function call, inspect class support or provenance, and distinguish a verified property from an unresolved assumption.

## Predetermined live and offline path

1. Open the live application and show its existing four-step flow. Use historical dataset examples for the five classes; these are demonstration references, not independent evaluation.
2. Run the fixed-reference client. It checks model identity, original CLI/API parity, actual labels, timing headers and missing/negative/unexpected-target rejection. It never searches predictions for a desired class.
3. If internet fails, start the already-installed local API in a second terminal and use `--url http://127.0.0.1:8000`. If the local server is unavailable, omit `--url` for completely offline CLI verification.
4. Distinguish original illustrative presets (all currently predictshade), TRAIN-derived empirical perturbations (249/250 conditioning agreements, not independent accuracy), and historical references. Never substitute intent for the returned prediction.

The [submission checklist](Submission_Readiness.md) contains exact Windows/Linux preparation and fallback commands. The [learning guide](Student_Learning_Guide.md) and [66-question examination](Mock_Technical_Examination.md) supply derivations and answers.
