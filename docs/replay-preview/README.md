# Historical replay — Step 4 integration and preview

Status: **PREVIEW READY — AZURE CONNECTION BLOCKED BY CORS — NO-GO FOR PRODUCTION**. Branch `feature/train-class-measurement-ranges`, implementation baseline `ce064d6a811f0bb45b2d70b34e588cffa1a4d4f0`.

The existing production deployment and Azure resource configuration are preserved. This step updates current documentation, verifies the real Azure API from an already-approved local origin, and publishes only tested prebuilt static output to the existing Hobby project. No source build, proxy, CORS wildcard, model change or main merge is permitted.

Public preview: **https://pv-anomaly-detection-8u71v1zjs-prince-r-k.vercel.app**. Existing project `prj_crdyiWPhHbKADgYXLtaSoTzAd2Ox`, Hobby plan. Preview deployment `dpl_CxdDd7gXxnJxBFhkzz5uCfZNTGHM`, runtime commit `044be27c3d113b42bc075bccc013b6f92a3c1b7c`. Final evidence/documentation commits may follow without changing deployed assets. Production remains `dpl_EobcLSoR4iY4NSXYn5jxNCX5jvba`; no aliases were reassigned.

## Exact CORS blocker and smallest safe next step

Azure preflight for the exact preview origin returns **HTTP 400**, body `Disallowed CORS origin`, with no `Access-Control-Allow-Origin`. A normal Chromium cross-origin POST also rejects with `TypeError: Failed to fetch`. Therefore **manual and automatic Azure inference from this preview browser have not passed**. No proxy, successful mocked response, custom Origin header or disabled browser security was used to hide the failure.

The smallest proposed correction requires separate approval: append exactly

`https://pv-anomaly-detection-8u71v1zjs-prince-r-k.vercel.app`

to the existing Azure `PV_FRONTEND_ORIGINS` JSON list, preserving all six existing origins, image, model, resource limits and other settings. No such update was performed. After approval/configuration, rerun actual browser-to-Azure reference predictions, replay and cancellation checks on this hostname. Production promotion and main merge still require separate authorization; CORS approval alone does not authorize a release.

## Tests passed, blocked and corrected

| Check | Result | Evidence / scope |
| --- | --- | --- |
| Python regression tests | PASS: 53 | [Test summary](Tests.json), including all150 original-model offline predictions, frozen source values and protected evidence |
| Node scheduling/transport tests | PASS: 14 | Fake timers/mocked transport, plus a new native Window timer-receiver regression |
| Existing local browser functions | PASS | [Retained functional suite](local-regression/Legacy_Functional_Verification.json); original test source/receipts preserved, previously retired height-only assumption remains explicitly adapted |
| Local browser feature tests | PASS: 21 checks | [Local browser receipt](local-regression/Browser_Verification.json): mocked scheduling/UI checks separated from26 actual local original-model HTTP predictions |
| Actual production Azure manual references | PASS: 5 | [Preserved successful checkpoint](Azure_Manual_Checkpoint.json); HTTP200 and original reference fields verified; full response bodies were not retained |
| Actual production Azure automatic replay | PASS: 10 observations | [Azure integration](Azure_Integration.json), plus 1 restart and 1 out-of-range manual prediction: 17 completed genuine predictions in total across both receipts |
| Real-time sequential cadence | PASS | Response-to-next-request intervals approximately 5003–5171 ms, maximum one in-flight prediction; no virtual time during genuine predictions |
| Actual source/prediction disagreement | PASS | Observation 10: source normal 0, returned shade 4. The dataset label never replaces the response |
| Failure/Pause/Restart/visibility behavior | PASS within stated scope | Actual pause/restart and simulated visibility event; controlled client network abort for failure, not a fabricated Azure outage |
| Sampled chart contrast | PASS: 14.59:1 | Opaque white value backgrounds with dark ink; prior straddling fill/track backgrounds could yield 1.10:1 or 3.09:1. Class-badge assertions also passed during the five manual cases |
| Automated accessibility | No violations in four sampled views | Color-contrast incomplete results supplemented by sampled computed-color/visual review; no exhaustive assistive-technology certification |
| Actual Vercel static build/upload | PASS | Eleven allowlisted files, ten served asset hashes match, frozen150-row replay included; zero models/Python/functions. [Static verification](Preview_Static_Verification.json) |
| Public preview UI | PASS | [Actual preview browser](Preview_Browser_Verification.json): manual default, all150 examples, five source classes, charts, ranges, input validation, four-step keyboard/focus/navigation and desktop/mobile views |
| Public preview → Azure manual/automatic inference | **FAIL/BLOCKED: CORS** | [Exact preflight](Preview_CORS.json) and native browser rejection. Five-second live inference and actual returned classes cannot be certified on this hostname |
| Original model/scientific files/configuration | PASS | [Original-file integrity](Local_Integrity.json), [Azure preservation](Azure_Preservation.json), [final summary](Final_Verification.json) |

