# Technical evaluation evidence

Audit: 24 November 2026. Initial engineering self-assessment76/100; final88/100. These are conservative estimates, not an official grade.

Start with the [technical report](Technical_Evaluation_Report.md), [43-requirement matrix](Rubric_Compliance_Matrix.md), [reproduction guide](Reproduction_Guide.md) and [limitations](Limitations_and_Risks.md). The [initial audit](Initial_Rubric_Compliance_Matrix.md) is retained. All original academic deliverables remain in their original locations.

```powershell
uv venv --python 3.14.10 .venv
uv pip install --python .venv -r technical_evaluation/requirements.txt
.\.venv\Scripts\python.exe -B -m technical_evaluation.audit
```

Default verification runs23 tests, validates220 protected files, original RF hash, frozen protocol, disjoint splits, calibration fit/evaluation ledgers, five CLI cases, saved-confusion-derived F1 and relative documentation links. It does not fit models or make cloud requests. See [audit receipt](evidence/rubric5/audit_verification.json).

Expensive opt-ins: `--run` recomputes data/calibration/robustness diagnostics; `--train` fits separate clipping and grouped-validation models; `--cloud` makes bounded live API requests; `--private-cache PATH` verifies original private LR/RF/LightGBM explanation artifacts. Reconstructed candidates can be trained with `python -B -m technical_evaluation.reconstruct --candidate RF__E4` or `--candidate all`. These are new fits, not original model bytes.

Historical TEST was previously inspected. New TEST metrics are retrospective; no new TEST-guided model, calibration, threshold or synthetic-preset selection occurred. Calibration remains experimental and is not deployed. Signal blocks are not verified days/sessions/hours. Docker execution and confirmed cloud cold starts remain NOT VERIFIED.

Evidence folders: [rubric1](evidence/rubric1), [rubric2](evidence/rubric2), [rubric3](evidence/rubric3), [rubric4](evidence/rubric4), [rubric5](evidence/rubric5), [figures](figures). Large probability arrays, newly fitted models, calibration objects, environments and screenshots are ignored local artifacts. Every public numeric table is derived from executed evidence. The frozen [protocol](Protocol.json) and [supplemental contiguous-dropout protocol](Supplemental_Dropout_Protocol.json) preserve the design.
