# Reproduction guide

Run from the repository root. Python3.14.10 is parity-verified with the original artifact; scientific dependency versions are strict. `uv` must already be installed. Installation downloads public packages and does not provision paid services.

## Clean public setup and quick audit

```powershell
git clone https://github.com/Ruganji-Prince/AISD-Assignment2-PV-Anomaly-Detection.git
cd AISD-Assignment2-PV-Anomaly-Detection
uv venv --python 3.14.10 .venv
uv pip install --python .venv -r technical_evaluation/requirements.txt
.\.venv\Scripts\python.exe -B -m technical_evaluation.audit
.\.venv\Scripts\python.exe -B -m src.inference.cli --input deployment/example_input.json
.\.venv\Scripts\python.exe -B phase2_implementation/verify_submission.py
```

On POSIX use `.venv/bin/python` instead. No account, secret or private cache is required for the default audit or original RF inference. The public CSV and original RF binary are regular Git files, not generated during this audit. The audit checks their recorded SHA256 values. New original-report generation is not required.

The default audit verifies saved experimental evidence and recomputes F1 from confusion matrices; it does not independently regenerate every probability array or retrain all models. The full clean-environment receipt records an actual baseline clone, newly installed41-package environment,13-cell notebook execution,23 tests, original RF parity and real localhost API startup. Linux/Docker equivalence is not asserted. A fresh full-run verification can take several minutes; training opt-ins take longer and depend on hardware.

## Scientific execution, explicitly opt-in

```powershell
# Minutes: data/duplicate audit, block14 calibration, public RF/baselines, subgroup/shift/stress.
.\.venv\Scripts\python.exe -B -m technical_evaluation.audit --run
# Expensive: three full-TRAIN clipping fits and nine grouped-fold model fits.
.\.venv\Scripts\python.exe -B -m technical_evaluation.audit --train
# Regenerate12 figures after the --run probability cache exists.
.\.venv\Scripts\python.exe -B -c "from technical_evaluation.plots import main; main()"
# Fresh experimental reconstruction, never modifies models/rf_e4/model.pkl.
.\.venv\Scripts\python.exe -B -m technical_evaluation.reconstruct --candidate RF__E4
# Optional21 experimental model/sensor reconstructions, potentially expensive.
.\.venv\Scripts\python.exe -B -m technical_evaluation.reconstruct --candidate all
```

Reconstruction uses [hash-verified archived parameters](evidence/rubric3/original_model_parameters.json) and the preserved preprocessor factory. Full TRAIN alone fits every learned transformation and class weight; block13 supplies validation. TEST is not used in reconstruction. The RF reconstruction was actually executed; the optional all21 new-fit sweep was not executed during this audit. Original21 artifacts were separately hash-verified and their validation metrics reproduced from the private cache. Do not substitute experimental binaries for originals or claim byte identity from matching scores.

For exact original LR/LightGBM reproduction, supply a trusted locally preserved cache root containing stage2/models, or that model directory directly:

```text
python -B -m technical_evaluation.audit --run --private-cache PATH_TO_TRUSTED_ORIGINAL_CACHE
```

The code verifies recorded SHA256 before unpickling original cached objects. Private cache paths/credentials are not committed. With no cache, the public run compares Dummy baselines and original RF; it does not pretend to reproduce unavailable original LR/LightGBM objects. Existing published archive-comparison evidence remains in the initial published commit; a subsequent public-only run writes a reduced fresh comparison receipt. Preserve a run-specific copy if comparing multiple runs. No experiment retrains or serializes the deployed original model. New heavy binaries/arrays stay under ignored `.cache/technical_evaluation`.

Preprocessing reproduction overwrites the executed notebook and execution receipt in the checkout where it runs. Use a disposable clone to preserve approved bytes:

```text
python -B phase2_implementation/execute_preprocessing.py
```

The actual audit ran this command only in its separate scratch clone. Its output timestamps/serialization are not asserted byte-identical to the historical notebook. Standardized/median/PCA/MI fitting checks and diagnostic references are verified separately.

## Local API and existing four-step UI

```text
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. Health: `/api/health`; predictions: POST `/api/predict`, JSON with exactly vdc1/vdc2 in V and idc1/idc2 in A. Example: `{"vdc1":327.5482,"vdc2":327.8977,"idc1":6.5402,"idc2":6.2579}`. This illustrative input actually predicts natural building shade; it is not a validated normal-operation reference. No target/index/metadata or calibrated-confidence field is required.

```text
python -B -m unittest technical_evaluation.tests -v
python -B -m unittest discover -s tests -v
python -B -m unittest discover -s web/tests -v
python -B -m src.evaluation.verify_recovery
```

Optional browser checks use the existing [web instructions](../web/README.md), Node and Playwright. `PV_APP_URL` chooses localhost or the public URL; screenshots should remain outside tracked files. The actual live smoke test passed five viewports and all existing scenario modes.

## Docker: recipe available, execution NOT VERIFIED

```text
docker build -t pv-rf-e4 .
docker run --rm -p 8000:8000 pv-rf-e4
curl http://127.0.0.1:8000/api/health
curl -H "Content-Type: application/json" -d @deployment/example_input.json http://127.0.0.1:8000/api/predict
```

Docker is not installed on the audit machine. The recipe uses Python3.14.10, existing pinned inference requirements and a nonroot runtime. Build, Linux wheel resolution and container startup must be tested on a Docker-capable host. No verified-container claim is made.

## Live benchmark and security

`python -B -m technical_evaluation.audit --cloud` explicitly permits a modest sequential20-request benchmark plus schema/parity checks. No load-testing concurrency or paid resources are enabled. First observed request does not prove cold start. Account plan/price evidence is separate from actual charges, which were unavailable.

```text
python -B -c "from technical_evaluation.security import main; main()"
uv tool run pip-audit -r technical_evaluation/requirements.txt --no-deps --disable-pip --format json
```

Git must be on PATH for the history scan. The scan prints no secret values. Heuristics/advisory databases cannot guarantee complete security. Exact pins are in [requirements](requirements.txt); original deployment pins are unchanged. See [limitations](Limitations_and_Risks.md).
