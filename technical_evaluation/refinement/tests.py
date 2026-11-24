import unittest,json,time,asyncio,importlib
from unittest.mock import patch
from fastapi.testclient import TestClient
from starlette.requests import Request
from fastapi import HTTPException
from technical_evaluation.common import ROOT,SHA,sha
from src.inference.cli import load_model,predict
from joblib import parallel_backend
class RefinementTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.web=importlib.import_module('web.app');cls.client=TestClient(cls.web.app);cls.case=json.loads((ROOT/'deployment/example_cases.json').read_text())[0]['input']
 def test_timing_and_sequential_preserve_original(self):
  m=load_model();params=m.pipeline[-1].get_params().copy();timing={};expected=predict(self.case,m)
  with parallel_backend('sequential'):actual=predict(self.case,m,timings=timing)
  self.assertEqual(actual,expected);self.assertEqual(m.pipeline[-1].get_params(),params);self.assertEqual(sha(ROOT/'models/rf_e4/model.pkl'),SHA);self.assertEqual(set(timing),{'validation','frame','preprocessing','forest'})
 def test_api_timings_do_not_expose_confidence(self):
  response=self.client.post('/api/predict',json=self.case);self.assertEqual(response.status_code,200)
  for key in ['forest;dur=','preprocessing;dur=','server;dur=']:self.assertIn(key,response.headers['server-timing'])
  self.assertNotIn('probabilities',response.json());self.assertNotIn('confidence',response.json());self.assertIn(response.headers['x-pv-initialized'],['0','1'])
 def test_local_capacity_is_bounded(self):
  gate=self.web._INFERENCE_CAPACITY;gate.acquire();gate.acquire()
  try:
   response=self.client.post('/api/predict',json=self.case);self.assertEqual(response.status_code,503);self.assertEqual(response.headers['retry-after'],'1')
  finally:gate.release();gate.release()
 def test_response_deadline(self):
  def slow(*args):time.sleep(.05);return {}
  with patch('web.app.INFERENCE_TIMEOUT_SECONDS',.001),patch('web.app.guarded_inference',slow):self.assertEqual(self.client.post('/api/predict',json=self.case).status_code,504)
 def test_probability_maps_normalize(self):
  import numpy as np
  from technical_evaluation.experiments import ProbabilityMap
  rng=np.random.default_rng(42);p=rng.dirichlet(np.ones(5),500);y=np.repeat(np.arange(5),100)
  for method in ['sigmoid','isotonic']:
   q=ProbabilityMap(method).fit(p,y).transform(p);np.testing.assert_allclose(q.sum(1),1,atol=1e-12);self.assertTrue(np.isfinite(q).all());self.assertTrue((q>=0).all())
 def test_body_deadline(self):
  async def receive():await asyncio.sleep(.05);return {'type':'http.request','body':b'{}','more_body':False}
  async def check():
   req=Request({'type':'http','method':'POST','path':'/api/predict','headers':[(b'content-type',b'application/json')]},receive);req.state.timing={}
   with patch('web.app.BODY_TIMEOUT_SECONDS',.001):
    with self.assertRaises(HTTPException) as e:await self.web.predict_measurements(req)
    self.assertEqual(e.exception.status_code,408)
  asyncio.run(check())
 def test_model_verification_failure_is_unavailable(self):
  with patch('web.app.fitted_model',side_effect=ValueError('secret local path')):
   response=self.client.post('/api/predict',json=self.case);self.assertEqual(response.status_code,503);self.assertNotIn('secret',response.text)
if __name__=='__main__':unittest.main()
