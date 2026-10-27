"""Build the Phase 2 report from frozen evidence; never execute experiments."""
import html,json,re,os
import numpy as np
import pandas as pd
import pymupdf as pdf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import *
E3='phase2_implementation/stage3/evidence/'
E2='phase2_implementation/stage2/evidence/'
KEYS=['LR__F6','RF__E4','LightGBM__E4']
C=pd.read_csv(ROOT/(E3+'final_candidate_comparison.csv')).set_index('candidate')
V=pd.read_csv(ROOT/(E2+'sensor_ablation_validation.csv')).set_index('key')
T=load(E3+'stage3_threshold_selection.json')['results']
D=load(E3+'final_test_details.json')['results']
CLAIMS=[];FIGURES=[];TABLES=[]
def c(key,field,digits=4,percent=False):
 value=float(C.loc[key,field]);s=f'{value*(100 if percent else 1):.{digits}f}'
 CLAIMS.append({'source':E3+'final_candidate_comparison.csv','row_key':key,'field':field,'raw':value,'multiplier':100 if percent else 1,'digits':digits,'rendered':s});return s
def v(key,field='macro_f1',digits=4):
 value=float(V.loc[key,field]);s=f'{value:.{digits}f}'
 CLAIMS.append({'source':E2+'sensor_ablation_validation.csv','row_key':key,'field':field,'raw':value,'multiplier':1,'digits':digits,'rendered':s});return s
def t(key,field,digits=4,percent=False):
 value=float(T[key][field]);s=f'{value*(100 if percent else 1):.{digits}f}'
 CLAIMS.append({'source':E3+'stage3_threshold_selection.json','json_path':['results',key,field],'raw':value,'multiplier':100 if percent else 1,'digits':digits,'rendered':s});return s
def h(s):return ('h',s)
def p(s):return ('p',s)
def table(n,title,headers,rows,note=''):
 TABLES.append({'number':n,'title':title,'headers':headers,'rows':rows,'note':note});return ('table',TABLES[-1])
def fig(n,path,caption,height):
 FIGURES.append({'number':n,'source':path,'caption':caption,'sha256':sha(ROOT/path)});return ('figure',FIGURES[-1],height)
def scientific_figures():
 path=OUT/'figures/final_candidate_confusion_matrices.png';f,axes=plt.subplots(3,2,figsize=(7.3,8.4));labels=['Normal','Short circuit','Degradation','Open circuit','Shade']
 for row,key in enumerate(KEYS):
  for col,field in enumerate(['confusion_matrix','row_normalized_confusion_matrix']):
   a=np.array(D[key][field]);ax=axes[row,col];ax.imshow(a,cmap='Blues',vmin=0,vmax=a.max() if col==0 else 1,aspect='auto')
   ax.set_xticks(range(6),labels+['Abstain'],rotation=38,ha='right',fontsize=7);ax.set_yticks(range(5),labels,fontsize=7);ax.set_title(key.replace('__',' ')+' — '+('counts' if col==0 else 'row fraction'),fontsize=9)
   for i in range(5):
    for j in range(6):ax.text(j,i,str(int(a[i,j])) if col==0 else f'{a[i,j]:.3f}',ha='center',va='center',fontsize=6.8,color='white' if a[i,j]>(a.max()*.6 if col==0 else .6) else 'black')
   ax.set_xlabel('Predicted state',fontsize=8);ax.set_ylabel('True state',fontsize=8)
 f.suptitle('TEST — frozen five-class candidates; all 146,461 observations',fontsize=10);f.tight_layout(rect=(0,0,1,.97));f.savefig(path,dpi=300);plt.close(f)
