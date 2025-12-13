$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -Path (Join-Path $PSScriptRoot "..")
Set-Location -Path $repoRoot

$env:BRIDGE_ENABLED = "false"

python -m mcpbla.server.mcp_server
