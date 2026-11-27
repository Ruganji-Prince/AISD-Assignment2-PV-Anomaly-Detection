"""Committed-blob allowlist for the Azure CORS revision; no scientific artifacts changed."""
import argparse
import hashlib
import json
from pathlib import Path
from deployment.azure.prepare_context import FILES,ATTRIBUTION,SECRET,MODEL_SHA,git


def prepare(destination,revision="HEAD"):
    commit=git("rev-parse","--verify",revision+"^{commit}").decode().strip()
    destination=Path(destination)
    if destination.exists():raise ValueError("Use a fresh context directory")
    destination.mkdir(parents=True)
    sources=[v for v in FILES if v!="Dockerfile"]+["deployment/decoupled/Dockerfile","web/azure_app.py","web/static/api.js",*ATTRIBUTION]
    records=[]
    for source in sources:
        data=git("show",commit+":"+source)
        assert not SECRET.search(data),source
        digest=hashlib.sha256(data).hexdigest()
        if source=="models/rf_e4/model.pkl":assert digest==MODEL_SHA
        target="Dockerfile" if source=="deployment/decoupled/Dockerfile" else ATTRIBUTION.get(source,source)
        path=destination/target;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        records.append({"source":source,"path":target,"bytes":len(data),"sha256":digest})
    return {"source_commit":commit,"model_sha256":MODEL_SHA,"files":records,"scope":"Original runtime plus CORS wrapper and API/readiness transport; no credentials, raw CSV, private artifacts or training output."}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("destination",type=Path);parser.add_argument("--revision",default="HEAD");parser.add_argument("--manifest",type=Path,required=True);args=parser.parse_args()
    value=prepare(args.destination,args.revision);args.manifest.write_text(json.dumps(value,indent=2)+"\n",encoding="utf8");print(json.dumps(value,indent=2))

if __name__=="__main__":main()
