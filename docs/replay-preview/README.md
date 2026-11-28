# Historical replay — Step 4 integration and preview

Status: **verification in progress; no production promotion authorized**. Branch `feature/train-class-measurement-ranges`, implementation baseline `ce064d6a811f0bb45b2d70b34e588cffa1a4d4f0`.

The existing production deployment and Azure resource configuration are preserved. This step updates current documentation, verifies the real Azure API from an already-approved local origin, and publishes only tested prebuilt static output to the existing Hobby project. No source build, proxy, CORS wildcard, model change or main merge is permitted.

The final verification receipt will distinguish local/mocked scheduling, actual Azure predictions, public static preview checks and any CORS blocker. A preview that cannot call Azure from its own hostname will be marked **NO-GO** for production promotion.

See [TRAIN measurement statistics](../../technical_evaluation/PV_Class_Measurement_Ranges.md), [frozen replay provenance](../../technical_evaluation/PV_Replay_Verification.json), [current web instructions](../../web/README.md) and [Step 3 local verification](../historical-replay/README.md).
