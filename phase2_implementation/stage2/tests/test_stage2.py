"""Semantic sparse-channel, frozen-estimator, metric and shortlist tests."""
import sys,unittest,json
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from src.phase2_stage2.contracts import *
from src.phase2_stage2.models import AblationModel,RetainedQuality
from src.phase2_stage2.selection import select,pass_flags
from src.phase2_stage1.features import PhysicalFeatures,eligible

class Stage2Tests(unittest.TestCase):
 def test_foundation(self):self.assertTrue(foundation_check()['all_hashes_match'])
 def test_exact_seven_configurations(self):
  self.assertEqual(list(CONFIGS),['F6','E5','E4','C3','C2','S4','S2']);self.assertEqual([len(v) for v in CONFIGS.values()],[6,5,4,3,2,4,2])
 def test_dependency_gating_and_counts(self):
  expected={'F6':['P1','P2','P_total','V_diff','I_diff'],'E5':['P1','P2','P_total','V_diff','I_diff'],
   'E4':['P1','P2','P_total','V_diff','I_diff'],'C3':['I_diff'],'C2':['I_diff'],'S4':['P1'],'S2':['P1']}
  for c,cols in CONFIGS.items():
   X=pd.DataFrame(np.arange(1,len(cols)*3+1).reshape(3,len(cols)),columns=cols,dtype=float)
   t=PhysicalFeatures(cols).fit(X);self.assertEqual(t.derived_,expected[c]);self.assertEqual(t.transform(X).shape[1],len(cols)+len(expected[c]))
   self.assertEqual(available_features(c,'LightGBM')['mathematical_feature_count'],2*len(cols)+len(expected[c]))
   self.assertEqual(available_features(c,'LR')['engineered_features'],[])
   self.assertEqual(available_features(c,'LR')['availability_indicators'],['missingindicator_'+x for x in cols])
   self.assertEqual(available_features(c,'LightGBM')['mathematical_feature_names'],['numeric__'+x for x in cols+expected[c]]+['missing__missingindicator_'+x for x in cols])
 def test_quality_without_removed_irradiance_or_temperature(self):
  X=pd.DataFrame({'idc1':[1.,-1.],'idc2':[2.,3.]});q=RetainedQuality(['idc1','idc2']).fit(X);z=q.transform(X)
  self.assertTrue(np.isnan(z.idc1.iloc[1]));self.assertEqual(list(z),['idc1','idc2'])
  with self.assertRaises(ValueError):q.transform(X.assign(irr=500.))
 def test_index_and_stage_guards(self):
  X=pd.DataFrame(np.ones((2,2)),columns=CONFIGS['C2']);X.index=[BLOCK13[0],BLOCK13[0]+1]
  schema(X,CONFIGS['C2'])
  with self.assertRaises(ValueError):schema(X.assign(block_id=13),CONFIGS['C2'])
  with self.assertRaises(ValueError):schema(X,CONFIGS['C2'],training=True)
  m=AblationModel('LR','C2')
  for indices in [[1140571,1140572],[1227337,1227338]]:
   X.index=indices
   with self.assertRaisesRegex(ValueError,'block 14 and test disabled'):m.predict_proba(X)
 def test_frozen_weights_and_estimator_settings(self):
  for family in FAMILIES:
   model=AblationModel(family,'S2');self.assertEqual(model.pipeline.named_steps['model'].get_params(),model.frozen_estimator_params)
   self.assertEqual(model.frozen_estimator_params['class_weight'],frozen_weights())
  self.assertEqual(AblationModel('LR','S2').frozen_estimator_params['C'],1.)
  self.assertEqual(AblationModel('RF','S2').frozen_estimator_params['max_depth'],10)
  self.assertEqual(AblationModel('LightGBM','S2').frozen_estimator_params['num_leaves'],31)
 def test_selection_minimizes_channels_among_passing_not_top_score(self):
  def row(key,n,f1,recall,delta):
   d={'key':key,'model':'LR','configuration':key.split('__')[1],'physical_channels':n,'macro_f1':f1,
    'hardware_macro_recall':recall,'class1_recall':recall,'class2_recall':recall,'class3_recall':recall,
    'delta_s':delta,'artifact_MiB':.01,'p95_ms':5.,'converged':True};d['criteria']=pass_flags(d);return d
  rows=[row('LR__F6',6,.90,.96,0),row('LR__E4',4,.89,.95,.01),row('LR__C2',2,.86,.93,.04),row('LR__S2',2,.95,.2,-.05)]
  s=select(rows);self.assertEqual(s['best_at_most_4_channels'],'LR__S2');self.assertEqual(s['minimum_channel_currently_passing'],'LR__C2')
  self.assertFalse(s['final_engineering_acceptance'])
 def test_dropout_positions_and_prefix(self):
  n=32800;pos=np.sort(np.random.default_rng(SEED).choice(np.arange(0,n,2),size=int(n*.01),replace=False))
  self.assertEqual(len(pos),328);self.assertTrue((np.diff(pos)>=2).all())
  X=pd.DataFrame(np.ones((8,2)),columns=['idc1','idc2']);X.loc[2,'idc1']=np.nan
  self.assertTrue(eligible(X,()).all())

if __name__=='__main__':unittest.main(verbosity=2)
