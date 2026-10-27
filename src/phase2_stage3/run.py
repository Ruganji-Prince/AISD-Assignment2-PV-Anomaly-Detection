import argparse,json
import numpy as np
from threadpoolctl import threadpool_limits
from .common import *

def freeze():
 protect();check_protected()
 if (E/'stage3_threshold_selection.json').exists():raise RuntimeError('Threshold freeze exists; overwrite prohibited')
 protocol={'created_utc':now(),'candidates':CANDIDATES,'diagnostic_F6_references':REFERENCES,'reference_policy':'Only the frozen RF/LightGBM F6 models are scored on TEST to calculate same-family test Delta_s; not extra candidates or model selection.',
  'model_sha256':{k:sha(model_path(k)) for k in CANDIDATES+REFERENCES},'threshold_partition':BLOCK14,'test_partition':TEST,'explanation_partition':BLOCK13,
  'threshold_rule':RULE,'threshold_sentinel':'Finite nextafter(max score,+infinity) included; zero-alert point is feasible, but zero recall must be disclosed.',
  'engineering_criteria':{'macro_f1_min':.8,'each_hardware_classification_recall_min':.9,'same_family_delta_max':.05,'sparse_channels_max':4,'test_combined_alert_FPR_max':.01,'validation_single_row_p95_ms_max':10,'artifact_MiB_max':10,'validation_isolated_dropout_macro_f1_loss_max':.05},
  'delta_policy':'Primary final Delta_s uses frozen same-family F6 TEST scores; Stage 2 validation Delta_s also retained separately. LR F6 is a reference: sparse-channel/Delta conditions not applicable.',
  'resources':'Reuse corrected frozen Stage 2 block-13 100-warmup/2000 single-observation end-to-end measurements, including two-thread settings; do not combine with Stage 1 batch-average timings.',
  'dropout':'Preserve existing LR F6/RF E4 block-13 outcomes; evaluate LightGBM E4 with identical 328 even-position, seed42 row mask and seed44 E4 channel mask.',
  'explanation_sample':{'partition':'validation block 13','seed':42,'per_class':200,'N':1000,'strategy':'Uniform without replacement within each class; class balanced, not representative of prevalence. Sorted source positions; 3 permutation repeats.'},
  'explainability':'LR standardized coefficients, RF impurity importance, LightGBM gain and native exact Tree SHAP raw-score contributions. Raw-channel permutation regenerates dependent features. SHAP sample only; no causality.',
  'prior_test_exposure':True,'prior_test_disclosure':'The approved test partition was evaluated in an earlier legacy implementation and is not pristine or previously unseen. Revised settings were frozen from training/block13, and thresholds from block14. No legacy test metrics are read by revised selection code; earlier human exposure cannot be undone or independently disproved by software.',
  'no_retraining':True,'no_post_test_selection':True,'seed':42,'runtime':runtime()}
 write_json(E/'stage3_protocol.json',protocol)
 val=load_part(BLOCK14);results={}
 with threadpool_limits(2):
  for key in CANDIDATES:
   m=load_model(key);p=FrozenPredictor(m,BLOCK14).predict_proba(val[m.channels]);r=select_threshold(p,val.f_nv.to_numpy())
   r.update({'candidate':key,'configuration':m.config,'model_sha256':sha(model_path(key)),'population':'validation block14','N':len(val),'index_digest':index_digest(val.index)})
   results[key]=r;print(key,json.dumps(r),flush=True)
 write_json(E/'stage3_threshold_selection.json',{'frozen_utc':now(),'protocol_sha256':sha(E/'stage3_protocol.json'),'results':results})
 write_json(E/'threshold_freeze_receipt.json',{'created_utc':now(),'threshold_sha256':sha(E/'stage3_threshold_selection.json'),'protocol_sha256':sha(E/'stage3_protocol.json'),'model_sha256':protocol['model_sha256'],'test_access_started':False})
 print('THRESHOLDS FROZEN; no revised test evaluation has started.',flush=True)

def final_test():
 check_protected();receipt=json.loads((E/'threshold_freeze_receipt.json').read_text());assert receipt['threshold_sha256']==sha(E/'stage3_threshold_selection.json')
 if (E/'test_access_started.json').exists():raise RuntimeError('Final test access already recorded; no silent rerun')
 thresholds=json.loads((E/'stage3_threshold_selection.json').read_text())['results']
 write_json(E/'test_access_started.json',{'created_utc':now(),'threshold_sha256':receipt['threshold_sha256'],'receipt_sha256':sha(E/'threshold_freeze_receipt.json'),'frozen_model_sha256':receipt['model_sha256']})
 test=load_part(TEST);details={};cache=ROOT/'.cache/stage3';cache.mkdir(exist_ok=True,parents=True)
 with threadpool_limits(2):
  for key in CANDIDATES+REFERENCES:
   assert sha(model_path(key))==receipt['model_sha256'][key]
   m=load_model(key);p=FrozenPredictor(m,TEST).predict_proba(test[m.channels]);threshold=thresholds[key]['threshold'] if key in CANDIDATES else None
   metrics=evaluate(p,test.f_nv.to_numpy(),threshold)
   if threshold is not None:
    metrics['hardware_alert_status']='Frozen block14 threshold applied without test adjustment.'
    metrics['hardware_alert_metrics']['average_precision']=metrics['hardware_AP']
   cm=np.array(metrics['confusion_matrix']);metrics['hardware_to_shading']={str(k):{'count':int(cm[k,4]),'rate':float(cm[k,4]/cm[k].sum())} for k in [1,2,3]}
   details[key]=metrics;np.savez_compressed(cache/(key+'_test.npz'),p=p,y=test.f_nv.to_numpy(),index=test.index.to_numpy())
   print('TEST',key,'macro-F1',metrics['macro_f1'],'hardware recalls',[metrics['per_class'][str(k)]['recall'] for k in [1,2,3]],flush=True)
 write_json(E/'final_test_details.json',{'completed_utc':now(),'threshold_sha256':receipt['threshold_sha256'],'prior_test_exposure':True,'population':'TEST [1227337,1373798), all 146461 rows, no irradiance filtering','results':details})
 csv('final_test_class_metrics.csv',[{'candidate':key,'class':k,**details[key]['per_class'][str(k)]} for key in CANDIDATES for k in range(5)])
 csv('final_test_metrics.csv',[{'candidate':key,**{k:details[key][k] for k in ['macro_f1','weighted_f1','macro_AP','hardware_macro_recall','coverage']}} for key in CANDIDATES])
 csv('final_hardware_alert_metrics.csv',[{'candidate':key,**{k:v for k,v in details[key]['hardware_alert_metrics'].items() if k!='hardware_class_alert_recall'}} for key in CANDIDATES])

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('step',choices=['freeze','test']);a=parser.parse_args()
 {'freeze':freeze,'test':final_test}[a.step]()
