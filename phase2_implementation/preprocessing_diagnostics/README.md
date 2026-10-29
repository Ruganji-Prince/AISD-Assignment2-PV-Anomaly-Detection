# Eight preprocessing diagnostics

These assignment diagnostics use TRAIN only for fitted statistics. The full raw missingness count is an audit fact, not a test-driven preprocessing decision. Models, sensor configurations, thresholds, class weights, test scores and the scientific conclusion remain frozen.

| # | Diagnostic | Population and interpretation |
| --- | --- | --- |
| 1 | [Missingness heatmap](fig1_1_missingness_heatmap.png) | Seed-42 display of 5,000 TRAIN rows; zero conventional missing cells in the released export. Paired zeros remain observations. |
| 2 | [Target distribution](fig1_2_target_distribution.png) | Full TRAIN class counts; severe imbalance motivates class weighting and macro/classwise metrics. |
| 3 | [Raw/reference-cleaned boxplots](fig2_1_outlier_boxplots.png) | Full TRAIN box statistics/fliers. No statistical capping/deletion; one near-zero irradiance correction follows the existing physical-quality rule. |
| 4 | [Correlation heatmap](fig3_1_correlation_matrix.png) | Six raw TRAIN predictors; target excluded. Five pairs satisfy the predeclared warning threshold. |
| 5 | [Collinear-pair scatterplots](fig3_2_collinear_scatterplots.png) | Seed-42 display of 20,000 TRAIN positions; full-TRAIN descriptive OLS lines and correlations. |
| 6 | [Feature-target MI](fig3_3_target_importance.png) | Seed-42 proportional sample of 50,000 TRAIN observations; continuous predictors and nominal target. Irradiance has the largest marginal MI in this diagnostic; this does not determine conditional sensor utility or revise ablation decisions. |
| 7 | [Transformation grid](fig4_1_transformation_grid.png) | TRAIN-fitted Standard/Robust/MinMax alternatives. Scale changes do not Gaussianize distributions; only StandardScaler is selected for LR, and trees retain native scale. |
| 8 | [PCA scree/cumulative variance](fig5_1_pca_scree_plot.png) | Full TRAIN, standardized with TRAIN statistics. Two mathematical components explain about 95.17% variance; all six channels remain needed to calculate them. No sensor reduction is inferred. |

All eight PNGs are 300 DPI with population labels, axes, units where relevant and captions in the [executed preprocessing notebook](../notebooks/Phase2_Preprocessing_Implementation.ipynb). Numeric details, sample definitions and fit provenance are in [Preprocessing_Evidence.json](../compliance/Preprocessing_Evidence.json); dimensions/hashes are in [Diagnostic_Inventory.json](../compliance/Diagnostic_Inventory.json).

These post-experiment compliance diagnostics are descriptive, not causal or post-test selection evidence. They do not replace the frozen physical-channel ablation experiment.