The first live-browser attempt hit an incorrectly short 30-second harness wait before predictions; the harness now follows the existing 120-second startup allowance. A subsequent unmocked browser check exposed native timer methods called with the wrong receiver (`Illegal invocation`), which fake timers had masked. Small client-side wrappers fix the binding; both the new regression and real-time Azure replay passed. An accidental UTF-8 delimiter change in an intermediate test edit was corrected; the exact 20-cell statistics test remains intact. No failure was hidden by weakening scientific or output criteria.

The genuine Azure checks ran from the **already-approved `http://127.0.0.1:8080` origin**, using the real static build and existing Azure model. This proves that flow at that origin, not preview-host CORS connectivity or independent accuracy. No 150-request cloud sweep was run. The complete replay remains 137 agreements/13 disagreements on deliberately selected TRAIN data.

## Screenshots

Actual public preview, with inference unavailable and no fabricated results:

- [Preview manual desktop](screenshots/preview-manual-1440.png), [mobile](screenshots/preview-manual-390.png)
- [Preview automatic desktop](screenshots/preview-automatic-1440.png), [mobile](screenshots/preview-automatic-390.png)

Genuine Azure results from the approved local origin:

- [Azure manual desktop](screenshots/azure-manual-1440.png), [mobile](screenshots/azure-manual-390.png)
- [Azure automatic disagreement desktop](screenshots/azure-automatic-1440.png), [mobile](screenshots/azure-automatic-390.png)
- [Chart contrast desktop](screenshots/azure-chart-1440.png), [mobile](screenshots/azure-chart-390.png)

## Reproduction and preservation

Use the pinned Python environment and existing Playwright tooling. Run the Python/Node commands in [Tests.json](Tests.json). Run local browser checks without overwriting old receipts:

```sh
python -B web/tests-browser/run_replay_checks.py --output docs/replay-preview/local-regression --legacy
```

The dedicated [Azure harness](../../web/tests-browser/verify_azure_replay.cjs) requires the built frontend served from an already-approved origin and `PV_APP_URL`, `PV_EVIDENCE_DIR`; it reuses the verified manual checkpoint when present rather than repeating successful cases. Genuine predictions use real time; only the final controlled failure test accelerates the existing startup bound. The [preview harness](../../web/tests-browser/verify_replay_preview.cjs) uses `PV_PREVIEW_URL` and `PV_EVIDENCE_DIR` and explicitly expects/report the current CORS-blocked state; it is not a success test for connected inference. Once CORS is authorized, use the genuine Azure harness on the preview origin instead of treating a changed CORS result as a failure of the feature.

The original model hash remains `55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb`. TRAIN/VAL/TEST, raw data, all frozen scientific results/reports, the 150 replay vectors and submission tag remain unchanged. Azure remains on revision `pv-anomaly-detection--submission-api-20261128`, image `sha256:8c233e77ec370131f44670fcaf812a5aa27a79f7ca56bb8b7eff1beebc9cd946`, 0.5 vCPU/1 GiB, min 0/max 1. The six CORS origins and production safeguard remain intact. No paid service, new Azure resource, source build, model retraining, main merge or production promotion occurred.

See [TRAIN measurement statistics](../../technical_evaluation/PV_Class_Measurement_Ranges.md), [frozen replay provenance](../../technical_evaluation/PV_Replay_Verification.json), [current web instructions](../../web/README.md) and [Step 3 local verification](../historical-replay/README.md).
