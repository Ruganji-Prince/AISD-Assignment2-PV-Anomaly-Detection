"""Verify local/API/cloud original-model parity and public deployment contracts."""
import argparse
import csv
import datetime
import hashlib
import json
import subprocess
from pathlib import Path
import httpx
from fastapi.testclient import TestClient
from src.inference.cli import load_model, predict, SHA256
from web.app import app

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "940f5e2ca116c5413428348faa82b77bca3915c3"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--azure-url",required=True)
    parser.add_argument("--vercel-url",default="https://pv-anomaly-detection-prince-r-k.vercel.app")
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args();out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    if (out/"Deployment_Verification.json").exists():raise ValueError("Use a fresh output directory; preserve prior evidence")
    cases=json.loads((ROOT/"deployment/example_cases.json").read_text(encoding="utf8"));model=load_model();rows=[];report={}
    with TestClient(app) as local:
        for case in cases:
            cli=predict(case["input"],model);response=local.post("/api/predict",json=case["input"])
            assert cli==case["output"] and response.status_code==200
            assert all(response.json()[k]==v for k,v in cli.items())
            rows.append({"platform":"Local CLI and FastAPI","case":case["case"],"reference_class":cli["predicted_class"],"predicted_class":response.json()["predicted_class"],"match":True,"model_sha256":SHA256})
    for platform,url in (("Azure",args.azure_url),("Vercel",args.vercel_url)):
        assert url.startswith("https://")
        with httpx.Client(base_url=url.rstrip("/"),timeout=90,follow_redirects=True) as client:
            health=client.get("/api/health");assert health.status_code==200 and health.json()["model_sha256"]==SHA256
            page=client.get("/");assert page.status_code==200
            for key,expected in (("x-content-type-options","nosniff"),("x-frame-options","DENY")):
                assert page.headers[key]==expected
            assert "default-src 'self'" in page.headers["content-security-policy"]
            assets=[]
            for path in ("index.html","app.js","style.css","scenarios.js","explanations.js","favicon.svg"):
                response=page if path=="index.html" else client.get("/assets/"+path)
                original=subprocess.check_output(["git","show",SOURCE+":web/static/"+path],cwd=ROOT)
                assert response.status_code==200 and hashlib.sha256(response.content).digest()==hashlib.sha256(original).digest()
                assets.append({"path":path,"sha256":hashlib.sha256(original).hexdigest(),"exact_original_bytes":True})
            parity=[]
            for case in cases:
                response=client.post("/api/predict",json=case["input"]);assert response.status_code==200
                value=response.json();assert all(value[k]==v for k,v in case["output"].items())
                assert "probabilities" not in value and "confidence" not in value
                assert response.headers.get("server-timing")
                assert response.headers["cache-control"]=="no-store"
                parity.append({"case":case["case"],"input":case["input"],"reference_class":case["output"]["predicted_class"],"output":value,"server_timing":response.headers["server-timing"]})
                rows.append({"platform":platform,"case":case["case"],"reference_class":case["output"]["predicted_class"],"predicted_class":value["predicted_class"],"match":True,"model_sha256":value["model_sha256"]})
            good=cases[0]["input"];invalid=[]
            for name,value in (("missing",{}),("target",{**good,"f_nv":0}),("negative",{**good,"idc1":-1}),
                               ("boolean",{**good,"idc1":True}),("text",{**good,"idc1":"1"}),("null",{**good,"idc1":None})):
                response=client.post("/api/predict",json=value);assert response.status_code==422
                invalid.append({"case":name,"HTTP":response.status_code})
            for name,body,expected in (("nonfinite",b'{"vdc1":1,"vdc2":1,"idc1":NaN,"idc2":1}',422),
                                       ("duplicate",b'{"vdc1":1,"vdc1":2}',422),("malformed",b'{',422),("oversize",b'x'*2049,413)):
                response=client.post("/api/predict",content=body,headers={"Content-Type":"application/json"})
                assert response.status_code==expected,(platform,name,response.status_code)
                invalid.append({"case":name,"HTTP":response.status_code})
            assert client.get("/api/predict").status_code==405
            report[platform]={"URL":url,"health":health.json(),"assets":assets,"reference_cases":parity,"invalid_checks":invalid,"GET_predict_HTTP":405,"HTTPS_certificate_verified":True,"timing_headers":True,"no_probability_or_calibrated_confidence_exposed":True}
    result={"status":"VERIFIED","recorded_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),"model_sha256":SHA256,"platforms":report,
            "local_CLI_and_FastAPI_cases":5,"cloud_cases_each":5,"inference_decision":"Original multiclass argmax; class 4 environmental shade, not hardware failure",
            "reference_scope":"Five fixed historically exposed TEST observations demonstrate deployment consistency, not independent accuracy or generalization.",
            "probability_scope":"Public APIs do not expose probabilities; no fabricated public probability-parity claim. Container 200-row numerical parity is separately recorded.",
            "deadline_capacity_scope":"Existing local automated tests exercise deadlines/capacity; live concurrency-two behavior is measured separately, without deliberate overload or slow-request attacks."}
    (out/"Deployment_Verification.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    with (out/"Prediction_Parity.csv").open("w",newline="",encoding="utf8") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps({"status":"VERIFIED","local_cases":5,"Azure_cases":5,"Vercel_cases":5,"assets_each":6,"invalid_cases_each":10,"model_sha256":SHA256}))

if __name__ == "__main__":main()
