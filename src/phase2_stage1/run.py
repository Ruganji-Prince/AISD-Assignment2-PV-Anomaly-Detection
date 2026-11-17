"""Bounded F6 train/block-13 execution. No block-14 thresholds or test scoring."""
import argparse,csv,io,json,pickle,time,warnings
from pathlib import Path
import numpy as np
from sklearn.datasets import make_classification
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import average_precision_score
from lightgbm import LGBMClassifier
from threadpoolctl import threadpool_limits
from .contracts import *
from .models import F6Model,EngineeringReference
from .evaluation import evaluate

def smoke_test():
 X,y=make_classification(n_samples=200,n_features=6,n_informative=5,n_redundant=0,n_classes=5,random_state=SEED)
 with threadpool_limits(2):
  model=LGBMClassifier(n_estimators=5,num_leaves=7,min_child_samples=5,n_jobs=2,verbosity=-1,
   objective='multiclass',num_class=5,deterministic=True,force_col_wise=True,random_state=SEED).fit(X,y)
  p=model.predict_proba(X)
 assert p.shape==(200,5) and np.isfinite(p).all() and np.allclose(p.sum(axis=1),1)
 result={'status':'passed','synthetic_rows':200,'classes':5,'probability_shape':list(p.shape),
  'purpose':'Dependency/import/small synthetic execution test only; not PV scientific evidence.','runtime':runtime()}
 write_json(EVIDENCE/'dependency_smoke_test.json',result);return result