def contents():
 F='phase2_implementation/stage4/figures/';pages=[]
 pages.append([
 ('title','Resource-Efficient and Explainable AI for Photovoltaic Anomaly Detection Under Sparse Sensing Constraints'),
 ('subtitle','Phase 2: Experimental Evaluation and Engineering Trade-offs'),
 ('byline','Ruganji Prince · Carnegie Mellon University Africa<br>04-652 Artificial Intelligence System Design · Assignment 2 · October 2026'),
 h('Abstract'),
 p(f'This study evaluates whether photovoltaic operating-state classification can retain useful fault sensitivity with fewer physical measurement channels and limited computational resources. Training-only preprocessing, bounded model selection and seven predeclared sensor configurations compare Logistic Regression (LR), Random Forest (RF) and LightGBM. The frozen RF E4 candidate achieves test macro-F1 {c("RF__E4","test_macro_f1")} from four electrical channels, with each hardware-state recall above 0.99, but exceeds latency and artifact-size limits. LightGBM E4 meets both resource limits but achieves short-circuit classification recall {c("LightGBM__E4","test_R1")}, despite aggregate hardware-alert recall {c("LightGBM__E4","test_alert_recall")}. No evaluated configuration satisfied all predeclared engineering criteria. The results identify a measured sensing–prediction–computation trade-off. Prior test exposure and absent explicit timestamps limit interpretation.'),
 h('1. Introduction and Phase 2 objective'),
 p('The engineering objective is to identify a practically useful sensing and computational configuration for PV anomaly detection rather than maximize one aggregate score. Reliable electricity and affordable monitoring motivate the application in relation to SDG 7 [1]. Evidence derives from one controlled Brazilian PV installation [2,3]; Rwanda or other field generalization is not established. The task is observation-level multiclass classification, not forecasting or detection-delay estimation.'),
 h('2. Phase 1 decisions carried forward'),
 p('The approved Phase 1 PDF, raw export, labels, buffered split, seven sensor sets and engineering thresholds remain unchanged. Training-fitted median contingency imputation and retained-channel availability indicators are used; LR receives StandardScaler and trees retain native scale. Statistical outliers are retained. The 62 paired irradiance/temperature zeros remain suspicious observations rather than confirmed missing values. Slightly negative irradiance is clamped under the predeclared near-zero convention; negative Celsius values remain valid. Neither source index nor block identity is a predictor.'),
 h('3. Professor feedback and Phase 2 extensions'),
 p('The implementation addresses the row-count discrepancy, class imbalance, hardware-fault versus environmental-shade distinction and timestamp limitations. A bounded LightGBM comparison extends the linear/tree references. Explicit physical-feature dependencies, fixed-setting sensor ablation, alert thresholds, single-observation resource measurements and validation explanations support the sensing/resource question. All outcomes derive from approved frozen evidence without post-test tuning.')])
 pages.append([
 h('4. Dataset and row-count investigation'),
 table(1,'Dataset and task summary',['Property','Frozen definition'],[
 ['Source','Original-author PV Fault Dataset [2,3]; pinned commit e9ed8ad8072dcb3ffc643b0f3604219798708551'],
 ['Dimensions','N = 1,373,798 source positions; P = 7 variables (6 predictors + 1 target)'],
 ['Predictors','vdc1, vdc2 (DC RMS voltage, V); idc1, idc2 (DC RMS current, A); irr (plane-of-array irradiance, W/m²); pvt (module temperature, °C)'],
 ['Target','f_nv: five nominal labels; integer codes are neither ordinal nor continuous'],
 ['Class counts (0–4)','1,162,931; 5,999; 10,371; 6,024; 188,473'],
 ['States','0 normal; 1 short circuit; 2 resistive degradation; 3 open circuit; 4 natural building shade'],
 ['Missingness','0 conventional missing cells; 62 paired irr = 0 / pvt = 0 observations retained'],
 ['Time metadata','No explicit timestamp; source order preserved']]),
 p('The complete released arrays/export contain 1,373,798 positions, whereas the paper-reported class counts total 515,958. The irr ≥ 100 W/m² subset contains exactly 515,958 positions and reproduces every paper-reported count: 309,253 normal; 5,999 short circuit; 10,371 degradation; 6,024 open circuit; 184,311 shade. Exact numerical agreement is verified. An irradiance-qualified published population is plausible, but the inspected source does not explicitly establish use of that filtering operation. The primary experiment retains the approved full population; low irradiance is not automatically interpreted as nighttime.'),
 p('The study describes nominal 1 Hz acquisition, per-second electrical RMS calculations, one-second irradiance/temperature averages and a 16-day experiment [2]. No timestamp variable exists in the released MAT/CSV data. Absolute timestamps and uninterrupted one-second spacing throughout the export cannot be verified; no synthetic timestamps are assigned.'),
 h('5. Experimental methodology'),h('5.1 Leakage-safe ordered split'),
 p('Sixteen signal-defined blocks use irr &lt; 100 W/m² for at least 3,600 consecutive source positions. Blocks are not verified days, sessions or hours. Adjacent-position dependence motivates ordered buffered splitting instead of naive random rows. TRAIN: blocks 1–12, [0,1006129), N = 1,006,129. VALIDATION: [1056990,1173967), N = 116,977; block 13, [1056990,1089790), N = 32,800, selects model settings; block 14, [1140571,1173967), N = 33,396, selects alert thresholds. TEST: blocks 15–16, [1227337,1373798), N = 146,461. Two separator regions exclude 104,231 positions. Validation separator positions outside the designated selection blocks are not additional selection data.'),
 h('5.2 Physical feature engineering'),
 p('LightGBM uses P1 = vdc1 × idc1; P2 = vdc2 × idc2; P_total = P1 + P2; V_diff = |vdc1 − vdc2|; I_diff = |idc1 − idc2|. A feature requires every parent channel. P1/P2 are RMS-product proxies, not independently measured power sensors. Derivatives do not reduce physical sensing requirements. LR/RF use retained raw channels plus availability indicators. No additional ratios are introduced.')])
 pages.append([
 h('5.3 Training-only imbalance handling and preprocessing'),
 p('Normal comprises approximately 84.65% of the full export; hardware states are rare. Weights follow w_k = N_train / (K × n_k), K = 5, from TRAIN only. Training class counts are 844,805; 1,226; 5,695; 1,204; 153,199. Corresponding weights are 0.238192; 164.131974; 35.333766; 167.131063; 1.313493. One explicit class-weight mechanism is used. No SMOTE or synthetic oversampling is applied; validation/test distributions are not rebalanced.'),
 p('Pipeline-owned medians and LR scaling are fitted only on TRAIN. Isolated one-channel unavailability permits imputation for the first two consecutive source positions; sustained or multichannel loss abstains. Runs reset across source gaps/block boundaries and separate batches. Removed channels are never reconstructed. Correlation/VIF warnings motivate regularization and physical ablation rather than automatic sensor deletion. No statistical winsorization, log transform or PCA is added to the frozen primary pipelines. PCA would reduce mathematical dimension, not physical sensor requirements.'),
 h('5.4 Models and bounded selection'),
 p('Sixteen F6 trials compare weighted/unweighted LR (C = 0.1 or 1.0), RF (depth 6 or 10), and LightGBM (15 leaves/depth 4 or 31 leaves/depth 6; raw/engineered features). Block-13 selection freezes balanced LR C = 1.0 (lbfgs, max_iter = 2,000); balanced RF depth 10 (100 trees, min_samples_leaf = 20); and balanced engineered LightGBM (31 leaves, depth 6, 150 estimators, learning_rate = 0.05, min_child_samples = 50, max_bin = 127, reg_lambda = 1). Seed 42 and two-thread settings where applicable remain fixed. Sparse configurations receive no independent hyperparameter search. Complete parameters remain in machine-readable evidence.'),
 h('5.5 Predeclared sensor configurations'),
 table(2,'Physical channels retained',['Set','Channels','Count'],[
 ['F6','vdc1, vdc2, idc1, idc2, irr, pvt','6'],['E5','vdc1, vdc2, idc1, idc2, irr','5'],['E4','vdc1, vdc2, idc1, idc2','4'],['C3','idc1, idc2, irr','3'],['C2','idc1, idc2','2'],['S4','vdc1, idc1, irr, pvt','4'],['S2','vdc1, idc1','2']], 'Channel counts differ from mathematical feature counts and physical device counts.'),
 h('5.6 Evaluation metrics'),
 p('Macro-F1 is primary; weighted-F1 and classwise precision/recall/F1 and one-vs-rest average precision (AP) are complementary. Macro AP is the unweighted mean of five AP values, not trapezoidal PR integration. Hardware macro recall is (R1 + R2 + R3)/3. Hardware H = {1,2,3}; natural building shade is not hardware failure. Abstentions count as misses in all-row recall. Hardware-to-normal/shade confusions are explicit. Accuracy is not the selection objective.'),
 h('5.7 Predeclared engineering criteria'),
 p('Aspirations are macro-F1 ≥ 0.80; each hardware-class recall ≥ 0.90; same-family sparse Δ_s ≤ 0.05; at most four channels for sparse candidates; combined normal/shade alert FPR ≤ 1%; single-observation p95 ≤ 10 ms; complete artifact ≤ 10 MiB; isolated 1% dropout macro-F1 loss ≤ 0.05. These are project aspirations, not safety or certification thresholds.')])
 pages.append([
 h('6. Validation and sensor ablation'),
 p('Each frozen family is trained on the same TRAIN population for all seven sets and evaluated on VALIDATION block 13. The 21 fits preserve settings and weights. Table 3 and Fig. 1 report validation macro-F1; no test score enters this comparison.'),
 table(3,'VALIDATION block-13 macro-F1 with fixed family settings',['Set','Channels','LR','RF','LightGBM'],[[cfg,str(n),v('LR__'+cfg),v('RF__'+cfg),v('LightGBM__'+cfg)] for cfg,n in [('F6',6),('E5',5),('E4',4),('C3',3),('C2',2),('S4',4),('S2',2)]]),
 fig(1,F+'validation_sensor_ablation.png','VALIDATION block 13: fixed-setting sensor-ablation macro-F1. The horizontal line denotes the 0.80 aspiration.',175),
 p('RF E4 retains strong predictive performance and is the only configuration satisfying all four validation predictive/channel conditions: macro-F1, individual hardware recalls, family-specific degradation and at most four channels. Reductions below E4 generally cause substantial degradation. Removing voltage channels is particularly damaging in tested C2/C3 configurations. Environmental-channel removal does not universally reduce shade classification. These comparisons do not establish causal redundancy. Sparse engineered models do not isolate an engineering effect against matched raw-feature controls.'),
 h('7. Frozen final candidates'),
 p('LR F6 is the full-sensing lightweight reference. RF E4 is the sparse predictive-performance candidate and the minimum-channel qualifying candidate among the seven predeclared sensor configurations tested, based on the four validation predictive/channel conditions. This does not establish global minimum sensing or final engineering acceptance. LightGBM E4 remains the sparse resource-efficient candidate despite weak validation short-circuit classification. Candidates and settings were frozen before block-14 threshold selection and final TEST. No universal best model is asserted.')])
 pages.append([
 h('8. Final test results'),
 p('Frozen candidates are evaluated on unchanged TEST without irradiance filtering or rebalancing. This partition had been evaluated in a legacy implementation and is not pristine or previously unseen. Revised model/sensor/feature decisions use training/validation evidence; no legacy test outcomes are loaded for revised selection. Earlier human exposure remains a limitation (Section 13).'),
 table(4,'TEST classification of frozen candidates',['Metric','LR F6','RF E4','LightGBM E4'],[[label]+[c(k,field) for k in KEYS] for label,field in [('Macro-F1','test_macro_f1'),('Weighted-F1','test_weighted_f1'),('Macro AP','test_macro_AP'),('Short-circuit recall R1','test_R1'),('Degradation recall R2','test_R2'),('Open-circuit recall R3','test_R3'),('Hardware macro recall','test_hardware_macro_recall')]]+[['Same-family TEST Δ_s','N/A',c('RF__E4','same_family_test_delta_s',6),c('LightGBM__E4','same_family_test_delta_s',6)]], 'Sparse degradation uses frozen RF F6 / LightGBM F6 TEST references, never LR F6. Negative values are preserved.'),
 fig(2,F+'test_per_class_metrics.png','TEST: per-class precision, recall and F1. Shade remains an environmental operating state.',190),
 p('RF E4 achieves the strongest macro-F1 among the frozen candidates and hardware macro recall 0.9968, but resource compliance is separate. LightGBM E4 has high weighted-F1 and macro AP while short-circuit recall remains low. Aggregate scores do not supersede the individual-class requirement. Shade recall is 0.7505 for LR F6, 0.9911 for RF E4 and 0.9937 for LightGBM E4.'),
 p('Detailed evidence contains all class metrics/supports. Confusions (Fig. 3) include 357 LR open-circuit observations assigned to short circuit, rather than normal or shade. RF assigns six degradation observations to normal and one short-circuit observation to shade. LightGBM assigns 729 short-circuit observations to shade and 453 to degradation; five degradation observations are assigned to shade. No model or threshold change follows these findings.')])
 pages.append([
 h('8.1 Final test confusion diagnostics'),
 fig(3,'phase2_implementation/stage4/figures/final_candidate_confusion_matrices.png','TEST: counts and row-normalized confusions. Rows are true labels; columns are predictions, including abstention. Supports remain unchanged. Layout derives directly from frozen JSON; predictions are not regenerated.',595),
 p('All candidates have complete reference-test coverage. Aggregate hardware alerting remains separate from five-class diagnosis.')])
 pages.append([
 h('9. Hardware-alert evaluation'),
 p('Hardware score s_H = p(class 1) + p(class 2) + p(class 3) alerts when s_H ≥ τ. VALIDATION block 14 alone selects τ to maximize alert recall subject to combined FPR ≤ 1% among Y ∈ {0,4}; equal-recall points prefer lower combined FPR, then higher τ. Distinct tied-score points and a no-alert sentinel are enumerated. Thresholds, model hashes and a freeze receipt precede revised test access. No threshold is adjusted after TEST.'),
 table(5,'VALIDATION block-14 threshold selection',['Candidate','Frozen τ','Recall','Precision','Combined FPR'],[[k.replace('__',' '),t(k,'threshold',8),t(k,'recall'),t(k,'precision'),t(k,'combined_nonhardware_FPR',4,True)+'%'] for k in KEYS], 'Exact thresholds remain in JSON. All candidates achieve 1.0000 validation alert recall without selecting the zero-alert sentinel.'),
 table(6,'TEST hardware alerts with frozen thresholds',['Metric','LR F6','RF E4','LightGBM E4'],[[label]+[c(k,field,4,percent)+('%' if percent else '') for k in KEYS] for label,field,percent in [('Alert recall','test_alert_recall',False),('Alert precision','test_alert_precision',False),('Alert F1','test_alert_F1',False),('Hardware AP','test_alert_AP',False),('Normal FPR','test_normal_FPR',True),('Shade FPR','test_shade_FPR',True),('Combined FPR','test_combined_FPR',True)]]),
 fig(4,F+'test_hardware_alerts.png','TEST: hardware-alert performance and separate FPRs. Thresholds originate only from VALIDATION block 14. The 1% target applies to combined FPR.',200),
 p('All combined TEST FPRs satisfy 1%. LR shade-only FPR exceeds 1% and remains visible. LightGBM alert recall 0.9969 alongside short-circuit classification recall 0.4994 is not contradictory: summed hardware probability can exceed τ even when another state has the largest individual probability. Some short-circuit observations are classified as degradation; others are labeled shade despite a sufficient summed hardware score. Strong aggregate detection therefore does not establish reliable fault-type diagnosis.')])
 pages.append([
 h('10. Explainability'),
 p('Explanations use a seeded, balanced sample of 1,000 VALIDATION block-13 observations, 200 per class (seed 42). This supports class comparison but does not represent natural prevalence. LR standardized coefficients, RF impurity importance and LightGBM split gain describe fitted models. Three raw-channel permutation repeats rerun the complete pipeline and regenerate every dependent feature. Correlation disruption can create implausible combinations; losses describe model associations, not causal sensor effects.'),
 fig(5,F+'validation_physical_channel_importance.png','VALIDATION block 13, balanced N = 1,000: raw-channel permutation macro-F1 losses (three repeats); dependent features are regenerated.',175),
 p('vdc2 has the largest raw-channel permutation loss in every candidate; current channels also contribute substantially. LR additionally relies on irradiance. RF E4 retains useful electrical information without irr/pvt, but environmental sensing is not proved universally unnecessary. Aggressive validation sensor reduction is consistent with lost predictive information, not a unique physical mechanism.'),
 fig(6,F+'validation_lightgbm_short_circuit_shap.png','VALIDATION block 13, balanced N = 1,000: LightGBM E4 short-circuit Tree SHAP for nine numerical features in raw-margin units; availability indicators have zero contribution. Derived features are not independent sensors.',185),
 p('Native LightGBM Tree SHAP [4,5] emphasizes P1, V_diff and vdc2 for short circuit; vdc2/idc1 for degradation; and V_diff/I_diff for open circuit. Raw-margin additivity is verified to maximum error 6.13 × 10⁻¹⁴. These associations are not causal explanations of errors. Deterministic dependencies/correlation limit unique attribution. Optional RF SHAP was not run; RF native and raw-channel permutation analyses are provided.')])
 pages.append([
 h('11. Computational and sensing trade-offs'),
 p('Corrected VALIDATION block-13 measurements use 100 warm-up calls and 2,000 timed single-observation calls through the complete wrapper/pipeline, including quality checks, imputation, derivatives and scaling where applicable. Data loading/input-frame construction are outside timing. Applicable estimators and numerical pools use two threads. Artifact size is the uncompressed complete fitted wrapper/pipeline pickle, excluding dependencies. These host-dependent results are not hard real-time guarantees. Host: Windows 11; Intel Family 6 Model 170; 16 physical/22 logical cores; Python 3.14.7.'),
 table(7,'Sensing, resource and robustness comparison',['Metric / population','LR F6','RF E4','LightGBM E4'],[
 ['Physical channels','6','4','4'],['Mathematical inputs','12','8','13'],
 ['p95 (ms), VALIDATION']+[c(k,'validation_p95_ms',2) for k in KEYS],
 ['Fitted artifact (MiB)']+[c(k,'artifact_MiB',4) for k in KEYS],
 ['1% dropout loss, VALIDATION']+[c(k,'validation_dropout_loss',6) for k in KEYS]],'LR/RF dropout evidence is unchanged; LightGBM uses the identical frozen E4 mask. Every loss satisfies 0.05.'),
 fig(7,F+'performance_resource_tradeoff.png','Explicitly mixed quantities: TEST macro-F1; VALIDATION block-13 p95; TRAIN-fitted artifact size. Labels identify physical-channel counts; marker area indicates fitted artifact size.',170),
 h('12. Engineering criteria assessment'),
 table(8,'Frozen engineering criteria: no complete passing configuration',['Criterion','LR F6','RF E4','LightGBM E4'],[
 ['TEST macro-F1 ≥ 0.80','PASS','PASS','PASS'],['Every hardware-class recall ≥ 0.90','FAIL','PASS','FAIL'],['Same-family TEST Δ_s ≤ 0.05','N/A','PASS','PASS'],['Sparse physical channels ≤ 4','N/A','PASS','PASS'],['Combined TEST alert FPR ≤ 1%','PASS','PASS','PASS'],['VALIDATION p95 ≤ 10 ms','FAIL','FAIL','PASS'],['Artifact ≤ 10 MiB','PASS','FAIL','PASS'],['VALIDATION dropout loss ≤ 0.05','PASS','PASS','PASS']], 'N/A means inapplicable to the full-sensing reference; no criterion was weakened.'),
 p('No evaluated configuration satisfied all predeclared engineering criteria. LR fails hardware-class recall and latency; RF E4 fails latency and artifact size; LightGBM E4 fails short-circuit recall. This measured trade-off does not justify relabeling a failing system as accepted.')])
 pages.append([
 h('13. Limitations'),
 p('No explicit timestamps or uninterrupted source continuity are verifiable. Ordered buffered splitting does not establish calendar intervals, verified days/sessions, alerts per hour or detection delay in seconds. The controlled installation contains induced electrical faults and natural shade; external field generalization and maintenance effectiveness remain untested. Severe class imbalance and neighboring-row dependence limit aggregate-score interpretation; no independent-site evaluation is available.'),
 p('The approved test partition was evaluated in an earlier legacy implementation before the revised protocol. It is not described as pristine or previously unseen. Revised settings, sensor sets, feature policy and thresholds were frozen using training/validation evidence without using legacy test outcomes for revised decisions. Revised runners do not load legacy test metrics. Earlier human exposure cannot be removed; software cannot independently exclude all influence from that exposure.'),
 p('Only seven predeclared sensor sets were tested; RF E4 is not established as globally minimum sensing. Fixed settings avoid repeated sparse tuning but may not be optimal for each set. Engineered versus raw sparse LightGBM effects lack matched controls. Targets are project aspirations, not industry certification or safety thresholds. No temporal CNN/TCN is implemented because sufficient temporal continuity was not established for the minimum experiment. No unsupervised model is required for the primary supervised question. Explanations are non-causal, and balanced explanation samples do not represent natural prevalence.'),
 h('14. Conclusion'),
 p('Four electrical channels supported strong RF E4 classification among the seven tested sensor sets, but latency and artifact-size limits were exceeded. LightGBM E4 met computational/four-channel constraints while failing short-circuit classification recall. LR F6 provided a small full-sensing reference but failed latency and open-circuit recall. No evaluated configuration satisfied all predeclared engineering criteria. The experiment identifies a measurable sensing–prediction–computation trade-off rather than a universally best configuration.'),
 h('15. Reproducibility and repository structure'),
 p('The unchanged Phase 1 report/audit and immutable raw CSV remain the foundation. Experiment modules reside under src/phase2_stage1, src/phase2_stage2 and src/phase2_stage3, with compact CSV/JSON evidence in corresponding directories. The PDF, editable Markdown and evidence-only report builder are separate from experiment runners. phase2_implementation/README.md documents root-based setup, data hashes, split/weight/feature/model references, threshold chronology and resource protocol. Portable review: python -B phase2_implementation/verify_submission.py. Report rendering and verification do not fit models. Committed model binaries are unnecessary for evidence inspection.'),
 h('References'),
 p('[1] United Nations, Goal 7: Affordable and Clean Energy. https://sdgs.un.org/goals/goal7 (application motivation).'),
 p('[2] A. E. Lazzaretti et al., “A Monitoring System for Online Fault Detection and Classification in Photovoltaic Plants,” Sensors, 20(17), 4688, 2020. https://doi.org/10.3390/s20174688.'),
 p('[3] C. H. da Costa, PV Fault Dataset, original-author repository; pinned commit e9ed8ad8072dcb3ffc643b0f3604219798708551. https://github.com/clayton-h-costa/pv_fault_dataset.'),
 p('[4] LightGBM, Booster.predict: pred_contrib contributions and expected-value term. https://lightgbm.readthedocs.io/en/latest/pythonapi/lightgbm.Booster.html.'),
 p('[5] S. M. Lundberg et al., “From local explanations to global understanding with explainable AI for trees,” Nature Machine Intelligence, 2, 56–67, 2020. https://doi.org/10.1038/s42256-019-0138-9.')])
 return pages
