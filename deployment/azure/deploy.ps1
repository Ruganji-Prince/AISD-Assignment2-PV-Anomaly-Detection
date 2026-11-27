param([switch]$ApproveProvisioning)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $repoRoot
try {
    if ($ApproveProvisioning) { python -B -m deployment.azure.deploy --approve-provisioning }
    else { python -B -m deployment.azure.deploy }
    if ($LASTEXITCODE -ne 0) { throw 'Azure deployment command failed; inspect existing resources before retrying.' }
} finally { Pop-Location }
