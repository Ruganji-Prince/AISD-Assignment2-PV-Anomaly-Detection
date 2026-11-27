"""Transparent monthly activity scenarios, not billing inferred from HTTP latency."""
import argparse
import datetime
import json
from pathlib import Path


def estimate(requests, replica_hours):
    # Reviewed France Central USD rates, refreshed in Provisioning_Pricing_Refresh.json.
    seconds=replica_hours*3600
    cpu_seconds=.5*seconds;memory_seconds=seconds
    cpu_billable=max(0,cpu_seconds-180000)
    memory_billable=max(0,memory_seconds-360000)
    request_billable=max(0,requests-2000000)
    return {"requests":requests,"allocated_replica_hours_assumed":replica_hours,"vCPU_seconds":cpu_seconds,"GiB_seconds":memory_seconds,
            "vCPU_grant_used":min(cpu_seconds,180000),"GiB_grant_used":min(memory_seconds,360000),
            "estimated_compute_USD":cpu_billable*.000024+memory_billable*.000003,
            "estimated_request_USD":request_billable/1000000*.4,
            "estimated_compute_and_requests_USD":cpu_billable*.000024+memory_billable*.000003+request_billable/1000000*.4}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True);args=parser.parse_args()
    scenarios=[]
    for requests,sessions in [(1000,30),(10000,90),(100000,600)]:
        row=estimate(requests,sessions/3)
        row["assumptions"]={"monthly_sessions":sessions,"allocated_minutes_per_session":20,
            "session_window":"Hypothetical 20-minute allocated replica window including startup, requests, probes and cooldown; zero outside windows", "request_grouping":"Requests distributed inside session windows; other subscription grants unused", "logging":"No persistent log ingestion", "registry":"Public GHCR currently free"}
        scenarios.append(row)
    report={"recorded_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"ESTIMATED_SCENARIOS_NOT_OBSERVED_BILLING",
            "CPU":0.5,"memory_GiB":1,"replicas":[0,1],"scenarios":scenarios,"continuous_30_day_active":estimate(100000,720),
            "excluded":["Internet egress","Taxes/currency conversion","Optional features not provisioned","Other subscription consumption"],
            "limitations":["Actual frequency and idle cooldown change replica lifetime; these are explicit activity assumptions, not a forecast.",
                           "Monthly free grants are shared per subscription and may be partly consumed elsewhere.",
                           "Request latency, CPU utilization and billed allocated replica-seconds are different quantities.",
                           "Student credit can be consumed beyond grants; USD100 starting balance is user-confirmed, not a verified remaining balance.",
                           "Scale-to-zero and a spending-limit policy do not constitute a project-specific small hard spending cap."]}
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print(json.dumps(scenarios,indent=2))

if __name__=="__main__":main()
