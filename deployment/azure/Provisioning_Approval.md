# Separate Azure provisioning approval

Status: **NOT PROVISIONED**. Only provider registration and approved container preparation/publication have occurred. The [subscription preflight](Infrastructure_Preflight.json) confirms Azure for Students, Enabled, spending limit On, Microsoft.App Registered, France Central environment quota 1 with usage 0, and no existing resources. No quota-increase request was needed. Microsoft.OperationalInsights was not registered because no Log Analytics workspace is planned.

## Proposed configuration

| Item | Proposed setting |
|---|---|
| Subscription | Existing Azure for Students; no upgrade |
| Region | France Central, allowed by subscription policy |
| Resource group | rg-pv-anomaly-detection |
| Environment | pv-anomaly-env; Consumption profile only |
| App | pv-anomaly-detection; single active revision |
| CPU / memory | 0.5 vCPU / 1 GiB |
| Replicas | Minimum 0, maximum 1 |
| Container | Verified public GHCR image, immutable digest |
| Ingress | External HTTPS; port 8000; insecure HTTP disabled |
| Health probes | Existing /api/health; startup grace for original model loading |
| Logs | logs-destination none; live log streaming; no persistent Log Analytics ingestion |
| Additional infrastructure | No dedicated profile, GPU, database, private endpoint, customer VNet or paid registry |
| Credentials | Anonymous image pull; existing authenticated CLI for manual deployment |

The per-environment consumption-core quota cannot be inspected before an environment exists. After environment creation is separately authorized, inspect that quota before creating the app; stop if 0.5 vCPU cannot be supported. Do not increase allocation or create a substitute service without review. All regional, policy and cost checks must be refreshed immediately before provisioning.

## Potential costs

The [official-rate receipt](Pricing_Preflight.json) records USD 0.000024 per active vCPU-second, USD 0.000003 per active GiB-second and USD 0.40 per million HTTP requests for France Central. Monthly subscription-wide grants are 180,000 vCPU-seconds, 360,000 GiB-seconds and two million HTTP requests. At 0.5 vCPU and 1 GiB, otherwise-unused compute grants cover approximately 100 replica-hours. The resource group itself has no deployment compute allocation; the app is potentially billable beyond shared grants. Features such as private endpoints and planned maintenance are excluded because additional environment/management charges can apply.

One active replica costs approximately USD 0.054 per hour before grants. A conservative continuously-active 30-day illustration is USD 33.48 compute after unused grants, plus any applicable request/network charges and taxes. This is not a hard cap or a prediction of demonstration usage. Minimum zero enables scale-to-zero but does not guarantee how quickly each idle period ends, and traffic or probes can affect activity. Request latency alone is not a valid billing estimate.

GHCR container storage/bandwidth and standard public-repository GitHub Actions runners are currently free under the documented policies. The user-confirmed USD 100 student balance was not independently retrieved. The subscription spending limit remains On. No pay-as-you-go upgrade, paid support, paid registry or budget-alert resource was created. Budget alerts, if later approved, are notifications rather than hard spending caps.

Sources: [Azure Container Apps billing](https://learn.microsoft.com/en-us/azure/container-apps/billing), [Azure pricing](https://azure.microsoft.com/en-us/pricing/details/container-apps/), [GitHub Packages billing](https://docs.github.com/en/billing/concepts/product-billing/github-packages), [GitHub runner policy](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job).

## Approval scope still required

Separate explicit authorization is required to create the named Azure resource group, Consumption environment and app with the configuration above, accepting potential usage of student credit beyond applicable grants. Container publication approval does not authorize these resources. No deployment or benchmark is claimed before that authorization and successful execution. The existing Vercel application, protected submission tag and all scientific artifacts remain preserved.
