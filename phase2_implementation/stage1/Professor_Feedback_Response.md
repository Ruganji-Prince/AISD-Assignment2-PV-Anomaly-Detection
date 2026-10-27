# Professor feedback response: Phase 2 Stage 1

Status: bounded F6 validation implementation only. Full sensor ablation, validation-block-14 threshold selection, revised test evaluation, final SHAP and the final report are deferred pending approval.

| Recommendation | Stage 1 response | Implementation/evidence |
| --- | --- | --- |
| Row-count discrepancy | Reproduce threshold and per-class counts; distinguish exact agreement from unverified source filtering | `evidence/row_count_discrepancy.json`; `Row_Count_Discrepancy.md` |
| Class imbalance | Unweighted versus explicit training-balanced LR/RF/LightGBM; one weighting mechanism | `evidence/class_weights.json`; validation table |
| Hardware versus shade | Five nominal classes retained; hardware classes 1/2/3 and shade false alarms reported separately | Evaluation module; per-trial metrics |
| Timestamp limitation | Source positions are metadata only; no timestamps, clock-based windows or index predictors | Contracts; training/prediction guards |
| Boosted trees | LightGBM import/synthetic smoke test before bounded full-data fits; no fallback without approval | Dependency smoke evidence; models module |
| Physical features | Exactly five deterministic target-free derivatives; explicit parent-channel ledger | `Feature_Dependencies.json`; feature transformer |
| Diagnostics | Seeded plotting functions prepared; no final figure set generated | Diagnostics module |
| Sensor ablation | F6 only in Stage 1; original seven configurations remain unchanged in Phase 1 | Experiment configuration; Stage 1 verifier |
| Explainability | Native, raw-channel permutation with derivative regeneration, and lazy Tree SHAP support | Explainability module; expensive analysis deferred |

## Prior test exposure

The preserved earlier local Phase 2 experiment evaluated the approved test population. This test set is not newly unseen. No legacy test metric is used by the revised selection runner. Revised decisions use training and validation block 13 only. The approved split is retained; a new split is not invented to hide exposure. This remains a methodological limitation of later revised test reporting.

## Scientific contracts

The task is observation-level five-class classification, not forecasting. Shade is an environmental condition. All 40 finalized Phase 1 files are hash-protected, including the report, CSV, source material, split manifest, decision records, and original verifier. The engineering acceptance targets are unchanged; Stage 1 validation does not establish final acceptance. No SMOTE, synthetic timestamps, source-index predictors, or test-driven selection is permitted.

The primary experiment retains the frozen full training population, including low-irradiance observations. A training-fitted median contingency, retained-channel availability indicators, LR standardization, tree native scale, physically grounded quality checks, and no automatic statistical capping are preserved. Isolated one-channel unavailability permits the first two source positions; sustained or multichannel loss abstains. This is positional ordered-batch behavior, not a clock-time deployment claim.

The assignment's eight preprocessing diagnostics remain required later. Correlation does not automatically remove physical sensors; PCA does not establish sensor reduction. The final strategy-versus-reality report and notebook are not generated in Stage 1.
