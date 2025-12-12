Param(
    [string]$BaseUrl = $env:MCP_SERVER_URL
)

$ErrorActionPreference = "Stop"

$base = if ($BaseUrl) { $BaseUrl } else { "http://127.0.0.1:8000" }
$base = $base.TrimEnd('/')
$url = "$base/tools/bridge_probe/invoke"
$payload = @{ arguments = @{} }

try {
    $resp = Invoke-RestMethod -Method Post -Uri $url -ContentType "application/json" -Body ($payload | ConvertTo-Json -Depth 5)
    Write-Output ($resp | ConvertTo-Json -Depth 8)
} catch {
    Write-Warning "Bridge probe failed: $($_.Exception.Message)"
    exit 1
}
