"""Separate experimental reconstructions; never mutates or refits the deployed model."""
import json,pickle,time,warnings
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator,TransformerMixin,clone
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import precision_recall_fscore_support
from .common import *
from .metrics import evaluate,probability_metrics,hypothetical_cost

class TrainingClipper(TransformerMixin,BaseEstimator):
 def __init__(self,method='none'):self.method=method
 def fit(self,X,y=None):
  self.columns_=list(X);a=np.asarray(X,dtype=float)
  if self.method=='iqr':q1,q3=np.nanquantile(a,[.25,.75],axis=0);self.lower_=q1-1.5*(q3-q1);self.upper_=q3+1.5*(q3-q1)
  elif self.method=='quantile':self.lower_,self.upper_=np.nanquantile(a,[.005,.995],axis=0)
  else:self.lower_=np.full(a.shape[1],-np.inf);self.upper_=np.full(a.shape[1],np.inf)
  self.fit_rows_=len(X);self.fit_digest_=digest(X.index);return self
 def transform(self,X):
  if list(X)!=self.columns_:raise ValueError('Clip schema mismatch')
  return pd.DataFrame(np.clip(np.asarray(X,dtype=float),self.lower_,self.upper_),columns=X.columns,index=X.index)
 def get_feature_names_out(self,input_features=None):return np.asarray(self.columns_,dtype=object)

def assert_fit_isolated(fit_index,evaluation_index):
 if set(fit_index)&set(evaluation_index):raise ValueError('Fit/evaluation source overlap')
 if len(fit_index)==0:raise ValueError('Empty fit population')

def build(family,y,clipping='none'):
 from src.phase2_stage2.models import build_preprocessor
 from lightgbm import LGBMClassifier
 model=original();params=model.pipeline.named_steps['model'].get_params().copy();counts=pd.Series(y).value_counts();weights={int(k):len(y)/(len(counts)*int(v)) for k,v in counts.items()}
 if family=='RF':est=clone(model.pipeline.named_steps['model']);est.set_params(class_weight=weights)
 elif family=='LR':est=LogisticRegression(C=1.,max_iter=2000,solver='lbfgs',class_weight=weights,random_state=SEED)
 elif family=='LightGBM':est=LGBMClassifier(n_estimators=150,max_depth=6,num_leaves=31,learning_rate=.05,min_child_samples=50,max_bin=127,reg_lambda=1.,deterministic=True,force_col_wise=True,n_jobs=2,random_state=SEED,verbosity=-1,class_weight=weights)
 else:raise ValueError(family)
 prep=build_preprocessor(family,CHANNELS)
 return Pipeline([('quality',prep.named_steps['quality']),('clip',TrainingClipper(clipping)),('columns',prep.named_steps['columns']),('model',est)])

def padded_probability(pipe,X):
 p=pipe.predict_proba(X);out=np.zeros((len(X),5));out[:,np.asarray(pipe.named_steps['model'].classes_,dtype=int)]=p;return out

def fit_one(pipe,X,y,evaluation_index):
 assert_fit_isolated(X.index,evaluation_index)
 with warnings.catch_warnings(record=True) as caught:
  warnings.simplefilter('always');start=time.perf_counter();pipe.fit(X,y);seconds=time.perf_counter()-start
 numeric=pipe.named_steps['columns'].named_transformers_['numeric'];clean=pipe.named_steps['quality'].transform(X);clipped=pipe.named_steps['clip'].transform(clean)
 np.testing.assert_allclose(numeric.named_steps['median'].statistics_,np.nanmedian(clipped,axis=0),atol=1e-12,rtol=1e-12)
 assert pipe.named_steps['clip'].fit_digest_==digest(X.index)
 if 'scale' in numeric.named_steps:np.testing.assert_allclose(numeric.named_steps['scale'].mean_,np.nanmean(clipped,axis=0),atol=1e-12,rtol=1e-12)
 return {'fit_N':len(X),'fit_index_digest':digest(X.index),'eval_index_digest':digest(evaluation_index),'fit_eval_index_overlap':0,'full_pipeline_fitted_per_fold':True,'seconds':seconds,'classes_seen':pipe.named_steps['model'].classes_.tolist(),'weights':pipe.named_steps['model'].class_weight,'warnings':[str(w.message) for w in caught],'columns_remainder':pipe.named_steps['columns'].remainder,'feature_names':pipe.named_steps['columns'].get_feature_names_out().tolist()}

