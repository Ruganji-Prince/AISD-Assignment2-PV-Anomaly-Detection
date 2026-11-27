"""Matched, bounded HTTP benchmarking; never changes a model or scientific result."""
import argparse
import asyncio
import csv
import datetime
import json
import platform
import re
import time
from pathlib import Path
import httpx
import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def stats(values):
    a = np.asarray(values, dtype=float)
    if not len(a): return None
    return {"N": len(a), "min_ms": float(a.min()), "max_ms": float(a.max()),
            "mean_ms": float(a.mean()), "std_ms": float(a.std(ddof=1)) if len(a)>1 else 0.0,
            "p50_ms": float(np.quantile(a,.5)), "p95_ms": float(np.quantile(a,.95)), "p99_ms": float(np.quantile(a,.99))}


async def benchmark(urls):
    sample = json.loads((ROOT / "deployment/example_cases.json").read_text(encoding="utf8"))[0]
    records = []
    clients = {name: httpx.AsyncClient(base_url=url.rstrip("/"), timeout=60, follow_redirects=True,
               limits=httpx.Limits(max_connections=2,max_keepalive_connections=2)) for name,url in urls.items()}
    async def one(name, phase, index):
        start = time.perf_counter()
        record = {"platform": name, "phase": phase, "request": index, "HTTP": 0, "correct_class": False}
        try:
            response = await clients[name].post("/api/predict",json=sample["input"])
            record["HTTP"] = response.status_code
            record["server_timing_ms"] = {k:float(v) for k,v in re.findall(r"([a-z_]+);dur=([0-9.]+)",response.headers.get("server-timing",""))}
            record["instance"] = response.headers.get("x-pv-instance")
            record["model_initialized"] = response.headers.get("x-pv-initialized") == "1"
            if response.status_code == 200:
                result=response.json()
                record["correct_class"] = result["predicted_class"] == sample["output"]["predicted_class"]
                record["model_sha256"] = result["model_sha256"]
        except (httpx.HTTPError, ValueError, KeyError) as error:
            record["error"] = type(error).__name__
        record["network_ms"] = (time.perf_counter()-start)*1000
        records.append(record)
    try:
        # Same client configuration and three unmeasured warmup requests on each platform.
        for i in range(3):
            for name in urls: await one(name,"warmup",i)
        for i in range(30):
            order=list(urls) if i%2==0 else list(urls)[::-1]
            for name in order: await one(name,"sequential",i)
        for i in range(0,12,2):
            order=list(urls) if i%4==0 else list(urls)[::-1]
            for name in order: await asyncio.gather(one(name,"concurrency2",i),one(name,"concurrency2",i+1))
    finally:
        for client in clients.values(): await client.aclose()
    result={"recorded_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),"URLs":urls,
            "client":{"OS":platform.platform(),"python":platform.python_version(),"timezone_context":"Africa/Johannesburg",
                      "physical_egress_location":"Not geolocated; no claim of a Rwanda measurement location", "HTTP_library":"httpx "+httpx.__version__},
            "protocol":{"warmups_per_platform":3,"measured_per_platform":42,"sequential":30,"concurrency2":12,
                        "payload":"Fixed normal reference case 0; identical JSON on both platforms", "ordering":"Alternating platform order, same client and network", "quantiles":"numpy linear quantile; sample standard deviation ddof=1"},
            "platforms":{},"requests":records,"engineering_complete_path_target_ms":10,
            "limitations":["42 measured requests/platform cannot establish tail reliability; p99 is sample-sensitive.",
                           "Server timing ends at response headers and excludes network, response transfer and pre-application platform startup.",
                           "X-PV-Initialized identifies model-cache loading, not confirmed full platform cold start.",
                           "Wall-clock HTTP latency is not billed CPU or billed replica lifetime."]}
    for name in urls:
        result["platforms"][name]={}
        for phase in ("sequential","concurrency2"):
            rows=[r for r in records if r["platform"]==name and r["phase"]==phase]
            good=[r for r in rows if r["HTTP"]==200 and r["correct_class"]]
            warm=[r for r in good if not r.get("model_initialized",False)]
            result["platforms"][name][phase]={"requests":len(rows),"successes":len(good),"failures":len(rows)-len(good),
                "success_rate":len(good)/len(rows),"network_all":stats([r["network_ms"] for r in rows]),
                "warm_success_network":stats([r["network_ms"] for r in warm]),
                "warm_server_components":{key:stats([r.get("server_timing_ms",{}).get(key) for r in warm if key in r.get("server_timing_ms",{})])
                    for key in ("body_validate","validation","frame","preprocessing","forest","server","init")}}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--azure-url",required=True)
    parser.add_argument("--vercel-url",default="https://pv-anomaly-detection-prince-r-k.vercel.app")
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    if (out/"Latency_Summary.json").exists():raise ValueError("Use a fresh output directory; preserve prior measurements")
    result=asyncio.run(benchmark({"Azure":args.azure_url,"Vercel":args.vercel_url}))
    (out/"Latency_Summary.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    keys=["platform","phase","request","HTTP","correct_class","network_ms","instance","model_initialized","body_validate","validation","frame","preprocessing","forest","server","init"]
    with (out/"Latency_Benchmark.csv").open("w",newline="",encoding="utf8") as stream:
        writer=csv.DictWriter(stream,fieldnames=keys);writer.writeheader()
        for record in result["requests"]:
            row={k:record.get(k,"") for k in keys};row.update(record.get("server_timing_ms",{}));writer.writerow(row)
    print(json.dumps(result["platforms"],indent=2))
    if any(v["failures"] for p in result["platforms"].values() for v in p.values()):
        raise SystemExit("Benchmark failures recorded; inspect before publication")

if __name__ == "__main__":main()
