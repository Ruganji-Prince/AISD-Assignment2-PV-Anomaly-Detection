"""Scoped extension checks; historical frozen receipts are never rewritten."""
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASELINE="8d4a6b5fdcd9f236cc6e9ade7a0bc093603b773f"
ALLOWED={"README.md","web/static/app.js","web/static/index.html","web/static/style.css","deployment/azure/verify_image.py"}

def main():
    original=set(subprocess.check_output(["git","ls-tree","-r","--name-only",BASELINE],cwd=ROOT).decode().splitlines())
    changed=set(subprocess.check_output(["git","diff",BASELINE,"--name-only"],cwd=ROOT).decode().splitlines())
    assert not (changed&original)-ALLOWED,sorted((changed&original)-ALLOWED)
    expected={"models/rf_e4/model.pkl":"55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb",
              "data/raw/pv_fault_dataset.csv":"717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a",
              "phase1_strategy/Phase1_Strategy_Report.pdf":"dfb3f253f3e059ece168d9c6edffc10f68a0a21ba8b738a6fb2b2d2c1d962497"}
    for name,digest in expected.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    tag=subprocess.check_output(["git","rev-parse","submission-ready-20261124^{}"],cwd=ROOT).decode().strip()
    assert tag=="d49cff533e5fe8860bacfb9942779ab003db47db"
    print(json.dumps({"status":"PASS","baseline":BASELINE,"protected_existing_files":len(original-ALLOWED),"authorized_changes":sorted(changed&original),"model_raw_CSV_approved_PDF_byte_identical":True,"tag_preserved":True,"scope":"Only approved frontend transport/readiness and backward-compatible image-verifier option may change existing files; scientific/inference sources and all historical receipts remain unchanged."}))
if __name__=="__main__":main()
