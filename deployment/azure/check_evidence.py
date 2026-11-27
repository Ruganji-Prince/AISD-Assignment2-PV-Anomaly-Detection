"""Read-only integrity and benchmark-recomputation acceptance checks."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path
import numpy as np
from deployment.azure.benchmark import stats

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"deployment/azure"


def main():
    manifest=json.loads((BASE/"Submission_Protection.json").read_text(encoding="utf8"))
    revision=manifest["submission_commit"]
    bad=[]
    for name,digest in manifest["protected_files"].items():
        data=(ROOT/name).read_bytes()
        # Repository text checkout can differ only in newline convention; validate protected Git blobs separately.
        blob=subprocess.check_output(["git","show",revision+":"+name],cwd=ROOT)
        if hashlib.sha256(blob).hexdigest()!=digest or data.replace(b"\r\n",b"\n")!=blob.replace(b"\r\n",b"\n"):
            bad.append(name)
    assert not bad,bad
    summary=json.loads((BASE/"live/Latency_Summary.json").read_text(encoding="utf8"))
    with (BASE/"live/Latency_Benchmark.csv").open(encoding="utf8",newline="") as stream:rows=list(csv.DictReader(stream))
    assert len(rows)==90
    comparisons=0
    for platform in ("Azure","Vercel"):
        for phase in ("sequential","concurrency2"):
            selected=[v for v in rows if v["platform"]==platform and v["phase"]==phase]
            expected=summary["platforms"][platform][phase]
            assert len(selected)==expected["requests"]
            good=[v for v in selected if v["HTTP"]=="200" and v["correct_class"]=="True"]
            assert len(good)==expected["successes"]
            actual=stats([float(v["network_ms"]) for v in selected])
            for key,value in actual.items():assert abs(value-expected["network_all"][key])<1e-8
            warm=[v for v in good if v["model_initialized"]!="True"]
            for component,reference in expected["warm_server_components"].items():
                actual=stats([float(v[component]) for v in warm if v[component]!=""])
                for key,value in actual.items():assert abs(value-reference[key])<1e-8
                comparisons+=1
    model=BASE/"../../models/rf_e4/model.pkl"
    assert hashlib.sha256(model.read_bytes()).hexdigest()=="55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb"
    print(json.dumps({"status":"PASS","original_submission_files_protected":len(manifest["protected_files"]),"benchmark_CSV_rows":len(rows),"component_statistic_groups_recomputed":comparisons,"model_hash_unchanged":True}))

if __name__=="__main__":main()
