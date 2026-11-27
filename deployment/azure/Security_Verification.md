# Azure security verification

The original RF E4 runtime is reused without training, calibration, threshold changes or new inference endpoints. [Live checks](live/Deployment_Verification.json), [image audit](Container_Verification.json), [actual Azure model probe](live/Azure_Runtime_Parity.json) and [dependency database check](Dependency_Scan.json) provide bounded evidence; no complete-security claim is made.

| Control | Evidence and outcome | Limitation |
| --- | --- | --- |
| HTTPS | Public certificate validated by httpx and browser; ingress external, allowInsecure false | Certificate management is Azure-managed; no custom key was created |
| Input schema | Ten invalid cases rejected on Azure and Vercel; missing/extra/negative/null/text/boolean/nonfinite/duplicate/malformed/oversize | Observed ranges are not certified PV equipment safety limits |
| Output semantics | Five classes match original CLI; shade is environmental; no confidence or probabilities exposed | Scientific TEST remains historically exposed |
| Headers | CSP self, nosniff, frame denial, no-store API, timing headers verified | Headers do not establish resistance to every web attack |
| Model deserialization | SHA-256 checked before trusted original pickle load; actual Azure file hash matches | Never load user-supplied or untrusted pickle artifacts |
| Container contents | Every application file in every image layer matches the committed allowlist; no dataset/credentials/private folders | Heuristic secret scanning is not exhaustive; base packages are separate |
| Runtime account | Verified image uses nonroot appuser; no override in deployed template | Azure root filesystem is not claimed read-only; read-only mode was separately tested in Linux CI |
| Registry | Public immutable digest; anonymous manifest and all runtime-layer access verified | Registry immutability is addressed by digest pinning, not mutable tags |
| GitHub Actions | contents read, packages write; ephemeral token supplied only after image verification | No Azure continuous deployment or OIDC integration was added |
| Azure authentication | Existing authenticated CLI; no new service principal, long-lived key, role assignment or app secret | Existing deployment identity has broad preexisting Owner permissions; future CI should use scoped OIDC |
| Dependency versions | Hash-locked runtime install; 41-package local consistency check; OSV package lookup returned no matches | OS/base-image vulnerability scan not completed; databases can miss new issues |
| Capacity and deadlines | Existing two-operation/process bound, five-second body and fifteen-second response deadlines; local tests passed, live concurrency two succeeded | Not distributed IP/user rate limiting; timed-out worker threads continue until completion |
| Billing scope | 0.5 vCPU/1 GiB, 0-1 replicas, no persistent Log Analytics or additional infrastructure | Public traffic can consume grants/credit; no small project-specific hard budget cap |

No Azure token, GitHub token, registry login, private key or credential file is included in the reviewed publication context. Context construction reads only specified committed blobs. The original dataset and scientific artifacts remain outside the runtime image. The app has zero configured secrets and no registry credentials. Only two harmless runtime environment variables are configured. No credential is required by browser visitors.

Live logs are limited because persistent ingestion is disabled. No public request payload logging or private local path is added. No purchased WAF, networking service, paid support or subscription upgrade was activated. Distributed rate limiting, centralized incident monitoring, formal penetration testing and industrial security certification remain outside this prototype.
