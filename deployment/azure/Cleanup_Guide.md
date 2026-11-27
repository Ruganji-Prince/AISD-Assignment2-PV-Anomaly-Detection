# Monitoring and resource control

The professor-facing deployment must remain available for the December 1 or December 4, 2026 evaluation. The commands below are documentation only; interruption and deletion have not been performed.

## Inspect resources and usage

```sh
az account show --query '{name:name,state:state,isDefault:isDefault}'
az resource list --resource-group rg-pv-anomaly-detection --output table
az containerapp show --name pv-anomaly-detection --resource-group rg-pv-anomaly-detection
az containerapp revision list --name pv-anomaly-detection --resource-group rg-pv-anomaly-detection
az containerapp env list-usages --name pv-anomaly-env --resource-group rg-pv-anomaly-detection
az containerapp logs show --name pv-anomaly-detection --resource-group rg-pv-anomaly-detection --type console --tail 30
```

In Azure Portal, open the named resource group, then the Container App. Review Revisions and replicas, Metrics, Scale, Ingress and Containers. Cost Management can show accumulated costs after reporting delay. Azure for Students remaining credit is available through the [Azure Sponsorships balance portal](https://www.microsoftazuresponsorships.com/Balance). The USD100 starting credit remains user-confirmed unless an independent balance query is recorded. Retain the subscription spending limit. A budget alert is not a hard cap; no budget resource was created.

## Temporary interruption requires approval

Minimum zero allows automatic scale-to-zero after inactivity; it does not make the application permanently stopped. Inspect actual replica state rather than inferring it from an idle browser.

The installed CLI does not provide `az containerapp stop` or `start`. Do not copy those unsupported commands. Microsoft documents REST stop/start operations even though the installed CLI has no matching convenience commands. They were not executed against this deployment, to preserve availability. After explicit interruption approval, the documented operations use the actual app ID:

```sh
az rest --method post --url 'https://management.azure.com/subscriptions/38a91a22-90a0-45e3-aad6-ce69bf22ed3a/resourceGroups/rg-pv-anomaly-detection/providers/Microsoft.App/containerApps/pv-anomaly-detection/stop?api-version=2026-07-01'
az rest --method post --url 'https://management.azure.com/subscriptions/38a91a22-90a0-45e3-aad6-ce69bf22ed3a/resourceGroups/rg-pv-anomaly-detection/providers/Microsoft.App/containerApps/pv-anomaly-detection/start?api-version=2026-07-01'
```

Recheck service support/response before relying on these operations; no stop/start result is claimed here. See [Microsoft stop API](https://learn.microsoft.com/en-us/rest/api/resource-manager/containerapps/container-apps/stop?view=rest-resource-manager-containerapps-2026-07-01) and [start API](https://learn.microsoft.com/en-us/rest/api/resource-manager/containerapps/container-apps/start?view=rest-resource-manager-containerapps-2026-07-01). Revision deactivation/activation commands also exist, but single-revision-mode restrictions must be checked before using them. Any intentional interruption requires approval and must preserve the image digest and original resource limits. Do not change the application to a different plan or increase replicas as a workaround.

## Destructive project removal requires explicit approval

The following command deletes the entire dedicated project resource group, including the environment and app. It removes the Azure endpoint and must not be executed before evaluation or without explicit approval:

```sh
az group delete --name rg-pv-anomaly-detection --yes --no-wait
```

First inspect the resource list to ensure the dedicated group contains only project resources. Never delete unrelated resource groups, the public GitHub repository, GHCR package, protected tag, original model, scientific artifacts or the existing Vercel application. No deletion is performed by the deployment/verification scripts.

After an approved deletion, restoration uses the documented immutable image and the guarded deployment script with fresh quota/policy checks. Restoration can receive a different Azure hostname. Re-verify the actual endpoint and update links rather than assuming the former URL returns.
