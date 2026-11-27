# Azure container preparation

This subsequent engineering extension preserves the protected `submission-ready-20261124` snapshot and existing Vercel application. Azure infrastructure has **not** been provisioned. A separate infrastructure approval is required before creating resources.

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
