# Finalized Phase 1 rubric and scope checklist

Official report: [Phase1_Strategy_Report.pdf](Phase1_Strategy_Report.pdf). This is a criterion-based local evidence check, not a predicted grade. Remote publication/Canvas submission remains pending.

| Category | Points | Local coverage | Official report references / evidence |
| --- | --- | --- | --- |
| GitHub architecture/documentation | 15 | Required local structure, protected ignore rules, pinned dependencies, complete Phase 1 README with explicit Task Type: Multiclass Classification | XXI; root README; source/future-folder placeholders. Live Phase 1 repository is pending approval. |
| Data audit/metadata inventory | 20 | N=1,373,798; P=7; six continuous predictors and nominal f_nv; every column zero conventional missing; overall 0%; all rows complete; exact five-class distribution | IV?VI; Variable_Inventory.csv; Class_Distribution.csv; primary_audit.json |
| Cleaning/imputation/outlier strategy | 20 | Unidentifiable MCAR/MAR/MNAR with zero NaNs; 62 paired-zero suspicions retained; tiny negative irradiance convention; valid negative temperatures; training-median contingency and alternatives; IQR/Z rules; no automatic fault-value capping/deletion | VI?IX; Training_Distributions.csv; decisions D04?D07 |
| Statistics/encoding/scaling | 25 | Explicit matching matrix; MI/OVR plan; Pearson/Spearman; absolute r>=0.85 and VIF>10; physical-channel retention; no categorical X encoding; nominal Y; StandardScaler LR/native RF; optional transforms and training-only PCA, not physical sensor removal | X?XIV; primary_audit.json; Training_Correlation.csv; decisions D08?D11 |
| Split/leakage architecture | 20 | Sixteen signal-defined blocks; ordered 12/2/2; N=1,006,129/116,977/146,461; 104,231 separators; absent clocks/no verified days; validation 13 settings/14 threshold; training-only fitted stages; excluded target/index/future information | XV?XVII; Phase1_Split_Manifest.json; decisions D12?D13 |

All raw class counts are verified: normal 1,162,931; short circuit 5,999; degradation 10,371; open circuit 6,024; shade 188,473. No categorical predictor, timestamp, ordinal or text fields are invented.

Phase 1 describes planned evaluation, not final scores, latency/size measurements, fitted PCA outcomes or sensor-ablation conclusions. The required future directories contain structural placeholders only. The rationale is truncated before its execution appendix.

The official PDF is preserved byte-for-byte. Equation 42 on page 7 has an existing right-edge overflow; it is not corrected here. The complete planned information-flow chain is written in README and the surrounding report text explains the training-only restrictions.

No false geographic transfer, proven missingness mechanism or causality claim is added. Large raw CSV inclusion is intentional and source-licensed; environments, model artifacts, processed arrays and credentials are excluded.
