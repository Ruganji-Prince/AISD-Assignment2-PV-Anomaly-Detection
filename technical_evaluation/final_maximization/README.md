# Final independent technical evaluation audit

28 November 2026. Baseline public release: `d007880c89a0312dbdf540678e9c8bf4cec3216e`. Scope: audit branch `audit/final-rubric-maximization` only. No model fitting, deployment changes, main integration or scientific-result edits.

The independently supported conservative mock score remains **91/100: 18, 18, 18, 19, 18**. This is an engineering judgment against the official bands, not an official grade or a statistical estimate. New documentation does not justify a score increase.

- [Final audit and measured findings](Final_Rubric_Audit.md)
- [87-row requirement matrix](Requirement_Evidence_Matrix.md), [structured version](Requirement_Evidence_Matrix.json)
- [Remaining gaps and A/B/C/D classification](Remaining_Gaps.md)
- [Five-minute technical examination guide](Technical_Examination_Guide.md)
- [Independent score justification](Final_Score_Justification.md)
- [Verification results and execution scope](Verification_Results.json)
- [Protected release manifest](Release_Manifest.json)

## Essential reproduction

Run from the repository root, with Git on PATH and the same verified Python patch. `uv` and Python require prior installation. No Azure/GitHub credentials are needed for these public clone and essential checks. After the audit branch is published:

```sh
git clone --branch audit/final-rubric-maximization https://github.com/Ruganji-Prince/AISD-Assignment2-PV-Anomaly-Detection.git
cd AISD-Assignment2-PV-Anomaly-Detection
uv venv --python 3.14.10 .venv
uv pip install --python .venv -r technical_evaluation/requirements.txt
uv pip check --python .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -B -m technical_evaluation.final_maximization.verify --tests
.\.venv\Scripts\python.exe -B -m technical_evaluation.defense.run_demo
.\.venv\Scripts\python.exe -B -m technical_evaluation.defense.run_demo --url https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io
```

Linux/macOS equivalents use `.venv/bin/python`. The first command checks current raw schema, exact cross-partition feature overlap, original fitted medians, model integrity, five local predictions, stored confusion-derived macro-F1, file links and 50 tests. It does not refit models, repeat every scientific experiment or rewrite tracked evidence. The offline demonstration makes no network requests. The optional URL command checks live parity and rejects invalid inputs; it does not measure independent accuracy. For full bounded health/CORS/static-asset checks, run the verifier with `--live`.

The original quick verifier remains unchanged and rejects the three later-approved frontend files. [Exact failure and Windows path diagnosis](Historical_Check_Failure.json). No criterion was weakened: the new check protects all other **588** release files, including every scientific artifact and all application code. Root README changes are limited to current commands, the serving-boundary correction and this audit link.

The deployment image already has [actual Linux verification](../../docs/azure-backend-identity/deployment/README.md). No Docker runtime is available locally; no new image/build/deployment was created for this audit. Optional complete scientific regeneration commands can fit experimental objects and overwrite receipts; the [historical reproduction guide](../Reproduction_Guide.md) must be used only in disposable clones, outside this frozen submission check.

## Evidence interpretation

**REPRODUCED:** raw/schema/medians/exact overlap, local and live case parity, stored macro-F1 consistency, fresh RF validation/TEST metrics with the explicitly retained hardware-AP exception, and fixed-weight balanced-accuracy sensitivity.

**VERIFIED:** source fitting boundaries, protected hashes, current cloud identity/configuration/static assets, fresh browser flow and existing experiment receipts.

**ARCHIVED-ONLY in this audit:** complete 21-model refitting, grouped model training, calibration fitting, SHAP and stress experiments, full notebook execution and Linux image execution. Earlier execution receipts remain available; none is represented as newly rerun.

**NOT COMPLETED:** prospective independent validation, field-calibrated costs/confidence, certified dropout safety, distributed rate limiting, actual-charge/student-credit accounting, and original complete-path 10 ms / model 10 MiB targets.
