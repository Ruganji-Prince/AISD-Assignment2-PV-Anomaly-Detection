"""Assert actual static artifact boundaries, CSP and API configuration."""
import json
import tempfile
import unittest
from pathlib import Path
from frontend.build import build,AZURE,ASSETS
class StaticTests(unittest.TestCase):
    def test_output_has_only_frontend_files(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"output";report=build(out)
            self.assertEqual(len(report["files"]),9)
            self.assertFalse((out/"functions").exists())
            self.assertTrue(all(Path(r["path"]).suffix in {".json",".html",".js",".css",".svg"} for r in report["files"]))
            self.assertIn(AZURE,(out/"static/config.js").read_text())
            self.assertIn(AZURE,json.loads((out/"config.json").read_text())["routes"][0]["headers"]["Content-Security-Policy"])
    def test_foreign_api_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):build(Path(temp)/"output","https://unrelated.invalid")
    def test_local_dev_explicit_port(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(build(Path(temp)/"output","http://127.0.0.1:8765")["api_base"],"http://127.0.0.1:8765")
if __name__=="__main__":unittest.main()
