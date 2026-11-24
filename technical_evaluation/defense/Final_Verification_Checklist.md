# Final verification checklist

| Check | Evidence / command | Scope |
| --- | --- | --- |
| Original model/datasets/reports unchanged | `python -B -m technical_evaluation.refinement.verify` | Prior baseline hashes, exact authorized code/config exceptions |
| Existing/new unit tests | Same quick command |30 tests:7 audit,6 inference,10 API,6 refinement |
| Split/features/fitting | [Split evidence](../evidence/rubric2/leakage.json), [fold ledgers](../evidence/rubric2/grouped_validation.json) | No identified target/preprocessing leakage; historicalTEST not pristine |
| Full near-neighbor screen | [Full query receipt](../refinement/results/full_near_duplicates.json) | All TRAIN references and all later rows, fixed distance criterion |
| Original/reconstructed distinction | [First pass](../refinement/results/reconstruction_comparison.json), [controlled LR](../refinement/results/LR_thread_sensitivity.json) |21 new fits; no original replacement/byteidentity claim |
| Calibration/uncertainty | [Calibration](../refinement/results/baseline_reverification.json), [bootstrap](../refinement/results/bootstrap_sensitivity.json) | Experimental, retrospective and conditional limitations preserved |
| Linux Docker actually runs | [Matrix evidence](../refinement/results/container_matrix.json) | Both3.14.10 and 3.14.2; actual builds, nonroot/read-only,5fixture and 200TRAIN probability parity |
| Runtime dependencies pinned/security scanned | [Lock](../../web/requirements.lock), [advisory receipt](../refinement/results/runtime_dependency_audit.json) | Exact closure with hashes; known-advisory check is not a guarantee |
| Fresh install/preprocessing/API | [Clean-clone receipt](../refinement/results/clean_clone.json) | Isolated clone+reviewed overlay; protected originals never regenerated in active repository |
| Cloud preview, timings and layout | [Profile](../refinement/results/cloud_preview_profile.json) |42 measured requests and separate five-viewport browser smoke |
| Public production after publication | [Public main](https://github.com/Ruganji-Prince/AISD-Assignment2-PV-Anomaly-Detection/tree/main) and `/api/health` | Remote SHA/tree, public guides, health/model parity and browser outcome |
| Secrets and paths | [Security receipt](../refinement/results/security.json) | Reachable Git history and reviewed changes; heuristic checks, no secret values printed |
| Optional distributed rate limit | [Review](../refinement/Rate_Limit_Review.json) | Not activated; local guard is not distributed protection |

No checkbox supersedes the machine-readable receipt. Full platform cold-start latency, actual invoices, external-site generalization, field reliability and operational safety certification remain unverified or dataset-limited.
