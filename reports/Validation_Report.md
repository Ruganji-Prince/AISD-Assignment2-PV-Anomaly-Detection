# Recovery validation report

## Reproduced scientific evidence

- All 24 original fitted model files matched the preserved pre-compliance SHA-256 record. Only original RF E4 (12,232,020 bytes) is included for inference; its SHA-256 is fixed in the CLI and provenance.
- All 21 original Stage-2 validation scores reproduce: macro-F1, weighted F1 and hardware macro recall within 1e-12; macro AP within 1e-7. RF F6 AP has approximately 3.1e-8 rank-tie sensitivity from parallel floating-point summation. No tolerance was loosened for class predictions or F1.
- Original LR F6, RF E4 and LightGBM E4 TEST probabilities agree with preserved per-row NPZ evidence within 1e-12 (maximum observed differences approximately 1.2e-15, 4.4e-16 and zero). Label/source positions match exactly. Confusion matrices and macro-F1 reproduce.
- TRAIN imputer medians, LR means/variances, fit population digests/counts, frozen estimator parameters, seed 42, class weights/order and feature exclusion pass. Fixed block-14 threshold TP/FP/FN counts reproduce; freeze hashes and chronology pass. No fitting or threshold search occurred.
- All archived raw-channel permutation outcomes, native LightGBM SHAP tables/saved contributions and additivity, and three isolated-dropout outcomes reproduce with original fixed validation samples/masks. Results are separate from noise-study reconstructed models.

## Executable checks

```text
python -B -m src.evaluation.verify_recovery --all-originals
python -B -m src.evaluation.verify_explanations
python -B -m unittest discover -s tests -v
python -B -m src.inference.cli --input deployment/example_input.json
python -B phase2_implementation/verify_submission.py
```

The all-originals/explanation commands require the privately preserved model and saved-array caches. The default recovery verifier requires only the public RF artifact. Six inference unit tests pass, including five actual released-data cases predicting classes 0?4, schema rejection, original-pipeline parity, hash rejection and environmental shade handling. CLI sample returns class 0, normal. Eighteen applicable archived semantic tests pass; two historical whole-tree foundation guards are inapplicable to the integrated tree and are replaced by current baseline/recovery hash checks. Details: [semantic receipt](semantic_test_verification.json).

The original pinned Python 3.14.7 environment was copied into a separate recovery environment. Package dependency consistency checks found no conflicts. A second minimal environment containing only the explicitly pinned inference packages passes CLI startup and all six inference tests; required cloudpickle/narwhals runtime imports were discovered and included. No reliance on LightGBM, notebook or plotting packages is needed for RF inference. Packages were copied from the preserved environment; fresh online wheel installation was not repeated.

## Preservation and publication safety

All 79 baseline files remain present. Only README.md and the preprocessing verifier are modified. The Phase 1 PDF, raw CSV, source README/license, Assignment 3 IEEE PDF/TeX/class, executed preprocessing notebook, preprocessing implementation, evidence and eight diagnostics remain byte-identical to the base public tree. The verifier retains all existing scientific checks and adds exact recovery hashes plus one fixed-hash model exception. It excludes ignored private caches/environments from public-file checks.

Original advanced code and compact evidence were copied byte-for-byte from the archived commit. Eleven original diagnostic PNGs absent from the Git tree were recovered from the preserved project and matched against archived inventory hashes. No figures or scientific results were regenerated. Binary/publication size checks, private-path/credential pattern scans and all relative Markdown links pass. The existing raw CSV is retained; it is not a newly uploaded intermediate dataset. No private review directory, original/reconstructed model cache, environment, intermediate prediction array or oversized new artifact is included.

Archived branch, source models, Git bundles and large backup ZIPs are preserved. Backup ZIPs/bundles did not require hydration because the archived Git commit and required individual originals were available. Git object integrity checks pass. [Exact changed-file manifest](Changed_File_Manifest.md).

## Limitations

Prior TEST inspection remains a scientific limitation, not something recovery can remove. No candidate met all predeclared engineering criteria. Resource timings are original archived measurements, not fresh latency benchmarks. Optional reconstructed noise-study results are not published as original-model verification. The retained executed preprocessing notebook was checked by hash/outputs and existing verifier, not rerun. No prospective external validation, calibrated probability reliability, cloud or production deployment has been completed.
