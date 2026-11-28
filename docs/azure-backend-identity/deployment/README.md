# Controlled backend identity deployment - rolled back

**Final status: browser verification failed; rollback completed and verified.** The new interface is not currently active on Azure. No Vercel deployment or main merge was performed.

## Image and provenance

Application source: `6cf6e8a216d3828ee8ebe005efa6a220e79a31b4`.

Linux-verified new immutable image (published and retained, **not active**):

`ghcr.io/ruganji-prince/pv-anomaly-detection@sha256:8c233e77ec370131f44670fcaf812a5aa27a79f7ca56bb8b7eff1beebc9cd946`

[Successful Linux workflow](https://github.com/Ruganji-Prince/AISD-Assignment2-PV-Anomaly-Detection/actions/runs/46049197680) checked the approved runtime allowlist, original dependency lock and Dockerfile, model identity, five-class parity,200-row numerical parity, layer/secret checks, nonroot/read-only runtime,0.5CPU/1GiB test caps, root identity, all six CORS origins, invalid payloads and anonymous public-registry pulls before publication. See [image provenance](Verified_Image.json), [Linux container evidence](Linux_Container_Verification.json), [identity/CORS HTTP evidence](Linux_Identity_HTTP_Verification.json), [original Docker evidence](Original_Docker_Verification.json) and [registry evidence](Registry_Verification.json).

Two earlier runs stopped before publication: the first identity test harness depended on optional TestClient packages intentionally absent from the production image; it was replaced by standard-library HTTP checks of the real container. The historical Docker verifier also assumed inference on Vercel; an explicit in-memory adapter now checks the actual Azure endpoint and labels it Azure. No assertion was removed and no runtime dependency, historical script or scientific receipt was rewritten.

## Deployment verification and rollback

The verified image was deployed as `pv-anomaly-detection--api-identity-6cf6e8a` and reached READY. [Pre-rollback live API evidence](Pre_Rollback_Live_API_Verification.json) records the correct root and asset hashes, five classes, all CORS origins, input rejection and identical non-image configuration.

The next live-browser gate failed at `page.goto`: navigation exceeded the harness default30-second page-load timeout. The deployed page had already passed direct HTTPS/asset checks; this timeout alone does not establish a model or application defect. It does mean the requested browser demonstration and live screenshots were not completed, so deployment success cannot be claimed.

The guard restored the last verified image and full template/configuration using a new rollback revision:

- Active rollback revision: **pv-anomaly-detection--api-rollback-1795804638**.
- Restored image: `ghcr.io/ruganji-prince/pv-anomaly-detection@sha256:234cba831be3b1465a8447c16922602dc54f5f0dcb3a86cc5b465c0890e5023f`.
- Original healthy revision **pv-anomaly-detection--cors-design-h8tneats1** remains preserved.

[Rollback verification](Rollback_Verification.json) confirms the original dashboard root and health return200, original model SHA matches, all five predictions pass, both Vercel-origin preflights pass, both Vercel releases are unchanged, six origins are retained and every non-suffix template/configuration value matches the pre-deployment snapshot. CPU0.5/memory1GiB/min0/max1, ingress, environment and security settings are unchanged. No new Azure resource was created.

## Verification checklist

| Gate | Result |
| --- | --- |
| Exact-source Linux build and registry verification | PASS |
| Linux model integrity, numerical/class parity and security | PASS |
| Linux landing/API/CORS/invalid-input checks | PASS |
| New Azure revision READY and direct live API checks | PASS before rollback |
| Live Azure browser completion and screenshots | FAIL / NOT COMPLETED:30-second navigation timeout |
| Both Vercel end-to-end browser reruns after rollout | NOT COMPLETED:guard rolled back before those runs |
| Rollback health/five classes/CORS | PASS |
| Existing Vercel release IDs, main and submission tag | PASS:unchanged |

The [existing screenshots](../screenshots/1440.png) are local-candidate screenshots, not a successful live-deployment capture. No live screenshot has been fabricated.

## Smallest next correction

Align browser navigation with the existing bounded cloud startup/readiness allowance instead of using its default30-second deadline. Keep the app, model, image, CORS and resource settings unchanged. Review this failure/rollback result before another controlled rollout, then complete live Azure and both Vercel browser checks. No further rollout was attempted after rollback.
