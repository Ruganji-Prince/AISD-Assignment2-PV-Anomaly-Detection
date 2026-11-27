"""CORS contract checks around the unchanged original application."""
import unittest
from fastapi.testclient import TestClient
from web.azure_app import app,trusted_origins
class CORSTests(unittest.TestCase):
    def test_explicit_preflight_and_untrusted_origin(self):
        with TestClient(app) as c:
            for origin,expected in [("https://pv-anomaly-detection-prince-r-k.vercel.app",200),("https://unrelated.invalid",400)]:
                r=c.options("/api/predict",headers={"Origin":origin,"Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"content-type"})
                self.assertEqual(r.status_code,expected)
                self.assertEqual(r.headers.get("access-control-allow-origin"),origin if expected==200 else None)
    def test_validation_response_exposes_timing_without_credentials(self):
        with TestClient(app) as c:
            origin="https://pv-anomaly-detection-prince-r-k.vercel.app"
            r=c.post("/api/predict",json={},headers={"Origin":origin})
            self.assertEqual(r.status_code,422);self.assertEqual(r.headers["access-control-allow-origin"],origin)
            self.assertIn("Server-Timing",r.headers["access-control-expose-headers"])
            self.assertNotIn("access-control-allow-credentials",r.headers)
    def test_wildcards_and_foreign_hosts_rejected(self):
        for value in ['["*"]','["https://unrelated.invalid"]','["https://example.vercel.app/path"]']:
            with self.assertRaises(ValueError):trusted_origins(value)
if __name__=="__main__":unittest.main()
