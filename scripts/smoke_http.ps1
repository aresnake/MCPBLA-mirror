$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -Path (Join-Path $PSScriptRoot "..")
Set-Location -Path $repoRoot

$healthUrl = "http://127.0.0.1:8000/health"
$toolsUrl = "http://127.0.0.1:8000/tools"

function Fail {
    param (
        [string]$Message
    )

    Write-Host $Message
    exit 1
}

try {
    $healthResponse = Invoke-WebRequest -Uri $healthUrl -TimeoutSec 3 -ErrorAction Stop
    $healthStatus = [int]$healthResponse.StatusCode
    Write-Host ("Health status code: {0}" -f $healthStatus)
    if ($healthStatus -ne 200) {
        Fail "Health check failed (expected HTTP 200)."
    }
} catch {
    Fail ("Health request failed: {0}" -f $_.Exception.Message)
}

try {
    $toolsResponse = Invoke-WebRequest -Uri $toolsUrl -TimeoutSec 5 -ErrorAction Stop
    $toolsJson = $toolsResponse.Content | ConvertFrom-Json -ErrorAction Stop

    $toolCount = $null
    if ($null -ne $toolsJson) {
        if ($toolsJson -is [System.Collections.IEnumerable] -and -not ($toolsJson -is [string])) {
            $toolCount = ($toolsJson | Measure-Object).Count
        } elseif ($toolsJson.PSObject.Properties.Name -contains "tools") {
            $toolCount = ($toolsJson.tools | Measure-Object).Count
        }
    }

    if ($toolCount -eq $null) {
        Fail "Could not determine tool count from /tools response."
    }

    Write-Host ("Tool count: {0}" -f $toolCount)
} catch {
    Fail ("Tools request failed: {0}" -f $_.Exception.Message)
}

Write-Host "Smoke HTTP checks passed."
exit 0
