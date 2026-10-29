"""Required semantic checks for assignment-compliance preprocessing artifacts."""
import ast,json,hashlib,unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from PIL import Image
from .common import *
from .study import fit_training_preprocessor
from src.phase2_stage2.models import build_preprocessor
from src.phase2_stage2.contracts import CONFIGS,available_features
REQUIRED={'Missing-value strategy','Paired-zero handling','Negative irradiance','Negative temperature','Outlier policy','Target encoding','LR scaling','RF scaling','LightGBM preprocessing','Class imbalance','SMOTE decision','Split strategy','Leakage prevention','Correlation analysis','VIF','Mutual information','PCA','Physical feature engineering','Sensor ablation','Explainability','Computational evaluation'}
class ComplianceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.stats=load('phase2_implementation/compliance/Preprocessing_Evidence.json');cls.figures=load('phase2_implementation/compliance/Diagnostic_Inventory.json')
 def test_frozen_split_and_model_ready_shapes(self):
  s=self.stats['splits'];expected={'TRAIN':TRAIN,'VALIDATION':VALIDATION,'TEST':TEST}
  for name,bounds in expected.items():self.assertEqual(s[name]['interval'],list(bounds));self.assertEqual(s[name]['N'],bounds[1]-bounds[0])
  self.assertEqual(self.stats['excluded_separator_intervals'],[[1006129,1056990],[1173967,1227337]])
  for key,cols in [('LR__F6',12),('RF__E4',8),('LightGBM__E4',13)]:
   for name,bounds in expected.items():self.assertEqual(self.stats['model_ready'][key]['partitions'][name]['shape'],[bounds[1]-bounds[0],cols])
 def test_nontraining_fit_is_rejected_before_factory(self):
  for start in [VALIDATION[0],TEST[0]]:
   X=pd.DataFrame(np.zeros((1,6)),columns=SENSORS,index=[start])
   with patch('src.phase2_compliance.study.build_preprocessor') as factory:
    with self.assertRaises(ValueError):fit_training_preprocessor(X,'LR','F6')
    factory.assert_not_called()
 def test_correlation_and_MI_use_training_predictors(self):
  c=self.stats['correlation'];self.assertEqual(c['columns'],SENSORS);self.assertNotIn('f_nv',c['columns']);self.assertEqual(c['population'],'TRAIN');self.assertEqual(c['N'],TRAIN[1])
  frozen=pd.read_csv(ROOT/'phase1_strategy/Training_Correlation.csv',index_col=0);np.testing.assert_allclose(c['matrix'],frozen.to_numpy(),rtol=0,atol=1e-12)
  mi=self.stats['mutual_information'];self.assertEqual(mi['population'],'TRAIN');self.assertEqual(mi['N'],50000);self.assertEqual(set(mi['scores_nats']),set(SENSORS))
  weights=load('phase2_implementation/stage1/evidence/class_weights.json')
  for k,n in mi['class_counts'].items():self.assertLessEqual(abs(n-50000*weights['training_counts'][k]/TRAIN[1]),1)
 def test_PCA_and_scalers_are_fit_on_training_only(self):
  p=self.stats['PCA'];self.assertEqual(p['N'],TRAIN[1]);self.assertEqual(p['population'],'TRAIN');self.assertEqual(p['input_columns'],SENSORS)
  for fit in self.stats['fit_ledger']:self.assertEqual(fit['population'],'TRAIN');self.assertEqual(fit['N'],TRAIN[1]);self.assertEqual(fit['index_digest'],digest(np.arange(*TRAIN)))
  corr=np.asarray(self.stats['correlation']['matrix']);expected=np.linalg.eigvalsh(corr)[::-1]/6
  np.testing.assert_allclose(p['explained_variance_ratio'],expected,rtol=0,atol=1e-10)
 def test_shared_factory_excludes_metadata_and_matches_frozen_policies(self):
  banned={'f_nv','source_position','acquisition_index','block_id','timestamp'}
  for family in ['LR','RF','LightGBM']:
   for config,channels in CONFIGS.items():
    pre=build_preprocessor(family,list(channels));self.assertIsInstance(pre,Pipeline);self.assertNotIn('model',pre.named_steps);columns=pre.named_steps['columns'];self.assertIsInstance(columns,ColumnTransformer)
    numeric=columns.transformers[0][1];self.assertEqual(columns.transformers[0][2],channels);self.assertFalse(banned&set(channels));self.assertEqual('scale' in numeric.named_steps,family=='LR');self.assertEqual('physical' in numeric.named_steps,family=='LightGBM')
    if family=='LightGBM':self.assertEqual(numeric.named_steps['physical'].channels,channels)
  for key,r in self.stats['model_ready'].items():
   family,config=key.split('__');self.assertEqual(r['feature_names'],available_features(config,family)['mathematical_feature_names'])
 def test_strategy_table_covers_every_required_category(self):
  table=pd.read_csv(OUT/'Strategy_vs_Reality.csv',keep_default_na=False);self.assertEqual(set(table.Category),REQUIRED)
  for field in ['Phase 1 planned decision','Actual implementation','Status','Deviation / finding','Rationale / evidence']:self.assertTrue(table[field].str.len().gt(0).all())
  self.assertTrue(set(table.Status)<={'IMPLEMENTED AS PLANNED','REFINED','NOT REQUIRED','DEFERRED WITH JUSTIFICATION'})
  self.assertIn('after frozen',table.set_index('Category').loc['Mutual information','Deviation / finding'])
 def test_executed_notebook_has_all_diagnostics_without_model_calls(self):
  nb=load('phase2_implementation/notebooks/Phase2_Preprocessing_Implementation.ipynb');cells=[c for c in nb['cells'] if c['cell_type']=='code'];self.assertEqual(len(cells),13)
  for c in cells:
   self.assertTrue(c['execution_count']);self.assertFalse(any(o['output_type']=='error' for o in c['outputs']))
   for node in ast.walk(ast.parse(''.join(c['source']))):
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):self.assertNotIn(node.func.attr,['predict','predict_proba','partial_fit'])
  markdown='\n'.join(''.join(c['source']) for c in nb['cells'] if c['cell_type']=='markdown')
  for figure in self.figures:self.assertIn(Path(figure['file']).name,markdown)
  self.assertEqual(self.stats['classifier_training_calls'],0);self.assertFalse(self.stats['classifier_predictions_generated'])
 def test_all_eight_figures_and_retention_policy(self):
  self.assertEqual([r['number'] for r in self.figures],list(range(1,9)))
  for r in self.figures:
   self.assertEqual(r['population'],'TRAINING ONLY');self.assertEqual(sha(ROOT/r['file']),r['sha256'])
   with Image.open(ROOT/r['file']) as im:self.assertEqual(list(im.size),r['dimensions_px']);self.assertLess(abs(im.info['dpi'][0]-300),1)
  self.assertEqual(self.stats['reference_cleaning']['removed_rows'],0);self.assertEqual(self.stats['reference_cleaning']['winsorized_cells'],0);self.assertEqual(self.stats['raw_audit']['paired_zero_observations'],62)
if __name__=='__main__':unittest.main()