def trial_specs():
 for family in ['LR','RF','LightGBM']:
  policies=['raw','engineered'] if family=='LightGBM' else ['raw']
  settings=[{'C':.1},{'C':1.}] if family=='LR' else ([{'max_depth':6},{'max_depth':10}] if family=='RF' else [{'num_leaves':15,'max_depth':4},{'num_leaves':31,'max_depth':6}])
  for policy in policies:
   for params in settings:
    for weighted in [False,True]:yield family,policy,params,weighted

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--smoke-only',action='store_true');args=parser.parse_args()
 smoke=smoke_test();print('LightGBM smoke test: passed',flush=True)
 if args.smoke_only:return
 if (EVIDENCE/'validation_comparison.csv').exists():raise RuntimeError('Completed Stage 1 evidence exists; no automatic overwrite/retraining.')
 train,val,discrepancy=load_stage1();X=train[SENSORS];y=train.f_nv.to_numpy();V=val[SENSORS];vy=val.f_nv.to_numpy();w=weights(y)
 write_json(EVIDENCE/'row_count_discrepancy.json',discrepancy)
 write_json(EVIDENCE/'class_weights.json',{'formula':'N_train / (5 * n_k)','training_rows':len(y),'training_counts':TRAIN_COUNTS,'weights':w,'fit_index_digest':index_digest(X.index),'one_weighting_mechanism':True})
 configuration={'stage':1,'physical_configuration':'F6','seed':SEED,'training_interval':TRAIN,'selection_interval':BLOCK13,
  'threshold_block14_used':False,'test_predictions_generated':False,'prior_test_exposure':True,'SMOTE':False,
  'feature_policies':{'raw':'Six raw numerical values plus six retained-channel availability indicators.',
  'engineered':'Six imputed raw values plus five deterministic physical derivatives plus six raw-channel availability indicators.'},
  'search_budget':16,'selection':'Highest block-13 macro-F1 per family; ties: hardware macro recall, lower serialized size, then trial identifier.',
  'LR':{'C':[.1,1.],'max_iter':2000,'solver':'lbfgs'},
  'RF':{'depth':[6,10],'n_estimators':100,'min_samples_leaf':20},
  'LightGBM':{'num_leaves_depth':[[15,4],[31,6]],'n_estimators':150,'learning_rate':.05,'min_child_samples':50,'max_bin':127,'reg_lambda':1.,'deterministic':True,'force_col_wise':True},
  'class_weighting':['none','explicit_training_balanced_dictionary'],'threads':2,
  'timing':'Fit wall time; end-to-end ordered validation batch per-row mean from three repeats, not single-row p95.',
  'artifact_size':'Uncompressed Python pickle bytes of complete fitted wrapper/pipeline; not standalone dependency footprint.',
  'forbidden_stages':['seven-configuration ablation','block-14 threshold selection','revised test evaluation','final SHAP','final report']}
 write_json(EVIDENCE/'experiment_configuration.json',configuration)
 manifest=runtime();manifest.update({'training_fit_index_digest':index_digest(X.index),'block13_index_digest':index_digest(V.index),'foundation':foundation_check()});write_json(EVIDENCE/'runtime.json',manifest)
 cache=ROOT/'.cache/stage1/models';cache.mkdir(parents=True,exist_ok=True)
 with threadpool_limits(2):
  rule=EngineeringReference().fit(X,y);rs=rule.score(V)
 write_json(EVIDENCE/'engineering_reference.json',{'physical_configuration':'F6','effective_channels':['vdc1','vdc2','idc1','idc2'],
  'training_fit_index_digest':rule.fit_index_digest_,'normal_training_reference_rows':TRAIN_COUNTS[0],
  'baseline_only_epsilon':{'voltage_V':1.,'current_A':.1,'IQR_denominator':1e-6},
  'block13_hardware_AP':float(average_precision_score(np.isin(vy,[1,2,3]),rs)),
  'five_class_metrics':'Not applicable: binary engineering score only.','threshold':'Deferred; block 14 not accessed for scoring.'})
 rows=[];details={};best={}
 for i,(family,policy,params,weighted) in enumerate(trial_specs(),1):
  trial=f'{family}_{policy}_{i:02d}_'+('weighted' if weighted else 'unweighted');print(f'[{i}/16] Fitting {trial} {params}',flush=True)
  model=F6Model(family,policy,params,w if weighted else None)
  with threadpool_limits(2),warnings.catch_warnings(record=True) as captured:
   warnings.simplefilter('always');t=time.perf_counter();model.fit(X,y);fit=time.perf_counter()-t
   p=model.predict_proba(V);m=evaluate(p,vy);timings=[]
   for _ in range(3):
    t=time.perf_counter();model.predict_proba(V);timings.append(time.perf_counter()-t)
  message=[{'category':type(x.message).__name__,'message':str(x.message)} for x in captured]
  converged=not any(isinstance(x.message,ConvergenceWarning) for x in captured)
  data=pickle.dumps(model,protocol=5);size=len(data)
  row={'trial':trial,'model':family,'weighting':'training_balanced' if weighted else 'unweighted','feature_policy':policy,
   'parameters':json.dumps(params,sort_keys=True),'macro_f1':m['macro_f1'],'weighted_f1':m['weighted_f1'],
   'class1_recall':m['per_class']['1']['recall'],'class2_recall':m['per_class']['2']['recall'],'class3_recall':m['per_class']['3']['recall'],
   'hardware_macro_recall':m['hardware_macro_recall'],'class4_recall':m['per_class']['4']['recall'],'macro_AP':m['macro_AP'],
   'fit_seconds':fit,'batch_mean_ms_per_row':float(np.mean(timings)*1000/len(V)),'model_pickle_bytes':size,
   'physical_channels':6,'numerical_plus_indicator_features':len(model.names()),'converged':converged}
  rows.append(row);details[trial]={'metrics':m,'warnings':message,'parameters':model.pipeline.named_steps['model'].get_params(),
   'class_weights':w if weighted else None,'feature_names':model.names(),'fit_rows':model.fit_rows_,
   'fit_index_digest':model.fit_index_digest_,'prediction_index_digest':index_digest(V.index),'validation_rows':len(V),
   'scaler_fit_rows':int(model.pipeline.named_steps['columns'].named_transformers_['numeric'].named_steps['scale'].n_samples_seen_) if family=='LR' else None,
   'training_medians':model.pipeline.named_steps['columns'].named_transformers_['numeric'].named_steps['median'].statistics_.tolist(),
   'predictor_columns':SENSORS,'prediction_partition':'block13','timing_seconds':timings}
  rank=(row['macro_f1'],row['hardware_macro_recall'],-size)
  if converged and (family not in best or rank>best[family][0]):
   best[family]=(rank,row.copy());(cache/(family+'.pkl')).write_bytes(data)
  write_json(EVIDENCE/'trial_details.json',details)
  with (EVIDENCE/'validation_comparison.csv').open('w',encoding='utf8',newline='') as f:
   writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
  print(f'  macro-F1={m["macro_f1"]:.6f}, hardware recall={m["hardware_macro_recall"]:.6f}, fit={fit:.1f}s',flush=True)
 if set(best)!=set(['LR','RF','LightGBM']):raise RuntimeError('A model family has no converged candidate; review before advancing.')
 selected={family:record[1] for family,record in best.items()}
 winner=sorted(selected.values(),key=lambda z:(-z['macro_f1'],-z['hardware_macro_recall'],z['model_pickle_bytes'],z['trial']))[0]
 write_json(EVIDENCE/'stage1_selection.json',{'per_family':selected,'recommended_stage2_candidate':winner,
  'selection_population':'validation operating block 13 only','block14_threshold_selection':'not performed',
  'test_evaluation':'not performed','sparse_recommendation':'not determined; ablation is not authorized yet',
  'engineering_acceptance':'Not certified by Stage 1 validation metrics or batch-average timing.'})
 from .verification import verify
 print(json.dumps(verify(),indent=2),flush=True)
