"""Observe natural zero-replica activation without forcing shutdown or changing scale."""
import argparse
import datetime
import json
import time
from pathlib import Path
import httpx
from deployment.azure.deploy import az, GROUP, APP

ROOT=Path(__file__).resolve().parents[2]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--azure-url",required=True);parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError("Use a fresh output file to preserve observations")
    revision=az("containerapp","show","--name",APP,"--resource-group",GROUP)["properties"]["latestRevisionName"]
    replicas=lambda:az("containerapp","replica","list","--name",APP,"--resource-group",GROUP,"--revision",revision)
    before=replicas()
    report={"recorded_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),"revision":revision,"replicas_before":before,
            "configuration_changed":False,"scope":"One observed request after verified zero replicas, not isolated full platform cold-start timing. Control-plane observations cannot exclude unrelated public traffic."}
    if before:
        report["status"]="NOT_OBSERVED";report["reason"]="Replica count was nonzero; no cold-start claim or forced deactivation."
    else:
        case=json.loads((ROOT/"deployment/example_cases.json").read_text(encoding="utf8"))[0]
        records=[]
        with httpx.Client(timeout=120,follow_redirects=True) as client:
            for phase in ("first_after_observed_zero","subsequent_request"):
                start=time.perf_counter()
                response=client.post(args.azure_url.rstrip("/")+"/api/predict",json=case["input"])
                elapsed=(time.perf_counter()-start)*1000
                row={"phase":phase,"HTTP":response.status_code,"network_ms":elapsed,
                     "server_timing":response.headers.get("server-timing"),"instance":response.headers.get("x-pv-instance"),
                     "model_initialized_in_request":response.headers.get("x-pv-initialized")=="1"}
                if response.status_code==200:
                    row["predicted_class"]=response.json()["predicted_class"]
                    assert row["predicted_class"]==case["output"]["predicted_class"]
                records.append(row)
                if phase=="first_after_observed_zero":report["replicas_after_first_request"]=replicas()
        report["requests"]=records
        report["status"]="OBSERVED_ZERO_TO_RUNNING" if report["replicas_after_first_request"] and all(r["HTTP"]==200 for r in records) else "PARTIAL"
        report["limitations"]="Single activation sample; DNS/TLS, ingress queueing, replica startup/readiness and network are combined. Health probes can initialize the model before the request handler; no component is fabricated or equated to billed CPU."
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
