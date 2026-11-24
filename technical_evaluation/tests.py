import unittest
import numpy as np,pandas as pd
from .experiments import TrainingClipper,assert_fit_isolated,ProbabilityMap
from .metrics import evaluate,probability_metrics
from .common import *
class AuditTests(unittest.TestCase):
 def test_fit_evaluation_overlap_rejected(self):
  with self.assertRaises(ValueError):assert_fit_isolated([1,2],[2,3])
 def test_clipping_uses_fit_only(self):
  x=pd.DataFrame({'vdc1':[0.,1.,2.,3.]},index=[0,1,2,3]);c=TrainingClipper('iqr').fit(x);upper=c.upper_.copy();z=c.transform(pd.DataFrame({'vdc1':[1e9]},index=[9]));np.testing.assert_array_equal(c.upper_,upper);self.assertLess(z.iloc[0,0],10)
 def test_missing_class_metric_undefined(self):
  p=np.tile([1.,0,0,0,0],(3,1));m=evaluate(p,[0,0,0]);self.assertIsNone(m['per_class']['1']['AP']);self.assertIsNone(m['per_class']['1']['recall']);self.assertIsNone(m['macro_AP'])
 def test_probability_definition(self):
  m=probability_metrics(np.eye(5),np.arange(5));self.assertLess(m['multiclass_Brier'],1e-20);self.assertLess(m['log_loss'],1e-8)
 def test_all_abstentions_are_misses(self):
  m=evaluate(np.full((5,5),np.nan),np.arange(5),.5);self.assertEqual(m['coverage'],0);self.assertEqual(m['hardware_alert_recall'],0);self.assertEqual(sum(r[-1] for r in m['confusion_matrix']),5)
 def test_calibration_support_guard(self):
  with self.assertRaises(ValueError):ProbabilityMap('isotonic').fit(np.eye(5),np.arange(5))
 def test_frozen_protocol_and_original_model(self):freeze_check()
if __name__=='__main__':unittest.main()
