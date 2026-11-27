"""Generate a bounded read-only shell probe for Azure administrative exec."""
import argparse
import base64
import zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise ValueError("Use a fresh probe file")
    raw=(ROOT/"technical_evaluation/refinement/fixtures/runtime_probability_reference.json").read_bytes()
    encoded=base64.b64encode(zlib.compress(raw)).decode()
    chunks="\n".join(repr(encoded[i:i+1500]) for i in range(0,len(encoded),1500))
    code="python -B - <<'PV_AZURE_CHECK'\nimport json,base64,zlib,hashlib,platform\nimport numpy as np,pandas as pd\nfrom src.inference.cli import load_model,CHANNELS,MODEL\nencoded=(\n"+chunks+"\n)\n"
    code+="d=json.loads(zlib.decompress(base64.b64decode(encoded)))\nm=load_model()\np=m.pipeline.predict_proba(pd.DataFrame(d['X'],columns=CHANNELS))\nq=np.array(d['probabilities'])\nnp.testing.assert_allclose(p,q,rtol=0,atol=1e-12)\ncases=json.load(open('deployment/example_cases.json'))\nfive=m.pipeline.predict_proba(pd.DataFrame([c['input'] for c in cases],columns=CHANNELS))\nassert five.argmax(1).tolist()==[0,1,2,3,4]\n"
    code+="print(json.dumps({'status':'VERIFIED','actual_model_sha256':hashlib.sha256(MODEL.read_bytes()).hexdigest(),'TRAIN_reference_N':len(p),'TRAIN_max_probability_difference':float(abs(p-q).max()),'five_reference_probabilities':five.tolist()}))\nPV_AZURE_CHECK\nexit\n"
    args.output.write_text(code,encoding="utf8",newline="\n")
    print("Probe contains fixed TRAIN reference data only; paste into the authenticated container shell in bounded lines. No credentials, training or container file writes.")

if __name__=="__main__":main()
