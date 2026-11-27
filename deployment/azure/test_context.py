"""Safety tests for the publication context; no model fitting or cloud writes."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from deployment.azure.prepare_context import FILES, MODEL_SHA, SECRET, blob, prepare

class ContextTests(unittest.TestCase):
    def test_unapproved_path_rejected(self):
        for path in (".env.local", "data/raw/pv_fault_dataset.csv", "../credentials.json"):
            with self.assertRaises(ValueError):
                blob("HEAD", path)

    def test_original_model_hash(self):
        self.assertEqual(hashlib.sha256(blob("HEAD", "models/rf_e4/model.pkl")).hexdigest(), MODEL_SHA)

    def test_context_exact_and_existing_destination_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "context"
            report = prepare(dest)
            actual = {p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file()}
            self.assertEqual(actual, {v["path"] for v in report["files"]})
            self.assertNotIn("data/raw/pv_fault_dataset.csv", actual)
            with self.assertRaises(ValueError):
                prepare(dest)

    def test_secret_detection(self):
        self.assertTrue(SECRET.search(b"ghp_" + b"a" * 36))
        self.assertTrue(SECRET.search(b"-----BEGIN PRIVATE KEY-----"))
        self.assertFalse(SECRET.search(b"GITHUB_TOKEN is provided by the workflow environment"))

if __name__ == "__main__":
    unittest.main()
