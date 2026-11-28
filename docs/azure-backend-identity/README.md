# Azure backend identity - local candidate

> Current release: both official services are verified live as of 28 November 2026. See the [final release and submission freeze](../final-release/README.md). The earlier checkpoint evidence below remains historical.


Historical checkpoint status: implemented and locally verified on `design/azure-backend-identity`. **A controlled deployment was attempted and rolled back after a live browser navigation timeout.** At that checkpoint, Azure was restored to the preserved image/configuration. See the [deployment and rollback report](deployment/README.md). Vercel production, redesigned preview, main and protected submission tag remain unchanged.

## Implementation and exact changed source files

| File | Change |
| --- | --- |
| `web/app.py` | Root handler chooses `backend.html` only when an internal ASGI scope flag is supplied; all API route source and security/timing middleware remain byte-identical |
| `web/azure_app.py` | Small forwarding function sets that flag only for the Azure root; the original inference app and exact CORS middleware arguments remain in use |
| `web/static/backend.html` | Developer-facing API information page, not the four-step user dashboard |
| `web/static/backend.css` | Independent navy/white/blue styling with limited yellow accents and responsive layout |
| `web/static/backend.js` | Readiness presentation using the unchanged bounded health transport; no prediction call or keepalive |
| `deployment/decoupled/prepare_context.py` | Add exactly the three new landing assets to the existing runtime allowlist |
| `web/tests/test_backend_identity.py` | Five focused regression tests covering root isolation, assets, five-class parity, CORS/validation and disabled docs/playground |

The remaining added files under this documentation directory are review evidence, screenshots and the browser test harness. No frontend source, model, fitted preprocessing, scientific evidence, requirements, Dockerfile or Vercel configuration was modified.

The Azure-only forwarding function does not replace FastAPI. HTTP API requests and lifespan messages go to the original application unchanged. Root requests still traverse the original timing/security middleware. A normal `web.app:app` process retains its original dashboard; `web.azure_app:app` selects the distinct backend landing page. The internal scope flag cannot be supplied as a JSON predictor or query parameter.

The information page documents the actual GET health/examples and POST prediction endpoints, four finite nonnegative electrical inputs, five nominal labels and public model SHA. Class 4 is environmental shade, not hardware failure. Both Vercel links and GitHub remain available. Swagger/OpenAPI were already disabled and remain disabled; no broken documentation link or prediction playground was added.

## Readiness behavior

The unchanged `api.js` module validates the real health status and original model SHA before READY is displayed. Connecting/starting map to STARTING; failed bounded startup becomes UNAVAILABLE. Check readiness explicitly retries. There is no interval, scheduled warmup or polling after success/failure. The existing 120-second startup bound, 30-second individual health deadline and scale-to-zero caveat are preserved. No inference threshold or server deadline was changed.

## Verification evidence

- [Regression results](Regression_Verification.json): **50 tests passed**, including all 45 previous tests and five focused identity tests. Existing failure-path log messages and the Starlette httpx deprecation warning are expected; no dependency upgrade was made.
- Five local candidate predictions exactly matched all original reference fields. [Read-only live comparison](Preservation_Verification.json) additionally compares complete candidate and current Azure responses for classes 0, 1, 2, 3 and 4. These are historical fixtures for deployment parity, not fresh independent accuracy.
- Existing local CORS tests used all six live allowlisted origins, including production and redesigned preview. All were permitted, foreign origin rejected and invalid payloads returned422. The actual Azure CORS list was only read, never changed.
- [Browser verification](Browser_Verification.json): desktop1440, tablet768 and mobile390 screenshots, no horizontal overflow, console errors, unexpected external requests or model predictions. Actual READY, bounded simulated UNAVAILABLE, explicit retry and absence of post-ready keepalive passed.
- Axe-core4.14.1 found zero automated A/AA violations at those three widths. An incomplete aria check still needs manual review; this is not a full screen-reader certification. Test injection is development tooling and is not deployed.
- Vercel static build output retains **all nine original hashes**: no backend page, backend script or backend style is added to the Vercel output. The static builder is unchanged.
- Current Vercel deployment IDs, Azure image/revision, six CORS origins, CPU/memory/min/max and protected Git refs were checked read-only and recorded in [preservation evidence](Preservation_Verification.json).

[Desktop screenshot](screenshots/1440.png) | [Tablet screenshot](screenshots/768.png) | [Mobile screenshot](screenshots/390.png)

## Local review

```sh
python -m uvicorn web.azure_app:app --host 127.0.0.1 --port 8766
```

Open http://127.0.0.1:8766. No new dependency or local model training is required. `python -B -m unittest discover -s web/tests` includes the new five tests. To repeat all six-origin tests, supply the existing allowlist in the local process environment; this is not an Azure configuration update. The browser harness expects existing Playwright tooling on NODE_PATH and the temporary axe script at ignored `.review/axe.min.js`.

## Container build requirements and deployment impact

At initial local review, no image had been built and Docker was unavailable locally. A subsequent approved Linux build and Azure deployment attempt are documented in the [deployment report](deployment/README.md); the new image was rolled back after the browser gate timed out.

The current approved live image remains:

`ghcr.io/ruganji-prince/pv-anomaly-detection@sha256:234cba831be3b1465a8447c16922602dc54f5f0dcb3a86cc5b465c0890e5023f`

After deployment approval, build a new image from this branch's committed runtime allowlist using the unchanged `deployment/decoupled/Dockerfile`, Python3.14.10, existing hash-locked requirements, nonroot user and `web.azure_app:app` command. The updated context adds only backend.html/css/js to the existing allowlist. Model SHA must remain:

`55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb`

A new image digest is an expected consequence of the new presentation files. Never describe the old image digest as containing this candidate. Before publication/rollout, verify all layers, runtime assets, local/container five-class parity, validation, CORS, resource caps and secret/size scans. The existing workflow supports manual dispatch on the design branch; this branch's push does not trigger its engineering-only image publication rule. Do not invoke publication until authorized.

The rollout would update **only the image reference and required unique revision identifier on the existing app**. Preserve the exact six-origin CORS variable, all other environment values, configuration, probes, ingress8000, Consumption profile,0.5vCPU/1GiB,min0/max1 and disabled persistent logging. No CORS addition, service, resource or Vercel action is needed. A new revision can have startup delay; do not promise interruption-free service or increase replicas to conceal it.

## Approval gate and rollback

1. Review this candidate and screenshots. Obtain explicit approval before image publication and modification of the running Azure app.
2. Build/verify the candidate Linux image, capture its new immutable digest and retain the current image/revision. Stop if any integrity or parity check fails.
3. Re-read live configuration immediately before rollout. Preserve every non-image setting and use a unique revision suffix. Never reuse a revision suffix or send response-only ARM metadata in a write request.
4. After the new revision is healthy, verify root identity, real health, five classes, both Vercel browser workflows, all six CORS origins, invalid input and unchanged resources. No main merge or Vercel promotion is included.
5. If verification fails, restore the current image digest above in the existing app, preserving the current six-origin configuration, or reactivate the preserved healthy revision **pv-anomaly-detection--cors-design-h8tneats1** with explicit traffic/readiness verification. Do not roll back to an older five-origin revision that would break the redesigned preview. Do not delete retained revisions/images or rewrite Git history.

The original model, scientific results and approved PDF remain byte-identical. The only intended externally visible behavior after a separately approved deployment is the Azure root information page and its static assets.
