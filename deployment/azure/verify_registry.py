"""Verify public GHCR access, OCI digests and Linux image provenance anonymously."""
import argparse
import datetime
import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path


def verify(image):
    match = re.fullmatch(r"ghcr.io/(ruganji-prince/pv-anomaly-detection)@(sha256:[a-f0-9]{64})", image)
    if not match:
        raise ValueError("An immutable digest of the approved project package is required")
    name, digest = match.groups()
    base = "https://ghcr.io"
    # This is an anonymous pull token, not a user credential. Never print or persist it.
    with urllib.request.urlopen(base + "/token?" + urllib.parse.urlencode({
            "service": "ghcr.io", "scope": "repository:" + name + ":pull"}), timeout=60) as response:
        token = json.load(response)["token"]
    headers = {"Authorization": "Bearer " + token,
               "Accept": "application/vnd.oci.image.index.v1+json,application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.v2+json"}

    def get(kind, sha):
        request = urllib.request.Request(base + "/v2/" + name + "/" + kind + "/" + sha, headers=headers)
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
        if "sha256:" + hashlib.sha256(data).hexdigest() != sha:
            raise ValueError("Remote registry object digest mismatch")
        return json.loads(data)

    index = get("manifests", digest)
    if "manifests" in index:
        candidates = [v for v in index["manifests"] if v.get("platform") == {"architecture": "amd64", "os": "linux"}]
        if len(candidates) != 1:
            raise ValueError("Exactly one Linux amd64 runtime manifest required")
        runtime_digest = candidates[0]["digest"]
        manifest = get("manifests", runtime_digest)
    else:
        runtime_digest, manifest = digest, index
    config = get("blobs", manifest["config"]["digest"])
    assert config["architecture"] == "amd64" and config["os"] == "linux"
    assert config["config"]["User"] == "appuser"
    labels = config["config"]["Labels"]
    assert labels["org.opencontainers.image.source"] == "https://github.com/Ruganji-Prince/AISD-Assignment2-PV-Anomaly-Detection"
    layers = []
    for layer in manifest["layers"]:
        request = urllib.request.Request(base + "/v2/" + name + "/blobs/" + layer["digest"], headers=headers, method="HEAD")
        with urllib.request.urlopen(request, timeout=60) as response:
            assert response.status == 200
        layers.append({"digest": layer["digest"], "compressed_bytes": layer["size"], "anonymous_access": True})
    return {"status": "VERIFIED", "recorded_UTC": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "image": image, "linux_amd64_manifest_digest": runtime_digest,
            "image_config_digest": manifest["config"]["digest"], "source_commit": labels["org.opencontainers.image.revision"],
            "platform": "linux/amd64", "anonymous_pull_manifest_and_all_layers_accessible": True,
            "user_registry_credentials_used": False, "runtime_layer_bytes_compressed": sum(v["compressed_bytes"] for v in layers),
            "layers": layers,
            "scope": "Public pull authorization and manifest/config digest verification plus layer HEAD availability. Layer payload integrity was checked in the prepublication Docker audit; no Azure pull is claimed."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.image)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    print("PV_GHCR_VERIFICATION_BEGIN")
    print(json.dumps(report, indent=2))
    print("PV_GHCR_VERIFICATION_END")

if __name__ == "__main__":
    main()
