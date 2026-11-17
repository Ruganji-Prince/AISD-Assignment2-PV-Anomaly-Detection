"""Independent Phase 2 Stage 1 evidence and leakage checks; never trains models."""
import csv,json,re,ast
import numpy as np
import pandas as pd
from .contracts import *
from .evaluation import evaluate

def verify():
 result=foundation_check()
 def read(name):return json.loads((EVIDENCE/name).read_text(encoding='utf8'))
 d=read('row_count_discrepancy.json');w=read('class_weights.json');cfg=read('experiment_configuration.json');trials=read('trial_details.json')
 assert d['thresholds']['irr_ge_100']['N']==515958 and d['thresholds']['irr_lt_100']['N']==857840
 assert {int(k):v for k,v in d['thresholds']['irr_ge_100']['class_counts'].items()}==PAPER_COUNTS
 expected={k:1006129/(5*n) for k,n in TRAIN_COUNTS.items()};assert {int(k):v for k,v in w['weights'].items()}==expected
 assert cfg['physical_configuration']=='F6' and not cfg['threshold_block14_used'] and not cfg['test_predictions_generated']
 assert read('semantic_tests.json')['status']=='passed'
 assert read('dependency_smoke_test.json')['status']=='passed'
 code_hashes=read('implementation_hashes.json')
 for filename,expected_hash in code_hashes.items():assert sha(ROOT/filename)==expected_hash,filename
 assert len(trials)==16
 rows=pd.read_csv(EVIDENCE/'validation_comparison.csv');assert len(rows)==16 and set(rows.model)=={'LR','RF','LightGBM'}
 assert rows.physical_channels.eq(6).all()
 expected_digest=index_digest(np.arange(*TRAIN));vd=index_digest(np.arange(*BLOCK13))
 for name,t in trials.items():
  assert t['fit_index_digest']==expected_digest and t['prediction_index_digest']==vd
  assert t['fit_rows']==1006129 and t['validation_rows']==32800 and t['predictor_columns']==SENSORS
  assert t['prediction_partition']=='block13' and t['metrics']['hardware_alert_metrics'] is None
  assert t['class_weights'] is None or {int(k):v for k,v in t['class_weights'].items()}==expected
  assert len(t['training_medians'])==6 and np.isfinite(t['training_medians']).all()
  assert t['parameters']['class_weight']==t['class_weights']
  assert len(t['feature_names'])==(17 if '_engineered_' in name else 12)
  assert t['scaler_fit_rows'] in [None,1006129]
  assert not set(['source_position','acquisition_index','block_id','f_nv','timestamp'])&set(t['feature_names'])
  m=t['metrics'];cm=np.array(m['confusion_matrix']);supports=np.array([m['per_class'][str(k)]['support'] for k in range(5)])
  assert np.array_equal(cm.sum(axis=1),supports) and supports.sum()==32800
  assert np.isclose(m['weighted_f1'],sum(m['per_class'][str(k)]['f1']*supports[k] for k in range(5))/32800)
  assert np.isclose(m['macro_f1'],np.mean([m['per_class'][str(k)]['f1'] for k in range(5)]))
  assert np.isclose(m['macro_AP'],np.mean([m['per_class'][str(k)]['AP'] for k in range(5)]))
  assert np.isclose(m['hardware_macro_recall'],np.mean([m['per_class'][str(k)]['recall'] for k in [1,2,3]]))
 selection=read('stage1_selection.json')
 for family,selected in selection['per_family'].items():
  available=rows[(rows.model==family)&rows.converged].sort_values(['macro_f1','hardware_macro_recall','model_pickle_bytes','trial'],ascending=[False,False,True,True])
  assert selected['trial']==available.iloc[0].trial
 # Independently verify learned raw medians against the frozen training rows only.
 training=pd.read_csv(ROOT/'data/raw/pv_fault_dataset.csv',nrows=TRAIN[1],float_precision='round_trip')
 from .features import Quality
 clean=Quality().fit(training[SENSORS]).transform(training[SENSORS])
 medians=clean.median().to_numpy()
 for t in trials.values():assert np.allclose(t['training_medians'],medians,rtol=0,atol=0)
 validation=pd.read_csv(ROOT/'data/raw/pv_fault_dataset.csv',skiprows=range(1,BLOCK13[0]+1),nrows=BLOCK13[1]-BLOCK13[0],float_precision='round_trip')
 validation.index=np.arange(*BLOCK13)
 assert counts(validation.f_nv)==BLOCK13_COUNTS
 import pickle
 for family,record in selection['per_family'].items():
  with (ROOT/'.cache/stage1/models'/(family+'.pkl')).open('rb') as f:model=pickle.load(f)
  assert model.fit_index_digest_==expected_digest and model.fit_rows_==TRAIN[1]
  assert model.policy==record['feature_policy']
  assert len(model.names())==record['numerical_plus_indicator_features']
  assert model.class_weights==(expected if record['weighting']=='training_balanced' else None)
  est=model.pipeline.named_steps['model']
  assert list(est.classes_)==list(range(5))
  assert est.get_params()['class_weight']==model.class_weights
  probabilities=model.predict_proba(validation[SENSORS])
  assert np.isfinite(probabilities).all() and np.allclose(probabilities.sum(axis=1),1)
  recomputed=evaluate(probabilities,validation.f_nv.to_numpy())
  assert np.isclose(recomputed['macro_f1'],record['macro_f1'],rtol=0,atol=1e-12)
  assert recomputed['confusion_matrix']==trials[record['trial']]['metrics']['confusion_matrix']
 for feature,parents in DEPENDENCIES.items():assert set(parents)<=set(SENSORS)
 ledger=json.loads((OUT/'Feature_Dependencies.json').read_text(encoding='utf8'));assert ledger['dependencies']==DEPENDENCIES
 broken=[]
 for p in OUT.rglob('*.md'):
  for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf8')):
   if '://' not in link and not link.startswith('#') and not (p.parent/link.split('#')[0]).exists():broken.append(str(p.name)+': '+link)
 assert not broken,broken
 assert not list(OUT.rglob('*.png')) and not list(OUT.rglob('*.ipynb'))
 result.update({'status':'passed','F6_trials':16,'weight_provenance':'training only','selection_partition':'block13',
  'block14_threshold_selection':False,'revised_test_evaluation':False,'full_sensor_ablation':False,
  'final_SHAP':False,'final_report_generated':False,'prior_test_exposure_disclosed':True,
  'phase1_verifier_unchanged':True,'large_models_location':'ignored .cache/stage1/models',
  'notes':'Pipeline fit-index/evidence checks and semantic tests passed; model probabilities are validation-only.'})
 write_json(EVIDENCE/'verification.json',result);return result

if __name__=='__main__':print(json.dumps(verify(),indent=2))
