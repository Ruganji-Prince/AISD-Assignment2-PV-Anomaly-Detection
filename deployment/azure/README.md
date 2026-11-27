# Azure PV inference engineering extension

**[Open Azure application](https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io)** | [Existing Vercel application](https://pv-anomaly-detection-prince-r-k.vercel.app) | [Five-minute professor demonstration](Professor_Azure_Demonstration.md)

The approved original RF E4 application is deployed to Azure Container Apps in France Central. The protected `submission-ready-20261124` snapshot, original model/scientific artifacts, existing Vercel production and four-step interface are preserved. This engineering extension is published on `engineering/azure-container-20261127`; it does not replace the submission tag or rewrite main history.

**First-access limitation:** one observed zero-to-running prediction took **56.94 seconds**. Open the application/health endpoint and wait for **Model ready** before demonstration. The unchanged frontend prediction timeout is60 seconds. Warm measurements are separate; no always-on replica or scheduled warming was enabled.

## Verified deployment

| Item | Actual setting/result |
| --- | --- |
| Subscription | Azure for Students, Enabled, spending limit On |
| Region/resource group | France Central / rg-pv-anomaly-detection |
| Environment/app | pv-anomaly-env / pv-anomaly-detection |
| Environment/profile | WorkloadProfiles / Consumption only |
| Allocation/scaling |0.5 vCPU,1 GiB,min0/max1,single active revision |
| Ingress | External HTTPS to8000, insecure access disabled |
| Revision | pv-anomaly-detection--rf-e4-940f5e2 |
| Image | Public GHCR immutable digest sha256:51be78bd92b20af85628dd07009afd0cdad5689353fcf8a621604b7ea82e70e6 |
| Container source |940f5e2ca116c5413428348faa82b77bca3915c3; final documentation commit is separate |
| Model | Original RF E4 SHA-256 55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb |
| Tests |30 existing +9 Azure scope/context safety tests passed;41-package environment consistent |
| Deployment parity | Five fixed cases agree across CLI/local API/Linux image/Vercel/Azure; actual Azure 200-row max probability difference3.33e-16 |
| Browser | Five viewport sizes, four-step state/navigation/charts/explanations/error controls passed |
| Matched reliability | Azure42/42 and Vercel42/42 measured requests succeeded |
| Warm sequential p95 | Azure network248.99 ms/server16.62 ms; Vercel network448.21 ms/server16.71 ms |
| Logging/secrets | No persistent Log Analytics, app secrets or registry credentials |
| Actual costs | Resource-group ActualCost query returned no rows; delayed/unverified charges, not a zero-cost guarantee |

The original10 ms complete-path and10 MiB model targets remain unmet: measured server p95 exceeds10 ms and the unchanged artifact is11.665 MiB. Historical TEST references establish parity only, not independent generalization. The current engineering mock assessment remains91/100, Rubric 5=18/20.

## Evidence navigation

- [Architecture and input contract](Architecture.md), [actual deployed configuration](live/Deployment_Configuration.json), [quota before app creation](Consumption_Quota_Before_App.json).
- [Container provenance](Container_Provenance.json), [allowlisted context hashes](Context_Manifest.json), [image-layer checks](Container_Verification.json), [anonymous registry access](Registry_Verification.json).
- [Live verification](live/Deployment_Verification.json), [class parity CSV](live/Prediction_Parity.csv), [actual Azure numerical probe](live/Azure_Runtime_Parity.json), [browser checks](live/Browser_Verification.json).
- [Cloud comparison](Cloud_Comparison.md), [raw latency CSV](live/Latency_Benchmark.csv), [latency summary](live/Latency_Summary.json), [observed zero-to-running activation](live/Scale_From_Zero.json).
- [Costs](Cost_Analysis.md), [activity assumptions](Monthly_Cost_Scenarios.json), [Azure resource observations](after_benchmark/Resource_Usage.json), [billing query](after_benchmark/Billing_Observation.json).
- [Security](Security_Verification.md), [acceptance and Rubric 5 extension](Acceptance_Matrix.md), [submission protection](Submission_Protection.json), [test receipt](Automated_Tests.json), [troubleshooting](Troubleshooting.md), [monitoring/cleanup](Cleanup_Guide.md).

Container-preparation receipts that state Azure was not provisioned describe the earlier preparation checkpoint. They remain historical records; current deployed configuration and live verification supersede that status without rewriting the receipts.

## Reproduction

Use Git, an authenticated Azure CLI and the existing exact Python 3.14.10 scientific environment from the [root instructions](../../README.md). No runtime dependencies were upgraded. From repository root:

```sh
python -B -m unittest deployment.azure.test_context deployment.azure.test_deployment -v
python -B -m technical_evaluation.refinement.verify
python -B -m deployment.azure.deploy
```

The last command is a read-only scope plan. Creating resources requires explicit acceptance of the approved potentially billable scope:

```sh
python -B -m deployment.azure.deploy --approve-provisioning
```

An existing matching app is preserved rather than redeployed. The script checks active Students subscription, exact resource profile and consumption quota; it never changes to a paid plan or deletes resources. Environment creation explicitly sets WorkloadProfiles mode because the installed CLI otherwise selected Express. Disabled logging is JSON null in REST, or `--logs-destination none` in CLI. Existing payloads are [environment.json](environment.json) and [containerapp.json](containerapp.json).

PowerShell entrypoint:

```powershell
.\deployment\azure\deploy.ps1
# Only after the stated infrastructure scope has explicit approval:
.\deployment\azure\deploy.ps1 -ApproveProvisioning
```

Use fresh output directories to preserve evidence:

```sh
python -B -m deployment.azure.verify --azure-url https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io --output-dir /tmp/pv-azure-verification
python -B -m deployment.azure.benchmark --azure-url https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io --output-dir /tmp/pv-azure-benchmark
python -B -m deployment.azure.collect --output-dir /tmp/pv-azure-observations
python -B -m deployment.azure.scale_zero --azure-url https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io --output /tmp/pv-scale-zero.json
python -B -m deployment.azure.costs --output /tmp/pv-cost-scenarios.json
python -B -m deployment.azure.figures --results-dir /tmp/pv-azure-benchmark --costs /tmp/pv-cost-scenarios.json --resource /tmp/pv-azure-observations/Resource_Usage.json --output-dir /tmp/pv-azure-figures
```

On Windows replace `/tmp/...` with fresh paths under `$env:TEMP`. PowerShell live verification wrapper accepts `-AzureUrl` and `-OutputDir`. The scale observation never forces shutdown; a nonzero replica count is reported as not observed. The benchmark performs only30 sequential +12 concurrency-two measured requests per platform, plus three warmups. No paid load-test service is used.

The dedicated [GHCR publication workflow](../../.github/workflows/azure-container-publication.yml), [context preparation](prepare_context.py), [image verifier](verify_image.py) and [anonymous registry verifier](verify_registry.py) reproduce container preparation using the unchanged root Dockerfile. Container build validation runs on standard public GitHub Actions Linux runners when local Docker is unavailable; publication never provisions Azure automatically. The deployed image remains the explicitly approved immutable digest.


### Administrative numerical parity reproduction

The public API intentionally exposes no probabilities. The recorded Azure numerical check used an authenticated administrative shell, original model bytes and only the fixed 200-row TRAIN reference in memory; no container file or image was changed. A reproducible bounded-line shell probe can be generated locally:

```sh
python -B -m deployment.azure.runtime_probe --output /tmp/pv-runtime-probe.sh
az containerapp exec --name pv-anomaly-detection --resource-group rg-pv-anomaly-detection --container pv-inference --command /bin/sh
```

Paste the generated probe into that authenticated shell; the probe closes the session when complete. On Windows use a fresh path under `$env:TEMP`. Keep input lines bounded, and do not paste credentials. The expected model hash, reference count200 and tolerance1e-12 are recorded in [actual Azure parity](live/Azure_Runtime_Parity.json). This administrative diagnostic does not add a public probability endpoint or calibrated confidence.

Read-only evidence integrity and saved-metric recomputation: `python -B -m deployment.azure.check_evidence`. The published CSV, not newly generated synthetic measurements, is the source for this check.

Final [deployment provenance](Deployment_Provenance.json), [approved resource inventory](Resource_Inventory.json), [Vercel plan observation](Vercel_Plan_Observation.json) and [verification receipt](Final_Verification.json) retain the current extension state separately from earlier preparation checkpoints.
