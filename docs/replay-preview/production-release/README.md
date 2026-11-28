# Final historical replay production release

Verified 28 November 2026. **Production release passed.**

- [Public application](https://pv-anomaly-detection-prince-r-k.vercel.app)
- [Unchanged Azure API](https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io)
- Production deployment: `dpl_2vL2km2fbH8GYrppVnXtXh3zysZG`.
- Preserved rollback deployment: `dpl_EobcLSoR4iY4NSXYn5jxNCX5jvba`, `https://pv-anomaly-detection-231o7tyw5-prince-r-k.vercel.app`.
- Approved feature: `12700e78d742442ac535323611958227f2873032`.
- Normal two-parent merge: `b6702e4ae01ffb0c3868e22ee7987c777e4660d2`; parent main `d007880c89a0312dbdf540678e9c8bf4cec3216e`. The merge tree exactly matched the approved feature tree before this release-status documentation was added.

## Release evidence

[Verification summary](Release_Verification.json), [Vercel inventory and preserved rollback](Vercel_Release.json), [served asset hashes](Static_Parity.json).

Direct API promotion of the preview returned 422 without changing production. The documented CLI promotion then created a new READY production deployment. All eleven output file identifiers and all ten served asset hashes match the approved preview. No source build was enabled, no model or Python files were uploaded, and no inference functions exist. [Fail-closed safeguards](Safeguard.json) remained enabled; Git integration remains disconnected.

[Live production browser-to-Azure verification](Azure_Integration.json): all five manual classes matched the original CLI references; the complete bounded 25-observation replay matched original-model references, retained 4 source/prediction disagreements, and stopped without a 26th request. Maximum replay concurrency was one. Measured response-end to next-request intervals: 5001.7?5176.1 ms. [Separate actual Pause/Restart/mode-switch checks](Production_Controls.json) passed with two real requests. [Rendered values, categories, explanations, navigation and responsive layouts](Production_UI.json) passed at 320, 390, 768 and 1440 pixels. The production verification used 39 genuine Azure predictions in total, not a full 150-row sweep.

[Regression tests](Regression_Tests.json): 53 Python and 14 Node tests passed, zero failures. Step 5 browser/accessibility evidence remains available [without modification](../cors-resolution/README.md), and production serves the exact same assets. Accessibility remains sampled rather than exhaustive certification. Controlled failure and hidden-tab checks are simulations, separate from successful genuine inference. Selected TRAIN agreement is not independent accuracy; historically inspected reference cases establish parity only.

[Azure read-back](Azure_Unchanged.json) confirms identical configuration and template, including all seven origins, immutable image, resource limits and revision `pv-anomaly-detection--cors-replay-20261128`. No Azure mutation, new resource, capacity increase, model fitting or scientific-result change occurred.

[Protected-file integrity](Integrity.json) confirms 604 protected files and the original submission tag unchanged. Original RF E4 SHA-256: `55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb`. The raw data, frozen split, approved PDF and prior evaluation evidence are preserved. [TRAIN class ranges](../../../technical_evaluation/PV_Class_Measurement_Ranges.md), [full-precision CSV](../../../technical_evaluation/PV_Class_Measurement_Ranges.csv), [web documentation](../../../web/README.md).

## Screenshots

[Completed replay desktop](screenshots/azure-automatic-1440.png), [mobile](screenshots/azure-automatic-390.png); [manual desktop](screenshots/azure-manual-1440.png), [mobile](screenshots/azure-manual-390.png); [chart labels desktop](screenshots/azure-chart-1440.png), [mobile](screenshots/azure-chart-390.png). All screenshots in this directory were captured from canonical production, including files with inherited `preview-ui` names.

## Rollback

The previous healthy static production deployment remains preserved. If a critical regression is found, inspect the current aliases, then run the supported `vercel rollback dpl_EobcLSoR4iY4NSXYn5jxNCX5jvba --scope prince-r-k` operation and verify canonical asset identity and five reference predictions. Do not rebuild, alter Azure or change the model. No rollback was necessary for this successful release.

No unresolved critical blocker remains. Cold starts, selected-TRAIN replay limitations, uncalibrated outputs and prior scientific performance limitations remain explicit. No additional improvements were introduced.