class ProbabilityMap:
 def __init__(self,method):self.method=method
 def fit(self,p,y):
  self.maps=[];self.support={}
  for k in range(5):
   binary=np.asarray(y)==k;positive=int(binary.sum());negative=len(y)-positive;minimum=100 if self.method=='isotonic' else 50
   if positive<minimum or negative<100:raise ValueError(f'Insufficient calibration support class{k}: {positive}/{negative}')
   self.support[str(k)]={'positive':positive,'negative':negative}
   if self.method=='sigmoid':m=LogisticRegression(C=1e6,solver='lbfgs',max_iter=1000,random_state=42).fit(p[:,k,None],binary)
   else:m=IsotonicRegression(y_min=0,y_max=1,out_of_bounds='clip').fit(p[:,k],binary)
   self.maps.append(m)
  return self
 def transform(self,p):
  q=np.column_stack([m.predict_proba(p[:,k,None])[:,1] if self.method=='sigmoid' else m.predict(p[:,k]) for k,m in enumerate(self.maps)]);q=np.clip(q,1e-12,1);return q/q.sum(1,keepdims=True)

def calibration(d):
 m=original();cal=d.iloc[slice(*B14)];p=probs(m,cal);y=cal.f_nv.to_numpy();tiles=np.arange(len(cal))//256;folds=tiles%4;ledger=[];oof={name:np.full_like(p,np.nan) for name in ['sigmoid','isotonic']}
 for fold in range(4):
  valid=np.flatnonzero(folds==fold);fit_mask=folds!=fold
  for tile in np.unique(tiles[valid]):fit_mask[max(0,int(tile)*256-64):min(len(cal),(int(tile)+1)*256+64)]=False
  fit=np.flatnonzero(fit_mask);assert_fit_isolated(cal.index[fit],cal.index[valid]);assert not set(tiles[fit])&set(tiles[valid])
  for name in oof:
   mapper=ProbabilityMap(name).fit(p[fit],y[fit]);oof[name][valid]=mapper.transform(p[valid]);ledger.append({'fold':fold,'method':name,'fit_N':len(fit),'eval_N':len(valid),'fit_index_digest':digest(cal.index[fit]),'eval_index_digest':digest(cal.index[valid]),'purged_N':int(((folds!=fold)&~fit_mask).sum()),'fit_eval_overlap':0,'source_tile_overlap':0,'positive_negative_support':mapper.support})
 results={'uncalibrated':probability_metrics(p,y)}
 for name,q in oof.items():assert np.isfinite(q).all();results[name]=probability_metrics(q,y)
 selected=min(results,key=lambda k:(results[k]['log_loss'],results[k]['multiclass_Brier'],k))
 write('evidence/rubric3/calibration_selection_freeze.json',{'selected_by_block14_OOF_only':selected,'OOF_probability_quality':results,'folds':ledger,'fit_population':'VALIDATION block14; base-model TRAIN is disjoint','final_evaluation':'Historical TEST after this receipt; prior TEST exposure disclosed','new_calibrated_threshold_search':False,'deployed_model_changed':False,'source_tile_limitation':'Artificial source-position groups from one operating block, not verified independent sessions. Historical threshold selection used block14; no new calibrated-alert threshold is fitted or evaluated here.'})
 final={};CACHE.mkdir(parents=True,exist_ok=True)
 for name in oof:
  mapper=ProbabilityMap(name).fit(p,y);path=CACHE/f'calibration_{name}.pkl';path.write_bytes(pickle.dumps(mapper));final[name]={'mapper':mapper,'sha256':sha(path),'fit_rows':len(cal),'fit_digest':digest(cal.index)}
 # Protocol and calibration-selection receipt exist before this new retrospective diagnostic.
 freeze_check();test=part(d,'TEST');pt=probs(m,test);yt=test.f_nv.to_numpy();comparison={'uncalibrated':{'probability_quality':probability_metrics(pt,yt),'classification':evaluate(pt,yt)}}
 for name,item in final.items():
  q=item['mapper'].transform(pt);comparison[name]={'probability_quality':probability_metrics(q,yt),'classification':evaluate(q,yt),'private_artifact_sha256':item['sha256'],'fit_rows':item['fit_rows'],'fit_digest':item['fit_digest']}
 write('evidence/rubric3/calibration_TEST_retrospective.json',{'population':'TEST; previously inspected historically; no method selected using these results','methods':comparison,'deployed_model_unchanged':True,'calibrated_hardware_threshold_metrics':'NOT APPLICABLE: no calibrated threshold was selected; original tau belongs only to original probabilities.'})
 print('CALIBRATION_COMPLETE',selected,flush=True)

