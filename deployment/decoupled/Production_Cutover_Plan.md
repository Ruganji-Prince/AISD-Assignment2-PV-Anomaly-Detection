# Production cutover - approval required

All actions below remain pending. The verified static preview is `https://pv-anomaly-detection-pbyhom77a-prince-r-k.vercel.app` (dpl_7d4mEEWCvfvUnRCJ9ukKX9Js8oLD). Current production remains dpl_D24pfF7JJsBL5PRSy8VRQFAeXcpU. Azure already serves the verified CORS revision at the same URL and allocation.

1. Obtain explicit approval to promote this verified deployment and, separately within that approval, integrate the engineering changes into main. Re-fetch main and engineering heads; stop on unexpected changes. Preserve the submission tag and earlier history.
2. Recheck preview health, five-case parity, exact production CORS origins and the preserved rollback deployment. No model or resource change is required.
3. Before any main integration, address the existing Git-connected FastAPI configuration. Review and apply the candidate `frontend/production.vercel.json` as the root Vercel configuration in a subsequent authorized change. It selects no framework/install/build and disables main Git deployments, using manual verified prebuilt releases. This candidate has not been applied or exercised as a production source-build pipeline. Confirm effective Vercel project settings and prevent a legacy Python Git rebuild; do not merge blindly.
4. Promote only the tested static deployment using `vercel promote https://pv-anomaly-detection-pbyhom77a-prince-r-k.vercel.app --yes --scope prince-r-k`. Do not create another project. Confirm the canonical production aliases resolve to this deployment.
5. Run public frontend asset inventory, five-class API parity, browser requests, validation/CORS, failure handling and mobile smoke tests on the canonical production URL. Ensure the static output has no functions/models and Azure limits remain unchanged.
6. Publish final evidence and approved integration with normal fast-forward-compatible Git operations only. If any check fails, restore the preserved previous deployment using the [rollback guide](Rollback_Guide.md).

No production promotion, main merge, Git trigger change or project setting change has occurred in this preview checkpoint. The requested approval must cover this concrete release plan; new expenditure or resource expansion remains prohibited.
