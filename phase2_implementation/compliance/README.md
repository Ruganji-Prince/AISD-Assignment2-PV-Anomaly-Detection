# Preprocessing evidence

[Reference statistics](Preprocessing_Reference.json) retain existing audited preprocessing values. [Executed preprocessing evidence](Preprocessing_Evidence.json) records the current standalone run. [Strategy versus reality](Strategy_vs_Reality.md) covers current-stage decisions only. [Diagnostic inventory](Diagnostic_Inventory.json) identifies the eight retained images. Historical Phase 1 scientific evidence is unchanged.

## Empirical justification

- [Measured per-stage dimensions](Pipeline_Stage_Dimensions.csv): all three preprocessing policies and ordered partitions; physical inputs remain distinct from mathematical columns.
- [TRAIN distributions and outlier screens](Training_Distribution_Diagnostics.csv): quartiles, fences, counts/percentages, skewness and explicitly defined excess kurtosis.
- [TRAIN scaling behavior](Scaling_Diagnostics.csv): raw/standard/robust/minmax descriptive summaries.
- [TRAIN PCA eigenvalues and variance](PCA_Diagnostics.csv): individual/cumulative variance and diagnostic dimensions.
- [Empirical audit](Empirical_Audit.json): independent VIF verification, leakage guard, fit population and policy scope.

Zero conventional missingness makes Little's MCAR test and missing-indicator association testing not applicable. No mechanism or p-value is invented. The empirical reflection is included in the [IEEE report](../reports/Assignment3_Phase2.pdf).
