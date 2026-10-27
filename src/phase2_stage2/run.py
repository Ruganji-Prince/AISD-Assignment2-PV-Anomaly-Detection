"""Exactly 21 frozen model/configuration fits; validation and resource evaluation only."""
import csv,json,pickle,time,warnings,argparse,collections
import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from threadpoolctl import threadpool_limits
from src.phase2_stage1.evaluation import evaluate
from .contracts import *
from .models import AblationModel
from .resources import measure,protocol
from .selection import pass_flags,select


def save_csv(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def dropout(selected,val):
 """Legacy isolated-position definition applied to block 13 after shortlist freezing."""
 n=len(val);positions=np.sort(np.random.default_rng(SEED).choice(np.arange(0,n,2),size=int(n*.01),replace=False))
 assert len(positions)==328 and np.all(np.diff(positions)>=2)
 record={'seed':SEED,'validation_rows':n,'fraction':.01,'masked_rows':len(positions),'positions_in_block13':positions.tolist(),
  'definition':'Seeded choice without replacement from even local positions; one uniformly selected retained channel per row; shared positions across configurations and shared channel mask within configuration across families.',
  'position_scope':'Block-13 source positions, not timestamps. Isolated positions have no adjacent masked row.',
  'channel_seed':'42 + index of configuration in F6,E5,E4,C3,C2,S4,S2',
  'provenance':'Preserved legacy src/experiments.py isolated mask algorithm; validation population substitutes for test population; no legacy test scores/metrics are read.',
  'changes_selection':False,'shortlist_frozen_before_run':selected['shortlist_before_dropout'],'outcomes':{}}
 for key in selected['shortlist_before_dropout']:
  family,config=key.split('__');cols=CONFIGS[config]
  with (ROOT/'.cache/stage2/models'/(key+'.pkl')).open('rb') as f:model=pickle.load(f)
  X=val[cols];baseline=evaluate(model.predict_proba(X),val.f_nv.to_numpy());altered=X.copy()
  choices=np.random.default_rng(SEED+list(CONFIGS).index(config)).integers(0,len(cols),size=len(positions))
  for j,c in enumerate(cols):altered.iloc[positions[choices==j],j]=np.nan
  p=model.predict_proba(altered);m=evaluate(p,val.f_nv.to_numpy());loss=baseline['macro_f1']-m['macro_f1']
  record['outcomes'][key]={'baseline_macro_f1':baseline['macro_f1'],'dropout_macro_f1':m['macro_f1'],'loss':loss,
   'loss_le_005':loss<=.05,'coverage':m['coverage'],'masked_hardware_rows':int(np.isin(val.f_nv.iloc[positions],[1,2,3]).sum()),
   'channel_choices':choices.tolist(),'metrics':m,'abstention_convention':'All-row recall includes abstentions as misses; model selection remains frozen.'}
  print(f'DROPOUT {key}: loss={loss:.6f}',flush=True)
 write_json(EVIDENCE/'isolated_dropout_validation.json',record)


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');args=parser.parse_args()
 if (EVIDENCE/'stage2_selection.json').exists():raise RuntimeError('Completed selection exists; no silent rerun or overwrite.')
 train,val=load_partitions();source=json.loads((ROOT/'phase2_implementation/stage1/evidence/stage1_selection.json').read_text())
 ledger={f:{c:available_features(c,f) for c in CONFIGS} for f in FAMILIES}
 write_json(EVIDENCE/'feature_availability_by_configuration.json',ledger)
 write_json(EVIDENCE/'measurement_protocol.json',protocol())
 write_json(EVIDENCE/'frozen_stage1_settings.json',{'stage1_selection':source['per_family'],'weights':frozen_weights(),
  'new_hyperparameter_search':False,'selection_population':'block13 only','block14_used':False,'test_used':False,
  'criteria':{'macro_f1':.80,'each_hardware_recall':.90,'delta_s':.05,'max_sparse_channels':4,'p95_ms':10.,'artifact_MiB':10.},
  'remaining_acceptance_criteria':['block14 equipment-alert FPR <= 1%','isolated 1% dropout macro-F1 loss <= .05 for shortlisted candidates','later revised test evaluation'],
  'latency_protocol_frozen_before_results':{'warmups':WARMUPS,'timed_single_calls':TIMED_CALLS,'threads':2},
  'ranking_frozen_before_results':'Best F6/sparse by macro-F1 then hardware macro recall/size; minimum passing by channel count; compromise passes predictive and measured resource conditions then minimizes count/p95/size.'})
 cache=ROOT/'.cache/stage2/models';cache.mkdir(parents=True,exist_ok=True)
 rows=[];classes=[];resources=[];details={}
 with threadpool_limits(2):
  for family in FAMILIES:
   for config,cols in CONFIGS.items():
    key=family+'__'+config;checkpoint=EVIDENCE/'checkpoints'/(key+'.json')
    if checkpoint.exists() and not args.resume:raise RuntimeError('Partial results exist; explicit --resume required.')
    if checkpoint.exists():
     cp=json.loads(checkpoint.read_text());row=cp['summary'];detail=cp['details'];resource=cp['resource'];classrows=cp['class_rows']
     assert cp['model_sha256']==sha(cache/(key+'.pkl'));print('Resuming verified checkpoint '+key,flush=True)
    else:
     print(f'Fitting {key} on {len(train)} training rows; physical channels={len(cols)}',flush=True)
     model=AblationModel(family,config);X=train[cols];V=val[cols]
     with warnings.catch_warnings(record=True) as captured:
      warnings.simplefilter('default');start=time.perf_counter();model.fit(X,train.f_nv.to_numpy());fit=time.perf_counter()-start
      p=model.predict_proba(V);metrics=evaluate(p,val.f_nv.to_numpy())
      assert np.isfinite(p).all() and np.allclose(p.sum(axis=1),1)
      data=pickle.dumps(model,protocol=5);model_path=cache/(key+'.pkl');model_path.write_bytes(data)
      print(f'  validation macro-F1={metrics["macro_f1"]:.6f}; measuring {TIMED_CALLS} single-row predictions',flush=True)
      latency=measure(model,V)
     warning_counts=collections.Counter((type(w.message).__name__,str(w.message)) for w in captured)
     warning_records=[{'category':category,'message':message,'count':count} for (category,message),count in warning_counts.items()]
     convergence=not any(isinstance(w.message,ConvergenceWarning) for w in captured)
     resource={'key':key,'model':family,'configuration':config,'physical_channels':len(cols),'artifact_bytes':len(data),'artifact_MiB':len(data)/2**20,
      'training_seconds':fit,'p50_ms':latency['p50_ms'],'p95_ms':latency['p95_ms'],'p99_ms':latency['p99_ms'],
      'measurement_metadata_reference':'measurement_protocol.json','warmups':latency['warmups'],'timed_calls':latency['timed_calls']}
     row={'key':key,'model':family,'configuration':config,'physical_channels':len(cols),'mathematical_features':len(model.names()),
      'macro_f1':metrics['macro_f1'],'weighted_f1':metrics['weighted_f1'],
      **{'class'+str(k)+'_recall':metrics['per_class'][str(k)]['recall'] for k in [1,2,3,4]},
      'hardware_macro_recall':metrics['hardware_macro_recall'],'macro_AP':metrics['macro_AP'],
      'normal_to_hardware_rate':metrics['normal_classification_false_alarm_rate'],'shade_to_hardware_rate':metrics['shade_classification_false_alarm_rate'],
      'training_seconds':fit,'artifact_MiB':resource['artifact_MiB'],'p50_ms':resource['p50_ms'],'p95_ms':resource['p95_ms'],'converged':convergence}
     classrows=[{'key':key,'model':family,'configuration':config,'class':k,**metrics['per_class'][str(k)]} for k in range(5)]
     detail={'metrics':metrics,'raw_channels':cols,'feature_names':model.names(),'derived_features':ledger[family][config]['engineered_features'],
      'fit_index_digest':model.fit_index_digest_,'fit_rows':model.fit_rows_,'prediction_index_digest':index_digest(val.index),
      'prediction_population':'block13 only','class_weights':frozen_weights(),'estimator_parameters':model.pipeline.named_steps['model'].get_params(),
      'source_estimator_parameters':model.frozen_estimator_params,'warnings':warning_records,'latency':latency,
      'training_medians':model.pipeline.named_steps['columns'].named_transformers_['numeric'].named_steps['median'].statistics_.tolist()}
     cp={'summary':row,'details':detail,'resource':resource,'class_rows':classrows,'model_sha256':sha(model_path)};write_json(checkpoint,cp)
    rows.append(row);classes.extend(classrows);resources.append(resource);details[key]=detail
    save_csv(EVIDENCE/'resource_metrics.csv',resources);save_csv(EVIDENCE/'sensor_ablation_class_metrics.csv',classes)
    write_json(EVIDENCE/'ablation_details.json',details)
    print(f'Finished {key}: F1={row["macro_f1"]:.6f}; p95={row["p95_ms"]:.3f} ms; size={row["artifact_MiB"]:.3f} MiB',flush=True)
 references={f:next(r['macro_f1'] for r in rows if r['model']==f and r['configuration']=='F6') for f in FAMILIES}
 for row in rows:
  row['delta_s']=references[row['model']]-row['macro_f1'];row['criteria']=pass_flags(row)
  row['passes_current_four']=all(row['criteria'][k] for k in ['macro_f1_ge_080','each_hardware_recall_ge_090','delta_le_005','channels_le_4'])
 # CSV cells use explicit booleans, not opaque nested dictionaries.
 flat=[]
 for row in rows:flat.append({k:v for k,v in row.items() if k!='criteria'}|row['criteria'])
 save_csv(EVIDENCE/'sensor_ablation_validation.csv',flat)
 selection=select(rows);selection.update({'frozen_stage1_settings':source['per_family'],'F6_macro_f1_references':references,
  'criteria_note':'The four current predictive/channel conditions are not final engineering acceptance; FPR and final test remain deferred.',
  'selection_population':'validation block 13 only','revised_test_evaluation':False,'block14_threshold_selection':False,'prior_test_exposure':True})
 write_json(EVIDENCE/'stage2_selection.json',selection)
 dropout(selection,val)
 from .diagnostics import generate
 generate(pd.DataFrame(flat))
 from .verification import verify
 print(json.dumps(verify(),indent=2),flush=True)
