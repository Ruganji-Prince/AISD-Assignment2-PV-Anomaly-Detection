# Azure container preparation

This subsequent engineering extension preserves the protected `submission-ready-20261124` snapshot and existing Vercel application. Azure infrastructure has **not** been provisioned. A separate infrastructure approval is required before creating resources.

## Verified preparation evidence

The complete publication workflow passed on 2026-11-27. [Container provenance](Container_Provenance.json) records the source commit and immutable GHCR digest. [Image verification](Container_Verification.json) confirms the original model, five fixed cases, 200-row probability parity and all-layer application-file audit under 0.5 CPU/1 GiB limits. [Registry verification](Registry_Verification.json) confirms anonymous access to the OCI manifest and every runtime layer. The [context manifest](Context_Manifest.json) lists every included source file, size and hash.

The final Linux container test observed 151.1 MiB at its memory snapshot, 4.10 seconds from container launch to readiness, and maximum probability difference 2.22e-16 for 200 TRAIN reference rows. These are bounded GitHub-runner container checks, not Azure measurements, peak-memory guarantees or end-to-end latency benchmarks. The 10 ms complete-path and 10 MiB model targets and their existing limitations remain unchanged.

[Infrastructure preflight](Infrastructure_Preflight.json), [official pricing receipt](Pricing_Preflight.json) and the [separate provisioning approval report](Provisioning_Approval.md) describe the remaining gate. No Azure endpoint, Azure benchmark or completed Azure deployment is claimed. Earlier attempt receipts remain available as [first image verification](Container_Verification_First_Published.json) and [first registry verification](Registry_Verification_First_Published.json); the successful final workflow is distinguished in provenance.

## Runtime and publication

The dedicated [publication workflow](../../.github/workflows/azure-container-publication.yml) builds the unchanged root [Dockerfile](../../Dockerfile) for Python 3.14.10 and Linux amd64. Only committed files in the explicit [runtime allowlist](prepare_context.py) enter the build context. The original pickle import modules are required for deserialization; their historical fitting helpers are not executed. The raw CSV, academic results, private review folders, environments and credentials are excluded. Original source-license attribution accompanies the model.

Before publication, [verification](verify_image.py) inspects application content in every image layer, verifies source hashes and model identity, and runs a nonroot read-only container limited to 0.5 CPU and 1 GiB. Checks include the frontend assets, five predetermined inference cases, invalid requests and the existing 200-row TRAIN probability reference at absolute tolerance 1e-12. These are deployment consistency checks, not new independent model accuracy measurements. The public API does not expose probabilities.

The workflow has only repository-content read and package-write permissions. Its ephemeral GitHub token is supplied to `docker login` over stdin after image verification; it is not part of the build context or image. A commit-specific tag and immutable digest identify each image. Public GHCR visibility must be verified separately: new packages can initially be private despite a public source repository.

The workflow runs on the dedicated engineering branch or by manual dispatch once available on the default branch. It does not provision Azure or modify Vercel.

## Reproduction

From the repository root, with Git, Python and Docker available:

```sh
python -B -m unittest deployment.azure.test_context -v
python -B -m deployment.azure.prepare_context /tmp/pv-runtime --revision HEAD --manifest /tmp/pv-context.json
docker build --platform linux/amd64 --build-arg PYTHON_VERSION=3.14.10 --label org.opencontainers.image.revision=$(git rev-parse HEAD) -t pv-azure-runtime /tmp/pv-runtime
python -B -m deployment.azure.verify_image --image pv-azure-runtime --manifest /tmp/pv-context.json --output /tmp/pv-container-verification.json
```

On PowerShell, replace the `/tmp` destinations with fresh paths under `$env:TEMP`; use `$(git rev-parse HEAD)` unchanged. The context destination must not already exist. The verification script removes only its own temporary Docker container. It does not delete Azure resources.

## Pending infrastructure approval

Proposed resources remain France Central, `rg-pv-anomaly-detection`, `pv-anomaly-env`, and `pv-anomaly-detection`; Consumption only, 0.5 vCPU, 1 GiB, minimum zero and maximum one replica, HTTPS ingress to port 8000, and no Log Analytics workspace initially. Quota eligibility, actual resource configuration and costs must be rechecked before provisioning. No paid support, subscription upgrade or additional purchased service is authorized.

No Azure URL, Azure performance result or Azure cost observation is claimed here. Benchmarking and evaluation documentation follow only after deployment authorization and successful execution.
