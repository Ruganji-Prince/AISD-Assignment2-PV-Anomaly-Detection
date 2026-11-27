"""Generate new engineering figures from saved measurements and labeled scenarios."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def resource_figure(path, output):
    from datetime import datetime
    if output.exists(): raise ValueError("Preserve prior resource figures")
    report=json.loads(path.read_text(encoding="utf8"))
    fig,axes=plt.subplots(1,2,figsize=(10,3.5),layout="constrained")
    for axis,key,factor,label in zip(axes,["UsageNanoCores","WorkingSetBytes"],[1e-9,1/(2**20)],["Mean vCPU cores","Mean working set (MiB)"]):
        rows=[]
        for metric in report["metrics"]:
            for value in metric.get("value",[]):
                if value["name"]["value"]==key:
                    rows=[point for series in value.get("timeseries",[]) for point in series.get("data",[]) if point.get("average") is not None]
        axis.plot([datetime.fromisoformat(r["timeStamp"]) for r in rows],[r["average"]*factor for r in rows],marker="o",color="#176B87")
        axis.set_ylabel(label);axis.set_xlabel("UTC");axis.tick_params(axis="x",rotation=20)
    fig.suptitle("Azure platform one-minute averages: verification/benchmark window")
    fig.savefig(output,dpi=200);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir",type=Path,required=True)
    parser.add_argument("--costs",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--resource",type=Path)
    args=parser.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    if any(args.output_dir.glob("*.png")):raise ValueError("Use a fresh figure directory to preserve prior artifacts")
    summary=json.loads((args.results_dir/"Latency_Summary.json").read_text(encoding="utf8"))
    colors=["#176B87","#58516E"];names=["Azure","Vercel"]
    fig,axes=plt.subplots(1,4,figsize=(13,3.5),layout="constrained")
    for axis,key,title in zip(axes,["forest","preprocessing","server","network"],["Forest only","Preprocessing","Server processing","Network round trip"]):
        values=[summary["platforms"][n]["sequential"]["warm_success_network" if key=="network" else "warm_server_components"]["p95_ms"] if key=="network" else summary["platforms"][n]["sequential"]["warm_server_components"][key]["p95_ms"] for n in names]
        axis.bar(names,values,color=colors);axis.set_title(title);axis.set_ylabel("p95 (ms)")
        for i,v in enumerate(values):axis.text(i,v,f"{v:.2f}",ha="center",va="bottom")
        axis.set_ylim(0,max(values)*1.25);axis.spines[["top","right"]].set_visible(False)
    fig.suptitle("Matched warm sequential measurements: 30 requests per platform")
    fig.savefig(args.output_dir/"Latency_Comparison.png",dpi=200);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout="constrained")
    labels=["Azure seq","Vercel seq","Azure c2","Vercel c2"]
    for axis,key,title in zip(axes,["network_ms","server"],["All measured network round trips","All measured server timings"]):
        arrays=[]
        for phase in ("sequential","concurrency2"):
            for name in names:
                rows=[r for r in summary["requests"] if r["phase"]==phase and r["platform"]==name and r["HTTP"]==200]
                arrays.append([r[key] if key=="network_ms" else r["server_timing_ms"][key] for r in rows])
        axis.boxplot(arrays,tick_labels=labels,showfliers=True)
        for i,a in enumerate(arrays):axis.scatter(np.full(len(a),i+1),a,s=10,alpha=.45,color=colors[i%2])
        axis.set_yscale("log");axis.set_ylabel("Milliseconds (log scale)");axis.set_title(title);axis.tick_params(axis="x",rotation=20)
    fig.suptitle("All requests retained, including model-initialization events; seq N=30, c2 N=12")
    fig.savefig(args.output_dir/"Latency_Distributions.png",dpi=200);plt.close(fig)
    costs=json.loads(args.costs.read_text(encoding="utf8"));rows=costs["scenarios"]+[costs["continuous_30_day_active"]]
    labels=["1k / 10 h","10k / 30 h","100k / 200 h","100k / 720 h"]
    fig,axis=plt.subplots(figsize=(8,4),layout="constrained");values=[r["estimated_compute_and_requests_USD"] for r in rows]
    axis.bar(labels,values,color=[colors[0]]*3+[colors[1]])
    for i,v in enumerate(values):axis.text(i,v+.4,f"${v:.2f}",ha="center")
    axis.set_ylabel("Estimated USD / month");axis.set_xlabel("Requests / assumed allocated replica-hours")
    axis.set_title("Illustrative activity scenarios after otherwise-unused free grants")
    axis.set_ylim(0,max(values)*1.2);axis.spines[["top","right"]].set_visible(False)
    fig.get_layout_engine().set(rect=(0,.1,1,.9))
    fig.text(.5,.01,"0.5 vCPU / 1 GiB; excludes egress, taxes and other subscription usage; not observed billing",ha="center",fontsize=8)
    fig.savefig(args.output_dir/"Monthly_Cost_Scenarios.png",dpi=200);plt.close(fig)
    if args.resource: resource_figure(args.resource,args.output_dir/"Resource_Usage.png")
    print(json.dumps({"figures":sorted(p.name for p in args.output_dir.glob("*.png")),"measurement_source":str(args.results_dir),"costs_are_assumptions_not_observed_charges":True}))

if __name__=="__main__":main()
