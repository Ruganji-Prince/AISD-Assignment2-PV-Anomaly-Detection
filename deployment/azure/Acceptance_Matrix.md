# Azure extension acceptance and Rubric 5 evidence

The official Technical Evaluation Grid has five categories of twenty points. This subsequent engineering extension adds reproducible Azure serving evidence without changing the protected submission, classifier selection, scientific findings or historical TEST limitations. The existing mock assessment remains **91/100**, with **18/20 for Rubric 5**. A second platform alone does not justify a score increase; the complete-path/size targets, billed-consumption visibility, tail/cold behavior and distributed-rate-limit limitations remain.

| Requirement | Implementation / measured evidence | Status | Limitation |
| --- | --- | --- | --- |
| Original submission preserved | [Protected Git-blob hashes](Submission_Protection.json); original source/model/raw/PDF/frontend unchanged | PASS | README receives only Azure navigation; protected tag immutable |
| Correct subscription and region | Students Enabled, spending limit On, France Central policy; [preflight](Infrastructure_Preflight.json) and [deployed config](live/Deployment_Configuration.json) | PASS | Starting credit user-confirmed; remaining balance unavailable |
| Eligible Consumption quota | [Immediate pre-app receipt](Consumption_Quota_Before_App.json), 100 free cores vs 0.5 requested | PASS | Quota is permission/capacity, not allocated compute |
| Approved resource scope | Named RG, environment/app only; 0.5 vCPU/1 GiB/0-1 replicas, HTTPS8000, no Log Analytics | PASS | Standard service-managed platform internals are not customer-provisioned extra services |
| Image provenance and publication | [Source/digest](Container_Provenance.json), [anonymous registry verification](Registry_Verification.json) | PASS | Container source commit is distinct from final evidence commit |
| Runtime-only package | 24 context files, 22 in-image application files; all-layer hashes pass | PASS | Historical class modules are required to deserialize original pickle; fitting helpers are not executed |
| Original model and preprocessing | Actual Azure model SHA; [200 TRAIN probability rows](live/Azure_Runtime_Parity.json), max difference3.33e-16 at tolerance1e-12 | PASS | This is serving parity, not independent accuracy |
| Local/API/Vercel/Azure class parity | [Five fixed-case checks](live/Deployment_Verification.json), [CSV](live/Prediction_Parity.csv) | PASS | Fixed cases belong to historically inspected TEST |
| Frontend preserved | Six asset-byte checks and [browser test](live/Browser_Verification.json), five viewport sizes | PASS | Synthetic intents are illustrative and all existing synthetic fixtures predict shade |
| Schema and safe errors | Ten invalid cases rejected on each cloud, original local tests | PASS | No certification of physical input validity beyond existing contract |
| Tests and dependency consistency | [30 existing +9 Azure tests](Automated_Tests.json), 41 installed packages compatible | PASS | Notebook execution/retraining not repeated; unchanged earlier verified evidence retained |
| Matched latency and reliability | [84/84 measured requests](live/Latency_Summary.json), 30 sequential +12 concurrency-two per platform | PASS | Small single-client sample; p99 and SLA claims unsupported |
| Application timing components | Forest/preprocessing/server/network separately measured; all initialization events retained | PASS | Server wall-clock is not billed CPU |
| Scale-to-zero | [Zero replicas observed, new replica afterward](live/Scale_From_Zero.json); first request56.94s, subsequent705.50 ms | PARTIAL | First-access delay is substantial and near frontend60s timeout; one sample is not isolated cold-start profiling |
| Resource utilization | [Azure platform observations](after_benchmark/Resource_Usage.json) | PASS | Minute averages, not instantaneous peaks or billing meters |
| Cost estimates | [Explicit monthly scenarios](Cost_Analysis.md), official rate refresh | PASS | Assumed replica activity/shared grants/egress determine actual costs |
| Actual charges and remaining credit | [ActualCost query](after_benchmark/Billing_Observation.json) succeeded with no cost rows | PARTIAL | Billing delay; no verified zero invoice or remaining-credit assertion |
| Secret management | [Security review](Security_Verification.md), no app/registry credentials or new service principals | PASS | Existing CLI Owner permission is broad; no comprehensive security certification |
| Dependency vulnerabilities | OSV check of recorded Python versions returned no matches | PARTIAL | Base OS/image scan not completed; absence of matches is not absence of risk |
| Distributed rate limiting | Original per-process capacity preserved | NOT COMPLETED | No paid WAF or global IP limiter authorized/activated |
| Complete-inference and model-size targets | Original10 ms and10 MiB targets retained | FAIL TO MEET TARGETS | Azure server p95 16.62 ms; original artifact11.665 MiB; no target relaxation |
| Reproduction and operations | [Deployment](deploy.py), [verification](verify.py), [benchmark](benchmark.py), [resource control](Cleanup_Guide.md) | PASS | Use approved scope and fresh output paths; interruption/deletion requires approval |

## Relationship to existing academic evidence

The [Rubric Compliance Matrix](../../technical_evaluation/Rubric_Compliance_Matrix.md), [Technical Evaluation Report](../../technical_evaluation/Technical_Evaluation_Report.md), [43-row evidence index](../../technical_evaluation/defense/Rubric_Evidence_Index.md), [Submission Readiness](../../technical_evaluation/defense/Submission_Readiness.md), [Professor Quick Start](../../technical_evaluation/defense/Professor_Quick_Start.md) and [Technical Defense Guide](../../technical_evaluation/defense/Technical_Defense_Guide.md) were reviewed. They remain historical verified deliverables, with the current91/100 refinement assessment retained. This extension supplies Rubric 5 cloud-container, actual Azure configuration, parity, latency/resource and cost evidence through a separate dated index. Earlier records are not rewritten to imply that Azure existed at the submission tag.

No new train/validation/test split, preprocessing fit, model/feature/threshold choice, calibration deployment or model-performance claim is introduced. The original scientific evidence and limitations continue to support Rubrics 1-4. No official professor grade is claimed.
