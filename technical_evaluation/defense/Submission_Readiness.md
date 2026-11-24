# Submission readiness and technical defense

Preparation date:24 November2026. Evaluation:1 or4 December2026. This is a stabilized research demonstration, not operational PV protection certification.

## Submission references

- Repository: [AISD PV Anomaly Detection](https://github.com/Ruganji-Prince/AISD-Assignment2-PV-Anomaly-Detection).
- Production: [four-step application](https://pv-anomaly-detection-prince-r-k.vercel.app).
- Verified application/runtime source commit: `869a0a5fbb3036a7a909746d87298ed5676bfffe`.
- Final submission reference: [submission-ready-20261124](https://github.com/Ruganji-Prince/AISD-Assignment2-PV-Anomaly-Detection/tree/submission-ready-20261124). This immutable annotated tag records the final documentation-ready commit. Resolve its exact commit SHA with `git rev-list -n 1 submission-ready-20261124`. The completion message also reports the full final SHA. A file cannot literally contain its own commit hash; the tag avoids a misleading self-reference or history rewrite.
- Current [43-requirement traceability](Rubric_Evidence_Index.md), [91/100 evidence-based assessment](../refinement/results/mock_assessment.json) and [technical report](../refinement/Final_Report.md).

## Five-rubric summary

| Rubric | Score/20 | Remaining deduction |
| --- | ---: | --- |
| Data hygiene/features/collinearity |18|Single-study physical validity and hypothetical stakeholder costs.|
| Split integrity/leakage-free pipeline |18|Historical TEST exposure, missing timestamps/external sites, singleton rare-fault block.|
| Modeling/evaluation rigor |18|Single-block calibration and assumption-sensitive grouped-OOF uncertainty.|
| Error analysis/robustness |19|Simulated and TRAIN-derived demonstrations are not independent field validation.|
| Reproducibility/cloud |18|Complete-path10ms/model10MiB targets, full platform cold/billedCPU and distributed rate limits unresolved.|
| **Total** |**91/100**|Engineering mock assessment, not an official professor grade.|

The grade is retained; improved navigation and study material do not justify an artificial increase.

## Confirmed engineering evidence

The [readiness verification receipt](Readiness_Verification.json) records final execution. Earlier evidence includes [clean environment/30 tests](../refinement/results/clean_clone.json), [actual Linux Docker runs](../refinement/results/container_final_runtime.json), [passing published-runtime Actions](https://github.com/Ruganji-Prince/AISD-Assignment2-PV-Anomaly-Detection/actions/runs/45359434733), [production timing/parity](../refinement/results/cloud_production_profile.json) and [browser checks](../refinement/results/production_browser.json). The current stabilization changes no application, model, dataset, notebook or scientific report.

Mandatory checks are independently recorded: public repository with runnable README; no identified unaddressed target/preprocessing leak, with historical exposure still disclosed; public live endpoint and safe secret handling. Formal independence, operational safety and perfect security are not implied.

Original model SHA256:

```text
55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb
```

The two Linux images run nonroot/read-only, verify five original cases and200 TRAIN probability references, and do not constitute a new fitted production model. Full retained-partition runtime comparison has zero class mismatches over1,269,567 observations. No retraining is needed for readiness.

## Prepare the environment before the evaluation

Run from the repository root. Prerequisites are Git, uv and enough time/network to install the pinned environment. Installation needs public packages, not private credentials.

```powershell
uv venv --python 3.14.10 .venv
uv pip install --python .venv -r technical_evaluation/requirements.txt
.\.venv\Scripts\python.exe -B -m technical_evaluation.refinement.verify
.\.venv\Scripts\python.exe -B -m technical_evaluation.defense.run_demo
.\.venv\Scripts\python.exe -B -m technical_evaluation.defense.run_demo --url https://pv-anomaly-detection-prince-r-k.vercel.app
```

Linux: replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`. For Windows shell activation use `.\.venv\Scripts\Activate.ps1`; Linux uses `source .venv/bin/activate`. The portable commands below then use `python`.

## Live demonstration: fixed references, never prediction search

1. Explain the task and show model provenance/hash. Open the actual four-step application.
2. Use historical dataset examples to show normal, short circuit, resistive degradation, open circuit and natural building shade. The returned prediction must be shown rather than assumed from scenario intent.
3. Run `python -B -m technical_evaluation.defense.run_demo --url https://pv-anomaly-detection-prince-r-k.vercel.app`. It uses the five existing JSON references in their fixed order, compares every original CLI output field with the API, checks health/model identity, displays Server-Timing and verifies missing/negative/unexpected-target rejection.
4. Explain original illustrative presets (all predictshade), historical references, and TRAIN-derived empirical demonstrations separately.249/250 agreement on TRAIN-derived perturbations is not independent accuracy or validated physical simulation.
5. State the resource limits: sequential forest-only p95~6.74ms, complete server p95~16.99ms and network p95~638.94ms are distinct. The unchanged artifact is11.665MiB. Concurrent forest p95 can exceed10ms; no blanket target compliance is claimed.
6. A readiness request can warm the model. Do not call a subsequent request a confirmed cold start or infer billedCPU from network time.

### Exact provenance of the five fixed references

The immutable raw CSV confirms exact equality of all four measurements and their source labels. Every reference is from the historically exposed TEST partition; it is used only to demonstrate unchanged inference/parity, not new model selection or unbiased evaluation.

| Reference class | Raw source position |
| --- | ---: |
|0 normal|1227337|
|1 short circuit|1244416|
|2 resistive degradation|1242691|
|3 open circuit|1242672|
|4 natural building shade|1230229|

No reference was newly selected by searching predictions. The API receives only the four measurement values, not these positions or labels.

## Offline fallback

Before internet becomes unavailable, install the environment and retain this full checkout including the original model and references. No Docker or cloud access is required for local fallback.

Terminal1:

```text
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

Terminal2:

```text
python -B -m technical_evaluation.defense.run_demo --url http://127.0.0.1:8000
```

Open http://127.0.0.1:8000 for the identical four-step interface. If a local server cannot start, `python -B -m technical_evaluation.defense.run_demo` runs entirely offline CLI inference and validation. It makes no network calls and still demonstrates every fixed class/reference. A cloud outage is an availability limitation; the local fallback is not evidence that the cloud was live during the outage.

## Preparation checklist

- Explain every variable, nominal target and shade/hardware distinction without notes.
- Derive IQR, Z-score, VIF, precision/recall/F1, AP and probability-scoring definitions.
- Trace TRAIN-only fitting and point to the frozen bounds/validation roles.
- Explain prior TEST exposure and why grouped folds lose class support.
- Justify the four-input RF selection without claiming global minimal sensing or full engineering acceptance.
- Explain calibration isolation and why no calibrated production confidence exists.
- Separate permutation, SHAP, descriptive MI and causal interpretation.
- Explain simulated stress, persistent dropout, near states and synthetic intent limitations.
- Trace a JSON request through validation, fitted inference, error handling and timing headers.
- Run quick verification and five fixed cases; rehearse both10-minute and20-minute walkthroughs.
- Complete the [66-question examination](Mock_Technical_Examination.md) after studying the [learning guide](Student_Learning_Guide.md).
- Prepare local fallback in advance; do not fit models or regenerate protected notebooks during the session.

## Remaining limitations

Historical TEST is not pristine; timestamps and independent PV sites are absent; rare faults are concentrated in few blocks. Calibration and bootstrap evidence remains conditional. Noise/dropout/saturation/OOD evidence is simulated, and persistent channel failure is not safely imputed. Source-class demonstration agreement is not generalization. Distributed rate limiting, operational monitoring, real invoices/full platform cold-start measurements and safety qualification are incomplete. The original10ms and10MiB targets remain unchanged and unmet for the complete system/artifact.
