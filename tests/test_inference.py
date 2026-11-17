import json
import tempfile
import unittest
from pathlib import Path
from src.inference.cli import CHANNELS, LABELS, ROOT, load_model, predict, validate
class InferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = load_model()
        cls.record = json.loads((ROOT/'deployment/example_input.json').read_text())
    def test_schema_rejects_invalid_inputs(self):
        for record in [None, {}, dict(self.record, f_nv=0), dict(self.record, vdc1=True),
                       dict(self.record, idc1=None), dict(self.record, idc2=float('nan')),
                       dict(self.record, vdc2=-1), dict(self.record, idc2='1')]:
            with self.subTest(record=record), self.assertRaises(ValueError): validate(record)
    def test_order_independent_input(self):
        self.assertEqual(validate(self.record), validate(dict(reversed(list(self.record.items())))))
    def test_actual_example_and_pipeline_parity(self):
        import pandas as pd
        output=predict(self.record,self.model)
        expected=json.loads((ROOT/'deployment/example_output.json').read_text())
        self.assertEqual(output,expected)
        self.assertEqual(output['predicted_class'],int(self.model.pipeline.predict(pd.DataFrame([validate(self.record)],columns=CHANNELS))[0]))
    def test_released_observation_examples(self):
        cases=json.loads((ROOT/'deployment/example_cases.json').read_text())
        self.assertEqual(len(cases),5)
        for case in cases:
            with self.subTest(case=case['case']):
                self.assertEqual(predict(case['input'],self.model),case['output'])
    def test_shade_is_not_hardware_failure(self):
        import numpy as np
        class Pipe:
            def predict_proba(self,x):return np.array([[0,0,0,0,1.]])
        class Model: pipeline=Pipe()
        result=predict(self.record,Model())
        self.assertEqual(result['label'],'natural building shade')
        self.assertFalse(result['hardware_fault_class']);self.assertTrue(result['environmental_shade'])
    def test_hash_rejection_before_pickle(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.pkl';p.write_bytes(b'not a pickle')
            with self.assertRaisesRegex(ValueError,'integrity'):load_model(p)
if __name__=='__main__':unittest.main()
