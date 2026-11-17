"""Independent semantic checks before test evaluation."""
import unittest
import numpy as np
import pandas as pd
from src.phase2_stage3.common import select_threshold,FrozenPredictor,load_model,BLOCK14
class Semantics(unittest.TestCase):
 def test_threshold_matches_exhaustive(self):
  rng=np.random.default_rng(42);p=rng.dirichlet(np.ones(5),500);y=np.arange(500)%5
  r=select_threshold(p,y);s=p[:,1:4].sum(1);h=np.isin(y,[1,2,3])
  feasible=[]
  for t in np.r_[np.nextafter(s.max(),np.inf),np.unique(s)]:
   a=s>=t;fp=int((a&~h).sum());tp=int((a&h).sum())
   if fp/(~h).sum()<=.01:feasible.append((-tp,fp,-t,t))
  self.assertEqual(r['threshold'],min(feasible)[3])
 def test_ties_and_no_alert(self):
  p=np.tile([.2,.2,.2,.2,.2],(100,1));y=np.arange(100)%5
  r=select_threshold(p,y);self.assertTrue(r['no_alert_sentinel_selected']);self.assertEqual(r['recall'],0);self.assertEqual(r['combined_nonhardware_FPR'],0)
 def test_abstention_counts_miss(self):
  p=np.tile([.98,.005,.005,.005,.005],(100,1));y=np.arange(100)%5;p[np.isin(y,[1,2,3])]=[0,.4,.3,.3,0];p[1]=np.nan
  r=select_threshold(p,y);self.assertAlmostEqual(r['recall'],59/60)
 def test_guard_and_no_fit(self):
  m=load_model('LR__F6');adapter=FrozenPredictor(m,BLOCK14)
  self.assertFalse(hasattr(adapter,'fit'))
  for frame in [pd.DataFrame(np.zeros((1,6)),columns=m.channels,index=[1227337]),pd.DataFrame(np.zeros((1,7)),columns=m.channels+['source_index'],index=[1140571])]:
   with self.assertRaises(ValueError):adapter.predict_proba(frame)
if __name__=='__main__':unittest.main()
