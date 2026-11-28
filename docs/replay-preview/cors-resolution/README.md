# Step 5: CORS resolution and live preview verification

Verified 28 November 2026. **GO for a separately approved production promotion. No promotion or main merge performed.** Previous Step 4 NO-GO records remain historical evidence.

## Actual configuration

Only `https://pv-anomaly-detection-8u71v1zjs-prince-r-k.vercel.app` was appended to `PV_FRONTEND_ORIGINS`; all six previous origins remain in order, without wildcards. [Before](Before_Configuration.json) and [after](After_Configuration.json) record the exact lists. CORS preflight accepts preview and production and rejects an unrelated origin: [evidence](CORS.json).

Active Azure revision: `pv-anomaly-detection--cors-replay-20261128`. Prior revision: `pv-anomaly-detection--submission-api-20261128`.

Immutable image remains `ghcr.io/ruganji-prince/pv-anomaly-detection@sha256:8c233e77ec370131f44670fcaf812a5aa27a79f7ca56bb8b7eff1beebc9cd946`.

Original RF E4 SHA-256 remains `55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb`. Azure for Students; 0.5 vCPU, 1 GiB, minimum 0 / maximum 1 replicas remain unchanged. The full configuration matched before/after; the template differs only in the origin value and necessary revision suffix. No new resources were created. Existing consumption charges can still apply.

## Verification

[Acceptance matrix](Acceptance.json): **17 PASS, 0 FAIL**. Separately: 53 Python tests, 14 Node tests, 21 mocked browser regression checks and 26 genuine local HTTP model predictions passed. [Regression evidence](Regression_Tests.json), [browser evidence](local-regression/Browser_Verification.json), [legacy workflow](local-regression/Legacy_Functional_Verification.json).

[Public preview](https://pv-anomaly-detection-8u71v1zjs-prince-r-k.vercel.app): all five manual reference classes matched original CLI outputs. Rendered measurements, class, category and explanatory text were checked separately: [live integration](Azure_Integration.json), [rendered UI](Preview_UI.json).

The genuine browser replay completed exactly 25 changing source observations; all predictions matched the archived original-model references. Four source/model disagreements remained visible. Maximum concurrent prediction requests: one. Measured response-end to next-request gaps: 5,001?5,171 ms. Completion produced no 26th request. Restart reset to the first observation; hidden-tab pause and failure handling prevented invented outputs. Browser-hidden state and transport failure were controlled simulations, explicitly distinguished from genuine successful inference. Additional cancellation, duplicate prevention and Pause cases are covered by the local browser suite. Source labels never replace model outputs.

Total actual Azure prediction requests: **47** (32 preview integration, five production, five successful rendered-content cases before the inline accessibility-tool failure, five final rendered-content cases). No full 150-observation Azure run was performed. Selected TRAIN replay agreement is not independent accuracy. Historical reference cases provide parity checks, not new generalization estimates.

[Existing production](https://pv-anomaly-detection-prince-r-k.vercel.app) still serves `dpl_EobcLSoR4iY4NSXYn5jxNCX5jvba`: five classes and four-step navigation passed [production checks](Production_Browser.json). Preview remains `dpl_CxdDd7gXxnJxBFhkzz5uCfZNTGHM`. [Vercel state and complete inventory](Vercel_State.json) and [served asset hashes](Static_Parity.json) establish unchanged static-only output: zero model files, Python runtime files or inference functions.

Live layouts passed at 320, 390, 768 and 1440 pixels across all four steps. Local built-page axe audits found no violations in four sampled views; color contrast required manual computed checks, which passed. Live CSP blocked inline axe injection and was preserved. Accessibility remains a sampled audit, not exhaustive assistive-technology certification.

[Integrity](Integrity.json): original model, raw CSV, approved PDF, frozen split, 604 protected files and original protected submission tag remain unchanged. Only verification/documentation additions are included in this step.

## Screenshots

- [Preview manual desktop](screenshots/azure-manual-1440.png), [mobile](screenshots/azure-manual-390.png)
- [Completed replay desktop](screenshots/azure-automatic-1440.png), [mobile](screenshots/azure-automatic-390.png)
- [Chart labels desktop](screenshots/azure-chart-1440.png), [mobile](screenshots/azure-chart-390.png)
- [Preview assessment desktop](screenshots/preview-ui-1440.png), [mobile](screenshots/preview-ui-390.png)

## Reproduction and rollback

The checked-in verification scripts require Playwright and the existing browser installation, plus Node. From repository root set `PV_REPO_ROOT` to the root, `PV_EVIDENCE_DIR` to a fresh output directory, and `PV_APP_URL` to the preview (or production for `verify_production.cjs`). Run `node docs/replay-preview/cors-resolution/verify_preview.cjs`, `verify_ui.cjs`, or `verify_production.cjs`. Scripts make bounded real requests; do not rerun unnecessarily. Local regressions use the existing `web/tests-browser/run_replay_checks.py` with an explicit fresh `--output` directory and `--node` executable.

[Rollback_Patch.json](Rollback_Patch.json) preserves the original six-origin template and immutable image, using a unique rollback suffix. It contains only the three audited nonsecret runtime variables. No rollback was needed. If an authorized rollback becomes necessary, first re-read Azure to check for intervening changes, then use Azure REST PATCH against the existing Container App resource with this file as the body, API version `2026-07-01`. Wait for readiness and reverify health, original model hash and production predictions. Do not apply a stale rollback over subsequent changes. The complete original resource snapshot is kept only in ignored local cache; no credentials are published.

No technical blocker remains for requesting promotion approval. Production promotion and main integration remain separate, unperformed actions.