CSS='''body{font-family:serif;font-size:10pt;line-height:1.14;color:#151515;margin:0;}p{margin:5pt 0 7pt;text-align:justify;}h2{font-size:12pt;margin:10pt 0 5pt;font-weight:bold;}.title{font-size:18pt;text-align:center;font-weight:bold;margin:0 0 8pt;}.subtitle{font-size:12pt;text-align:center;margin:5pt;}.byline{font-size:10pt;text-align:center;margin:7pt 0 13pt;}table{border-collapse:collapse;width:100%;font-size:8.4pt;margin:5pt 0;}th,td{border:0.4pt solid #777;padding:3.3pt;vertical-align:top;}th{background-color:#f0f0f0;font-weight:bold;}.caption{font-size:8.4pt;text-align:left;margin:5pt 0;}.note{font-size:8.4pt;margin:4pt 0 7pt;}'''
def markup(b):
 kind=b[0]
 if kind in ['title','subtitle','byline']:return '<p class="'+kind+'">'+b[1]+'</p>'
 if kind=='h':return '<h2>'+b[1]+'</h2>'
 if kind=='p':return '<p>'+b[1]+'</p>'
 if kind=='table':
  z=b[1];header='<tr>'+''.join('<th>'+html.escape(x)+'</th>' for x in z['headers'])+'</tr>';rows=''.join('<tr>'+''.join('<td>'+html.escape(str(c))+'</td>' for c in row)+'</tr>' for row in z['rows'])
  return '<p class="caption"><b>Table '+str(z['number'])+'. '+z['title']+'</b></p><table>'+header+rows+'</table><p class="note">'+z['note']+'</p>'
 if kind=='figure':
  z=b[1];return '<p style="text-align:center;margin:5pt 0;"><img src="'+z['source']+'" width="520" height="'+str(b[2])+'"></p><p class="caption"><b>Fig. '+str(z['number'])+'.</b> '+z['caption']+'</p>'
 raise ValueError(kind)
