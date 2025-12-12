Param(
    [string]$Host = $env:MCP_HOST,
    [string]$Port = $env:MCP_PORT
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path "$PSScriptRoot/../.."
$runtimeDir = Join-Path $repoRoot ".runtime"
if (-not (Test-Path $runtimeDir)) {
    New-Item -ItemType Directory -Path $runtimeDir | Out-Null
}

$env:MCP_HOST = if ($Host) { $Host } else { "127.0.0.1" }
$env:MCP_PORT = if ($Port) { $Port } else { "8000" }

Write-Host "Starting MCP server at http://$($env:MCP_HOST):$($env:MCP_PORT) ..."
$process = Start-Process -FilePath "python" -ArgumentList "-m", "mcpbla.server.mcp_server" -WorkingDirectory $repoRoot -PassThru -WindowStyle Hidden
if (-not $process) {
    Write-Error "Failed to start MCP server"
    exit 1
}
$pidPath = Join-Path $runtimeDir "server.pid"
$process.Id | Out-File -FilePath $pidPath -Encoding ascii -Force
Write-Host "MCP server started. PID=$($process.Id) URL=http://$($env:MCP_HOST):$($env:MCP_PORT)"
