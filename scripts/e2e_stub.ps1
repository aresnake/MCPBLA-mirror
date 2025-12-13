$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path -Path (Join-Path $PSScriptRoot "..")
Set-Location -Path $repoRoot

$serverScript = Join-Path $repoRoot "scripts\run_server_stub.ps1"

Write-Host "Starting stub server..."
$job = Start-Job -ScriptBlock {
    & $using:serverScript
} -Name "mcp_stub_server"

Start-Sleep -Seconds 1

Write-Host "Running stub E2E..."
& python scripts/e2e_stub.py
$exitCode = $LASTEXITCODE

Write-Host "Stopping stub server..."
if ($job -and (Get-Job -Id $job.Id -ErrorAction SilentlyContinue)) {
    Stop-Job -Id $job.Id -ErrorAction SilentlyContinue
    Remove-Job -Id $job.Id -ErrorAction SilentlyContinue
}

exit $exitCode
