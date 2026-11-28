"""Build a static-only Vercel output from the single canonical frontend source."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]
AZURE="https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io"
ASSETS=("style.css","app.js","api.js","scenarios.js","explanations.js","favicon.svg","replay.js")


def build(destination, api_base=AZURE):
    parsed=urlsplit(api_base)
    if api_base!=AZURE and not (parsed.scheme=="http" and parsed.hostname in {"localhost","127.0.0.1"} and parsed.port and not parsed.path and not parsed.query and not parsed.fragment):
        raise ValueError("Only the approved Azure API or explicit local development origin is permitted")
    dest=Path(destination)
    if dest.exists():raise ValueError("Use a fresh build-output directory")
    static=dest/"static";assets=static/"assets";assets.mkdir(parents=True)
    source=ROOT/"web/static"
    for name in ASSETS:shutil.copyfile(source/name,assets/name)
    # One explicit historical-data asset; no broad data-directory publication.
    data=static/"data";data.mkdir()
    shutil.copyfile(ROOT/"web/data/pv_historical_replay.json",data/"pv_historical_replay.json")
    html=(source/"index.html").read_text(encoding="utf8")
    html=html.replace('<script type="module" src="/assets/app.js">','<script src="/config.js"></script><script type="module" src="/assets/app.js">',1)
    (static/"index.html").write_text(html,encoding="utf8",newline="\n")
    (static/"config.js").write_text('globalThis.PV_CONFIG=Object.freeze('+json.dumps({"apiBase":api_base},separators=(",",":"))+');\n',encoding="utf8")
    csp="default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self' "+api_base+"; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
    config={"version":3,"routes":[{"src":"/(.*)","headers":{"Content-Security-Policy":csp,"X-Content-Type-Options":"nosniff","X-Frame-Options":"DENY","Referrer-Policy":"strict-origin-when-cross-origin","Cache-Control":"public, max-age=0, must-revalidate"},"continue":True},{"handle":"filesystem"}]}
    (dest/"config.json").write_text(json.dumps(config,indent=2)+"\n",encoding="utf8")
    files=[{"path":p.relative_to(dest).as_posix(),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in dest.rglob("*") if p.is_file()]
    assert {r["path"] for r in files}=={"config.json","static/index.html","static/config.js","static/data/pv_historical_replay.json",*("static/assets/"+n for n in ASSETS)}
    return {"status":"STATIC_ONLY","api_base":api_base,"functions":0,"model_artifacts":0,"Python_runtime_files":0,"files":files}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--output",type=Path,required=True);parser.add_argument("--api-base",default=AZURE);parser.add_argument("--manifest",type=Path,required=True);args=parser.parse_args()
    report=build(args.output,args.api_base);args.manifest.write_text(json.dumps(report,indent=2)+"\n",encoding="utf8");print(json.dumps(report,indent=2))

if __name__=="__main__":main()
