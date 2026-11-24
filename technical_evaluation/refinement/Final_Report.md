# Final technical refinement and mock evaluation

Date:24 November 2026. Evaluation preparation:1 and 4 December 2026. Baseline public commit:c7f922133e4301f66a95612c46bc1bdea14f2ef2. Earlier academic reports, original scientific results and the original RF E4 fitted artifact remain historical/protected, not rewritten to claim improvements. This report supersedes only previous engineering readiness/status claims.

## Independent audit and assessment

The official grid was reread. All43 previous requirement rows were reviewed against implementation/evidence; the 88/100 assessment was not accepted as verification. Newly identified engineering issues included a quick audit that rewrote a tracked receipt, omission of the original BLAS thread control in public reconstruction, unexecuted containerization, insufficient cloud timing separation and a provider patch mismatch that could break fresh deployments. These were investigated with failures preserved in the [run notes](results/engineering_run_notes.json).

| Official category | Previous | Updated | Remaining deduction |
| --- | ---: | ---: | --- |
| Data hygiene/features/collinearity |18|18|2:single-study physical validity and hypothetical stakeholder costs.|
| Split integrity/leakage-free pipeline |17|18|2:historicalTEST, no verified timestamps/external site, singleton rare-fault block.|
| Modeling/evaluation rigor |18|18|2:one-block calibration and assumption-sensitive uncertainty.|
| Error analysis/robustness |18|19|1:simulated/within-TRAIN demonstrations are not field/external validation.|
| Reproducibility/cloud |17|18|2:whole-path/size targets, platform cold/billedCPU and distributed rate limit remain unresolved.|
| **Total** |**88/100**|**91/100**|Independent engineering mock evaluation, not an official professor grade.|

Each category is supported by the [43-row evidence index](../defense/Rubric_Evidence_Index.md), [machine-readable classification](results/independent_requirement_review.json) and [mock assessment](results/mock_assessment.json). Quick verification: `python -B -m technical_evaluation.refinement.verify`. Full scientific reproduction and separate local/container/cloud commands are in [Professor Quick Start](../defense/Professor_Quick_Start.md).

## Integrity and leakage

The original split remains TRAIN[0,1006129), VAL[1056990,1173967), TEST[1227337,1373798), with 104231 excluded separator positions. No source index, operating block, exact six/four-feature vector or target metadata overlap was introduced. Every learned preprocessing/weighting step remains TRAIN/fold-specific. Group0 is outside signal-defined operating intervals, not a shared verified session. Signal blocks/source positions are not days/sessions/hours. HistoricalTEST was previously inspected; no new model/feature/calibration/threshold choice uses those outcomes.

The previously bounded near-neighbor screen is now exhaustive over every TRAIN reference and every later-partition query. Scaling is TRAIN-fitted; exact cKDTree search uses eps0 and predefined standardized Euclidean distance<=.001. No observation was removed.

| Features | Query cohort | Query N | Within criterion | Zero-distance matches |
| --- | --- | ---: | ---: | ---: |
| 4 | VALIDATION | 116977 | 37313 | 0 |
| 4 | TEST | 146461 | 62917 | 0 |
| 6 | VALIDATION | 116977 | 1290 | 0 |
| 6 | TEST | 146461 | 1125 | 0 |

Close physical states are common and do not by themselves prove target leakage. The counts limit an interpretation of independent observation-level generalization. Source/block disjointness does not manufacture independence, and no random reshuffle or artificial sessions were introduced.

## Public model and probability reproduction

All21 public configurations were actually fitted using published parameters, separately from original binaries. Eighteen first-pass validation macro-F1 scores matched exactly. Three LR variants differed by up to.00222046 because the public entry point omitted the original documented two-thread BLAS limit. Restoring threadpool_limits(2) made all three match their archived validation F1 exactly. First-pass receipts and private model copies remain preserved. Neither matching F1 nor package versions establishes byte-identical reconstructed models. The original deployed RF bytes, thresholds and sensing policy were not replaced.

Brier, logloss and ECE for original/sigmoid/isotonic alternatives reproduced within 1e-12. Full block 14/TEST probability normalization, finite/nonnegative outputs and all positive/negative calibration supports were explicitly verified. Calibration fit/evaluation isolation uses the frozen purged tile protocol. Tiles are not independent sessions; no calibrated alert threshold or calibrated UI confidence was deployed. The [new reliability figure](figures/reproduced_reliability.png) comes from actual reproduced values.

| HistoricalTEST probability alternative | Brier | Log loss | Top-label ECE |
| --- | ---: | ---: | ---: |
| Original |.079293|.151089|.023762|
| Sigmoid |.051306|.089088|.014281|
| Isotonic |.053112|.092305|.011333|

