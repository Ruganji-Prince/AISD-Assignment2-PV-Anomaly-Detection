param([Parameter(Mandatory=$true)][string]$AzureUrl, [Parameter(Mandatory=$true)][string]$OutputDir)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $repoRoot
try {
    python -B -m deployment.azure.verify --azure-url $AzureUrl --output-dir $OutputDir
    if ($LASTEXITCODE -ne 0) { throw 'Azure verification failed.' }
} finally { Pop-Location }
