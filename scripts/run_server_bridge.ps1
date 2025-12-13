$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -Path (Join-Path $PSScriptRoot "..")
Set-Location -Path $repoRoot

$env:BRIDGE_ENABLED = "true"

if (-not $env:BRIDGE_URL -or [string]::IsNullOrWhiteSpace($env:BRIDGE_URL)) {
    Write-Host "BRIDGE_URL must be set when running the bridge server (e.g., http://127.0.0.1:5001)."
    exit 1
}

python -m mcpbla.server.mcp_server
