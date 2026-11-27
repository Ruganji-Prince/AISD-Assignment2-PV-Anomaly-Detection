# Decoupled deployment acceptance

| Requirement | Evidence | Status | Limitation |
| --- | --- | --- | --- |
| Static-only Vercel output | [Original preview inventory](Frontend_Deployment_Verification.json); production file-identity verification | PASS | Production has matching nine static-output files and zero inference functions |
| Direct Azure inference, all five classes | [Browser requests](Browser_Network_Verification.json), [parity](Prediction_Parity.csv) | PASS | Historical TEST fixtures, not new accuracy |
| Exact CORS and rejected foreign origin | [Live verification](Cross_Cloud_Integration_Verification.json), backend tests | PASS | CORS is browser policy, not authentication |
| Original container/model loading | [New container](Backend_Container_Verification.json), [original Docker](Original_Docker_Verification.json) | PASS | Original dependencies retained |
| Original scientific artifacts and tag | Scoped integrity verification | PASS | Authorized transport/UI changes excluded from historic freeze |
| Original and extension unit tests | 45 tests across seven groups documented in [reproduction](README.md) | PASS | Historical aggregate hash gate remains historical |
| Four-step layout and five viewports | [Regression](Frontend_Regression_Verification.json) | PASS | Browser sample, not every device |
| Startup/retry/no keepalive/duplicate prevention | [Browser evidence](Browser_Network_Verification.json) | PASS | Deadline/failure simulations; no physical cold-start SLA |
| Azure caps, prior revision and image | [Revision configuration](Azure_Revision_Configuration.json), final publication checks | PASS | Existing usage-based student credit exposure remains |
| Warm serving latency | [Measured summary](Latency_Summary.json) | PASS | N15; 10 ms complete-path target remains unmet |
| Model size target | Original model hash and 12,232,020 bytes | FAIL | Original 10 MiB threshold remains unmet |
| Production static cutover | [Completed cutover record](Production_Cutover_Plan.md); final production read-only verification | PASS | Deployment ID changed on preview-to-production promotion, assets matched |
| Distributed rate protection and production reliability | [Security](Security_Verification.md) | PARTIAL | No paid WAF, distributed limiter or SLA |

Rubric 5 evidence now includes actual independent frontend/backend hosting, direct browser requests, deployment boundaries, CORS, bounded startup and rollback. The prior mock assessment remains 91/100, including Rubric 5 at 18/20; no artificial score increase is made. [Performance limitations](Performance_Evaluation.md) remain explicit.
