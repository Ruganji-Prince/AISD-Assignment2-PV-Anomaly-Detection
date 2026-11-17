# PV Anomaly Detection web application

**Public application: [https://pv-anomaly-detection-prince-r-k.vercel.app](https://pv-anomaly-detection-prince-r-k.vercel.app)**

Production and preview API/browser checks passed without visitor authentication.

A responsive single-reading dashboard backed by FastAPI and the original fitted Random Forest E4 pipeline. No model fitting, replacement, confidence percentage or probability calibration is performed. Natural building shade is an environmental condition, not a hardware-failure class.

## Run locally

Use Python **3.14.10**, matching the verified Vercel function runtime:

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

## Vercel configuration

The root `pyproject.toml` declares exact model dependencies, the three verified Python patches 3.14.7/3.14.8/3.14.10 and the `web.app:app` FastAPI entrypoint. The existing academic requirements files remain intact. Vercel must run the guarded Python/dependency versions. The model was trained with Python 3.14.7; Vercel build and function environments can use different 3.14 patch versions. The `.python-version` selects 3.14; `requires-python` is restricted to the three verified patches and the loader checks the explicit allowlist. Before adding 3.14.8 and 3.14.10 to the explicit runtime allowlist, separate clean-environment tests reproduced the complete RF block-13 and TEST confusion matrices/metrics and all five original examples with unchanged model bytes and dependency pins. See [build-patch evidence](Python_Compatibility.json) and [function-runtime evidence](Python31410_Compatibility.json). Only the interpreter guard was extended; the model, preprocessing and prediction code remain unchanged. Other Python versions remain rejected.

`vercel.json` selects FastAPI and the function entrypoint; `.vercelignore` and function exclusions omit datasets, reports, scientific figures, environments, caches and test tooling from the service upload. These files remain in GitHub. Only the required fitted model, inference modules, examples, web code and configuration are needed for serving. The measured Linux wheels plus original model total approximately 253.88 MiB uncompressed, before the small application/runtime overhead, below the documented 500 MB Python-function limit. The Vercel build reported 253.65 MB before dependency optimization and completed successfully. Production readiness checks confirm model loading and the exact hash on Python 3.14.10; these are execution checks, not a claim of operational production-system reliability.

The project is linked once in the `prince-r-k` Hobby team. A tested preview was promoted to production only after real five-class API and desktop/mobile browser checks passed. Project deployment protection is disabled for this public research application; visitors do not need an account. No paid resources or plan upgrades were purchased. Future changes should be deployed with `vercel deploy --environment preview --scope prince-r-k`, verified, then promoted with `vercel promote PREVIEW_URL --yes --scope prince-r-k`. The GitHub main branch is connected for subsequent deployments.

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