def model_metrics(d,private_cache=None):
 train=part(d,'TRAIN');val=d.iloc[slice(*B13)];test=part(d,'TEST');tau=.5913558658757772;m=original();all_results={};baseline_support=train.f_nv.value_counts().sort_index().to_dict()
 for name in ['most_frequent','prior']:
  dummy=DummyClassifier(strategy=name).fit(train[CHANNELS],train.f_nv);all_results['Dummy_'+name]={}
  for partition,frame in [('VALIDATION_BLOCK13',val),('TEST',test)]:all_results['Dummy_'+name][partition]=evaluate(dummy.predict_proba(frame[CHANNELS]),frame.f_nv)
 all_results['original_RF_E4']={partition:evaluate(probs(m,frame),frame.f_nv,tau) for partition,frame in [('VALIDATION_BLOCK13',val),('TEST',test)]}
 if private_cache:
  proof=json.loads((ROOT/'reports/model_verification.json').read_text());cache=Path(private_cache)
  if (cache/'stage2/models').is_dir():cache=cache/'stage2/models'
  for key in ['LR__F6','LR__E4','RF__F6','LightGBM__E4','LightGBM__F6']:
   path=cache/(key+'.pkl');assert sha(path)==proof['original_models'][key]['sha256'];obj=pickle.loads(path.read_bytes());all_results[key]={}
   for partition,frame in [('VALIDATION_BLOCK13',val),('TEST',test)]:all_results[key][partition]=evaluate(probs(obj,frame),frame.f_nv)
  checks=[];ref=pd.read_csv(ROOT/'phase2_implementation/stage2/evidence/sensor_ablation_validation.csv')
  for row in ref.to_dict('records'):
   key=row['key'];path=cache/(key+'.pkl');assert sha(path)==proof['original_models'][key]['sha256'];obj=pickle.loads(path.read_bytes());result=evaluate(probs(obj,val),val.f_nv);assert abs(result['macro_f1_fixed_five']-row['macro_f1'])<1e-12;checks.append({'candidate':key,'sha256':sha(path),'validation_macro_f1':result['macro_f1_fixed_five'],'matches_archived':True})
  write('evidence/rubric3/original_model_reverification.json',{'candidates':checks,'private_cache_required':True,'no_original_model_refitted':True})
 # Binary physical relationship baseline, not a five-class diagnosis.
 def imbalance(frame):return abs(frame.idc1.to_numpy()-frame.idc2.to_numpy())/(abs(frame.idc1.to_numpy())+abs(frame.idc2.to_numpy())+1e-12)
 threshold=float(np.quantile(imbalance(train),.99));physical={}
 from sklearn.metrics import average_precision_score
 for name,frame in [('VALIDATION_BLOCK13',val),('TEST',test)]:
  score=imbalance(frame);alert=score>=threshold;y=frame.f_nv.to_numpy();hw=np.isin(y,[1,2,3]);physical[name]={'N':len(frame),'hardware_AP':float(average_precision_score(hw,score)),'hardware_recall':float(alert[hw].mean()),'normal_FPR':float(alert[y==0].mean()),'shade_FPR':float(alert[y==4].mean()),'combined_nonhardware_FPR':float(alert[~hw].mean())}
 write('evidence/rubric3/model_comparison.json',{'results':all_results,'TRAIN_class_support':baseline_support,'TRAIN_predictive_metrics':'Not estimated to avoid in-sample performance claims','comparison_policy':'Same E4 physical input comparison separated from F6 resource-reference comparisons; no TEST-based reselection.','physical_rule':{'definition':'abs(idc1-idc2)/(abs(idc1)+abs(idc2)+1e-12) >= TRAIN q99','threshold':threshold,'fit_N':len(train),'not_a_subtype_or_certified_fault_diagnosis':True,'metrics':physical},'MAE':'NOT APPLICABLE: nominal label-code distances are not physical errors.'})
 costs=[]
 for name in ['Dummy_most_frequent','original_RF_E4']:
  for partition,frame in [('VALIDATION_BLOCK13',val),('TEST',test)]:
   p=probs(m,frame) if name=='original_RF_E4' else np.tile([1,0,0,0,0],(len(frame),1))
   for weight in [2,5,10,20]:costs.append({'model':name,'partition':partition,**hypothetical_cost(frame.f_nv,p,weight)})
 write('evidence/rubric1/hypothetical_costs.json',{'policy':'Illustrative unitless sensitivity, not stakeholder-elicited monetary costs; no threshold/model chosen from TEST cost.','results':costs})
 print('BASELINES_AND_ORIGINAL_COMPARISONS_COMPLETE',flush=True)