Sigmoid selection remains based on block 14 cross-fitted logloss, before retrospectiveTEST reporting. Dummy calculations were independently rerun. No new TEST-guided winner was selected.

Uncertainty sensitivity uses 1000 draws of 12 preserved TRAIN grouped-OOF block confusions, seed 42. It does not refit models per bootstrap draw or estimate deployedTEST confidence intervals.

| Resampling metric convention | Draws |95% percentile range |
| --- | ---: | --- |
| Fixed five; absent support assigned zero explicitly | 1000 | 0.373881-0.721550 |
| Supported true classes only; class set varies | 1000 | 0.497714-0.921864 |
| Conditional all five true supports | 671 | 0.495205-0.623462 |

TRAIN class 1 exists only in block 12. Grouped folds withholding it cannot learn it; fixed-five and supported-class metrics must not be conflated. The wide sensitivity ranges and limited groups preclude established population coverage. External-site and timestamped evidence requires additional data, not another resampling label.

## Defensible empirical demonstration

The frozen generator sampled ten complete TRAIN observations/class for five seeds, then applied shared small lognormal voltage/current gains. Channel-pair ratios remain preserved; complete photovoltaic dynamics are not simulated. All250 generated cases were evaluated once with no prediction-based rejection.249 agreed with source-conditioning labels: seed 42=.98, seeds43-46=1.00. This is a balanced50/class TRAIN-derived demonstration whose parents were used in model fitting, not independent accuracy or validated fault simulation. Original illustrative presets remain unchanged and all predictshade. Historical examples remain a separate mode. [Demonstration command](../defense/Professor_Quick_Start.md) reports conditioning intent and actual output separately.

## Linux and runtime compatibility

Local Docker/WSL are unavailable. Actual verification used standard free public-repository Ubuntu GitHub runners, with no paid/large runner, image registry or artifact-storage purchase. The existing3.14.10 image first passed independently. The new Vercel preview selected3.14.2, which old project constraints correctly rejected before startup. Production was preserved during diagnosis.

A separate managed3.14.2 environment verified original SHA and 200 TRAIN probability references before adding that exact patch to the explicit allowlist. Unknown patches remain rejected; original scientific dependency versions are unchanged. The complete runtime closure is now locked in uv.lock and exported with hashes for Docker installation. Both actual Linux patch-version builds passed:

| Python | Image bytes | Startup to health-ready(s) | Nonroot UID |200TRAIN max probability difference |
| --- | ---: | ---: | ---: | ---: |
| 3.14.2 | 157460438 | 3.049 | 1000 | 3.33e-16 |
| 3.14.10 | 157909223 | 4.654 | 1000 | 2.22e-16 |

