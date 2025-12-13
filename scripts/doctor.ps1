$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -Path (Join-Path $PSScriptRoot "..")
Set-Location -Path $repoRoot

$healthUrl = "http://127.0.0.1:8000/health"
$statusUrl = "http://127.0.0.1:8000/status"

function Fail {
    param ([string]$Message)
    Write-Host $Message
    exit 1
}

function TryRequest {
    param (
        [string]$Url,
        [int]$TimeoutSec = 3
    )
    try {
        return Invoke-WebRequest -Uri $Url -TimeoutSec $TimeoutSec -ErrorAction Stop
    } catch {
        return $null
    }
}

$healthResp = TryRequest -Url $healthUrl -TimeoutSec 3
if (-not $healthResp) {
    Fail "Health check failed (server not reachable). Hint: start the server with scripts/run_server_stub.ps1"
}

$healthStatus = [int]$healthResp.StatusCode
if ($healthStatus -ne 200) {
    Fail "Health returned HTTP $healthStatus. Hint: restart the server."
}

$statusResp = TryRequest -Url $statusUrl -TimeoutSec 5
if (-not $statusResp) {
    Fail "Status endpoint unreachable. Hint: verify the server is running."
}

try {
    $statusJson = $statusResp.Content | ConvertFrom-Json -ErrorAction Stop
} catch {
    Fail "Could not parse /status response."
}

$bridge = $statusJson.bridge
$server = $statusJson.server
$tools = $statusJson.tools
$version = $statusJson.version

Write-Host ("Health: HTTP {0}" -f $healthStatus)
Write-Host ("Bridge: enabled={0} configured={1} reachable={2} url={3}" -f $bridge.enabled, $bridge.configured, $bridge.reachable, ($bridge.url -as [string]))
Write-Host ("Tools: count={0}" -f $tools.count)
Write-Host ("Uptime: {0}s" -f $server.uptime_seconds)
Write-Host ("Git SHA: {0}" -f ($version.git_sha -as [string]))

if ($statusJson.ok -ne $true) {
    Fail "Status reported not ok."
}

Write-Host "Doctor checks passed."
exit 0