def markdown(b):
 kind=b[0]
 if kind in ['title','subtitle','byline']:return ('# ' if kind=='title' else '')+b[1].replace('<br>','\n')+'\n'
 if kind=='h':return '## '+b[1]+'\n'
 if kind=='p':return html.unescape(b[1])+'\n'
 if kind=='table':
  z=b[1];return '**Table '+str(z['number'])+'. '+z['title']+'**\n\n'+'| '+' | '.join(z['headers'])+' |\n| '+' | '.join(['---']*len(z['headers']))+' |\n'+''.join('| '+' | '.join(map(str,row))+' |\n' for row in z['rows'])+'\n'+z['note']+'\n'
 z=b[1];rel=Path(os.path.relpath(ROOT/z['source'],REPORTS)).as_posix();return '![Fig. '+str(z['number'])+']('+rel+')\n\n**Fig. '+str(z['number'])+'.** '+z['caption']+'\n'
def main():
 protect();scientific_figures();from .presentation_figures import generate;generate(D,C);pages=contents();doc=pdf.open();layout=[];archive=pdf.Archive(str(ROOT))
 for i,blocks in enumerate(pages):
  page=doc.new_page(width=612,height=792);text=''.join(markup(b) for b in blocks)
  spare,scale=page.insert_htmlbox(pdf.Rect(42,43,570,747),text,css=CSS,archive=archive,scale_low=1)
  if spare<0:raise RuntimeError(f'Report page {i+1} overflow; revise layout, never silently shrink text.')
  if i:page.insert_text((42,28),'PV Anomaly Detection | Phase 2 Experimental Evaluation',fontname='tiro',fontsize=8,color=(.25,.25,.25))
  page.insert_text((299,770),str(i+1),fontname='tiro',fontsize=9);layout.append({'page':i+1,'spare_height_pt':spare,'scale':scale,'sections':[b[1] for b in blocks if b[0]=='h']})
 doc.set_metadata({'title':'AISD Assignment 2 — Phase 2: PV Anomaly Detection','author':'Ruganji Prince','subject':'Frozen predictive, sensing and computational trade-offs','keywords':'photovoltaic; sensor ablation; multiclass classification; explainability'})
 target=REPORTS/'Phase2_Final_Report.pdf';doc.save(target,garbage=4,deflate=True);doc.close()
 (REPORTS/'Phase2_Final_Report.md').write_text('\n\n'.join(markdown(b) for page in pages for b in page)+'\n',encoding='utf8')
 write(OUT/'evidence/report_evidence_map.json',{'numeric_claims':CLAIMS,'tables':TABLES,'figures':FIGURES,'report_sha256':sha(target),'source_sha256':sha(REPORTS/'Phase2_Final_Report.md'),'pages':len(pages),'layout':layout,'body_font_pt':10,'table_font_pt':8.4,'silent_text_scaling':False})
 print('REPORT',target.relative_to(ROOT),len(pages),'pages',target.stat().st_size,'bytes');print('Spare heights:',[round(x['spare_height_pt'],1) for x in layout]);print('Numeric claims:',len(CLAIMS));protect()
if __name__=='__main__':main()
