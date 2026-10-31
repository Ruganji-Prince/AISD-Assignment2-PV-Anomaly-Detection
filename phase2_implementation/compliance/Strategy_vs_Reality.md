# Preprocessing strategy versus reality

No downstream predictive result is used. Retained strategies are explicitly identified; descriptive implementation additions do not imply model or sensor selection.

| Preprocessing step | Phase 1 planned strategy | Phase 2 actual execution / change | Empirical justification / metric / figure |
| --- | --- | --- | --- |
| Missingness / imputation | TRAIN-median contingency and availability indicators | Retained; no exported gaps to fill | 0/9,616,586 missing cells (0%); Fig. 1; Table I |
| Suspicious paired zeros | Annotate, without assuming a missing sentinel | Retained as observations, not relabeled missing | 62 paired irr/pvt zeros; runs 1/32/29; Fig. 1 |
| Negative irradiance | Near-zero physical convention with caution | Retained: -1 <= irr < 0 becomes zero in processed data | One value -0.0381 W/m²; no raw CSV change; Fig. 3 |
| Negative temperature | Retain physically valid negative Celsius | Retained; no automatic zero-floor | 24,172 released negative-Celsius rows; TRAIN min -1.6543 °C; Fig. 3 |
| Outlier policy | IQR / distribution-qualified Z screening; no automatic capping | Retained; no winsorization or row deletion | All six TRAIN IQR counts=0 (0%); skew 0.0683–1.1450; Table II; Fig. 3 |
| Target / imbalance | Nominal f_nv; no categorical predictor encoding or initial SMOTE | Retained observed labels and natural partition prevalence | TRAIN counts 844805/1226/5695/1204/153199; normal 83.966%; Fig. 2 |
| Predictor correlation | TRAIN Pearson \|r\| >= 0.85; assess physical meaning before deletion | Retained screen; no automatic predictor removal | Five flagged pairs, r=0.8623–0.9891; Figs. 4–5; Table III |
| VIF / retention | TRAIN VIF >10 warning; preserve reference physical inputs | Retained; all six reference channels remain | Five VIF>10; maximum 56.3457; Table IV; Figs. 4–5 |
| Target relevance | TRAIN-only MI for continuous predictors / nominal target | Implemented descriptive proportional-sample MI; no feature deletion | N=50,000, k=3, seed=42; MI 0.1124–0.3006 nats; Fig. 6; Table IV |
| Standardization | TRAIN-fitted standardization for scale-sensitive representations | Retained six-channel standardized reference; flags unscaled | Max absolute TRAIN scaled mean 2.02e-16; each population std=1; Fig. 7; Table V |
| Scaling alternatives | Robust/MinMax sensitivity; optional justified log transform | Robust/MinMax diagnostic only; no log transform selected | irr robust median=0, IQR=1; MinMax TRAIN range=[0,1]; skew stays 0.8745; Fig. 7 |
| Exploratory PCA | TRAIN-standardized variance/loadings; not physical sensor reduction | Implemented six-component diagnostic; reference pipeline not reduced | PC1=82.5301%; first two=95.1677%; 90%/95% need two; Fig. 8; Table VI |
| Ordered split | 12/2/2 signal-block split and withheld separators | Retained exact bounds; no random row split or fabricated time | N=1006129/116977/146461; 104231 separators; Table VII |
| Leakage controls | Fit learned quantities on TRAIN; transform held-out only | Retained; guarded entry point rejects held-out fit before factory call | All fit-ledger N=1006129; TRAIN digest verified; Table VIII |
| Physical features | Domain-grounded features with retained-parent constraints | Existing optional electrical-derived representation retained; not a sensor-selection outcome | 4 raw + 5 derived + 4 flags=13 columns; all parents retained; Table VII |
| Output dimensions | Track retained observations and physical/mathematical inputs | Measured every quality, median, flag, feature and scaling stage | Primary: N×6 -> N×12; alternatives N×8 / N×13; Table VII |
| Population discrepancy | Verify source/count mismatch without forcing agreement | Retained full raw population; descriptive irradiance-qualified audit | irr >=100 gives N=515958 and literature counts exactly; source does not specify exact filter; Table I |
