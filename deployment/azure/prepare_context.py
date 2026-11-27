"""Build an allowlisted context from committed blobs, never from local secrets."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL_SHA = "55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb"
FILES = (
    "Dockerfile", ".dockerignore", "src/__init__.py",
    "src/inference/__init__.py", "src/inference/cli.py",
    "src/phase2_stage1/__init__.py", "src/phase2_stage1/contracts.py",
    "src/phase2_stage1/features.py", "src/phase2_stage2/__init__.py",
    "src/phase2_stage2/contracts.py", "src/phase2_stage2/models.py",
    "web/__init__.py", "web/app.py", "web/requirements.lock",
    "web/static/index.html", "web/static/style.css", "web/static/app.js",
    "web/static/scenarios.js", "web/static/explanations.js", "web/static/favicon.svg",
    "models/rf_e4/model.pkl", "models/rf_e4/provenance.json",
    "deployment/example_cases.json",
)
# Attribution is copied into the model directory, which the unchanged Dockerfile includes.
ATTRIBUTION = {"phase1_strategy/PRIMARY_SOURCE_LICENSE.txt": "models/rf_e4/PRIMARY_SOURCE_LICENSE.txt"}
SECRET = re.compile(rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|AccountKey=[A-Za-z0-9+/]{30,})")

def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)

def blob(revision, path):
    if path not in FILES and path not in ATTRIBUTION:
        raise ValueError("Path is outside the reviewed runtime allowlist")
    return git("show", revision + ":" + path)

def prepare(destination, revision="HEAD"):
    commit = git("rev-parse", "--verify", revision + "^{commit}").decode().strip()
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("A fresh non-existing build-context directory is required")
    destination.mkdir(parents=True)
    records = []
    for source in (*FILES, *ATTRIBUTION):
        data = blob(commit, source)
        if SECRET.search(data):
            raise ValueError("Potential secret detected in allowlisted file: " + source)
        digest = hashlib.sha256(data).hexdigest()
        if source == "models/rf_e4/model.pkl" and digest != MODEL_SHA:
            raise ValueError("Original model integrity mismatch")
        target = ATTRIBUTION.get(source, source)
        out = destination / target
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        records.append({"source": source, "path": target, "bytes": len(data), "sha256": digest})
    return {"source_commit": commit, "model_sha256": MODEL_SHA, "files": records,
            "policy": "Committed-blob allowlist; no raw CSV, review files, credentials, caches or training results."}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--revision", default="HEAD")
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    report = prepare(args.destination, args.revision)
    args.manifest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    print(json.dumps({"source_commit": report["source_commit"], "files": len(report["files"]),
                      "model_sha256": report["model_sha256"]}))

if __name__ == "__main__":
    main()
