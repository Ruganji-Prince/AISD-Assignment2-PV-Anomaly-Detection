# Azure deployment troubleshooting

## Check the active subscription and exact scope

```sh
az account show --query '{name:name,state:state,isDefault:isDefault}'
az group show --name rg-pv-anomaly-detection
az containerapp env show --name pv-anomaly-env --resource-group rg-pv-anomaly-detection
az containerapp env list-usages --name pv-anomaly-env --resource-group rg-pv-anomaly-detection
```

The active subscription must remain the approved Azure for Students subscription. Do not upgrade the offer or purchase support to bypass a restriction. Regional policy must permit France Central. An empty quota response is unknown capacity, not permission to assume a default.

## Explicit environment mode is required

The installed CLI initially selected Express even with the workload-profile flag. The empty environment was corrected in place; no application was created before quota verification. Reproduction therefore explicitly supplies `--environment-mode WorkloadProfiles`, `--enable-workload-profiles true` and `--logs-destination none`. Inspect `properties.environmentMode` through the current REST API when older CLI projections omit it. An environment can report Updating during asynchronous mode/infra preparation. Wait and inspect activity logs rather than creating duplicates or deleting resources.

```sh
az monitor activity-log list --resource-group rg-pv-anomaly-detection --max-events 20
```

## App startup and failed health

Check provisioning state, revision health and container logs. A healthy endpoint must report the preserved SHA-256. Do not substitute a new model or relax dependency checks. Public GHCR access, supported Linux amd64, port 8000, nonroot permissions, model import modules and the original dependency lock are required. Check CPU/memory and probe failures before retrying; resource increases require approval.

```sh
az containerapp revision list --name pv-anomaly-detection --resource-group rg-pv-anomaly-detection
az containerapp logs show --name pv-anomaly-detection --resource-group rg-pv-anomaly-detection --type console --tail 30
```

Keep logs free of credentials. No persistent Log Analytics workspace is configured, so historical log retention is limited.

## Input errors and latency

HTTP 422 indicates an invalid schema/value under the existing application contract. HTTP 413 rejects oversized bodies. HTTP 408 is a body deadline, HTTP 504 an inference response deadline, and HTTP 503 can indicate temporary capacity or model unavailability. Do not send a target label, index, irradiance or temperature to the selected four-channel endpoint.

Separate preprocessing, forest, server and network timing. Network location and TLS connections affect round trips. A first slow request is not necessarily a proven platform cold start. Public APIs intentionally do not expose probabilities; missing probabilities must not be replaced with fabricated confidence.

## Billing and quota visibility

Platform metrics and cost data can arrive late. A zero or empty cost query is not proof that no free grant was consumed. The student starting balance is user-confirmed unless independently retrieved. Budget notifications are not hard caps. Preserve the spending limit and use the resource-control guide only with approval for interruption or deletion.
