"""Collect sanitized Azure configuration, quota, metrics and delayed billing evidence."""
import argparse
import datetime
import json
import tempfile
from pathlib import Path
from deployment.azure.deploy import az, BASE, ENV_ID, GROUP, APP, API


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args();out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    env=az("rest","--method","get","--url","https://management.azure.com"+ENV_ID+"?api-version="+API)
    resource_id=BASE.replace("https://management.azure.com","")+"/resourceGroups/"+GROUP+"/providers/Microsoft.App/containerApps/"+APP
    app=az("rest","--method","get","--url","https://management.azure.com"+resource_id+"?api-version="+API)
    ep,ap=env["properties"],app["properties"]
    configuration={"recorded_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),"resource_id":resource_id,
        "region":app["location"],"resource_group":GROUP,"environment":env["name"],"environment_mode":ep.get("environmentMode"),
        "environment_provisioning_state":ep["provisioningState"],"profiles":ep["workloadProfiles"],
        "logs_configuration":ep.get("appLogsConfiguration"),"application":app["name"],"provisioning_state":ap["provisioningState"],
        "running_status":ap.get("runningStatus"),"latest_revision":ap.get("latestRevisionName"),"latest_ready_revision":ap.get("latestReadyRevisionName"),
        "workload_profile":ap["workloadProfileName"],"ingress":ap["configuration"]["ingress"],
        "active_revisions_mode":ap["configuration"]["activeRevisionsMode"],"secret_count":len(ap["configuration"].get("secrets") or []),
        "registry_credentials_configured":bool(ap["configuration"].get("registries")),"template":ap["template"]}
    (out/"Deployment_Configuration.json").write_text(json.dumps(configuration,indent=2)+"\n",encoding="utf8")
    usage={"recorded_UTC":configuration["recorded_UTC"],"allocated":{"vCPU":0.5,"GiB":1,"replicas":[0,1]},"observations":{}}
    for name,command in [
        ("environment_quota",("containerapp","env","list-usages","--name",env["name"],"--resource-group",GROUP)),
        ("revisions",("containerapp","revision","list","--name",APP,"--resource-group",GROUP)),
        ("replicas",("containerapp","replica","list","--name",APP,"--resource-group",GROUP,"--revision",ap["latestRevisionName"])),
        ("metric_definitions",("monitor","metrics","list-definitions","--resource",resource_id))]:
        try:
            value=az(*command)
            if name=="revisions":value=[{"name":v["name"],"properties":{k:v["properties"].get(k) for k in ("active","healthState","provisioningState","runningState","replicas","trafficWeight","createdTime")}} for v in value]
            if name=="replicas":value=[{"name":v["name"],"state":v["properties"].get("runningState"),"createdTime":v["properties"].get("createdTime"),"containers":[{"name":c["name"],"ready":c.get("ready"),"restartCount":c.get("restartCount"),"state":c.get("runningState")} for c in v["properties"].get("containers",[])]} for v in value]
            if name=="metric_definitions":value=[{"name":v["name"]["value"],"unit":v["unit"],"aggregation":v["primaryAggregationType"]} for v in value]
            usage["observations"][name]=value
        except RuntimeError as error:usage["observations"][name]={"status":"UNAVAILABLE","error":str(error)}
    metrics=[]
    for item in usage["observations"].get("metric_definitions",[]):
        if isinstance(item,dict) and item.get("name","").lower() in {"usageNanoCores".lower(),"workingSetBytes".lower(),"replicas","requests","cpuusage","memoryworkingsetbytes"}:
            try:metrics.append(az("monitor","metrics","list","--resource",resource_id,"--metric",item["name"],"--interval","PT1M","--aggregation",item["aggregation"],"--offset","1h"))
            except RuntimeError as error:metrics.append({"name":item["name"],"status":"UNAVAILABLE","error":str(error)})
    usage["metrics"]=metrics
    usage["limitations"]="Azure platform metrics can be delayed, absent or aggregated. Allocated limits, metric observations, local Docker snapshot and billed consumption are different quantities. No persistent monitoring workspace was created."
    (out/"Resource_Usage.json").write_text(json.dumps(usage,indent=2)+"\n",encoding="utf8")
    query={"type":"ActualCost","timeframe":"MonthToDate","dataset":{"granularity":"None","aggregation":{"totalCost":{"name":"PreTaxCost","function":"Sum"}}}}
    billing={"recorded_UTC":configuration["recorded_UTC"],"scope":"Resource group month-to-date ActualCost","student_credit":{"USD":100,"source":"User-confirmed starting balance; remaining credit not independently verified"},"limitations":"Billing can be delayed and free usage may not appear. A zero/empty result is not a final invoice or proof of zero grant consumption."}
    with tempfile.TemporaryDirectory() as temp:
        path=Path(temp)/"query.json";path.write_text(json.dumps(query),encoding="utf8")
        try:billing["response"]=az("rest","--method","post","--url",BASE+"/resourceGroups/"+GROUP+"/providers/Microsoft.CostManagement/query?api-version=2025-03-01","--body","@"+str(path))
        except RuntimeError as error:billing["status"]="UNAVAILABLE";billing["error"]=str(error)
    (out/"Billing_Observation.json").write_text(json.dumps(billing,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"configuration":configuration["provisioning_state"],"URL":"https://"+ap["configuration"]["ingress"]["fqdn"],"metrics_collected":len(metrics),"billing_available":"response" in billing}))

if __name__=="__main__":main()
