"""Verify actual Vercel outputs, cross-cloud API/CORS and original-model parity."""
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
import httpx
from src.inference.cli import load_model,predict,SHA256
from deployment.azure.deploy import az,GROUP,APP
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"deployment/decoupled"


def main():
    deployment=json.loads((OUT/"Preview_Deployment.json").read_text(encoding="utf8"))["deployment"]
    preview=deployment["url"];api="https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io"
    node=Path(os.environ["PV_NODE"]);cli=os.environ["PV_VERCEL_CLI"];env=dict(os.environ);env["PATH"]=str(node.parent)+os.pathsep+env["PATH"]
    def vercel(endpoint):
        r=subprocess.run([str(node),cli,"api",endpoint],capture_output=True,text=True,encoding="utf8",errors="replace",env=env,check=True)
        return json.loads(r.stdout)
    metadata=vercel("/v13/deployments/"+deployment["id"]+"?teamId=team_6XiekpkqcG4ZdtMZtV7k3vA6")
    tree=vercel("/v6/deployments/"+deployment["id"]+"/files?teamId=team_6XiekpkqcG4ZdtMZtV7k3vA6")
    def flatten(nodes,prefix=""):
        files=[]
        for node in nodes:
            path=prefix+node["name"]
            files+=flatten(node.get("children",[]),path+"/") if node["type"]=="directory" else [path]
        return files
    files=flatten(tree);assert len(files)==9 and all("/.vercel/output/" in p for p in files)
    assert not any(p.endswith((".py",".pkl",".joblib",".onnx",".npz",".csv")) or ".func/" in p for p in files)
    assert not any(v.get("output") for v in metadata.get("lambdas",[]))
    manifest=json.loads((OUT/"Frontend_Build_Manifest.json").read_text(encoding="utf8"))
    with httpx.Client(timeout=120,follow_redirects=True) as client:
        public=client.get(preview);assert public.status_code==200 and api in public.headers["content-security-policy"]
        for record in manifest["files"]:
            if record["path"]=="config.json":continue
            path=record["path"].removeprefix("static/")
            response=client.get(preview+"/"+path,headers={"x-vercel-skip-toolbar":"1"});assert response.status_code==200
            assert hashlib.sha256(response.content).hexdigest()==record["sha256"],path
        local_route=client.get(preview+"/api/predict");assert local_route.status_code==404
        for _ in range(40):
            r=client.options(api+"/api/predict",headers={"Origin":preview,"Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"content-type"})
            if r.status_code==200 and r.headers.get("access-control-allow-origin")==preview:break
            time.sleep(3)
        else:raise RuntimeError("Azure CORS revision not ready; production remains unchanged")
        health=client.get(api+"/api/health",headers={"Origin":preview});assert health.status_code==200 and health.json()["model_sha256"]==SHA256
        cors=[]
        for origin in [preview,"https://pv-anomaly-detection-prince-r-k.vercel.app","https://unrelated.invalid"]:
            r=client.options(api+"/api/predict",headers={"Origin":origin,"Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"content-type"})
            allowed=origin!="https://unrelated.invalid"
            assert r.status_code==(200 if allowed else 400)
            assert r.headers.get("access-control-allow-origin")== (origin if allowed else None)
            assert "access-control-allow-credentials" not in r.headers
            cors.append({"origin":origin,"HTTP":r.status_code,"allow_origin":r.headers.get("access-control-allow-origin")})
        model=load_model();cases=json.loads((ROOT/"deployment/example_cases.json").read_text(encoding="utf8"));parity=[]
        for case in cases:
            local=predict(case["input"],model);assert local==case["output"]
            r=client.post(api+"/api/predict",json=case["input"],headers={"Origin":preview});assert r.status_code==200
            body=r.json();assert all(body[k]==v for k,v in local.items());assert r.headers["access-control-allow-origin"]==preview
            assert "server-timing" in r.headers and "Server-Timing" in r.headers["access-control-expose-headers"]
            parity.append({"case":case["case"],"input":case["input"],"CLI":local,"Azure":body,"server_timing":r.headers["server-timing"],"instance":r.headers["x-pv-instance"]})
    invalid=[]
    with httpx.Client(timeout=120) as client:
        good=cases[0]["input"]
        for label,value in [("missing",{}),("target",{**good,"f_nv":0}),("negative",{**good,"idc1":-1}),("boolean",{**good,"idc1":True})]:
            response=client.post(api+"/api/predict",json=value,headers={"Origin":preview});assert response.status_code==422 and response.headers["access-control-allow-origin"]==preview
            invalid.append({"case":label,"HTTP":response.status_code})
        for label,body,expected in [("nonfinite",b'{"vdc1":1,"vdc2":1,"idc1":NaN,"idc2":1}',422),("duplicate",b'{"vdc1":1,"vdc1":2}',422),("oversize",b'x'*2049,413)]:
            response=client.post(api+"/api/predict",content=body,headers={"Origin":preview,"Content-Type":"application/json"});assert response.status_code==expected and response.headers["access-control-allow-origin"]==preview
            invalid.append({"case":label,"HTTP":response.status_code})
    actual=az("containerapp","show","--name",APP,"--resource-group",GROUP)["properties"]
    c=actual["template"]["containers"][0]
    assert c["resources"]["cpu"]==.5 and c["resources"]["memory"]=="1Gi"
    assert actual["template"]["scale"]["minReplicas"]==0 and actual["template"]["scale"]["maxReplicas"]==1
    result={"status":"VERIFIED","frontend":preview,"deployment_id":deployment["id"],"actual_deployment_files":files,"static_files":9,"served_asset_hashes_verified":8,"inference_functions":0,"model_artifacts":0,"Python_runtime_files":0,"Vercel_api_predict_HTTP":404,"build_output_records":len(metadata.get("lambdas",[])),"build_function_outputs":[],"Azure":api,"Azure_revision":actual["latestReadyRevisionName"],"Azure_image":c["image"],"Azure_resources":c["resources"],"scale":actual["template"]["scale"],"CORS":cors,"five_prediction_parity":parity,"live_invalid_checks":invalid,"model_sha256":SHA256,"asset_hash_method":"Provider-documented x-vercel-skip-toolbar request header excludes platform preview-feedback HTML injection; app assets otherwise unchanged. Default preview CSP blocks that optional external toolbar.","scope":"Real HTTPS previews and Azure inference; fixed historical TEST cases verify deployment consistency only."}
    (OUT/"Frontend_Deployment_Verification.json").write_text(json.dumps({k:v for k,v in result.items() if k not in ["five_prediction_parity","CORS"]},indent=2)+"\n",encoding="utf8")
    (OUT/"Cross_Cloud_Integration_Verification.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"status":"VERIFIED","frontend":preview,"files":len(files),"functions":0,"five_predictions":5,"Azure_revision":result["Azure_revision"]}))

if __name__=="__main__":main()
