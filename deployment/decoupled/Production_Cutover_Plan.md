# Production cutover — completed 27 November 2026

## Verified final state

- Canonical production frontend: https://pv-anomaly-detection-prince-r-k.vercel.app
- Active static-only Vercel deployment: `dpl_H77uanaDrGutfBv5vJkb5825u3Gi` (READY)
- Verified static preview: `dpl_7d4mEEWCvfvUnRCJ9ukKX9Js8oLD`; preserved for comparison
- Preserved legacy rollback deployment: `dpl_D24pfF7JJsBL5PRSy8VRQFAeXcpU`
- Azure inference service: https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io
- GitHub main integration: `d8e1b52860f587c0cf7e3d2be07dc555c2f139e6` via merged PR #1
- Original submission tag: `submission-ready-20261124`, pinned at `d49cff533e5fe8860bacfb9942779ab003db47db`.

## What happened

The earlier `vercel promote` operation created a **new** production deployment ID from the verified preview instead of retaining the preview ID. This is expected for preview-to-production promotion; an initial strict identity check stopped the local Codex cutover. The resulting production build `dpl_H77uanaDrGutfBv5vJkb5825u3Gi` was subsequently inspected: all nine deployed file paths and file identifiers matched the verified preview, with zero model artifacts, Python files or inference functions.

The Vercel production aliases were then assigned to that new, verified static deployment. The legacy deployment remained available for rollback. Root `vercel.json` and Vercel project settings were configured to disable automatic Git source deployments and reject unverified source builds. The decoupled engineering branch was merged normally into `main` without changing the original submission tag.

## Final read-only verification

The final production verification reported **PASS** for frontend/Azure health, direct browser POSTs to Azure, five original-model reference classes, production CORS and invalid input rejection, retry/timeout/no-fallback behavior, five viewport checks, frontend-only deployment inventory, immutable model SHA, historical PDF and submission tag. This verification established serving consistency and architecture, **not independent model accuracy**.

The Vercel frontend `/api/predict` returns 404, as expected; Azure owns model inference. No redeployment is necessary for documentation updates.

## Subsequent release policy

Use reviewed and tested **prebuilt static releases** only. Git source builds are fail-closed by policy and project configuration. Before any future promotion, verify production ownership, target deployment, byte-identical assets, Azure readiness, all five reference predictions, permitted CORS origins, and preserved rollback deployment. Do not assume a preview deployment ID will remain the same after promotion to production.

To recover from a future faulty release, follow [Rollback_Guide.md](Rollback_Guide.md), verify the canonical aliases and API behavior, and preserve all scientific artifacts. No additional Azure capacity or paid services are approved by this document.
