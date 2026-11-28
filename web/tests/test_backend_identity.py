"""Azure identity regression: only root presentation differs, never inference."""
import json
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from web.app import app as original_app
from web.azure_app import app,ORIGINS
ROOT=Path(__file__).resolve().parents[2]
SHA="55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb"
class BackendIdentityTests(unittest.TestCase):
    def test_azure_root_and_static_assets(self):
        with TestClient(app) as client:
            r=client.get("/");self.assertEqual(r.status_code,200);self.assertIn("PV Intelligence API",r.text)
            self.assertIn("Random Forest RF E4",r.text);self.assertIn(SHA,r.text)
            self.assertNotIn('id="prediction-form"',r.text);self.assertNotIn('id="step-0"',r.text)
            self.assertIn("default-src 'self'",r.headers['content-security-policy']);self.assertNotIn("unsafe-inline",r.headers['content-security-policy'])
            for name in ['backend.css','backend.js','api.js']:
                asset=client.get('/assets/'+name);self.assertEqual(asset.status_code,200)
    def test_non_azure_root_and_existing_frontend_remain_available(self):
        with TestClient(original_app) as client:
            self.assertIn('id="prediction-form"',client.get('/').text)
            self.assertEqual(client.get('/assets/app.js').content,(ROOT/'web/static/app.js').read_bytes())
            self.assertEqual(client.get('/assets/index.html').content,(ROOT/'web/static/index.html').read_bytes())
    def test_health_examples_and_five_original_predictions(self):
        with TestClient(app) as client:
            r=client.get('/api/health');self.assertEqual(r.status_code,200);self.assertEqual(r.json()['model_sha256'],SHA)
            self.assertEqual(len(client.get('/api/examples').json()),5)
            for case in json.loads((ROOT/'deployment/example_cases.json').read_text()):
                r=client.post('/api/predict',json=case['input']);self.assertEqual(r.status_code,200)
                self.assertTrue(all(r.json()[k]==v for k,v in case['output'].items()))
                self.assertEqual(r.json()['environmental_shade'],case['case']==4)
    def test_exact_configured_origins_and_invalid_input(self):
        with TestClient(app) as client:
            for origin in ORIGINS:
                r=client.options('/api/predict',headers={'Origin':origin,'Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type'})
                self.assertEqual(r.status_code,200);self.assertEqual(r.headers['access-control-allow-origin'],origin)
                self.assertNotIn('access-control-allow-credentials',r.headers)
                r=client.post('/api/predict',json={},headers={'Origin':origin});self.assertEqual(r.status_code,422)
                self.assertEqual(r.headers['access-control-allow-origin'],origin)
            self.assertEqual(client.options('/api/predict',headers={'Origin':'https://unrelated.invalid','Access-Control-Request-Method':'POST'}).status_code,400)
    def test_docs_remain_unexposed_and_no_playground(self):
        with TestClient(app) as client:
            for route in ['/docs','/redoc','/openapi.json']:self.assertEqual(client.get(route).status_code,404)
        self.assertNotIn('requestPrediction', (ROOT/'web/static/backend.js').read_text())
        self.assertNotIn('setInterval',(ROOT/'web/static/backend.js').read_text())
if __name__=='__main__':unittest.main()
