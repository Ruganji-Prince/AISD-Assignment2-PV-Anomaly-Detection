# Final release and submission freeze - 28 November 2026

**Status: both official services verified working. No further deployment is planned.**

- Production frontend: https://pv-anomaly-detection-prince-r-k.vercel.app
- Azure API information and inference: https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io
- Vercel production deployment: **dpl_EobcLSoR4iY4NSXYn5jxNCX5jvba**.
- Azure active revision: **pv-anomaly-detection--submission-api-20261128**.
- Azure immutable image: `ghcr.io/ruganji-prince/pv-anomaly-detection@sha256:8c233e77ec370131f44670fcaf812a5aa27a79f7ca56bb8b7eff1beebc9cd946`.

## Verified serving flow

The canonical frontend serves the already-approved static design. All eight served asset hashes match the approved preview; deployed output contains nine files including configuration, zero models, zero Python files and zero inference functions. Vercel Git deployment is disconnected and source builds remain fail-closed. The release staged the retained prebuilt output without domains, verified it, then promoted the staged production deployment. No application rebuild occurred.

The browser submits four physical electrical measurements directly to the Azure HTTPS API. All five fixed reference predictions matched:0normal,1short circuit,2resistive degradation,3open circuit,4natural building shade. Class4 remains an environmental condition. Browser request/response/display evidence is recorded in [production browser verification](Production_Browser_Verification.json). These historical fixtures verify serving parity, not fresh independent model accuracy.

The Azure information page is now distinct from the frontend. [Live API verification](Live_API_Verification.json) confirms root/asset identity, health/model SHA, all CORS origins, validation, five classes and preservation of every non-image/non-suffix template and configuration value. [Browser verification](Azure_Browser_Verification.json) confirms desktop/tablet/mobile rendering, actual READY, bounded simulated failure/retry, no keepalive and no unexpected network calls. [Desktop screenshot](azure-screenshots/1440.png) | [Mobile screenshot](azure-screenshots/390.png).

The previous browser failure used a default30-second navigation/load deadline. The corrected verification waits up to120seconds for DOM navigation, then separately waits for the existing bounded model-readiness mechanism. No application deadline, model or infrastructure was changed to accommodate testing. The already-Linux-verified image was reused; no new container build was made.

## Acceptance

| Requirement | Result | Evidence |
| --- | --- | --- |
| Both official URLs and live Azure identity | PASS | Live API/browser receipts |
| Five actual production predictions | PASS | Production browser request/response/display records |
| Four steps, navigation, reset, scenarios, charts, errors | PASS | [Functional regression](Production_Functional_Regression.json) |
| Responsive desktop/tablet/mobile behavior | PASS | Five frontend viewports and three Azure viewports |
| Failure handling, retry, no local fallback, duplicate prevention | PASS | Production browser checks; controlled browser interception only |
| Static-only production boundary and exact asset identity | PASS | [Production verification](Vercel_Production_Verification.json), [manifest](Frontend_Manifest.json) |
| Six exact CORS origins; unrelated origin rejected | PASS | Live API verification; no origin additions |
| Resource/network/security/environment preservation | PASS | Live template/configuration comparison |
| Original model, scientific artifacts and submission tag | PASS | [Freeze verification](Freeze_Verification.json) |
| Integrated branch compatibility and repository links | PASS | Freeze verification and existing test suite |

The old single-screen/no-desktop-vertical-scroll test assumption remains explicitly retired for the approved readable design. All functional assertions remain. Both design histories are preserved by normal merges; no reset, rebase, force push or tag rewrite was used.

## Preserved rollback assets

Vercel previous production remains READY: **dpl_H77uanaDrGutfBv5vJkb5825u3Gi**, `https://pv-anomaly-detection-nlfchrjvr-prince-r-k.vercel.app`. If a future separately authorized release fails, restore this deployment using the existing rollback process rather than rebuilding.

Azure previous healthy revision remains preserved: **pv-anomaly-detection--api-rollback-1795804638**, image `ghcr.io/ruganji-prince/pv-anomaly-detection@sha256:234cba831be3b1465a8447c16922602dc54f5f0dcb3a86cc5b465c0890e5023f`. The six-origin configuration, Consumption profile,0.5vCPU/1GiB,min0/max1, HTTPS ingress8000, probes and security settings are unchanged. No new resource or paid capacity was introduced.

The earlier failed/rolled-back attempt remains recorded in its historical report. This final release succeeded with the corrected harness; no rollback was needed and no speculative repeat deployment was made.

## Submission readiness and limits

The preserved original tag remains `submission-ready-20261124` at `d49cff533e5fe8860bacfb9942779ab003db47db`. The original model SHA remains `55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb`. The approved PDF, data, preprocessing/split definitions, scientific reports/results, citations and model artifacts remain unchanged.

No submission blocker remains in the verified serving flow. Existing limitations remain documented: scale-to-zero can delay startup, historical TEST was previously inspected, synthetic scenario intent is not a guaranteed prediction, calibrated confidence is not exposed, and original resource/latency targets remain unmet. Automated accessibility checks are not a full assistive-technology certification. These are unchanged research limitations, not reasons for additional release changes.

Course/Canvas submission itself was not performed. Use the two official URLs and the final main commit for the professor-facing submission as required by the course.
