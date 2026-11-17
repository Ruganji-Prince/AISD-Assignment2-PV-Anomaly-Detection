# Acceptance matrix

| Requirement | Evidence | Status | Limitation |
| --- | --- | --- | --- |
| Original-model integrity | model_verification.json, RF provenance, fixed SHA checks | PASS | 24 originals checked locally; only RF E4 published |
| Frozen split / schema | verify_recovery.py; recovered contracts | PASS | Source-position blocks, no timestamps |
| TRAIN-only preprocessing | Median and LR mean/variance checks, fit digests, class weights | PASS | Historical fit provenance supported by metadata/code, not a rerun |
| Validation selection | stage2_selection.json; all 21 reproduced validation scores | PASS | One historical validation block, multiple comparisons |
| TEST predictions | Saved probability comparison <=1e-12 and confusion/F1 reproduction | PASS | Prior TEST exposure; not independent prospective evidence |
| Fixed alert threshold | Freeze receipt before revised TEST access; reproduced block-14 counts | PASS | Threshold rule not retuned; classification differs from alerting |
| Explanations | explanation_robustness_verification.json | PASS | Balanced validation sample, associations not causality; RF SHAP not run |
| Archived dropout | Same receipt, original fixed mask | PASS | Simulated isolated loss, not sustained field outage |
| Noise robustness | Reconstruction provenance retained in archive | PARTIAL | Not included as validated original-model results |
| Resource targets | Original artifact bytes; archived timing protocol | PARTIAL | RF fails latency/size; no candidate passed all criteria |
| Executable inference | Six unit tests and actual CLI sample | PASS | Local research prototype only; strict full E4 input |
| Prior academic deliverables | Baseline hash preservation; preprocessing verifier | PASS | README/verifier intentionally updated for new scope |
| Notebook | Existing execution receipt, cell/output and hash verification | PASS | Preprocessing notebook retained; not executed again during recovery |
| Clean environment | Isolated original pinned packages, version/import checks | PASS | Packages copied from preserved environment; fresh online wheel installation not repeated |
| Repository hygiene | Final tracked manifest, size/secret/path/link checks | PASS | Sole fitted binary is fixed-hash original RF; no private caches |
| Production/cloud deployment | No claim | NOT COMPLETED | External evaluation, target-hardware benchmark and operational safeguards remain |

Recovery does not establish pristine TEST independence or satisfaction of all engineering targets. These limitations are disclosed in the README and model-selection report.
