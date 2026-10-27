# Phase 2: photovoltaic classification under sparse sensing

The completed experiment compares Logistic Regression, Random Forest and LightGBM across seven predeclared sensor configurations. Settings were selected with full sensing on validation block 13 and held fixed during ablation. Validation block 14 selected hardware-alert thresholds before the frozen test evaluation.

The [final report](reports/Phase2_Final_Report.pdf) presents the engineering trade-off. RF E4 achieved test macro-F1 0.9505 from four electrical channels but exceeded the latency and artifact-size targets. LightGBM E4 met both resource limits but failed the short-circuit classification-recall target. LR F6 remains a full-sensing lightweight reference. **No evaluated configuration satisfied all predeclared engineering criteria.**

[Prior test exposure](stage3/Methodology_Disclosure.md) remains an explicit limitation. Natural building shade is an environmental condition, not hardware failure. Strong aggregate hardware alerting does not imply reliable fault-type diagnosis.

## Review from the repository root

Use Python 3.14.7 and the [frozen Phase 2 dependencies](requirements.txt). Installation in a separate environment preserves existing environments:

```powershell
python -m venv .cache/phase2-review-env
.cache\phase2-review-env\Scripts\Activate.ps1
python -m pip install -r phase2_implementation/requirements.txt
python -B phase2_implementation/verify_submission.py
```

On POSIX systems, activate with `source .cache/phase2-review-env/bin/activate`. The verifier reads evidence and writes its new review output only under ignored `.cache/`. It does not fit models, select thresholds, access model binaries, or regenerate experimental predictions.

The [executed evidence-review notebook](notebooks/Phase2_Evidence_Review.ipynb) displays the approved results without training. Evidence-only rendering commands are:

```powershell
python -B phase2_implementation/build_report.py
python -B phase2_implementation/build_review_notebook.py
```

The [reproduction guide](Reproduction_Guide.md) distinguishes evidence inspection from independent experiment reproduction, explains frozen-run overwrite guards, and indexes all scientific settings. Report regeneration changes only newly prepared report/presentation outputs, never approved experiment evidence.

## Evidence index

- [Final candidate comparison](stage3/evidence/final_candidate_comparison.csv), [all class metrics](stage3/evidence/final_test_class_metrics.csv), [test details/confusions](stage3/evidence/final_test_details.json).
- [Hardware alerts](stage3/evidence/final_hardware_alert_metrics.csv), [engineering criteria](stage3/evidence/final_engineering_criteria.csv), [threshold freeze](stage3/evidence/stage3_threshold_selection.json), [chronology receipt](stage3/evidence/threshold_freeze_receipt.json).
- [Validation ablation](stage2/evidence/sensor_ablation_validation.csv), [class metrics](stage2/evidence/sensor_ablation_class_metrics.csv), [resource results](stage2/evidence/resource_metrics.csv).
- [Portable resource projection](stage4/evidence/resource_protocol_public.json) and [frozen model specification projection](stage4/evidence/final_model_specifications.json). Original machine-path-bearing records remain unedited locally; projections document their source hashes and selected fields.
- [Training weights](stage1/evidence/class_weights.json), [row-count investigation](stage1/evidence/row_count_discrepancy.json), [experiment configuration](stage1/evidence/experiment_configuration.json), [feature dependencies](stage1/Feature_Dependencies.json).
- [Explainability metadata](stage3/evidence/explainability_metadata.json), [raw-channel permutation](stage3/evidence/physical_channel_permutation.csv), [Tree SHAP summary](stage3/evidence/shap_mean_absolute.csv), [dropout](stage3/evidence/dropout_validation.json).
- [Editable report source](reports/Phase2_Final_Report.md). Selected figure captions identify TRAIN-fitted quantities, VALIDATION analysis and TEST performance explicitly.

The original Phase 1 README/report are retained as historical planning documentation. Statements describing planned implementation belong to that approved Phase 1 scope; completed Phase 2 evidence is indexed here. Historical stage records likewise describe the scope authorized at their creation.