def training_experiments(d):
 train=part(d,'TRAIN');val=d.iloc[slice(*B13)];clip_results={};CACHE.mkdir(parents=True,exist_ok=True)
 for method in ['none','iqr','quantile']:
  pipe=build('RF',train.f_nv,method);ledger=fit_one(pipe,train[CHANNELS],train.f_nv,val.index);p=padded_probability(pipe,val[CHANNELS]);clip=pipe.named_steps['clip'];mask=np.asarray(val[CHANNELS])!=np.asarray(clip.transform(val[CHANNELS]));train_mask=np.asarray(train[CHANNELS])!=np.asarray(clip.transform(train[CHANNELS]));artifact=CACHE/f'experimental_RF_{method}.pkl';artifact.write_bytes(pickle.dumps(pipe))
  clip_results[method]={'ledger':ledger,'validation':evaluate(p,val.f_nv),'TRAIN_changed_cells':int(train_mask.sum()),'VALIDATION_changed_cells':int(mask.sum()),'VALIDATION_changed_rows_by_class':{str(k):int(mask[np.asarray(val.f_nv)==k].any(1).sum()) for k in range(5)},'thresholds':{'lower':clip.lower_,'upper':clip.upper_},'private_artifact_sha256':sha(artifact),'provenance':'New experimental reconstruction, not original model bytes'}
  print('CLIPPING_EXPERIMENT',method,clip_results[method]['validation']['macro_f1_fixed_five'],flush=True)
 write('evidence/rubric1/clipping_comparison.json',clip_results)
 # Only the 12 TRAIN operating blocks enter grouped validation, not TEST/validation groups.
 g=groups(train.index);eligible=g>0;dev=train.loc[eligible];group=g[eligible];folds=[];rf_cms={};oof_labels={};
 for fold,(fit,valid) in enumerate(GroupKFold(n_splits=3,shuffle=False).split(dev,dev.f_nv,group)):
  a=dev.iloc[fit];b=dev.iloc[valid];assert not set(group[fit])&set(group[valid])
  for family in ['LR','RF','LightGBM']:
   pipe=build(family,a.f_nv);ledger=fit_one(pipe,a[CHANNELS],a.f_nv,b.index);p=padded_probability(pipe,b[CHANNELS]);metrics=evaluate(p,b.f_nv);folds.append({'fold':fold,'family':family,'fit_blocks':sorted(set(group[fit])),'eval_blocks':sorted(set(group[valid])),'fit_class_support':a.f_nv.value_counts().sort_index().to_dict(),'eval_class_support':b.f_nv.value_counts().sort_index().to_dict(),'unseen_true_classes':sorted(set(b.f_nv)-set(a.f_nv)),'ledger':ledger,'metrics':metrics})
   if family=='RF':
    for block in np.unique(group[valid]):rf_cms[int(block)]=np.asarray(evaluate(p[group[valid]==block],b.f_nv.to_numpy()[group[valid]==block])['confusion_matrix'])[:,:5]
   print('GROUP_FOLD',fold,family,'macro_present',metrics['macro_f1_present_classes'],'unseen',folds[-1]['unseen_true_classes'],flush=True)
 write('evidence/rubric2/grouped_validation.json',{'method':'3 nonshuffled GroupKFold folds over TRAIN operating blocks only','population_N':len(dev),'excluded_background_rows':int((~eligible).sum()),'folds':folds,'singleton_fault_block':'TRAIN class1 exists only in block12; folds lacking it cannot learn it. Fixed-five and supported-class metrics are both explicit.','selection':'No model or deployment changed from these retrospective development diagnostics.'})
 # Aggregate confusion matrices preserve dependence within an entire source block.
 matrices=np.stack([rf_cms[k] for k in sorted(rf_cms)]);rng=np.random.default_rng(SEED);values=[];rejected=0
 for _ in range(500):
  cm=matrices[rng.integers(0,len(matrices),len(matrices))].sum(0);support=cm.sum(1)
  if (support==0).any():rejected+=1;continue
  precision=np.divide(np.diag(cm),cm.sum(0),out=np.zeros(5),where=cm.sum(0)>0);recall=np.diag(cm)/support;f1=np.divide(2*precision*recall,precision+recall,out=np.zeros(5),where=(precision+recall)>0);values.append([f1.mean(),recall.mean()])
 values=np.array(values);write('evidence/rubric3/uncertainty.json',{'unit':'12 TRAIN signal-defined operating blocks; original-RF-configuration grouped-OOF experimental predictions','groups':sorted(rf_cms),'seed':42,'attempted_repetitions':500,'accepted_repetitions':len(values),'rejected_missing_class_support':rejected,'conditional_percentile_95':{'macro_f1':np.quantile(values[:,0],[.025,.975]),'balanced_accuracy':np.quantile(values[:,1],[.025,.975])},'RF_group_confusion_matrices':{k:v.tolist() for k,v in rf_cms.items()},'status':'PARTIAL: exploratory conditional block-bootstrap interval, not established population coverage','limitations':['Signal blocks are not verified independent sessions.','Class1 occurs in only one block; conditioning on class support cannot establish rare-fault uncertainty.','Historical TEST has only two operating blocks; no reliable prospective/test-site CI is claimed.']})
 print('GROUPED_VALIDATION_AND_BOOTSTRAP_COMPLETE',flush=True)