[Actual matrix run](https://github.com/Ruganji-Prince/AISD-Assignment2-PV-Anomaly-Detection/actions/runs/45355531883) also verifies read-only root operation, five-case containerCLI/API/Vercel parity, trusted model loading and invalid/duplicate/oversized input rejection. Container image size includes Python/dependencies and is not the 10MiB model-artifact target.

## Profiling and operational safeguards

Thread-local sequential joblib execution removes per-observation dispatch overhead while leaving the original estimator parameters, trees, preprocessing and argmax unchanged. TRAIN 200 probability/class parity passed within 1e-12. Local50-call original total p95 was43.852ms versus15.901ms sequential, measured separately from the archived36.808295ms result. These new loaded-host measurements do not overwrite historical benchmarks or prove a universal SLA.

The verified preview benchmark has 30 sequential and 12 concurrency-two requests, all 42 successful. One request explicitly reported model-cache initialization. Timing definitions distinguish frame construction, validation, fitted preprocessing, forest execution, initialization and total middleware-to-response-header processing. Server wall-clock time is not billedCPU; full platform bootstrap and response transmission are outside that interval.

| Preview warm measurement | N | Mean ms | SD ms | p50 ms | p95 ms | p99 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Forest only | 29 | 6.079 | 0.641 | 5.989 | 7.341 | 7.883 |
| Preprocessing | 29 | 6.249 | 0.944 | 6.148 | 7.563 | 8.752 |
| Server to response headers | 29 | 14.147 | 1.420 | 14.041 | 16.506 | 18.233 |
| End-to-end warm network | 29 | 381.848 | 10.228 | 379.605 | 400.958 | 409.468 |

Forest-only p95 below10ms does not satisfy the complete-path10ms target. The full server path still exceeds it, and the original model remains 11.665MiB>10MiB. Network location is only the configured Africa/Johannesburg timezone, not independently geolocated egress. Model initialization is observable, but not full confirmed platform cold-start latency. Current [production profile](results/cloud_production_profile.json) is recorded separately after preview acceptance; preview and production measurements are not mixed.

API safeguards add5s body and 15s response deadlines and two active inferences/process, retain the 2KB streamed cap, strict duplicate/unexpected/nonfinite/negative-field handling, generic errors, CSP/no-store headers and hash-before-unpickle. Model-load failures return503 rather than validation422. The capacity slot remains held by the worker until computation finishes after a response timeout; a response timeout does not kill a Python thread. Local capacity protection is not distributed IP/user rate limiting. The provider Hobby option and pricing review are documented without activating a paid/metered firewall configuration. No operational safety or availability certification is claimed.

## Reproducibility, security and mandatory checks

The [new clean-clone receipt](results/clean_clone.json) records an actual isolated install,13-cell preprocessing execution,30 tests, original inference and real localhost API startup. Reexecuted notebook outputs remain in the scratch clone; approved active originals remain byte-identical. Quick verification writes only ignored receipts. Exact expensive reproduction commands distinguish public reconstructions from private recovered originals. The [secret scan](results/security.json) and [locked runtime advisory scan](results/runtime_dependency_audit.json) are bounded checks, not guarantees; actual charges and platform CPU billing remain unavailable. Current Hobby cost scenarios retain explicit assumptions rather than deriving CPU from network latency.

Mandatory checks: public repository/README and live endpoint are verified at publication; source/preprocessing/target leakage checks identify no unaddressed implementation leak; historicalTEST/near-similarity/limited-group caveats remain prominent. Secret values are never logged or committed. Original academic deliverables, raw CSV, model and historical scientific outputs remain preserved.

Engineering gaps now addressed include Docker/Linux execution, public21-model fitting, thread determinism, complete near-neighbor diagnostics, empirical scenario integrity, calibration normalization/reproduction, bounded component/cloud timing, dependency locking, safe deadlines/capacity and a coherent professor-facing defense package. Dataset-limited issues require independent PV sites, verified timestamps, more rare-fault blocks and prospective calibration/evaluation. Operational remaining work includes distributed rate-limit review, monitoring, full cold-start/billedCPU observability and safety/resource qualification.

[Professor quick start](../defense/Professor_Quick_Start.md) | [Defense guide](../defense/Technical_Defense_Guide.md) | [Questions/answers](../defense/Expected_Questions_and_Answers.md) | [Demo checklist](../defense/Live_Demo_Checklist.md) | [Final checklist](../defense/Final_Verification_Checklist.md)

## Actual accepted production benchmark

The promoted existing project passed42/42 benchmark requests, plus five original-case parity and invalid-input checks. Timing samples retain failures rather than silently retrying. One model initialization occurred during the concurrency phase; it is not a full platform cold-start measurement.

| Phase / metric | N | Mean ms | SD ms | p50 ms | p95 ms | p99 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| sequential: All request network | 30 | 440.547 | 216.679 | 360.212 | 638.937 | 1221.762 |
| sequential: Warm forest | 30 | 6.337 | 1.657 | 5.974 | 6.743 | 12.703 |
| sequential: Warm preprocessing | 30 | 5.951 | 4.383 | 5.093 | 5.868 | 22.401 |
| sequential: Warm server | 30 | 14.540 | 6.232 | 13.028 | 16.988 | 38.379 |
| concurrency2: All request network | 12 | 562.453 | 604.429 | 367.907 | 1419.281 | 2261.502 |
| concurrency2: Warm forest | 11 | 7.598 | 1.939 | 6.381 | 10.703 | 11.010 |
| concurrency2: Warm preprocessing | 11 | 5.573 | 0.745 | 5.334 | 6.855 | 7.054 |
| concurrency2: Warm server | 11 | 15.130 | 2.305 | 13.768 | 17.954 | 18.020 |

Observed model-cache initialization: 2079.525ms, corresponding full request network duration 2472.057ms. Initialization excludes module/platform boot and is not billedCPU.

Production measurements are separate from historical/preview measurements. The full server p95 remains above10ms, and concurrency forest p95 can also exceed10ms. The original model-size target remains unmet. No target, model, calibration or output-label policy was weakened.

## Final execution equivalence

After the TRAIN-only backend choice was fixed, complete frozen TRAIN, VALIDATION and TEST probabilities were compared once as a runtime-equivalence check. All1,269,567 argmax predictions matched, with maximum absolute probability difference3.33e-16. No fit, threshold or scientific winner was changed. [Full parity receipt](results/full_runtime_parity.json). The final telemetry snapshot safety adjustment also passed a separate accepted preview and both Linux runtime builds; earlier timing profiles retain their original dated measurements.
