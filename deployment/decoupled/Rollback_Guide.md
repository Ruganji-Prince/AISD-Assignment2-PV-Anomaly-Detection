# Preserved rollback assets

No rollback or deletion was performed. Existing production deployment: dpl_D24pfF7JJsBL5PRSy8VRQFAeXcpU, `https://pv-anomaly-detection-jco5b5t1v-prince-r-k.vercel.app`. Canonical alias: `https://pv-anomaly-detection-prince-r-k.vercel.app`. [Preserved metadata](Previous_Vercel_Production.json) records its aliases and original source revision.

If an approved future cutover fails, restore the existing deployment with `vercel promote https://pv-anomaly-detection-jco5b5t1v-prince-r-k.vercel.app --yes --scope prince-r-k`, then verify the aliases, health and original predictions. This command is documented, not executed here.

Azure currently uses revision pv-anomaly-detection--cors-cf295ed and immutable digest sha256:234cba831be3b1465a8447c16922602dc54f5f0dcb3a86cc5b465c0890e5023f. Previous revision pv-anomaly-detection--rf-e4-940f5e2 remains present, healthy and inactive; original image digest sha256:51be78bd92b20af85628dd07009afd0cdad5689353fcf8a621604b7ea82e70e6 remains preserved. Both use `ghcr.io/ruganji-prince/pv-anomaly-detection`.

For backend recovery, first restore the legacy frontend to avoid dependence on new CORS. Inspect `az containerapp revision list --all --name pv-anomaly-detection --resource-group rg-pv-anomaly-detection`; activate the preserved original revision if supported by current single-revision state, or deploy the preserved immutable original image into the existing app. Verify traffic and readiness explicitly. Retain 0.5 vCPU / 1 GiB, min0/max1, existing environment and ingress; do not create resources, delete revisions or change the model. A backend rollback removes the new cross-origin support and therefore cannot accompany a functioning decoupled frontend without restoring that support.

Git rollback must be a new normal revert commit after review, never force push/reset/history rewrite. Preserve main, the archive, scientific artifacts and protected submission tag.
