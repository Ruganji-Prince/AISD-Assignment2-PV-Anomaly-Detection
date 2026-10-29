# Assignment-compliance completion

This directory adds the originally required preprocessing notebook, eight diagnostics and 21-category strategy-versus-reality table. Frozen classification experiments and results are not reopened.

- [Executed preprocessing notebook](../notebooks/Phase2_Preprocessing_Implementation.ipynb).
- [Eight diagnostics](../preprocessing_diagnostics/README.md) and [figure inventory](Diagnostic_Inventory.json).
- [Numeric preprocessing/fit evidence](Preprocessing_Evidence.json), [execution status](Notebook_Execution.json).
- [Strategy-versus-reality table](Strategy_vs_Reality.md) and [CSV](Strategy_vs_Reality.csv).
- [Final report](../reports/Phase2_Final_Report.pdf), with Table 9 on two appendix pages. The original ten pages retain identical text and rendering.

The shared preprocessing factory was extracted from the original Stage 2 constructor without changing quality rules, imputers, scaling, indicators or feature dependencies. Existing estimator parameters and fitted binaries are unchanged. The original RetainedQuality/fit/predict methods retain identical AST fingerprints. Current TRAIN preprocessing outputs match trusted local original preprocessing probes exactly; model caches are optional and not public prerequisites.

MI, Robust/MinMax alternatives and PCA are explicitly later TRAIN-only diagnostics. PCA is not part of any frozen classifier and does not establish physical sensor reduction. Negative Celsius values and suspicious paired zeros are retained. No statistical outlier capping/deletion was added.

[Approved_Science_Protection.json](Approved_Science_Protection.json) preserves original file hashes and report-page text/render fingerprints, with explicit authorized compliance exceptions for documentation, a shared-code extraction and the report appendix. Earlier historical manifests/verifiers remain unchanged for their original scope. The current full-project verifier is `python -B phase2_implementation/verify_submission.py`; it validates these compliance exceptions without weakening the historical scientific records.

The current prospective inclusion manifest is `Publication_File_Hashes.json`. No commit or push is performed by compliance execution or verification. Reproduction details appear in the [guide](../Reproduction_Guide.md).
