$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path "$PSScriptRoot/../.."
$runtimeDir = Join-Path $repoRoot ".runtime"
$pidPath = Join-Path $runtimeDir "server.pid"

if (Test-Path $pidPath) {
    $pid = Get-Content $pidPath | Select-Object -First 1
    if ($pid) {
        Write-Host "Stopping MCP server PID=$pid"
        try {
            Stop-Process -Id $pid -ErrorAction SilentlyContinue
        } catch {
            Write-Warning "Failed to stop process $pid: $($_.Exception.Message)"
        }
    }
    Remove-Item $pidPath -ErrorAction SilentlyContinue
}

Write-Host "Starting fresh MCP server..."
& "$PSScriptRoot/start_server.ps1"

Write-Host "Probing bridge..."
& "$PSScriptRoot/probe_bridge.ps1"
