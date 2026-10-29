"""Evidence-grounded Phase 1 plan versus Phase 2/compliance implementation."""
import csv,html
from .common import *
ROWS=[
 ('Missing-value strategy','TRAIN-median contingency plus availability indicators','Same median/indicator preprocessing; exported NaNs remain zero','IMPLEMENTED AS PLANNED','No missingness mechanism inferred from zero NaNs','final_model_specifications.json medians; Preprocessing_Evidence.json'),
 ('Paired-zero handling','Annotate suspicious simultaneous irr/pvt zeros','All 62 paired-zero observations retained as observations','IMPLEMENTED AS PLANNED','Not relabeled as confirmed missing values','Phase1 primary_audit.json; compliance raw audit'),
 ('Negative irradiance','Near-zero convention, with physical caution','Existing quality rule clamps -1 <= irr < 0; no new rule','IMPLEMENTED AS PLANNED','One released slightly negative observation; convention unchanged','src/phase2_stage2/models.py RetainedQuality'),
 ('Negative temperature','Retain physically valid negative Celsius values','Negative Celsius values remain unchanged','IMPLEMENTED AS PLANNED','No automatic zero-floor on module temperature','RetainedQuality; compliance cleaning comparison'),
 ('Outlier policy','Screen IQR/Z values; retain plausible fault observations','No statistical capping or row deletion; raw/reference boxplots','IMPLEMENTED AS PLANNED','Similar before/after plots reflect intentional retention','Training_Distributions.csv; diagnostic 3'),
 ('Target encoding','Treat f_nv codes as five nominal labels','Nominal 0–4 labels retained; no categorical predictors encoded','IMPLEMENTED AS PLANNED','No artificial ordinal or continuous target interpretation','Variable_Inventory.csv; report Table 1'),
 ('LR scaling','TRAIN-fitted StandardScaler for regularized LR','Six numerical channels standardized; indicators unchanged','IMPLEMENTED AS PLANNED','Frozen LR preprocessing reused without fitting a classifier','final_model_specifications.json; shared factory'),
 ('RF scaling','Retain native numerical scale for trees','E4 electrical values plus availability indicators, no scaler','IMPLEMENTED AS PLANNED','No normalization forced on RF','final_model_specifications.json; shared factory'),
 ('LightGBM preprocessing','Physically justified extension to initial LR/RF suite','Median + approved derivatives + indicators; native scale','REFINED','Boosted-tree extension approved after professor feedback','Professor_Feedback_Response.md; frozen specification'),
 ('Class imbalance','Compare weighted/unweighted variants; weights from TRAIN','Frozen balanced winners use N_train/(5*n_k)','IMPLEMENTED AS PLANNED','Validation/test distributions not rebalanced','class_weights.json; validation_comparison.csv'),
 ('SMOTE decision','Avoid initial row-level synthetic oversampling','No SMOTE or random oversampling in primary experiment','NOT REQUIRED','Dependent readings do not create independent fault episodes','Phase1 report p.3; Stage1 experiment configuration'),
 ('Split strategy','Ordered 12/2/2 signal-block allocation with buffers','Same TRAIN/VALIDATION/TEST bounds; 104231 separator rows','IMPLEMENTED AS PLANNED','Source-position order; no verified day/session claim','Phase1_Split_Manifest.json; compliance split checks'),
 ('Leakage prevention','Fit learned preprocessing only on TRAIN','Medians/scalers fit on TRAIN; held-out arrays only transformed','IMPLEMENTED AS PLANNED','New diagnostic scalers/PCA also train-only','Preprocessing_Evidence.json fit ledger; semantic tests'),
 ('Correlation analysis','TRAIN Pearson screen |r| >= .85; no automatic deletion','Same six-predictor matrix and five flagged pairs; new plots','IMPLEMENTED AS PLANNED','Correlation is not proof of physical redundancy','Training_Correlation.csv; diagnostics 4–5'),
 ('VIF','TRAIN VIF >10 warning; justify physical retention','Phase1 VIF audit retained: five warnings, not automatic drops','IMPLEMENTED AS PLANNED','No new VIF-based sensor selection after final evaluation','primary_audit.json training_vif; Phase1 report'),
 ('Mutual information','TRAIN nonlinear association for nominal f_nv','k=3 MI on seeded proportional TRAIN sample N=50000','REFINED','Completed as compliance diagnostic after frozen experiments; no reselection','Preprocessing_Evidence.json; diagnostic 6'),
 ('PCA','Exploratory TRAIN-scaled PCA; preserve sensor interpretation','TRAIN StandardScaler + full-SVD PCA; 90%/95% thresholds','REFINED','Completed for compliance; not deployed or equated to sensor reduction','Preprocessing_Evidence.json; diagnostic 8'),
 ('Physical feature engineering','Domain-grounded derivatives with parent-channel constraints','Only P1/P2/P_total/V_diff/I_diff where parents retained','REFINED','Bounded LightGBM branch; RMS products remain proxies','Feature_Dependencies.json; features.py'),
 ('Sensor ablation','Compare F6/E5/E4/C3/C2/S4/S2 on identical partitions','21 fixed-setting runs; three candidates frozen before TEST','IMPLEMENTED AS PLANNED','Minimum qualifying tested set is not a global optimum','sensor_ablation_validation.csv; stage3_protocol.json'),
 ('Explainability','Lightweight model/feature importance with physical caution','Native importance, raw-channel permutation and Tree SHAP','REFINED','Balanced validation sample; no causal physical claims','explainability_metadata.json; physical permutation CSV'),
 ('Computational evaluation','Compare latency/footprint with predictive and sensing budgets','Corrected 100 warmups/2000 single-row calls; full pickle size','REFINED','Protocol correction preserved; no architecture change to force a pass','resource_benchmark_correction.json; portable resource view')
]
HEADERS=['Category','Phase 1 planned decision','Actual implementation','Status','Deviation / finding','Rationale / evidence']
def main():
 OUT.mkdir(exist_ok=True,parents=True)
 with (OUT/'Strategy_vs_Reality.csv').open('w',encoding='utf8',newline='') as f:
  w=csv.writer(f);w.writerow(HEADERS);w.writerows(ROWS)
 text='# Strategy versus reality\n\nThe table distinguishes the frozen modelling experiment from subsequently completed assignment diagnostics. Mutual information, PCA and additional scaling views were completed for compliance only; none changed model, sensor or threshold decisions.\n\n'
 text+='| '+' | '.join(HEADERS)+' |\n| '+' | '.join(['---']*6)+' |\n'
 text+=''.join('| '+' | '.join(x.replace('|',r'\|').replace('\n',' ') for x in row)+' |\n' for row in ROWS)
 text+='\nEvidence filenames refer to the established Phase 1/Phase 2 evidence tree. Original scientific records and the Phase 1 report remain unchanged. New compliance diagnostic results are explicitly labeled.\n'
 (OUT/'Strategy_vs_Reality.md').write_text(text,encoding='utf8');print('Strategy-versus-reality table:',len(ROWS),'required categories.')
if __name__=='__main__':main()
