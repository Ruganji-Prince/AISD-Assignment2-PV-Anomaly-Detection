"""Semantic tests of dependencies, quality, availability, metrics, and leakage guards."""
import sys,unittest,json
from pathlib import Path
from itertools import combinations
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from src.phase2_stage1.contracts import SENSORS,DEPENDENCIES,TRAIN_COUNTS,weights,train_only,foundation_check
from src.phase2_stage1.features import PhysicalFeatures,Quality,eligible
from src.phase2_stage1.evaluation import evaluate,hardware_alert_metrics
from src.phase2_stage1.models import F6Model

class Stage1Tests(unittest.TestCase):
 def frame(self):return pd.DataFrame([[10,20,2,3,500,-1],[11,21,3,4,0,0]],columns=SENSORS,dtype=float)
 def test_physical_values_and_every_channel_subset(self):
  X=self.frame();f=PhysicalFeatures().fit(X);z=f.transform(X)
  np.testing.assert_equal(z[:,6:],[[20,60,80,10,1],[33,84,117,10,1]])
  self.assertEqual(len(f.get_feature_names_out()),11)
  for k in range(1,7):
   for subset in combinations(SENSORS,k):
    t=PhysicalFeatures(list(subset)).fit(X[list(subset)]);t.transform(X[list(subset)])
    self.assertEqual(t.derived_,[n for n,p in DEPENDENCIES.items() if set(p)<=set(subset)])
 def test_quality_preserves_fault_values_joint_zeros_and_temperature(self):
  X=self.frame();X.loc[0,'irr']=-.0381;Q=Quality().fit(X);z=Q.transform(X)
  self.assertEqual(z.irr.iloc[0],0);self.assertEqual(z.pvt.iloc[0],-1)
  self.assertEqual(z.irr.iloc[1],0);self.assertEqual(z.pvt.iloc[1],0)
  X.loc[0,'vdc1']=-1;self.assertTrue(np.isnan(Q.transform(X).vdc1.iloc[0]))
  X.loc[0,'irr']=-2;self.assertTrue(np.isnan(Q.transform(X).irr.iloc[0]))
 def test_metadata_and_fit_partition_rejected(self):
  X=self.frame()
  with self.assertRaises(ValueError):Quality().fit(X.assign(source_position=[0,1]))
  with self.assertRaises(ValueError):train_only(X)
  with self.assertRaises(ValueError):PhysicalFeatures(['f_nv']).fit([[0]])
  m=F6Model('LR','raw',{'C':1},None);X.index=[1227337,1227338]
  with self.assertRaisesRegex(ValueError,'block 14/test disabled'):m.predict_proba(X)
  X.index=[1140571,1140572]
  with self.assertRaisesRegex(ValueError,'block 14/test disabled'):m.predict_proba(X)
 def test_training_statistics_not_mutated_by_validation(self):
  X=self.frame();numeric=Pipeline([('median',SimpleImputer()),('physical',PhysicalFeatures()),('scale',StandardScaler())]).fit(X)
  mean=numeric.named_steps['scale'].mean_.copy();median=numeric.named_steps['median'].statistics_.copy()
  numeric.transform(X*1000)
  np.testing.assert_equal(mean,numeric.named_steps['scale'].mean_);np.testing.assert_equal(median,numeric.named_steps['median'].statistics_)
 def test_prefix_availability_and_boundary_reset(self):
  X=pd.DataFrame(np.ones((8,6)),columns=SENSORS);X.loc[1:6,'idc1']=np.nan
  mask=eligible(X,[4]);self.assertEqual(mask.tolist(),[True,True,True,False,True,True,False,True])
  for n in range(1,9):np.testing.assert_equal(eligible(X.iloc[:n],[4]),mask[:n])
 def test_metrics_and_distinct_shade_false_alarm(self):
  y=np.array([0,1,2,3,4]);p=np.eye(5)*.8+.04;m=evaluate(p,y)
  self.assertEqual(m['macro_f1'],1);self.assertEqual(m['hardware_macro_recall'],1)
  self.assertIsNone(m['hardware_alert_metrics']);self.assertEqual(m['macro_AP'],1)
  a=hardware_alert_metrics(np.array([.9,.9,.9,.9,.1]),y,.5)
  self.assertEqual(a['normal_false_alarm_rate'],1);self.assertEqual(a['shade_false_alarm_rate'],0)
  self.assertEqual(a['combined_nonhardware_FPR'],.5)
  p[1]=np.nan;m=evaluate(p,y);self.assertEqual(m['per_class']['1']['recall'],0);self.assertEqual(m['confusion_matrix'][1][5],1)
 def test_weights_exact_training_only(self):
  y=np.concatenate([np.full(n,k,dtype=np.uint8) for k,n in TRAIN_COUNTS.items()]);w=weights(y)
  for k,n in TRAIN_COUNTS.items():self.assertAlmostEqual(w[k]*n,len(y)/5)
  with self.assertRaises(ValueError):weights([0,1,2,3,4])
 def test_foundation(self):self.assertTrue(foundation_check()['all_hashes_match'])

if __name__=='__main__':unittest.main(verbosity=2)
