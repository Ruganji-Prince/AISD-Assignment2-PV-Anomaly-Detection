# Resource-Efficient and Explainable PV Anomaly Detection

**[Open the PV Anomaly Detection application](https://pv-anomaly-detection-prince-r-k.vercel.app)** | [Web setup and verification](web/README.md)


The project compares photovoltaic operating-state classifiers under reduced measurement availability, balancing class-specific detection, physical input requirements, interpretability and resource constraints. The public demonstration uses the preserved four-electrical-channel Random Forest pipeline; retrospective scientific results and unmet engineering targets are reported explicitly.

## Decoupled deployment preview - 27 November 2026

[Open the verified static-only frontend preview](https://pv-anomaly-detection-pbyhom77a-prince-r-k.vercel.app) | [Azure inference API](https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io) | [Architecture, evidence and reproduction](deployment/decoupled/README.md)

The preview serves only HTML/CSS/JavaScript assets from Vercel and sends measurements directly to the existing Azure FastAPI backend running the original RF E4 pipeline. Actual deployed-output inspection found zero inference functions, models or Python runtime files. Five original-model predictions match the CLI, and 45 unit tests plus live browser integration and layout checks passed. Explicit CORS and bounded readiness/retry handling preserve the four-step interface without local prediction fallback or keepalive. The measured 15-request warm API p95 was 263.00 ms; this is serving evidence, not a new scientific accuracy result.

**Production cutover completed on 27 November 2026.** The canonical Vercel application now serves the verified static-only production output (deployment `dpl_H77uanaDrGutfBv5vJkb5825u3Gi`), with the original Vercel production deployment `dpl_D24pfF7JJsBL5PRSy8VRQFAeXcpU` retained for rollback. Model inference executes on the separate Azure backend. The original scientific artifacts and protected submission tag are unchanged. A fail-closed source-build safeguard prevents unverified legacy FastAPI redeployments. See the [diagram](deployment/decoupled/Architecture.md), [acceptance matrix](deployment/decoupled/Acceptance_Matrix.md), [professor demonstration](deployment/decoupled/Professor_Demonstration.md), [cutover plan](deployment/decoupled/Production_Cutover_Plan.md) and [rollback guide](deployment/decoupled/Rollback_Guide.md). Original scientific findings, known TEST exposure, unmet engineering targets and mock assessment remain unchanged.

## Azure cloud engineering extension - 27 November 2026

[Open Azure application](https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io) | [Existing Vercel application](https://pv-anomaly-detection-prince-r-k.vercel.app) | [Azure setup and evidence](deployment/azure/README.md)

The original RF E4 pipeline is hosted in a Linux Consumption container in France Central at 0.5 vCPU / 1 GiB, minimum zero and maximum one replica, using the verified public GHCR immutable image. Five fixed cases and 200-row numerical parity passed; all 42 measured requests per platform succeeded in a matched Azure/Vercel run. Warm sequential network p95 was 248.99 ms / 448.21 ms; server p95 was 16.62 ms / 16.71 ms. These serving measurements do not establish independent model accuracy or platform-wide superiority.

**First-access limitation:** a request after observed zero replicas took 56.94 seconds. Open the app and wait for Model ready before demonstration; the unchanged prediction timeout is 60 seconds. No always-on capacity or scheduled warming was enabled. The original 10 ms / 10 MiB targets remain unmet, and the 91/100 mock assessment is unchanged.

See [architecture](deployment/azure/Architecture.md), [container provenance](deployment/azure/Container_Provenance.json), [cloud comparison and figures](deployment/azure/Cloud_Comparison.md), [latency evidence](deployment/azure/live/Latency_Summary.json), [cost analysis](deployment/azure/Cost_Analysis.md), [security](deployment/azure/Security_Verification.md), [reproduction](deployment/azure/README.md#reproduction), [Rubric 5 acceptance](deployment/azure/Acceptance_Matrix.md) and the [five-minute professor demonstration](deployment/azure/Professor_Azure_Demonstration.md). ActualCost currently has no reported rows; charges and remaining student credit remain unverified. The protected submission tag and scientific artifacts remain unchanged; Azure is a subsequent engineering extension on the existing engineering branch.

## Technical evaluation - professor quick start

For evaluation preparation, follow the [10/20-minute walkthrough](technical_evaluation/defense/Evaluation_Walkthrough.md), [learning guide](technical_evaluation/defense/Student_Learning_Guide.md), [mock examination](technical_evaluation/defense/Mock_Technical_Examination.md) and [submission/offline checklist](technical_evaluation/defense/Submission_Readiness.md). These are preparation documents; historical reports and measured results remain in their original locations.

Start with the [Professor Quick Start](technical_evaluation/defense/Professor_Quick_Start.md), [Technical Defense Guide](technical_evaluation/defense/Technical_Defense_Guide.md), [43-requirement evidence index](technical_evaluation/defense/Rubric_Evidence_Index.md) and [current refinement report](technical_evaluation/refinement/Final_Report.md). The independent engineering mock assessment is **91/100**, compared with the previous 88/100; this is not an official grade. The original dataset, fitted RF model, academic reports and four-step design are preserved.

```powershell
uv venv --python 3.14.10 .venv
uv pip install --python .venv -r technical_evaluation/requirements.txt
.\.venv\Scripts\python.exe -B -m technical_evaluation.refinement.verify
.\.venv\Scripts\python.exe -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

Linux: use `.venv/bin/python`. Quick verification runs 30 tests without training, cloud calls or tracked-receipt rewrites. Separate full-science, local API, container and live-cloud commands are in the guide. Actual Linux container runs, full near-neighbor checks, 21 public model reconstructions, calibrated-probability reproduction and bounded server/network profiling are evidenced. Historical TEST is retrospective; experimental calibration is not deployed. Original 10 ms/10 MiB targets remain unchanged. See the [demo checklist](technical_evaluation/defense/Live_Demo_Checklist.md) and [questions/answers](technical_evaluation/defense/Expected_Questions_and_Answers.md).

**Current milestone: Models, results and a public web inference application.** The completed Assignment 3 preprocessing workflow is retained below. Original archived LR, Random Forest and LightGBM models have been recovered and evaluated without refitting. The original four-channel RF pipeline is available through a public web application and the local CLI.

**Evaluation limitation:** the historical TEST partition was previously inspected. Results are retrospective, not pristine independent generalization estimates. No evaluated configuration met all engineering criteria; RF E4 was selected by the archived validation sensing/performance rule and exceeds separate latency and size targets.

**Task Type: Multiclass Classification.** The [original dataset](https://github.com/clayton-h-costa/pv_fault_dataset), pinned at `e9ed8ad8072dcb3ffc643b0f3604219798708551`, is associated with [Lazzaretti et al. (2020)](https://doi.org/10.3390/s20174688).

| Property | Description |
| --- | --- |
| N × P | 1,373,798 × 7 |
| Predictors | vdc1, vdc2 (V); idc1, idc2 (A); irr (W/m²); pvt (°C) |
| Target | f_nv: 0 normal, 1 short circuit, 2 resistive degradation, 3 open circuit, 4 natural building shade |
| Types | Six continuous measurements and one nominal target; integer labels are not ordinal or continuous |

The [raw CSV](data/raw/pv_fault_dataset.csv), [conversion/source provenance](data/raw/README.md), [variable inventory](phase1_strategy/Variable_Inventory.csv) and [original license](phase1_strategy/PRIMARY_SOURCE_LICENSE.txt) are retained unchanged apart from navigation in the raw-data guide. Voltage/current are source-described DC RMS quantities; module temperature aggregates source probes.

![First ten raw observations](figures/raw_dataset_preview.png)

Preview of the raw photovoltaic monitoring dataset. First ten observations in exported source order. All ten have f_nv = 0.

## Data-quality findings

The export has zero conventional missing cells and 1,373,798 complete rows. This does not diagnose MCAR/MAR/MNAR or prove uninterrupted monitoring. The 62 paired irr/pvt zeros remain suspicious observations, not confirmed missing values. One irradiance value is -0.0381 W/m²; the existing quality convention clamps -1 ≤ irr < 0 to zero. Valid negative Celsius observations remain unchanged. No automatic statistical outlier deletion or capping is used.

The irradiance-qualified subset irr ≥ 100 W/m² contains 515,958 observations and reproduces literature class counts exactly. This suggests a possible evaluation-population explanation, but the paper does not explicitly document that filtering operation. Low-irradiance rows are retained rather than deleted to force agreement.

## Preprocessing workflow

Immutable data → schema/quality audit → original ordered partitions → TRAIN-only median/scaling fit → transform validation/test → descriptive diagnostics and output-dimension checks. Paired zeros remain observed. Contingency median imputation and retained-channel indicators are preserved. StandardScaler, native-scale and physical-derived representations are demonstrated without fitting downstream predictors. Robust/MinMax scaling and PCA remain descriptive alternatives; no new transformation or sensor choice is selected.

TRAIN [0,1006129), VALIDATION [1056990,1173967), TEST [1227337,1373798) are retained, with 104,231 separator positions. Sixteen signal-defined blocks are not verified days, sessions or hours. Nominal 1 Hz acquisition, per-second electrical RMS values, one-second environmental averages and the study's 16-day duration do not reconstruct timestamps or uninterrupted spacing. CSV order is source-position order only. The separator remains irr < 100 W/m² for at least 3,600 consecutive source positions, not a verified hour. The reserved partition is not claimed to be historically unseen.

Five TRAIN predictor pairs have |r| ≥ 0.85; five VIF values exceed 10. Dependence does not justify automatic deletion. Nominal-target association uses a proportional 50,000-observation TRAIN MI sample; scatterplots use 20,000 TRAIN positions. Exploratory TRAIN-scaled PCA explains approximately 95.17% with two mathematical components; all six physical inputs are still required to calculate them.

## Deliverables and execution

- [Approved Phase 1 report](phase1_strategy/Phase1_Strategy_Report.pdf) and [audit evidence](phase1_strategy/Supporting_Evidence_Index.md)
- [Executed preprocessing notebook](phase2_implementation/notebooks/Phase2_Preprocessing_Implementation.ipynb)
- [Preprocessing-stage report](phase2_implementation/reports/Assignment3_Phase2.pdf)
- [Eight diagnostics](phase2_implementation/preprocessing_diagnostics/README.md)
- [Preprocessing strategy versus reality](phase2_implementation/compliance/Strategy_vs_Reality.md)
- [Setup and reproduction](phase2_implementation/Reproduction_Guide.md)

The following legacy preprocessing execution updates notebook outputs and its execution receipt. Run it only in a disposable clone to preserve the approved notebook bytes. The quick verification command above does not rewrite tracked evidence:

```text
python -B phase2_implementation/execute_preprocessing.py
python -B phase2_implementation/verify_submission.py
```

## Structure

```text
data/raw/                         Immutable CSV and provenance
phase1_strategy/                  Original strategy and audit evidence
src/transformers.py               Target-free quality and physical transformations
src/pipeline_builder.py           Pipeline / ColumnTransformer definitions
src/preprocessing/                Preprocessing study and shared constants
phase2_implementation/notebooks/   Executed preprocessing notebook
phase2_implementation/reports/     Preprocessing report and text
phase2_implementation/compliance/  Preprocessing evidence and reflection table
figures/                          Preprocessing diagnostics and raw preview
models/rf_e4/                     Original hash-verified production artifact
src/inference/                    Input contract and unchanged fitted inference
web/                              Four-step frontend and FastAPI adapter
deployment/                       Predetermined reference inputs and outputs
technical_evaluation/refinement/   Verified experiments and readiness evidence
technical_evaluation/defense/      Walkthrough, learning guide and examination
```

Processed arrays, environments and local review material are excluded. The reflection report records measured stage dimensions, empirical justification and figure-linked decisions; its source and build instructions are included. The analysis makes no deployment-performance, globally minimum-sensing or causal claims. 

## Archived model selection and reproduced results

The following tables report the recovered original models. Separate public reconstructions and runtime refinements are documented in the current technical report; neither replaces the production model.

Block-13 VALIDATION only (32,800 observations):

| Model | Physical / mathematical inputs | Macro precision | Macro recall | Macro-F1 | Macro AP |
| --- | --- | --- | --- | --- | --- |
| LR__F6 | 6 / 12 | 0.872022940 | 0.927024112 | 0.893869804 | 0.942431868 |
| RF__E4 | 4 / 8 | 0.955450596 | 0.962811690 | 0.956297122 | 0.989740014 |
| LightGBM__E4 | 4 / 13 | 0.908327034 | 0.866445735 | 0.855657128 | 0.991518322 |

Frozen TEST reporting only (146,461 observations; prior exposure disclosed):

| Model | Physical / mathematical inputs | Macro precision | Macro recall | Macro-F1 | Macro AP |
| --- | --- | --- | --- | --- | --- |
| LR__F6 | 6 / 12 | 0.889885493 | 0.912349415 | 0.898389062 | 0.917422666 |
| RF__E4 | 4 / 8 | 0.926440050 | 0.985651058 | 0.950481150 | 0.976218899 |
| LightGBM__E4 | 4 / 13 | 0.940383125 | 0.896340685 | 0.902137434 | 0.993577665 |

RF E4 is the only one of 21 evaluated channel/family configurations meeting the four archived validation sensing/performance constraints. It requires four electrical channels and eight mathematical inputs. This is not a globally minimum-sensor claim. RF's archived p95 latency is 36.808295 ms and its original artifact is 11.665363312 MiB; both exceed the separate engineering targets. LightGBM's TEST short-circuit recall is .499364676 despite high aggregate hardware-alert recall. Class 4 remains natural building shade, not hardware failure.

[Model-selection report](reports/Model_Selection_and_Deployment.md) | [Reproduction evidence](reports/model_verification.json) | [All sensor comparisons](phase2_implementation/stage2/evidence/sensor_ablation_validation.csv) | [RF confusion matrix](phase2_implementation/stage3/figures/test_confusion_RF__E4.png) | [Resource comparisons](phase2_implementation/stage3/evidence/final_candidate_comparison.csv)

Raw-channel permutation and native LightGBM Tree SHAP use a fixed balanced validation sample; vdc2 has the largest mean permutation loss for each frozen candidate. These model associations are not causal explanations. Simulated isolated dropout is separate from field reliability. Detailed provenance, class-specific errors, resource measurements and limitations are in the report. Reconstructed noise-study models are not substituted for originals.

## Local inference CLI

The prototype loads the hash-verified original fitted RF E4 pipeline, validates four voltage/current inputs, and returns a class/label with explicit environmental-shade handling. No true label, timestamp or source index is required. Missing channels are rejected; no calibrated confidence or production readiness is claimed.

Use the currently verified Python 3.14.10 environment from the quick start (the original model was trained with Python 3.14.7), then run from the repository root:

```text
python -B -m src.inference.cli --input deployment/example_input.json
python -B -m unittest discover -s tests -v
python -B -m src.evaluation.verify_recovery
```

[Model provenance](models/rf_e4/provenance.json) | [Actual example output](deployment/example_output.json) | [Recovery manifest](reports/Recovery_Manifest.json) | [Acceptance matrix](reports/Acceptance_Matrix.md)

The Phase 1 PDF, Assignment 3 IEEE report, executed preprocessing notebook, original diagnostic figures and raw data remain unchanged. Only the selected original model is published; other original models, saved arrays, environments and backups remain local. The research application is hosted on Vercel. Prospective external evaluation and production monitoring are not completed.

## Public web application

The [PV Anomaly Detection dashboard](https://pv-anomaly-detection-prince-r-k.vercel.app) accepts four electrical measurements and calls the original fitted RF E4 pipeline through a Python FastAPI endpoint on Vercel. The responsive HTML/CSS/JavaScript interface includes dataset examples, five-class results, validation, loading and error states. Natural building shade is identified as an environmental condition. No confidence percentages or calibrated probabilities are presented.

Anonymous live API and browser checks pass for all five existing examples, including desktop and 390/320-pixel mobile layouts. The original model SHA-256, fitted preprocessing, parameters and scientific results are unchanged. Explicitly verified runtimes include Python 3.14.2, 3.14.7, 3.14.8 and 3.14.10; training used 3.14.7. Current compatibility and Linux evidence are recorded in the technical evaluation package.

- [Local execution, architecture and deployment](web/README.md)
- [Current API/timing evidence](technical_evaluation/refinement/results/cloud_production_profile.json), [browser evidence](technical_evaluation/refinement/results/production_browser.json) and [passing Linux verification](https://github.com/Ruganji-Prince/AISD-Assignment2-PV-Anomaly-Detection/actions/runs/45359434733)
- [Historical deployment verification](web/Production_Verification.json) and [historical browser verification](web/Browser_Verification.json)
- [Runtime compatibility evidence](web/Python31410_Compatibility.json) and [deployment verification summary](web/Verification.json)

The application runs on the Vercel Hobby plan. Hosting the research demonstration does not establish production protection-system reliability, calibration, prospective generalization or operational monitoring.

### Interactive dashboard

The web application presents measurements, synthetic/dataset scenarios, animated voltage/current comparisons and actual-class explanations across four client-side steps, with only one main section visible at a time. Synthetic inputs are clearly labeled, generated independently of the model, and separated from historical observations. Selected scenario intent can differ from the real model output; that difference is shown explicitly. No model probabilities or feature contributions are fabricated. See the [dashboard design and scenario methodology](web/README.md).

[Preview layout verification](web/Redesign_Preview_Verification.json) | [Production browser evidence](technical_evaluation/refinement/results/production_browser.json)

The guided workflow preserves measurements, source, scenario, chart selections and predictions across Previous/Next and direct navigation. Measurement changes clear stale assessments; reduced-motion and keyboard navigation are supported.

[Four-step navigation and state verification](web/Workflow_Preview_Verification.json)
