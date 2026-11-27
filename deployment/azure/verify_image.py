"""Verify the exact image before GHCR publication; stdlib host, Docker required."""
import argparse
import hashlib
import io
import json
import subprocess
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from deployment.azure.prepare_context import MODEL_SHA, ROOT, SECRET


def command(*args, **kwargs):
    return subprocess.check_output(args, cwd=ROOT, **kwargs)


def request(path, payload=None, raw=None):
    data = json.dumps(payload).encode() if payload is not None else raw
    req = urllib.request.Request("http://127.0.0.1:8769" + path, data=data,
        headers={"Content-Type": "application/json"} if data is not None else {})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers)


def inspect_layers(image, manifest):
    expected = {r["path"]: r["sha256"] for r in manifest["files"]
                if r["path"] not in {"Dockerfile", ".dockerignore"}}
    seen = set()
    with tempfile.TemporaryDirectory() as temp:
        archive = Path(temp) / "image.tar"
        subprocess.run(["docker", "save", "-o", str(archive), image], check=True)
        with tarfile.open(archive) as outer:
            metadata = json.load(outer.extractfile("manifest.json"))[0]
            for layer in metadata["Layers"]:
                with tarfile.open(fileobj=outer.extractfile(layer), mode="r|*") as inner:
                    for entry in inner:
                        name = entry.name.removeprefix("./").lstrip("/")
                        if any(part in {".azure", ".aws", ".ssh", ".git", ".review", ".vercel"}
                               for part in name.split("/")):
                            raise ValueError("Unexpected private directory in image layer: " + name)
                        if name.startswith("app/") and entry.isfile():
                            relative = name[4:]
                            if relative not in expected:
                                raise ValueError("Unexpected /app image-layer file: " + relative)
                            data = inner.extractfile(entry).read()
                            if hashlib.sha256(data).hexdigest() != expected[relative]:
                                raise ValueError("Image-layer content differs from source: " + relative)
                            if SECRET.search(data):
                                raise ValueError("Potential secret in application layer")
                            seen.add(relative)
    if seen != set(expected):
        raise ValueError("Missing runtime files from image layers")
    return {"all_layers_inspected": True, "application_files": len(seen),
            "all_application_files_match_committed_blob_hashes": True,
            "unapproved_application_files": [], "private_directory_findings": [],
            "limitation": "Allowlist/hash checks and heuristic secret checks are not a complete security certification."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf8"))
    image = json.loads(command("docker", "image", "inspect", args.image))[0]
    assert image["Architecture"] == "amd64" and image["Os"] == "linux"
    assert image["Config"]["User"] == "appuser"
    assert image["Config"]["Cmd"] == ["python", "-m", "uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8000"]
    assert image["Config"]["Labels"]["org.opencontainers.image.revision"] == manifest["source_commit"]
    assert not SECRET.search(json.dumps(image["Config"]).encode())
    layer_report = inspect_layers(args.image, manifest)
    name = "pv-azure-prepublication-" + str(int(time.time()))
    command("docker", "run", "-d", "--read-only", "--tmpfs", "/tmp:rw,size=64m",
            "--cpus", "0.5", "--memory", "1g", "--memory-swap", "1g",
            "-e", "PYTHONDONTWRITEBYTECODE=1", "-p", "127.0.0.1:8769:8000",
            "--name", name, args.image)
    start = time.perf_counter()
    try:
        for _ in range(90):
            try:
                status, body, _ = request("/api/health")
                if status == 200:
                    health = json.loads(body)
                    break
            except (OSError, ValueError):
                pass
            time.sleep(1)
        else:
            raise RuntimeError("Container did not become ready")
        startup = time.perf_counter() - start
        assert health["model_sha256"] == MODEL_SHA and health["python_version"] == "3.14.10"
        assert int(command("docker", "exec", name, "id", "-u")) != 0
        assert request("/")[0] == 200
        for asset in ("app.js", "style.css", "scenarios.js", "explanations.js", "favicon.svg"):
            assert request("/assets/" + asset)[0] == 200
        cases = json.loads((ROOT / "deployment/example_cases.json").read_text(encoding="utf8"))
        predictions = []
        for case in cases:
            status, body, headers = request("/api/predict", case["input"])
            value = json.loads(body)
            assert status == 200 and headers.get("Server-Timing")
            reference = case["output"]
            assert all(value[key] == expected for key, expected in reference.items())
            if value["predicted_class"] == 4:
                assert value["environmental_shade"] and not value["hardware_fault_class"]
            predictions.append({"case": case["case"], "class": value["predicted_class"], "all_original_output_fields_match": True})
        good = cases[0]["input"]
        checks = []
        for label, value in [("missing", {}), ("target", {**good, "f_nv": 0}),
                             ("negative", {**good, "idc1": -1}), ("nonfinite", {**good, "idc1": float("nan")}),
                             ("boolean", {**good, "idc1": True}), ("text", {**good, "idc1": "1"})]:
            assert request("/api/predict", value)[0] == 422
            checks.append(label)
        assert request("/api/predict", raw=b'{"vdc1":1,"vdc1":2}')[0] == 422
        assert request("/api/predict", raw=b"x" * 2049)[0] == 413
        reference = (ROOT / "technical_evaluation/refinement/fixtures/runtime_probability_reference.json").read_text(encoding="utf8")
        code = "import json,sys,numpy as np,pandas as pd;from src.inference.cli import load_model,CHANNELS;d=json.load(sys.stdin);m=load_model();p=m.pipeline.predict_proba(pd.DataFrame(d['X'],columns=CHANNELS));q=np.array(d['probabilities']);np.testing.assert_allclose(p,q,rtol=0,atol=1e-12);print(json.dumps({'N':len(p),'max_probability_difference':float(abs(p-q).max())}))"
        parity = json.loads(command("docker", "exec", "-i", name, "python", "-B", "-c", code,
                                   input=reference.encode()))
        usage = json.loads(command("docker", "stats", "--no-stream", "--format", "{{json .}}", name))
        runtime = json.loads(command("docker", "exec", name, "python", "-B", "-c",
            "import json,platform;from importlib.metadata import distributions;print(json.dumps({'python':platform.python_version(),'packages':{d.metadata['Name']:d.version for d in distributions()}}))"))
        report = {"status": "VERIFIED", "source_commit": manifest["source_commit"], "image_id": image["Id"],
                  "image_uncompressed_bytes": image["Size"], "platform": "linux/amd64",
                  "resource_test": {"cpus": 0.5, "memory_GiB": 1, "read_only_root": True,
                                    "startup_to_ready_seconds": startup, "snapshot": usage},
                  "health": health, "reference_cases": predictions, "invalid_cases": checks + ["duplicate", "oversize"],
                  "TRAIN_probability_parity": parity, "runtime": runtime, "layer_audit": layer_report,
                  "scope": "Prepublication Linux container tests, not Azure execution, latency benchmarking or a comprehensive vulnerability scan."}
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
        print("PV_AZURE_CONTAINER_BEGIN")
        print(json.dumps(report, indent=2))
        print("PV_AZURE_CONTAINER_END")
    finally:
        subprocess.run(["docker", "rm", "-f", name], check=False)

if __name__ == "__main__":
    main()
