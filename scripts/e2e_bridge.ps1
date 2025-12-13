$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -Path (Join-Path $PSScriptRoot "..")
Set-Location -Path $repoRoot

Write-Host "BRIDGE_ENABLED=$($env:BRIDGE_ENABLED)"
Write-Host "BRIDGE_URL=$($env:BRIDGE_URL)"
Write-Host "Running bridge E2E..."

& python scripts/e2e_bridge.py
exit $LASTEXITCODE
