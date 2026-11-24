# Professor quick start

Technical evaluation: 1 or4 December 2026. Start with the [live application](https://pv-anomaly-detection-prince-r-k.vercel.app), [current report](../refinement/Final_Report.md) and [rubric index](Rubric_Evidence_Index.md). The previous 88/100 assessment is a dated engineering snapshot; the current mock assessment is 91/100, not an official grade.

## Quick verification from the repository root

Prerequisite: Git and uv. The public repository includes the immutable CSV and original RF binary; no credentials or private model cache are needed.

```powershell
git clone https://github.com/Ruganji-Prince/AISD-Assignment2-PV-Anomaly-Detection.git
cd AISD-Assignment2-PV-Anomaly-Detection
uv venv --python 3.14.10 .venv
uv pip install --python .venv -r technical_evaluation/requirements.txt
.\.venv\Scripts\python.exe -B -m technical_evaluation.refinement.verify
```

Linux/macOS: use `.venv/bin/python` for the final command. The quick audit runs 30 tests, verifies prior protected bytes, split/calibration ledgers, original-model fixtures and links, and writes only an ignored local receipt. It does not train models, contact cloud endpoints or rewrite published evidence.

## Five separate execution modes

| Mode | Command after environment activation | Expected behavior |
| --- | --- | --- |
| Quick verification | `python -B -m technical_evaluation.refinement.verify` | Tests and integrity checks; no network/fitting |
| Full refinement science | `python -B -m technical_evaluation.refinement.reproduce --reconstruct-all` | Full near-neighbor check, fixed empirical scenarios, bootstrap sensitivity, calibration/baselines,21 new model fits; expensive |
| Local API | `python -m uvicorn web.app:app --host 127.0.0.1 --port 8000` | Open localhost:8000; preserves four-step design |
| Actual container verification | `python technical_evaluation/refinement/container_verify.py` | Requires Docker; builds, starts, checks nonroot/schema/5cases/200TRAIN probabilities; also checks Vercel parity |
| Bounded live verification | `python -B -m technical_evaluation.refinement.cloud_benchmark --url https://pv-anomaly-detection-prince-r-k.vercel.app --receipt results/cloud_practice.json` |30 sequential+12 concurrency-two requests plus parity/schema checks; no automatic retry |

Full reproduction writes separate refinement results and ignored new model objects. Original reports/model/data remain untouched. Bootstrap defaults reuse preserved grouped-OOF confusion matrices rather than refitting all nine folds. The earlier audit's `--train` command regenerates those folds and changes historical receipts; use that command only in a disposable clone, as explained in the [original reproduction guide](../Reproduction_Guide.md). No byte-identical trained-model reproduction is asserted.

The original preprocessing notebook can be executed in a disposable clone using `python -B phase2_implementation/execute_preprocessing.py`; this updates notebook execution outputs only in that clone. The completed clean-clone evidence records this actual run.

## Fixed TRAIN-derived demonstration

```text
python -B -m technical_evaluation.refinement.demo --class 1 --seed 42
python -B -m technical_evaluation.refinement.demo --class 1 --seed 42 --url https://pv-anomaly-detection-prince-r-k.vercel.app
```

The first predetermined sample for the selected conditioning class/seed is used, without searching model outputs. Across the fixed250 samples,249 agree with source-conditioning labels. Parent observations belong to model-fitting TRAIN; the balanced50/class demonstration is not independent generalization accuracy or validated synthetic fault accuracy. Original illustrative presets remain unchanged and still all predictshade. Historical observations, empirical perturbations and actual predictions are distinct.

## Most important limitations

Historical TEST has prior exposure; no independent PV site is available. Signal-defined blocks are not verified days/sessions/hours. TRAIN short-circuit examples occur only in block 12. Experimental calibration is not deployed. Persistent sensor dropout causes abstention offline and is rejected by the API. Model size remains 11.665MiB and archived latency36.808295ms; the original 10MiB/10ms targets remain unchanged. New runtime measurements are separate and do not revise the historical results. A local capacity guard is not distributed rate limiting.

See [technical defense](Technical_Defense_Guide.md), [questions/answers](Expected_Questions_and_Answers.md), [live checklist](Live_Demo_Checklist.md) and [final verification](Final_Verification_Checklist.md).
