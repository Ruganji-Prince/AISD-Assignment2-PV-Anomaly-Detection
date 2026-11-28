# PV Anomaly Detection web application

**Public application: [https://pv-anomaly-detection-prince-r-k.vercel.app](https://pv-anomaly-detection-prince-r-k.vercel.app)**

The canonical production application remains the previously verified static frontend. The new feature-branch preview is subject to the separate connectivity status below.

A responsive four-step application backed by FastAPI and the original fitted Random Forest E4 pipeline. No model fitting, replacement, confidence percentage or probability calibration is performed. Natural building shade is an environmental condition, not a hardware-failure class.

## Historical replay and manual inference — feature-branch candidate

**Step 4: [public static preview](https://pv-anomaly-detection-8u71v1zjs-prince-r-k.vercel.app) is READY. Browser-to-Azure inference on that hostname is BLOCKED by CORS; production promotion is NO-GO. Both modes passed genuine Azure checks from the already-approved localhost origin. Production is unchanged.** Publication evidence will be recorded in [preview verification](../docs/replay-preview/README.md).

**Manual Inference** is selected by default. Enter four finite nonnegative measurements, optionally load any of the 150 recorded TRAIN examples, then press **Run model inference**. Loading an example fills inputs only; it never runs or supplies a prediction. Actual returned classes, physical-category explanations, charts and out-of-training-range warnings are displayed separately from the recorded source label.

**Automatic Monitoring Demo** starts only after **Start**. It loads the frozen 150-observation TRAIN selection, confirms Azure readiness, submits one four-channel vector and waits approximately five seconds **after inference completes** before advancing. It stops after 25 observations (five per source class). **Pause**, **Restart**, mode switching and tab hiding cancel browser work and reject stale responses. Returning to a visible tab does not resume automatically. A canceled browser request may already be computing on the server. API failures never produce substitute predictions or a local model fallback.

The replay is deliberately selected and balanced TRAIN data, not a chronological recording, physical sensor stream or representative class prevalence. All 13 disagreements remain in the 150-record pool; 137/150=91.33% is selected TRAIN-subset agreement, **not independent model accuracy**. The original RF E4 on Azure performs every inference in a cloud-connected demonstration. Vercel serves static assets only, with no model, Python runtime or inference function.

### Observed class-conditional TRAIN ranges

Frozen TRAIN positions [0,1,006,129), without filtering or new fitting. Values below are P5–P95 descriptive marginal intervals, rounded to four decimals.

| Source class | TRAIN N | vdc1 P5–P95 (V) | vdc2 P5–P95 (V) | idc1 P5–P95 (A) | idc2 P5–P95 (A) |
| --- | ---: | --- | --- | --- | --- |
| 0 — Normal operation | 844,805 | 0.4668–292.5700 | 0.4250–290.0140 | 0.0510–8.2122 | 0.0064–7.8652 |
| 1 — Short circuit | 1,226 | 258.7753–267.7080 | 200.5577–209.1983 | 8.7727–9.4214 | 8.4549–9.1426 |
| 2 — Resistive degradation | 5,695 | 246.8404–267.2385 | 227.2595–258.5468 | 7.8330–9.3198 | 6.6115–8.8145 |
| 3 — Open circuit | 1,204 | 1.6395–266.8979 | 2.1527–273.0028 | 0.1015–9.1426 | 0.0432–9.0932 |
| 4 — Natural building shade | 153,199 | 258.3207–320.4700 | 242.9450–348.6480 | 0.4538–7.2223 | 0.0994–6.1335 |

Class-conditional ranges overlap. These intervals are **not guaranteed classification thresholds or Random Forest decision boundaries**. The model evaluates joint combinations of four electrical measurements and its fitted preprocessing. Class4, natural building shade, is an **environmental condition**, not a hardware fault.

[Complete statistics: minimum, maximum, quartiles, median, mean and sample standard deviation](../technical_evaluation/PV_Class_Measurement_Ranges.md) | [Full-precision CSV](../technical_evaluation/PV_Class_Measurement_Ranges.csv) | [Deterministic analysis script](../technical_evaluation/class_measurement_ranges.py) | [Replay selection and limits](../technical_evaluation/PV_Replay_Selection_Method.md).

### Five fixed historical reference examples

In **Manual Inference**, type the four measurements from any row below into the matching Vdc1,Vdc2,Idc1,Idc2 fields, then press **Run model inference**. Open **Model Assessment** for the actual returned label. Expected labels below are parity references, never replacements for an API response.

| Expected class | vdc1 (V) | vdc2 (V) | idc1 (A) | idc2 (A) |
| --- | ---: | ---: | ---: | ---: |
| 0 — Normal operation | 300.031 | 329.544 | 0.2247 | 0.1272 |
| 1 — Short circuit | 256.461 | 208.699 | 9.1373 | 8.4463 |
| 2 — Resistive degradation | 259.212 | 246.611 | 9.0792 | 8.3303 |
| 3 — Open circuit | 262.91 | 0.8866 | 8.9742 | 0.0468 |
| 4 — Natural building shade | 334.823 | 335.877 | 0.4303 | 0.2274 |

These are the five original [historical reference fixtures](../deployment/example_cases.json), previously taken from TEST and retained for serving parity. They are separate from the new TRAIN-only replay and optional 150-observation selector. No additional TEST/VALIDATION observation was selected for replay or used to tune a model/threshold. Successful fixture predictions do not establish independent accuracy. The optional TRAIN selector contains 30 diverse observations per source class, including retained disagreements; a source label does not promise the model's output.

### Current static build and local checks

Use the pinned Python3.14.10 environment and `technical_evaluation/requirements.txt`. Run from the repository root, with Git and Node on PATH:

```sh
python -B -m unittest discover -s web/tests
node --test web/tests-browser/replay.test.mjs
python -B web/tests-browser/run_replay_checks.py --legacy
```

The browser command builds and tests static output against the real **local** original-model API; it does not establish live Azure or preview connectivity. Current cloud evidence is linked above and must distinguish live Azure calls from mocks. For interactive local review and full checks, see the [mode implementation guide](../docs/historical-replay/README.md).

Actual static-only build (use a fresh destination):

```sh
python -m frontend.build --output .cache/pv-preview/.vercel/output --manifest .cache/pv-preview-manifest.json
```

The default API origin is the existing Azure HTTPS endpoint. The exact eleven-file output includes only configuration, ten static assets and the curated 150-record replay. Full raw data, models, Python, tests and private review material are excluded. Source builds remain fail-closed; only verified prebuilt output may be deployed to the existing project. A new preview origin requires explicit Azure CORS approval if absent from the allowlist. No proxy, wildcard, browser-security bypass, production promotion or main merge is implied.

## Historical combined frontend/backend local setup

Historical combined-server instructions below predate the current decoupled architecture. Use the static-build instructions above for the new replay assets. Python **3.14.10** runs the preserved local model; current Vercel hosting is static only:

```text
python -m venv .venv
.venv\Scripts\python -m pip install -r web/requirements.txt -r web/requirements-test.txt
.venv\Scripts\python -B -m uvicorn web.app:app --host 127.0.0.1 --port 8765
```

Open http://127.0.0.1:8765. On POSIX use `.venv/bin/python`. The frontend uses HTML, CSS and browser JavaScript; no frontend build step, CDN or external font is required.

## Input and output

`POST /api/predict`, content type `application/json`:

```json
{"vdc1": 300.031, "vdc2": 329.544, "idc1": 0.2247, "idc2": 0.1272}
```

Voltage inputs are in V; current inputs are in A. Exactly four finite nonnegative numeric values are required. Missing/additional fields, booleans, strings, nonfinite values, duplicate fields and oversized requests are rejected. No target, timestamp or source index enters inference. Values outside observed TRAIN ranges produce warnings; those ranges are not certified physical limits and values are not silently clipped.

The response contains the original predicted class/label, `fault_category` (`normal`, `hardware_fault`, `environmental_condition`), hardware/shade flags, model version/hash and warnings. `GET /api/health` checks original model/dependency integrity; failure returns 503. `GET /api/examples` returns the five existing released-data examples. The homepage never fabricates a result when inference fails. Predictions are not automatically logged or stored by application code.

The API uses the [original CLI](../src/inference/cli.py), fitted pipeline and [model provenance](../models/rf_e4/provenance.json). SHA-256 remains `55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb`. Shade (class 4) is not a hardware fault. The category flag describes argmax classification, not the separate archived hardware-alert threshold rule.

## Verification

From the repository root:

```text
python -B -m unittest discover -s web/tests -v
python -B -m unittest discover -s tests -v
python -B -m pip check
npm ci --prefix web
node web/node_modules/playwright/cli.js install chromium
npm --prefix web run test:browser
```

Browser checks use the running local server. Set `PV_APP_URL` to a preview/production URL to run the same real five-class, error/reset/loading and 390/320-pixel mobile checks against that deployment. Optional `PV_SCREENSHOT_DIR` saves private review screenshots. Browser failure-path tests intercept a request deliberately; successful model parity tests always call the real API.

## Historical Python-on-Vercel implementation (superseded)

The root `pyproject.toml` declares exact model dependencies, the three verified Python patches 3.14.7/3.14.8/3.14.10 and the `web.app:app` FastAPI entrypoint. The existing academic requirements files remain intact. Vercel must run the guarded Python/dependency versions. The model was trained with Python 3.14.7; Vercel build and function environments can use different 3.14 patch versions. The `.python-version` selects 3.14; `requires-python` is restricted to the three verified patches and the loader checks the explicit allowlist. Before adding 3.14.8 and 3.14.10 to the explicit runtime allowlist, separate clean-environment tests reproduced the complete RF block-13 and TEST confusion matrices/metrics and all five original examples with unchanged model bytes and dependency pins. See [build-patch evidence](Python_Compatibility.json) and [function-runtime evidence](Python31410_Compatibility.json). Only the interpreter guard was extended; the model, preprocessing and prediction code remain unchanged. Other Python versions remain rejected.

`vercel.json` selects FastAPI and the function entrypoint; `.vercelignore` and function exclusions omit datasets, reports, scientific figures, environments, caches and test tooling from the service upload. These files remain in GitHub. Only the required fitted model, inference modules, examples, web code and configuration are needed for serving. The measured Linux wheels plus original model total approximately 253.88 MiB uncompressed, before the small application/runtime overhead, below the documented 500 MB Python-function limit. The Vercel build reported 253.65 MB before dependency optimization and completed successfully. Production readiness checks confirm model loading and the exact hash on Python 3.14.10; these are execution checks, not a claim of operational production-system reliability.

The project is linked once in the `prince-r-k` Hobby team. A tested preview was promoted to production only after real five-class API and desktop/mobile browser checks passed. Project deployment protection is disabled for this public research application; visitors do not need an account. No paid resources or plan upgrades were purchased. Those combined-service publication details are historical. Current Git deployment is disconnected, source builds are fail-closed, and only tested static prebuilt previews are permitted. No promotion is authorized by this feature-branch task; production release needs separate approval.

## Scientific limitations

This is a research application, not a protection system or evidence of production readiness. Historical TEST exposure limits independent-generalization claims. No evaluated model met all engineering criteria; RF E4 exceeds archived latency and size targets. Cross-site evaluation, calibration, field monitoring and operational safeguards are not established. See the [model-selection report](../reports/Model_Selection_and_Deployment.md) and [existing deployment guide](../deployment/README.md).

## Official runtime references

- [Vercel Python runtime, supported versions and bundle limit](https://vercel.com/docs/functions/runtimes/python)
- [Vercel Python version configuration](https://vercel.com/docs/functions/runtimes/python/python-version)

## Recheck the public deployment

```text
python -B -m web.verify_live --url https://pv-anomaly-detection-prince-r-k.vercel.app
```

[Production API receipt](Production_Verification.json) | [Browser receipt](Browser_Verification.json) | [Deployment summary](Verification.json)

Vercel used Python 3.14.8 at build time and 3.14.10 at function execution. Initial builds exposed this patch mismatch; it was resolved through independent full RF validation/TEST parity checks before adding exact allowed patches. The model was never retrained, replaced or reserialized. Future platform patches outside the allowlist require a new compatibility check rather than silently bypassing verification.

## Scenarios and visualizations

Four client-side steps contain physical inputs, scenario controls, interactive voltage/current comparisons and actual model assessment with three plain-language explanation sections. Only one main section is visible at a time. Desktop fit is verified at 1366 x 768 and 1920 x 1080; smaller displays use responsive scrolling. Teal/blue distinguish measurement channels; green/red/amber/purple/blue distinguish result classes. Chart tooltips, tab transitions, seeded sample regeneration and loading/reset/error states require no external chart service.

Synthetic Demonstration Data is generated independently of the model: five illustrative operating-pattern presets around 180-340 V and 0-8.2 A receive deterministic uniform variations of up to 1.5% in voltage and 4% in current (seed 42 initially, incremented on regeneration). Four-decimal rounding is used and the illustrative interrupted-current channel remains zero. These are plausible input examples, not calibrated PV circuit simulations, confirmed fault signatures or measured data. No timestamps or time-series values are generated. Exact fixture inputs are in [synthetic cases](synthetic_test_cases.json); generator source is [scenarios.js](static/scenarios.js).

All five default synthetic inputs are classified as natural building shade by the unchanged model. Four selected intents therefore differ from the predictions. This is deliberately disclosed rather than changing inputs or outputs to force agreement. Historical dataset examples remain separately labeled and exercise all five actual classes. Synthetic inputs are not evidence of reliable physical-fault simulation or model generalization.

The explanation sections use the actual returned class, never the selected intent. Possible physical causes are general context, not model attributions or a confirmed diagnosis. Guidance recommends qualified assessment rather than unsafe energized troubleshooting. [PNNL PV operations and maintenance guidance](https://www.pnnl.gov/projects/om-best-practices/solar-photovoltaic) and the [NABCEP certification study guide](https://www.nabcep.org/wp-content/uploads/2019/05/NABCEP-2019-PV-Certification-Study-Guide.pdf) support the inspection context. The application provides no calibrated confidence, invented probabilities, feature-contribution claims or certified safety-monitoring capability.

## Four-step, single-page-at-a-time workflow

The top navigation follows PV Measurements, PV Scenarios, Graphical Analysis and Model Assessment. Previous/Next and direct numbered navigation use sequential 125 ms exit and 125 ms entrance animations; the old panel is hidden before the next is shown. Reduced motion skips these animations. Inactive sections remain mounted and hidden rather than being destroyed or reloaded. Navigation focus moves to the visible section heading; navigation-arrow/Home/End keys retain focus in the step bar. Completed markers indicate previously visited steps, not validation or model-quality certification.

Measurements, selected scenario, data source, seeded sample, voltage/current chart tab and the latest prediction/explanation remain in memory between steps. An edit, reset or scenario change clears the previous prediction until inference is rerun. Refreshing the browser starts a new session; no sensor values or predictions are persisted to browser storage.

The measurements page retains its original inference button and offers View Model Assessment after success. The assessment page has a compact ready state with its own inference action. Missing inputs return focus to Measurements for validation. Model errors return to the visible measurement error message. Modify measurements and Try another scenario actions are available from Assessment. No scenario is automatically treated as a prediction.

Browser checks cover forward/back/direct navigation, one visible panel throughout transitions, state retention, stale-output invalidation, keyboard access, reduced motion, all five dataset classes and all five synthetic inputs. Desktop fit is checked at 1366 x 768 and 1920 x 1080; tablet at 820 x 1180 and mobile at 390/320-pixel widths use responsive natural scrolling. The original model, backend, fitted preprocessing and deployment configuration are unchanged by this workflow update.

[Verified workflow preview](https://pv-anomaly-detection-aokqgywq7-prince-r-k.vercel.app) | [Workflow preview test evidence](Workflow_Preview_Verification.json)
