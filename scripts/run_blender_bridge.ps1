Param(
    [string]$VenvPath = ".\\.venv"
)

$ErrorActionPreference = "Stop"

$activateScript = Join-Path $VenvPath "Scripts\\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Error "Virtual environment not found at $activateScript. Create it with 'python -m venv .venv'."
    exit 1
}

. $activateScript

Write-Host "Installing mcpbla in editable mode..."
pip install -e . | Out-Host

$env:BRIDGE_ENABLED = "true"
$env:BLENDER_BRIDGE_ENABLED = "true"
Write-Host "BRIDGE_ENABLED set to true (bridge mode). Starting MCP server with Blender bridge enabled..."

python -m mcpbla.server.mcp_server
