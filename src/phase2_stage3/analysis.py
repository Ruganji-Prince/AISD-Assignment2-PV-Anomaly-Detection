"""Post-freeze validation explanations and frozen engineering assessment."""
import json
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
from .common import *

def main():
 check_protected()
 if (E/'explainability_metadata.json').exists():raise RuntimeError('Completed explanation evidence exists; no silent overwrite')
 val=load_part(BLOCK13);rng=np.random.default_rng(SEED)
 idx=np.sort(np.concatenate([rng.choice(val.index[val.f_nv==k],200,replace=False) for k in range(5)]))
 sample=val.loc[idx];permutations=[];native=[];coefficients=[];drop={}
 old=json.loads((ROOT/'phase2_implementation/stage2/evidence/isolated_dropout_validation.json').read_text())
 for key in ['LR__F6','RF__E4']:drop[key]=old['outcomes'][key]
 cache=ROOT/'.cache/stage3';cache.mkdir(exist_ok=True,parents=True)
 with threadpool_limits(2):
  for key in CANDIDATES:
   m=load_model(key);adapter=FrozenPredictor(m,BLOCK13);X=sample[m.channels];y=sample.f_nv.to_numpy();base=evaluate(adapter.predict_proba(X),y)
   est=m.pipeline.named_steps['model'];names=m.names()
   if key=='LR__F6':
    for k in range(5):
     coefficients.extend({'candidate':key,'class':k,'feature':n,'coefficient':float(v)} for n,v in zip(names,est.coef_[k]))
    values=np.abs(est.coef_).mean(0);kind='Mean absolute standardized multiclass coefficient (availability indicators unscaled and zero in training)'
   elif key=='RF__E4':values=est.feature_importances_;kind='Mean decrease in impurity; TRAIN fitted; correlated-feature attribution is not unique'
   else:values=est.booster_.feature_importance(importance_type='gain');kind='Split gain; TRAIN fitted; not causal or independent sensor importance'
   native.extend({'candidate':key,'feature':n,'importance':float(v),'method':kind} for n,v in zip(names,values))
   for c in m.channels:
    for repeat in range(3):
     z=X.copy();z[c]=np.random.default_rng(SEED+repeat).permutation(z[c].to_numpy())
     met=evaluate(adapter.predict_proba(z),y)
     permutations.append({'candidate':key,'channel':c,'repeat':repeat,'baseline_macro_f1':base['macro_f1'],'macro_f1_loss':base['macro_f1']-met['macro_f1'],**{'class'+str(k)+'_recall_loss':base['per_class'][str(k)]['recall']-met['per_class'][str(k)]['recall'] for k in range(5)}})
   print('EXPLANATION native/permutation complete',key,flush=True)
   if key=='LightGBM__E4':
    positions=np.asarray(old['positions_in_block13']);choices=np.random.default_rng(SEED+list(CONFIGS).index('E4')).integers(0,len(m.channels),size=len(positions))
    assert choices.tolist()==old['outcomes']['RF__E4']['channel_choices']
    V=val[m.channels];altered=V.copy()
    for j,c in enumerate(m.channels):altered.iloc[positions[choices==j],j]=np.nan
    baseline=evaluate(adapter.predict_proba(V),val.f_nv.to_numpy());modified=evaluate(adapter.predict_proba(altered),val.f_nv.to_numpy());loss=baseline['macro_f1']-modified['macro_f1']
    drop[key]={'baseline_macro_f1':baseline['macro_f1'],'dropout_macro_f1':modified['macro_f1'],'loss':loss,'loss_le_005':loss<=.05,'coverage':modified['coverage'],'channel_choices':choices.tolist(),'metrics':modified}
    transformed=m.pipeline[:-1].transform(X)
    contributions=np.asarray(est.booster_.predict(transformed,pred_contrib=True,num_threads=2)).reshape(len(X),5,len(names)+1)
    raw=np.asarray(est.booster_.predict(transformed,raw_score=True,num_threads=2))
    error=float(np.max(np.abs(contributions.sum(2)-raw)));assert error<1e-7
    np.savez_compressed(cache/'LightGBM_E4_shap_validation.npz',values=contributions,raw_scores=raw,transformed=transformed,index=idx,y=y)
    csv('shap_mean_absolute.csv',[{'class':k,'feature':n,'mean_abs_SHAP':float(np.abs(contributions[:,k,j]).mean()),'mean_signed_on_true_class':float(contributions[y==k,k,j].mean())} for k in range(5) for j,n in enumerate(names)])
 csv('physical_channel_permutation.csv',permutations);csv('native_feature_importance.csv',native);csv('lr_coefficients.csv',coefficients)
 write_json(E/'dropout_validation.json',{'population':'validation block13','protocol_reference':'../../stage2/evidence/isolated_dropout_validation.json','new_selection':False,'positions_identical_to_stage2':True,'LightGBM_E4_channel_mask_identical_to_RF_E4':True,'outcomes':drop})
 write_json(E/'explainability_metadata.json',{'created_utc':now(),'source_partition':'validation block13','sample_size':len(sample),'class_counts':{str(k):int((y==k).sum()) for k in range(5)},'seed':42,'sampling_strategy':'200 observations per class without replacement, sorted source positions; class balanced and not representative of true prevalence','source_positions':idx.tolist(),'index_digest':index_digest(idx),'repeats':3,'permutation':'Permute each retained RAW channel and rerun frozen entire pipeline, regenerating all dependent features. Correlation disruption and class-balanced population limit interpretation. Negative losses retained.','SHAP':{'candidate':'LightGBM__E4','implementation':'Native LightGBM Booster.predict(pred_contrib=True), Tree SHAP, raw class margins, tree-path-dependent reference; last element is expected value','official_reference':'https://lightgbm.readthedocs.io/en/latest/pythonapi/lightgbm.Booster.html','shape':[1000,5,14],'additivity_max_absolute_error':error,'interpretation':'Mathematical feature attribution, not independent physical sensors; dependent-feature attribution is not unique; not causal evidence.'},'RF_SHAP':'Not run: optional; native importance and raw-channel permutation supplied. LightGBM native Tree SHAP needs no additional dependency.','LR':'Signed coefficients use standardized numeric features; magnitudes not causal effects. Missing indicators were constant zero in reference training.','decisions_frozen_before_explanation':True})
 assessment()

