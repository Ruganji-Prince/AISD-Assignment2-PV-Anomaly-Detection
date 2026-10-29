# Phase 2: implementation, preprocessing diagnostics and frozen evidence

The scientific experiment compares LR, RF and LightGBM across seven predeclared sensor configurations. Settings were selected on validation block 13; block 14 froze hardware-alert thresholds before final evaluation. **No evaluated configuration satisfied all predeclared engineering criteria.** The [final report](reports/Phase2_Final_Report.pdf) retains the original scientific pages and adds the assignment-required decision-table appendix.

## Assignment deliverables

- [Complete executable preprocessing notebook](notebooks/Phase2_Preprocessing_Implementation.ipynb): reuses the actual shared Pipeline/ColumnTransformer steps; fits only TRAIN preprocessing; transforms frozen validation/test partitions without classifier fitting or predictions.
- [Eight required preprocessing diagnostics](preprocessing_diagnostics/README.md): all included in the preprocessing notebook and saved at 300 DPI.
- [Strategy versus reality](compliance/Strategy_vs_Reality.md): 21 categories covering the approved plan, actual implementation, status and rationale.
- [Executed evidence-review notebook](notebooks/Phase2_Evidence_Review.ipynb): preserves the separate inspection-only workflow.
- [Reproduction guide](Reproduction_Guide.md): dependencies, honest fresh-training prerequisites, commands and output locations.

## Root-based execution

Use Python 3.14.7 and the frozen dependency lock referenced by [requirements.txt](requirements.txt). In a separate environment:

```powershell
python -m venv .cache/phase2-review-env
.cache\phase2-review-env\Scripts\Activate.ps1
python -m pip install -r phase2_implementation/requirements.txt
python -B phase2_implementation/execute_preprocessing.py
python -B phase2_implementation/verify_submission.py
```

On POSIX systems, use `source .cache/phase2-review-env/bin/activate`. The preprocessing notebook can also be run top-to-bottom in a Jupyter front end with the same environment. No Jupyter front end is required for the standard Python execution command. Figure links are relative; notebook outputs do not embed large arrays or models.

MI, diagnostic scaling and PCA were completed after modelling decisions were frozen. These TRAIN-only diagnostic calculations did not change models, physical features, sensors, weights, thresholds, splits or results. The original evidence-review notebook remains unchanged. Historical Phase 1/stage verifiers describe their original scope; current full-project review uses `verify_submission.py`.

## Frozen scientific evidence

- [Final candidate comparison](stage3/evidence/final_candidate_comparison.csv), [all class metrics](stage3/evidence/final_test_class_metrics.csv), [confusions](stage3/evidence/final_test_details.json).
- [Hardware alerts](stage3/evidence/final_hardware_alert_metrics.csv), [criteria](stage3/evidence/final_engineering_criteria.csv), [thresholds](stage3/evidence/stage3_threshold_selection.json), [freeze receipt](stage3/evidence/threshold_freeze_receipt.json).
- [Validation ablation](stage2/evidence/sensor_ablation_validation.csv), [class metrics](stage2/evidence/sensor_ablation_class_metrics.csv), [resources](stage2/evidence/resource_metrics.csv).
- [Complete frozen model specifications](stage4/evidence/final_model_specifications.json), [resource protocol and samples](stage4/evidence/resource_protocol_public.json), [training weights](stage1/evidence/class_weights.json), [feature dependencies](stage1/Feature_Dependencies.json).
- [Explainability metadata](stage3/evidence/explainability_metadata.json), [physical permutation](stage3/evidence/physical_channel_permutation.csv), [Tree SHAP](stage3/evidence/shap_mean_absolute.csv), [dropout](stage3/evidence/dropout_validation.json).
- [Prior-test-exposure disclosure](stage3/Methodology_Disclosure.md). Shade is environmental, not hardware failure; strong aggregate alerting does not establish reliable fault-type diagnosis.

## Report preparation

`build_compliance_report.py` appends/rebuilds only the strategy-versus-reality appendix while retaining the first ten scientific pages. It verifies identical text and rendering of those pages against the recorded approved baseline. It does not regenerate scientific figures or predictions. The historical Stage 4 report builder is retained as provenance and should not replace the current compliance-complete report.
