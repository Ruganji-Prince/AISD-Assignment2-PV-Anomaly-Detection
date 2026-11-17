import json
import subprocess
import sys
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.inference.cli import ROOT, SHA256, predict, load_model
from web.app import app

class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=TestClient(app)
        cls.cases=json.loads((ROOT/'deployment/example_cases.json').read_text())
    def test_original_cli_parity_for_all_five_classes(self):
        for case in self.cases:
            with self.subTest(case=case['case']):
                response=self.client.post('/api/predict',json=case['input'])
                self.assertEqual(response.status_code,200,response.text)
                actual=response.json();reference=predict(case['input'])
                for key,value in reference.items():self.assertEqual(actual[key],value)
                self.assertEqual(actual['predicted_class'],case['case'])
                expected='normal' if case['case']==0 else 'environmental_condition' if case['case']==4 else 'hardware_fault'
                self.assertEqual(actual['fault_category'],expected)
                self.assertNotIn('confidence',actual);self.assertNotIn('probabilities',actual)
    def test_health_verifies_model(self):
        response=self.client.get('/api/health');self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['model_sha256'],SHA256)
        self.assertIn(response.json()['python_version'],['3.14.7','3.14.8','3.14.10'])
    def test_rejects_missing_extra_non_numeric_and_negative(self):
        normal=self.cases[0]['input']
        for record in [None,[],{},dict(normal,f_nv=0),dict(normal,vdc1='300'),dict(normal,idc1=True),dict(normal,vdc2=None),dict(normal,idc2=-.1)]:
            with self.subTest(record=record):self.assertEqual(self.client.post('/api/predict',content=json.dumps(record),headers={'Content-Type':'application/json'}).status_code,422)
    def test_rejects_malformed_nonfinite_duplicate_and_oversize(self):
        for body in ['{bad','{"vdc1":NaN,"vdc2":1,"idc1":1,"idc2":1}', '{"vdc1":Infinity,"vdc2":1,"idc1":1,"idc2":1}', '{"vdc1":1,"vdc1":2,"vdc2":1,"idc1":1,"idc2":1}', '{"vdc1":1e999,"vdc2":1,"idc1":1,"idc2":1}']:
            with self.subTest(body=body):self.assertEqual(self.client.post('/api/predict',content=body,headers={'Content-Type':'application/json'}).status_code,422)
        self.assertEqual(self.client.post('/api/predict',content='x'*2049,headers={'Content-Type':'application/json'}).status_code,413)
        self.assertEqual(self.client.post('/api/predict',content='{}').status_code,415)
    def test_outside_observed_range_is_warned_not_clipped(self):
        record=dict(self.cases[0]['input'],vdc1=400)
        response=self.client.post('/api/predict',json=record);self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['range_warnings'],['vdc1'])
        self.assertTrue(response.json()['warnings'])
        self.assertEqual(response.json()['predicted_class'],predict(record)['predicted_class'])
    def test_model_failure_returns_no_prediction_or_private_details(self):
        with patch('web.app.fitted_model',side_effect=ValueError('private model path')):
            for response in [self.client.get('/api/health'),self.client.post('/api/predict',json=self.cases[0]['input'])]:
                self.assertEqual(response.status_code,503)
                self.assertNotIn('predicted_class',response.json());self.assertNotIn('private',response.text)
    def test_homepage_assets_and_security_headers(self):
        for path in ['/','/assets/style.css','/assets/app.js','/assets/favicon.svg']:
            response=self.client.get(path);self.assertEqual(response.status_code,200)
            self.assertEqual(response.headers['X-Content-Type-Options'],'nosniff')
        self.assertIn('PV Anomaly Detection',self.client.get('/').text)
        self.assertEqual(self.client.get('/models/rf_e4/model.pkl').status_code,404)
        self.assertEqual(self.client.get('/data/raw/pv_fault_dataset.csv').status_code,404)
        self.assertEqual(self.client.get('/api/examples').json()[4]['measurements'],self.cases[4]['input'])
    def test_unverified_python_patch_is_rejected(self):
        with patch('src.inference.cli.sys') as runtime:
            runtime.version_info=(3,14,9)
            with self.assertRaisesRegex(RuntimeError,'Verified runtimes'):
                load_model()
    def test_post_is_required(self):
        self.assertEqual(self.client.get('/api/predict').status_code,405)
if __name__=='__main__':unittest.main()
