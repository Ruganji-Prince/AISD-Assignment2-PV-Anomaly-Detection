# Decoupled production deployment - 27 November 2026

Status: production cutover completed and verified. Production Vercel deployment `dpl_H77uanaDrGutfBv5vJkb5825u3Gi` serves the verified static frontend; GitHub `main` integration was completed in merge commit `d8e1b52860f587c0cf7e3d2be07dc555c2f139e6`.

[Production static frontend](https://pv-anomaly-detection-prince-r-k.vercel.app) calls the [Azure inference API](https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io) directly. The [original verified preview](https://pv-anomaly-detection-pbyhom77a-prince-r-k.vercel.app) remains preserved. Original legacy Vercel deployment `dpl_D24pfF7JJsBL5PRSy8VRQFAeXcpU` remains available for rollback. No new cloud resource or paid service was added.

## Evidence and architecture

See [architecture diagram](Architecture.md), [API contract](API_Contract.md), [startup handling](Cold_Start_Handling.md), [security](Security_Verification.md), [acceptance matrix](Acceptance_Matrix.md), [performance](Performance_Evaluation.md), [demonstration](Professor_Demonstration.md), [cutover plan](Production_Cutover_Plan.md) and [rollback](Rollback_Guide.md).

[Actual deployment output](Frontend_Deployment_Verification.json) contains nine files: routing configuration plus eight served static assets, zero inference functions, zero models and zero Python runtime files. [Browser network evidence](Browser_Network_Verification.json) records five actual Azure predictions, failure handling and duplicate prevention. [Cross-cloud verification](Cross_Cloud_Integration_Verification.json) checks five original-model predictions, explicit CORS and seven rejected invalid payloads. These historical TEST fixtures establish deployment consistency, not independent model accuracy.

Backend source is cf295ed02ce909001f67e7d0199805e79ef2aff6; active revision is pv-anomaly-detection--cors-cf295ed. Immutable image is `ghcr.io/ruganji-prince/pv-anomaly-detection@sha256:234cba831be3b1465a8447c16922602dc54f5f0dcb3a86cc5b465c0890e5023f`. [Container tests](Backend_Container_Verification.json), [public registry verification](Backend_Registry_Verification.json) and [unchanged original Docker tests](Original_Docker_Verification.json) passed. The old revision and image remain available.

## Local reproduction

Install the pinned existing `technical_evaluation/requirements.txt` into a Python environment. No retraining is required. From the repository root:

```sh
python -m uvicorn web.azure_app:app --host 127.0.0.1 --port 8765
python -m frontend.build --output .local-preview/.vercel/output --manifest .local-preview-manifest.json --api-base http://127.0.0.1:8765
python -m http.server 8080 --bind 127.0.0.1 --directory .local-preview/.vercel/output/static
```

Use a fresh, ignored/external build directory; the builder intentionally rejects an existing output directory. Open http://127.0.0.1:8080. The CLI examples above do not change production.

```sh
python -B -m unittest technical_evaluation.tests
python -B -m unittest technical_evaluation.refinement.tests
python -B -m unittest discover -s tests
python -B -m unittest discover -s web/tests
python -B -m unittest deployment.azure.test_context deployment.azure.test_deployment deployment.decoupled.test_backend deployment.decoupled.test_frontend
python -B -m deployment.decoupled.verify_integrity
```

These groups total 45 tests. Existing historical full verification receipts deliberately retain their original UI hashes; their old all-files freeze check is not a current extension acceptance test. The scoped checker protects 437 existing files and verifies the original model, CSV, approved PDF and protected tag without changing historical baselines.

For browser tests install the existing Playwright dependency documented in [web setup](../../web/README.md), set `PV_APP_URL` to the production frontend (or the preserved preview), `PV_API_URL` to Azure and `PV_EVIDENCE_DIR` to an external evidence directory, then run `node deployment/decoupled/browser_verify.cjs`. The existing `node web/tests-browser/smoke.cjs` runs the four-step regression at five viewports. `python -m deployment.decoupled.verify_preview` performs bounded live checks; set `PV_NODE` and `PV_VERCEL_CLI` to installed executables and authenticate the existing Vercel/Azure accounts. It writes current verification evidence; preserve published receipts before rerunning.

## Preview build and release boundary

Build with `python -m frontend.build --output <fresh-project>/.vercel/output --manifest <external-manifest.json>`. Copy `frontend/vercel.json` to the fresh project, link only the existing Vercel project, then run `vercel deploy --prebuilt --environment preview --scope prince-r-k` there. Upload only that static project, never the repository or model. Add each exact new preview origin to the existing Azure CORS allowlist before use; no wildcard is permitted. Preserve local development and approved production origins. No secret belongs in the public API configuration.

**Current release policy:** the Vercel project framework is `null`, automatic Git deployments are disabled, and a fail-closed project-level source-build command is set. Root [`vercel.json`](../../vercel.json) also disables Git deployments and rejects source builds; verified static prebuilt output is the approved release path. The historical `frontend/production.vercel.json` is a candidate reference, not the effective root production configuration. Production promotion and main integration have already occurred. Further releases require independent verification; do not rerun the previous cutover.

## Limitations

Scale-to-zero remains enabled. Startup polling is bounded at 120 seconds and prediction at 60 seconds; startup success is not guaranteed. No keepalive, paid capacity or availability SLA is claimed. The browser benchmark is a small warm sample. Public ingress has existing bounded validation/capacity controls, not distributed abuse protection. Unmet 10 ms / 10 MiB targets and the 91/100 mock assessment (Rubric 5: 18/20) remain unchanged. No calibrated confidence, physical causality, production readiness or new scientific accuracy result is claimed.
