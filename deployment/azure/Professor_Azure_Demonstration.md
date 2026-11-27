# Five-minute Azure technical demonstration

Evaluation: December 1 or December 4, 2026. This is a subsequent engineering extension of the unchanged submission-ready scientific system. The current engineering mock assessment remains91/100, not an official grade.

## Before the five-minute walkthrough

Open [Azure health](https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io/api/health) and [the application](https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io) at least two minutes before the demonstration. Wait for **Model ready**. Natural scale-to-zero was observed; the first prediction afterward took56.94 seconds. The unchanged frontend prediction timeout is60 seconds, so first-access reliability is not guaranteed from a single activation sample. No paid always-on capacity or automated keepalive was added. Keep the local fallback ready:

```sh
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
python -B -m technical_evaluation.defense.run_demo --url http://127.0.0.1:8000
```

## Timed walkthrough

| Time | Demonstration | Evidence |
| --- | --- | --- |
| 0:00-0:45 | Azure Portal: rg-pv-anomaly-detection, environment pv-anomaly-env, app pv-anomaly-detection; show running revision rf-e4-940f5e2 | [Configuration](live/Deployment_Configuration.json) |
| 0:45-1:15 | Show Consumption profile,0.5 vCPU/1 GiB,min0/max1,HTTPS8000, startup/readiness/liveness probes | [Architecture](Architecture.md) |
| 1:15-2:00 | Open four-step application, select a historical example, inspect charts/explanation and assessment; class 4 is environmental shade | [Browser checks](live/Browser_Verification.json) |
| 2:00-2:45 | Run the five fixed cases and invalid-input checks against Azure | Command below and [parity](live/Deployment_Verification.json) |
| 2:45-3:30 | Show Server-Timing and matched Azure/Vercel p95 values; distinguish forest, preprocessing, server and network | [Cloud comparison](Cloud_Comparison.md) |
| 3:30-4:15 | Show model SHA and actual Azure 200-row probability parity, resource averages, cost assumptions and delayed actual-cost query | [Runtime probe](live/Azure_Runtime_Parity.json), [costs](Cost_Analysis.md) |
| 4:15-5:00 | Explain credential-free image pull, scope limits, scale-to-zero delay, preserved model/scientific snapshot and remaining limitations | [Security](Security_Verification.md), [acceptance](Acceptance_Matrix.md) |

From a prepared environment at repository root:

```sh
python -B -m technical_evaluation.defense.run_demo --url https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io
```

The five fixed observations belong to historically exposed TEST. The demonstration establishes serving consistency, not new independent accuracy. Synthetic scenario intent is illustrative; existing synthetic fixtures all predict shade and must not be adjusted to manufacture desired classes.

PowerShell timing/header example:

```powershell
$pvPayload = @{vdc1=300.031; vdc2=329.544; idc1=0.2247; idc2=0.1272} | ConvertTo-Json
$pvResponse = Invoke-WebRequest -UseBasicParsing -Uri 'https://pv-anomaly-detection.wittygrass-37610045.francecentral.azurecontainerapps.io/api/predict' -Method Post -ContentType 'application/json' -Body $pvPayload
$pvResponse.Headers['Server-Timing']
$pvResponse.Content
```

## Technical defense questions

| Question | Evidence-based answer |
| --- | --- |
| Why Container Apps? | Existing Linux container, explicit resource/scaling configuration, managed HTTPS and consumption grants; no cluster or VM administration required. |
| Why Docker? | Same original model/runtime files, hash-locked dependencies and entrypoint are packaged and tested before hosting. Digest pinning fixes the deployed artifact. |
| Why no retraining? | Hosting changes the serving environment, not the approved fitted model. Scientific selection and TEST limitations remain unchanged. |
| How is model integrity verified? | SHA before unpickling, original bytes unchanged, pinned image and actual Azure model-file hash confirmed. |
| How is the image retrieved? | Public GHCR anonymous pull, immutable digest; no registry username/password configured in Azure. |
| How do Vercel and Azure differ? | Existing Python serverless functions versus an explicit Linux Consumption container; matched same-client measurements compare actual behavior. |
| What is scale-to-zero? | No running replicas after inactivity, with startup delay when requests return; zero and a subsequent new replica were observed. |
| What causes first-request delay? | Scheduling, image/startup/readiness, ingress queueing and transport contribute. One56.94s activation does not isolate those components. |
| Why0.5 vCPU/1 GiB? | Approved allocation passed constrained Linux checks and actual live inference; observed Azure working-set averages stayed below the limit. No minimum-resource optimum is claimed. |
| How is inference latency measured? | Existing Server-Timing separately measures preprocessing and forest; client wall-clock measures the whole HTTP round trip. |
| Why is network latency larger? | Transport/TLS/queueing and platform activity are additional to handler execution; quantiles cannot simply be added. |
| How are costs estimated? | Explicit allocated replica-hours and current regional rates/shared grants; billing query delay and credit uncertainty are disclosed. HTTP latency is not billed CPU. |
| How are credentials protected? | Existing CLI session, no new client secrets, no credentials in build context/image/frontend; temporary workflow token has package-write scope. |
| What happens under simultaneous requests? | Two inferences per process are permitted; excess capacity can return503. Global per-IP rate limiting is not implemented. |
| Does parity prove generalization? | No. It proves consistent serving of the original model. Historical TEST exposure and single-study/operating-block limits remain. |
| What remains for industrial monitoring? | External/site/time validation with trustworthy timestamps, physical sensor and field fault validation, calibration/safety review, monitoring, abuse control, availability targets and operational incident procedures. |

No full production readiness, industrial safety, cloud-wide superiority or perfect TEST independence is claimed.
