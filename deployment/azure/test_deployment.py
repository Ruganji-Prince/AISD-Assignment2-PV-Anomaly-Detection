"""Enforce the approved scope independently of Azure authentication."""
import copy
import json
import unittest
from pathlib import Path
from deployment.azure.deploy import validate_payload, consumption_available

class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads((Path(__file__).parent / "containerapp.json").read_text(encoding="utf8"))

    def test_exact_approved_scope(self):
        self.assertTrue(validate_payload(self.payload))

    def test_cpu_memory_replica_and_image_expansion_rejected(self):
        for field, value in [("cpu", 1), ("memory", "2Gi")]:
            altered = copy.deepcopy(self.payload)
            altered["properties"]["template"]["containers"][0]["resources"][field] = value
            with self.assertRaises(AssertionError): validate_payload(altered)
        for field, value in [("maxReplicas", 2), ("minReplicas", 1)]:
            altered = copy.deepcopy(self.payload)
            altered["properties"]["template"]["scale"][field] = value
            with self.assertRaises(AssertionError): validate_payload(altered)
        altered = copy.deepcopy(self.payload)
        altered["properties"]["template"]["containers"][0]["image"] = "unapproved:latest"
        with self.assertRaises(AssertionError): validate_payload(altered)

    def test_unknown_quota_not_assumed(self):
        with self.assertRaises(RuntimeError): consumption_available({"value": []})
        row = {"name": {"value": "ManagedEnvironmentConsumptionCores"}, "currentValue": 1, "limit": 10}
        self.assertEqual(consumption_available({"value": [row]}), 9)

class CostBoundaryTests(unittest.TestCase):
    def test_unused_compute_grants_cover_exactly_100_hours(self):
        from deployment.azure.costs import estimate
        self.assertEqual(estimate(100000,100)["estimated_compute_and_requests_USD"],0)
        self.assertAlmostEqual(estimate(100000,101)["estimated_compute_and_requests_USD"],.054)
        self.assertAlmostEqual(estimate(100000,720)["estimated_compute_and_requests_USD"],33.48)

    def test_request_grant_boundary(self):
        from deployment.azure.costs import estimate
        self.assertEqual(estimate(2000000,0)["estimated_request_USD"],0)
        self.assertAlmostEqual(estimate(3000000,0)["estimated_request_USD"],.4)

if __name__ == "__main__": unittest.main()
