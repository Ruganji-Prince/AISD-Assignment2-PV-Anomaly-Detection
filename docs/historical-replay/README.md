# Historical replay and manual inference — local candidate

Branch: `feature/train-class-measurement-ranges`. Baseline: `b8a5be74ddd8215c4e2e00cbd05da09990255da2`. **Local implementation only: not pushed, merged or deployed.** Azure and Vercel production remain unchanged.

## Behavior

Manual Inference is selected by default. Existing inputs, scenario controls, four-step navigation, charts, class explanations and backend validation remain available. New recorded examples are loaded on request: all 150 observations, grouped as 30 per source class. Selection only fills inputs; submission is still required. Editing or resetting measurements removes the recorded-source association. Inputs have no class-range maximum or invented fault thresholds; finite nonnegative measurements are submitted to the existing API, whose validation/model numeric limits still apply.

Automatic Monitoring Demo waits for Start, loads the exact [frozen replay JSON](../../web/data/pv_historical_replay.json), checks readiness through the existing transport, then submits **only four physical measurements** to `/api/predict`. The source label is metadata, never a model feature or replacement prediction. The next observation is scheduled five seconds **after completion**, not on an overlapping interval. Slow requests therefore extend the presentation interval. The unchanged readiness allowance is 120 seconds; individual health and prediction requests retain 30/60-second limits.

Each run presents the first **25** observations, five per source class, then stops without keepalive. Restart explicitly starts again from observation one. Pause cancels pending browser work and retains the next uncompleted cursor; Start resumes. Mode switching, Restart and visibility hiding invalidate old generations and abort active work. Returning to a visible tab does not automatically resume. Cancellation can prevent UI updates and future browser requests but cannot guarantee that an already received server request stops computing. The original server capacity/deadline protections remain unchanged.

The source class, returned predicted class and agreement indicator are separate. Both summary interpretation and model-assessment badge use the actual returned class. All 150 observations and 13 recorded disagreements remain intact; all are available through manual examples. The bounded first-25 run includes **four** disagreements in current real-model verification. The 137/150=91.33% figure describes the entire selected TRAIN subset, not the first 25, field reliability or independent accuracy. The reordered observations are neither a continuous recording nor a live physical sensor stream. No timestamps or confidence percentages are fabricated.

The collapsible **Observed PV Measurement Ranges** table copies all 20 P5–P95 intervals from the verified CSV using round-trip float parsing. It explains marginal overlap and joint model use. No input clamp, threshold rule or model decision boundary is derived from these values. The analysis link targets this feature branch; it will become public only after a separately approved push.

## Static boundary and preserved artifacts

The static builder adds exactly two allowlisted assets: `assets/replay.js` and `data/pv_historical_replay.json`. Output now has **11** files: configuration plus ten static files, still **zero models, Python files or inference functions**. The existing build test was extended from the old nine-file set to the exact eleven-file set and checks replay bytes against the frozen source; no broad asset allowance was introduced. Default builds still use the approved Azure origin, and the source-build production safeguard is unchanged.

No backend file, API schema, CORS setting, model, scientific result, report, split or dependency lock was changed. Original model SHA-256:

`55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb`

The Step 2 generation script intentionally protects its entire pre-frontend snapshot, so it is not represented as passing after authorized frontend edits. New integrity tests protect all **586 non-UI files** from that 592-file snapshot, independently verify the unchanged replay hash, and recompute all 150 original-model classes. Only six existing frontend/build/test paths are explicitly permitted to differ; original scientific evidence is never rewritten.

## Verification evidence and scope

- [Acceptance and preservation checks](Verification.json): all 20 requested checks and changed-file manifest.
- [Browser verification](Browser_Verification.json): mocked scheduling/state tests and separate **26 actual local HTTP predictions** through unchanged `web.azure_app:app` and the original model. The real API context has no mocked routes; all five output classes and the four first-25 disagreements are verified.
- [Retained browser functional regression](Legacy_Functional_Verification.json): existing scenario, state, navigation, chart, validation and error assertions retained. Only the previously retired desktop-page-height assertion uses the already-documented readable-layout adaptation; horizontal-overflow checks remain. Original test source and historical receipts remain untouched.
- [Local test build manifest](Local_Build_Manifest.json): uses loopback API configuration solely for reproducible local integration; this is not a production deployment manifest.
- Python: **53 tests**, including the original 50 and three independent replay/source/range/integrity checks.
- Node: **13 deterministic tests** with injected fake timers and mocked transport. These verify no spontaneous start, sequential completion-based scheduling, bounded 25-run stop, cancellation, stale-result rejection, Restart, failures and exact payloads.
- Browser: four-step/navigation/layout checks at 320/390/768/1440 pixels, plus automated axe A/AA checks in both modes at 390 and 1440 pixels. Zero violations were detected; color-contrast checks also contain incomplete results requiring manual review. This is not full accessibility certification.

An initial generated-table encoding/float-rounding defect was caught by the new exact-CSV check and corrected, without modifying the CSV. Windows test-server launcher cleanup was corrected to own the actual server processes and refuse occupied ports. Neither correction changes scientific values or weakens a test criterion.

Screenshots show actual local-model outputs, not fabricated predictions:

- [Automatic desktop](screenshots/automatic-1440.png), [automatic mobile](screenshots/automatic-390.png)
- [Manual desktop](screenshots/manual-1440.png), [manual mobile](screenshots/manual-390.png)

## Reproduce locally

Use the existing pinned Python 3.14.10 environment (`technical_evaluation/requirements.txt`), Git and Node on PATH. Install the existing browser dependencies if needed:

```sh
npm --prefix web ci
npx --prefix web playwright install chromium
node --test web/tests-browser/replay.test.mjs
python -B -m unittest technical_evaluation.tests technical_evaluation.refinement.tests deployment.azure.test_context deployment.azure.test_deployment deployment.decoupled.test_backend deployment.decoupled.test_frontend
python -B -m unittest discover -s web/tests
python -B -m unittest discover -s tests
python -B web/tests-browser/run_replay_checks.py --legacy
```

The final command builds static output in an ignored temporary directory, starts loopback servers on 8080 and 8787, executes browser checks, writes this engineering evidence and stops its servers. The unchanged Azure wrapper already permits `http://127.0.0.1:8080`; no cloud CORS update is required. Set `PV_AXE_PATH` to an existing local axe-core script to repeat the optional accessibility checks. No runtime dependency or deployed asset includes that test-only library.

For interactive local review, build into a **fresh** output directory and use two terminals:

```sh
python frontend/build.py --output .cache/replay-review --api-base http://127.0.0.1:8787 --manifest .cache/replay-review-manifest.json
python -m uvicorn web.azure_app:app --host 127.0.0.1 --port 8787
```

```sh
python -m http.server 8080 --bind 127.0.0.1 --directory .cache/replay-review/static
```

Open `http://127.0.0.1:8080`. Stop both terminals after review. The backend information page itself is not the dashboard; new static replay assets must be served by the frontend build.

## Remaining release boundaries

No push, production build, preview deployment, main merge, Azure configuration change or cloud availability check was performed. Local inference demonstrates original-model/API parity, not current production availability. Review this candidate before separately authorizing publication. Manual assistive-technology/contrast review remains advisable. Historical TEST exposure, selected TRAIN replay bias, scale-to-zero behavior, uncalibrated confidence and existing model resource limits remain unchanged.