def assessment():
 d=json.loads((E/'final_test_details.json').read_text())['results'];drop=json.loads((E/'dropout_validation.json').read_text())['outcomes']
 rows=pd.read_csv(ROOT/'phase2_implementation/stage2/evidence/sensor_ablation_validation.csv').set_index('key');comparisons=[];criteria=[]
 for key in CANDIDATES:
  met=d[key];r=rows.loc[key];delta=None if key=='LR__F6' else d[key.split('__')[0]+'__F6']['macro_f1']-met['macro_f1']
  alert=met['hardware_alert_metrics'];flags={'macro_f1_ge_080':met['macro_f1']>=.8,'each_hardware_classification_recall_ge_090':min(met['per_class'][str(k)]['recall'] for k in [1,2,3])>=.9,'same_family_test_delta_le_005':None if delta is None else delta<=.05,'sparse_channels_le_4':None if key=='LR__F6' else int(r.physical_channels)<=4,'test_combined_alert_FPR_le_001':alert['combined_nonhardware_FPR']<=.01,'validation_p95_le_10ms':r.p95_ms<=10,'artifact_le_10MiB':r.artifact_MiB<=10,'validation_dropout_loss_le_005':drop[key]['loss']<=.05}
  for name,passed in flags.items():criteria.append({'candidate':key,'criterion':name,'status':'N/A' if passed is None else ('PASS' if passed else 'FAIL')})
  comparisons.append({'candidate':key,'physical_channels':int(r.physical_channels),'mathematical_features':int(r.mathematical_features),'test_macro_f1':met['macro_f1'],'test_weighted_f1':met['weighted_f1'],'test_macro_AP':met['macro_AP'],**{'test_R'+str(k):met['per_class'][str(k)]['recall'] for k in [1,2,3]},'test_hardware_macro_recall':met['hardware_macro_recall'],'same_family_test_delta_s':delta,'same_family_validation_delta_s':r.delta_s,'test_alert_recall':alert['recall'],'test_alert_precision':alert['precision'],'test_alert_F1':alert['f1'],'test_alert_AP':met['hardware_AP'],'test_normal_FPR':alert['normal_false_alarm_rate'],'test_shade_FPR':alert['shade_false_alarm_rate'],'test_combined_FPR':alert['combined_nonhardware_FPR'],'validation_p50_ms':r.p50_ms,'validation_p95_ms':r.p95_ms,'artifact_MiB':r.artifact_MiB,'validation_dropout_loss':drop[key]['loss'],'passes_all_applicable':all(v for v in flags.values() if v is not None)})
 csv('final_engineering_criteria.csv',criteria);csv('final_candidate_comparison.csv',comparisons)
 print(pd.DataFrame(comparisons).to_string(index=False),flush=True)
if __name__=='__main__':main()
