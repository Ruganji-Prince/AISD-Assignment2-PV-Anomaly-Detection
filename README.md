# Resource-Efficient and Explainable AI for Photovoltaic Anomaly Detection Under Sparse Sensing Constraints

Ruganji Prince · Carnegie Mellon University Africa  
**Course:** 04-652 Artificial Intelligence System Design  
**Assignment 2:** Phase 1 strategy and Phase 2 implementation  
**Task Type: Multiclass Classification**

## Research question

What sensing and computational configuration can provide practically useful PV anomaly detection under resource-constrained deployment assumptions? The experiment compares prediction quality, hardware-fault sensitivity, physical channel count, false alarms, latency, artifact size and robustness among seven predeclared sensor sets.

## Current project status

Phase 1 design and the Phase 2 modelling experiments are complete. Model settings, class weights, features, sensor configurations, thresholds, splits and final test results are frozen. The executable preprocessing notebook, eight preprocessing diagnostics and strategy-versus-reality appendix complete the assignment-specific deliverables without retraining classifiers.

**No evaluated configuration satisfied all predeclared engineering criteria.**

## Dataset and target

Source: [original-author PV Fault Dataset](https://github.com/clayton-h-costa/pv_fault_dataset), pinned commit `e9ed8ad8072dcb3ffc643b0f3604219798708551`; [Lazzaretti et al., Sensors 20(17), 4688 (2020)](https://doi.org/10.3390/s20174688).

The immutable export contains **N = 1,373,798 observations** and **P = 7 variables**: six continuous predictors and nominal target `f_nv`. [Raw CSV](data/raw/pv_fault_dataset.csv), [source/conversion provenance](data/raw/README.md), [variable inventory](phase1_strategy/Variable_Inventory.csv) and [class counts](phase1_strategy/Class_Distribution.csv) remain unchanged.

| Variable | Physical meaning / role | Unit |
| --- | --- | --- |
| vdc1, vdc2 | DC RMS voltage for PV strings 1 and 2 | V |
| idc1, idc2 | DC RMS current for PV strings 1 and 2 | A |
| irr | Plane-of-array irradiance | W/m² |
| pvt | Reported module temperature, aggregated from source probes | °C |
| f_nv | Five nominal operating-state labels | Unitless |

Labels are **0 normal; 1 short circuit; 2 resistive degradation; 3 open circuit; 4 natural building shade**. Integer codes are neither ordinal nor continuous. Classes 1–3 are hardware faults; class 4 is an environmental condition. Channel count is distinct from physical device count.

![First ten observations with the seven original columns](figures/raw_dataset_preview.png)

Preview of the raw photovoltaic monitoring dataset. First ten observations in exported source order. These ten observations have `f_nv = 0`.

## Phase 1 — strategy and audit

The [approved Phase 1 report](phase1_strategy/Phase1_Strategy_Report.pdf), [evidence index](phase1_strategy/Supporting_Evidence_Index.md) and [decision rationale](phase1_strategy/Decision_Rationale_Guide.md) preserve the original pre-implementation design. The audit found zero conventional missing values, 62 suspicious paired irradiance/temperature zeros, one slightly negative irradiance observation, strong predictor dependence and severe class imbalance. Unusual fault observations were retained; suspicious zeros were not falsely declared missing.

The fixed split uses exported source order and signal-defined blocks with separator buffers: TRAIN [0,1006129), VALIDATION [1056990,1173967), TEST [1227337,1373798). Validation block 13 selected settings; block 14 selected alert thresholds. [Exact split manifest](phase1_strategy/Phase1_Split_Manifest.json) and training-only median/scaling/weight definitions document leakage prevention.

## Phase 2 — implementation and diagnostics

[Phase 2 guide](phase2_implementation/README.md) and [reproduction guide](phase2_implementation/Reproduction_Guide.md) provide entry points and compact evidence.

- [Executable preprocessing notebook](phase2_implementation/notebooks/Phase2_Preprocessing_Implementation.ipynb): actual approved Pipeline/ColumnTransformer preprocessing, training-only fitting and model-ready matrices.
- [Eight preprocessing diagnostics](phase2_implementation/preprocessing_diagnostics/README.md): missingness, class balance, outlier comparison, predictor correlation, collinear pairs, nominal-target association, scaling alternatives and exploratory PCA.
- [Executed evidence-review notebook](phase2_implementation/notebooks/Phase2_Evidence_Review.ipynb): frozen model results, without training or prediction.
- [Strategy-versus-reality table](phase2_implementation/compliance/Strategy_vs_Reality.md): planned decisions, implementation, deviations and evidence; also included in the final report appendix.

LR, RF and LightGBM settings were selected using full-sensing validation evidence, then held fixed across F6, E5, E4, C3, C2, S4 and S2. No sparse configuration received independent retuning. Additional MI/PCA/scaling diagnostics do not reopen model or sensor selection.

## Final candidates and engineering conclusion

| Candidate / role | Test macro-F1 | p95 (ms) | Artifact (MiB) | Unmet criteria |
| --- | ---: | ---: | ---: | --- |
| LR F6 — full-sensing lightweight reference | 0.8984 | 14.72 | 0.0037 | Open-circuit classification recall; latency |
| RF E4 — sparse predictive-performance candidate | 0.9505 | 36.81 | 11.6654 | Latency; artifact size |
| LightGBM E4 — sparse resource-efficient candidate | 0.9021 | 6.12 | 1.5692 | Short-circuit classification recall |

RF E4 is the minimum-channel qualifying candidate among the seven predeclared configurations tested under the validation predictive/channel conditions; this is not a global minimum-sensing claim. Its final hardware-class recalls are 0.9996/0.9907/1.0000. LightGBM E4 hardware-alert recall is 0.9969, but short-circuit classification recall is 0.4994. Aggregate alert detection is distinct from five-class fault-type diagnosis.

**No evaluated configuration satisfied all predeclared engineering criteria.** [Frozen candidate comparison](phase2_implementation/stage3/evidence/final_candidate_comparison.csv) and [PASS/FAIL evidence](phase2_implementation/stage3/evidence/final_engineering_criteria.csv) retain all results, including failed targets.

## Reports

- [Phase 1: approved strategy report](phase1_strategy/Phase1_Strategy_Report.pdf).
- [Phase 2: final scientific report and strategy-versus-reality appendix](phase2_implementation/reports/Phase2_Final_Report.pdf).
- [Phase 2 editable report text](phase2_implementation/reports/Phase2_Final_Report.md).

## Reproducibility and verification

Use Python 3.14.7 and the frozen Phase 2 dependencies, from the repository root:

```powershell
python -m venv .cache/phase2-review-env
.cache\phase2-review-env\Scripts\Activate.ps1
python -m pip install -r phase2_implementation/requirements.txt
python -B phase2_implementation/execute_preprocessing.py
python -B phase2_implementation/verify_submission.py
```

On POSIX systems, activate with `source .cache/phase2-review-env/bin/activate`. Preprocessing execution fits only preprocessing/diagnostic estimators on TRAIN; it never retrains classifiers or regenerates predictions. For evidence-only review, run the verifier without rerunning the notebook. Full modelling reproduction has separate fresh-workspace prerequisites, listed honestly in the reproduction guide; it is not claimed to be one-command training reproduction.

The preserved `phase1_strategy/verify_phase1.py` verifies the historical Phase 1-only snapshot. It was designed before Phase 2 population and intentionally rejects implementation artifacts. It is **not the verifier for this complete repository**. The current full-project entry point is `phase2_implementation/verify_submission.py`.

## Repository structure

```text
data/raw/                         Immutable CSV and provenance
phase1_strategy/                  Approved report and audit/design evidence
src/phase2_stage1–3/               Frozen experiment modules
src/phase2_compliance/             Reused preprocessing, diagnostic and compliance helpers
phase2_implementation/notebooks/   Preprocessing and frozen-evidence notebooks
phase2_implementation/reports/     Final report/source
phase2_implementation/stage1–5/    Compact scientific and publication evidence
phase2_implementation/preprocessing_diagnostics/  Eight assignment figures
phase2_implementation/compliance/  Decision table, diagnostic evidence and checks
```

Models, processed arrays, predictions, SHAP arrays, environments and temporary artifacts remain local/ignored. Their absence does not prevent public evidence inspection or execution of preprocessing.

## Limitations and temporal interpretation

The source describes nominal 1 Hz acquisition, per-second electrical RMS calculations, one-second irradiance/temperature averages and a 16-day experiment. Released MAT/CSV data contain no explicit timestamp. Source order is preserved, but absolute timestamps and continuous one-second spacing across the entire export are not verifiable. The 16 signal-defined blocks are not verified days/sessions/hours. The separator is `irr < 100 W/m²` for at least 3,600 consecutive source positions, without assigning those positions a verified hour.

The test partition was evaluated in an earlier legacy implementation and is not pristine or previously unseen. Revised modelling and threshold decisions used training/validation evidence; prior human exposure remains a limitation. [Methodology disclosure](phase2_implementation/stage3/Methodology_Disclosure.md) documents this explicitly.

The irradiance-qualified subset has 515,958 positions and exactly reproduces paper-reported class counts; explicit use of that filtering operation by the paper is unverified. The primary experiment retains the full approved population. One controlled Brazilian installation does not establish field generalization. Explanations are non-causal, PCA does not establish physical sensor reduction, and engineering criteria are project aspirations rather than certification thresholds.
