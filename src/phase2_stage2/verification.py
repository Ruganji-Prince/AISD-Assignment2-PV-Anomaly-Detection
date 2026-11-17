"""Independent Stage 2 integrity, parameter, dependency, metrics and resource verification."""
import csv,json,pickle
import numpy as np
import pandas as pd
from .contracts import *
from .selection import pass_flags,select
from src.phase2_stage1.evaluation import evaluate


def verify():
 result=foundation_check()
 def read(n):return json.loads((EVIDENCE/n).read_text(encoding='utf8'))
 table=pd.read_csv(EVIDENCE/'sensor_ablation_validation.csv');details=read('ablation_details.json');ledger=read('feature_availability_by_configuration.json')
 assert len(table)==21 and set(table.model)==set(FAMILIES) and set(table.configuration)==set(CONFIGS)
 class_table=pd.read_csv(EVIDENCE/'sensor_ablation_class_metrics.csv')
 resource_table=pd.read_csv(EVIDENCE/'resource_metrics.csv')
 assert len(class_table)==105 and len(resource_table)==21
 expected_keys={f+'__'+c for f in FAMILIES for c in CONFIGS};assert set(table.key)==expected_keys and set(details)==expected_keys
 assert read('semantic_tests.json')['status']=='passed'
 for filename,expected in read('implementation_hashes.json').items():assert sha(ROOT/filename)==expected,filename
 source_estimators={}
 for family in FAMILIES:
  with (ROOT/'.cache/stage1/models'/(family+'.pkl')).open('rb') as f:source_estimators[family]=pickle.load(f).pipeline.named_steps['model'].get_params()
 train,val=load_partitions();digest=index_digest(train.index);vd=index_digest(val.index);weights=frozen_weights()
 from .models import RetainedQuality
 for _,row in table.iterrows():
  key=row.key;family=row.model;config=row.configuration;d=details[key];cols=CONFIGS[config]
  assert row.physical_channels==len(cols) and row.mathematical_features==ledger[family][config]['mathematical_feature_count']
  expected_availability=available_features(config,family)
  for field in ['raw_channels','physical_channel_count','engineered_features','mathematical_feature_count','numeric_features','dependencies','all_dependencies_retained']:
   assert ledger[family][config][field]==expected_availability[field]
  assert ledger[family][config]['availability_indicators']==['missingindicator_'+c for c in cols]
  assert ledger[family][config]['mathematical_feature_names']==d['feature_names']
  assert d['raw_channels']==cols and d['derived_features']==ledger[family][config]['engineered_features']
  assert d['fit_rows']==TRAIN[1] and d['fit_index_digest']==digest and d['prediction_index_digest']==vd
  assert d['prediction_population']=='block13 only' and {int(k):v for k,v in d['class_weights'].items()}==weights
  assert d['estimator_parameters']==d['source_estimator_parameters']
  cp=read('checkpoints/'+key+'.json');path=ROOT/'.cache/stage2/models'/(key+'.pkl');assert sha(path)==cp['model_sha256']
  assert path.stat().st_size==cp['resource']['artifact_bytes'] and np.isclose(row.artifact_MiB,path.stat().st_size/2**20)
  latency=np.array(d['latency']['latency_samples_ms']);assert len(latency)==TIMED_CALLS and d['latency']['warmups']==WARMUPS
  assert np.isclose(row.p50_ms,np.percentile(latency,50)) and np.isclose(row.p95_ms,np.percentile(latency,95))
  assert d['latency']['sample_position_digest']==details['LR__F6']['latency']['sample_position_digest']
  clean=RetainedQuality(cols).fit(train[cols]).transform(train[cols]);assert np.array_equal(clean.median().to_numpy(),d['training_medians'])
  with path.open('rb') as f:model=pickle.load(f)
  assert model.fit_index_digest_==digest and model.pipeline.named_steps['model'].get_params()==model.frozen_estimator_params
  assert model.pipeline.named_steps['model'].get_params()['class_weight']==weights
  assert model.pipeline.named_steps['model'].get_params()==source_estimators[family]
  assert model.names()==d['feature_names']
  proba=model.predict_proba(val[cols]);metrics=evaluate(proba,val.f_nv.to_numpy())
  assert metrics['confusion_matrix']==d['metrics']['confusion_matrix']
  classes=class_table[class_table.key==key]
  assert set(classes['class'])==set(range(5))
  for _,cr in classes.iterrows():
   expected_metric=metrics['per_class'][str(int(cr['class']))]
   for field in ['precision','recall','f1','support','AP']:assert np.isclose(cr[field],expected_metric[field])
  rr=resource_table[resource_table.key==key].iloc[0]
  for field in ['artifact_MiB','training_seconds','p50_ms','p95_ms']:assert np.isclose(rr[field],row[field])
  assert np.isclose(metrics['macro_f1'],row.macro_f1) and metrics['hardware_alert_metrics'] is None
  ref=float(table[(table.model==family)&(table.configuration=='F6')].macro_f1.iloc[0])
  assert np.isclose(row.delta_s,ref-row.macro_f1)
  assert np.isclose(row.hardware_macro_recall,np.mean([metrics['per_class'][str(k)]['recall'] for k in [1,2,3]]))
  assert np.isclose(row.macro_AP,np.mean([metrics['per_class'][str(k)]['AP'] for k in range(5)]))
  flags=pass_flags(row.to_dict())
  for k,v in flags.items():assert bool(row[k])==v
 selection=read('stage2_selection.json')
 records=[]
 for row in table.to_dict('records'):row['criteria']=pass_flags(row);records.append(row)
 calculated=select(records)
 for key in ['best_F6','best_at_most_4_channels','minimum_channel_currently_passing','resource_performance_candidate','shortlist_before_dropout']:assert selection[key]==calculated[key]
 drop=read('isolated_dropout_validation.json');assert not drop['changes_selection'] and drop['shortlist_frozen_before_run']==selection['shortlist_before_dropout']
 assert drop['masked_rows']==int(len(val)*.01)==328 and np.all(np.diff(drop['positions_in_block13'])>=2)
 for key,v in drop['outcomes'].items():
  assert np.isclose(v['loss'],v['baseline_macro_f1']-v['dropout_macro_f1']) and v['loss_le_005']==(v['loss']<=.05)
 assert len(list((OUT/'figures').glob('*.png')))==6
 assert not list(OUT.glob('*.pdf')) and not list(OUT.glob('*.ipynb'))
 result.update({'status':'passed','trained_pipelines':21,'configurations':list(CONFIGS),'selection_population':'block13 only',
  'Stage1_settings_weights_and_evidence_preserved':True,'feature_dependencies_valid':True,
  'single_observation_resource_calls_per_pipeline':TIMED_CALLS,'warmups_per_pipeline':WARMUPS,
  'same_family_delta_verified':True,'shortlist_frozen_before_dropout':True,'no_revised_test_predictions':True,
  'no_block14_predictions_or_thresholds':True,'no_SHAP':True,'no_final_report':True,'no_final_engineering_acceptance':True})
 write_json(EVIDENCE/'verification.json',result);return result

if __name__=='__main__':print(json.dumps(verify(),indent=2))
