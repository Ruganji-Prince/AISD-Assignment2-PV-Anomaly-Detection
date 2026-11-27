"""Idempotent deployment of the explicitly approved Azure resource scope."""
import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBSCRIPTION = "38a91a22-90a0-45e3-aad6-ce69bf22ed3a"
GROUP = "rg-pv-anomaly-detection"
ENVIRONMENT = "pv-anomaly-env"
APP = "pv-anomaly-detection"
BASE = "https://management.azure.com/subscriptions/" + SUBSCRIPTION
ENV_ID = "/subscriptions/" + SUBSCRIPTION + "/resourceGroups/" + GROUP + "/providers/Microsoft.App/managedEnvironments/" + ENVIRONMENT
IMAGE = "ghcr.io/ruganji-prince/pv-anomaly-detection@sha256:51be78bd92b20af85628dd07009afd0cdad5689353fcf8a621604b7ea82e70e6"
API = "2026-07-01"


def az(*args):
    executable = shutil.which("az")
    if not executable:
        raise RuntimeError("Azure CLI must be installed and authenticated")
    result = subprocess.run([executable, *args, "--output", "json", "--only-show-errors"],
                            capture_output=True, text=True, encoding="utf8", errors="replace")
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout) if result.stdout.strip() else None


def validate_payload(payload):
    assert payload["location"] == "francecentral"
    prop = payload["properties"]
    assert prop["managedEnvironmentId"] == ENV_ID and prop["workloadProfileName"] == "Consumption"
    config, template = prop["configuration"], prop["template"]
    assert config["activeRevisionsMode"] == "Single" and not config.get("secrets") and not config.get("registries")
    ingress = config["ingress"]
    assert ingress["external"] is True and ingress["targetPort"] == 8000 and ingress["allowInsecure"] is False
    assert len(template["containers"]) == 1
    container = template["containers"][0]
    assert container["image"] == IMAGE
    assert container["resources"] == {"cpu": 0.5, "memory": "1Gi"}
    assert template["scale"]["minReplicas"] == 0 and template["scale"]["maxReplicas"] == 1
    assert {p["type"] for p in container["probes"]} == {"Startup", "Readiness", "Liveness"}
    assert {v["name"] for v in container["env"]} <= {"PYTHONDONTWRITEBYTECODE", "PYTHONUNBUFFERED"}
    return True


def assert_environment(environment):
    prop = environment["properties"]
    if prop.get("environmentMode") != "WorkloadProfiles":
        raise RuntimeError("Environment must explicitly be WorkloadProfiles; do not accept Express defaults")
    assert [(v["name"], v["workloadProfileType"]) for v in prop["workloadProfiles"]] == [("Consumption", "Consumption")]
    assert prop.get("appLogsConfiguration", {}).get("logAnalyticsConfiguration") is None
    assert prop.get("appLogsConfiguration", {}).get("destination") in (None, "none")
    return prop["provisioningState"]


def consumption_available(usage):
    rows = [v for v in usage["value"] if v["name"]["value"] == "ManagedEnvironmentConsumptionCores"]
    if len(rows) != 1:
        raise RuntimeError("Consumption-core quota is not yet available; do not assume a default")
    return rows[0]["limit"] - rows[0]["currentValue"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approve-provisioning", action="store_true", help="Explicit acceptance of potentially billable approved resources")
    args = parser.parse_args()
    payload_path = ROOT / "deployment/azure/containerapp.json"
    payload = json.loads(payload_path.read_text(encoding="utf8"))
    validate_payload(payload)
    account = az("account", "show")
    if account["id"] != SUBSCRIPTION or account["name"] != "Azure for Students" or account["state"] != "Enabled":
        raise RuntimeError("The approved enabled Azure for Students subscription must be active")
    print(json.dumps({"subscription": account["name"], "resource_group": GROUP, "region": "francecentral", "image": IMAGE,
                      "cpu": 0.5, "memory_GiB": 1, "replicas": [0, 1], "approval_flag": args.approve_provisioning}))
    if not args.approve_provisioning:
        print("Read-only plan only. No resources changed.")
        return
    if not az("group", "exists", "--name", GROUP):
        az("group", "create", "--name", GROUP, "--location", "francecentral", "--tags", "project=pv-anomaly-detection", "purpose=academic-evaluation")
    group = az("group", "show", "--name", GROUP)
    assert group["location"] == "francecentral"
    environments = az("containerapp", "env", "list", "--resource-group", GROUP)
    matches = [v for v in environments if v["name"] == ENVIRONMENT]
    if not matches:
        az("containerapp", "env", "create", "--name", ENVIRONMENT, "--resource-group", GROUP,
           "--location", "francecentral", "--environment-mode", "WorkloadProfiles", "--enable-workload-profiles", "true", "--logs-destination", "none")
    for _ in range(120):
        environment = az("rest", "--method", "get", "--url", "https://management.azure.com" + ENV_ID + "?api-version=" + API)
        if assert_environment(environment) == "Succeeded":
            break
        time.sleep(5)
    else:
        raise RuntimeError("Environment did not become ready; inspect before retrying")
    apps = az("containerapp", "list", "--resource-group", GROUP)
    existing = [v for v in apps if v["name"] == APP]
    if existing:
        actual = existing[0]["properties"]
        assert actual["template"]["containers"][0]["image"] == IMAGE
        assert actual["template"]["containers"][0]["resources"]["cpu"] == 0.5
        assert actual["template"]["containers"][0]["resources"]["memory"] == "1Gi"
        assert actual["template"]["scale"]["minReplicas"] == 0 and actual["template"]["scale"]["maxReplicas"] == 1
        assert actual["workloadProfileName"] == "Consumption"
        assert actual["configuration"]["activeRevisionsMode"] == "Single"
        assert not actual["configuration"].get("secrets") and not actual["configuration"].get("registries")
        ingress = actual["configuration"]["ingress"]
        assert ingress["external"] is True and ingress["targetPort"] == 8000 and ingress["allowInsecure"] is False
        print("Existing approved app preserved; no PUT or new revision requested.")
        return
    usage = az("rest", "--method", "get", "--url", "https://management.azure.com" + ENV_ID + "/usages?api-version=" + API)
    if consumption_available(usage) < 0.5:
        raise RuntimeError("Verified free consumption-core quota below approved 0.5 vCPU; stop")
    app_url = BASE + "/resourceGroups/" + GROUP + "/providers/Microsoft.App/containerApps/" + APP + "?api-version=" + API
    az("rest", "--method", "put", "--url", app_url, "--body", "@" + str(payload_path))
    print("Approved app request submitted; verify provisioning state, revision and HTTPS before claiming success.")

if __name__ == "__main__":
    main()
