$ErrorActionPreference = "Stop"

$targetPorts = @(8000, 8001)
$pids = New-Object System.Collections.Generic.HashSet[int]

Write-Host "Scanning for MCP-related processes to stop..."

foreach ($port in $targetPorts) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        if ($conn.OwningProcess) {
            [void]$pids.Add($conn.OwningProcess)
            Write-Host " - Flagged PID $($conn.OwningProcess) listening on port $port"
        }
    }
}

$processQuery = Get-CimInstance Win32_Process | Where-Object {
    ($_.ProcessName -match "python" -and $_.CommandLine -match "mcpbla") -or
    ($_.ProcessName -match "python" -and $_.CommandLine -match "mcp_server") -or
    ($_.ProcessName -match "blender")
}

foreach ($proc in $processQuery) {
    [void]$pids.Add([int]$proc.ProcessId)
    Write-Host " - Flagged PID $($proc.ProcessId) ($($proc.ProcessName)) via command-line match"
}

if ($pids.Count -eq 0) {
    Write-Host "No matching MCP or Blender processes found."
    exit 0
}

foreach ($pid in $pids) {
    try {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Write-Host "Stopped process PID $pid"
    } catch {
        Write-Warning "Could not stop PID ${pid}: $($_.Exception.Message)"
    }
}

Write-Host "Reset complete."
