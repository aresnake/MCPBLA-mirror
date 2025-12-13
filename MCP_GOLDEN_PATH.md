# MCP golden path

Two run modes are available for the MCP server:

- **Mode A - Stub MCP only**: `BRIDGE_ENABLED=false` (default). No Blender bridge is loaded. The server exposes `/health`, `/tools`, `/tools/{tool}/invoke`, and stub handlers for scene snapshots. Tools include `ping`, `echo`, `scene_snapshot_stub`, and the in-memory scene-state helpers (`create_cube_stub`, `get_scene_state`, etc.).
- **Mode B - Full Blender bridge**: `BRIDGE_ENABLED=true`. The live bridge, scenegraph, and event bus are wired. Endpoints `/blender/scene_snapshot` and `/bridge/event` operate against the live bridge. Requires a reachable Blender bridge handler configured via `BRIDGE_URL`.

## How to run

1) Create a virtual environment and install the project once:
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

2) Start the MCP server and run the smoke check (copy/paste):
- Terminal 1 (stub mode): `pwsh -File .\scripts\run_server_stub.ps1`
- Terminal 2 (smoke): `pwsh -File .\scripts\smoke_http.ps1`
- Stop the server: press `Ctrl+C` in Terminal 1 when finished.
- Optional bridge diagnostics: `curl http://127.0.0.1:8000/bridge/status` (or `Invoke-WebRequest http://127.0.0.1:8000/bridge/status | Select-Object -ExpandProperty Content` in PowerShell).
- Legacy tool invoke path: `POST /tools/{name}/invoke` (response wraps result).
- Clean invoke path: `POST /tools/{name}/invoke_v2` (returns tool payload directly).
- Quick doctor check: `pwsh -File .\scripts\doctor.ps1`
- Status endpoint: `curl http://127.0.0.1:8000/status` (or PowerShell `Invoke-WebRequest http://127.0.0.1:8000/status | Select-Object -ExpandProperty Content`)
- Bridge timeouts (env): `BRIDGE_TIMEOUT_SECONDS` (default 5.0), `BRIDGE_PING_TIMEOUT_SECONDS` (default 1.0)

Bridge mode (requires a live bridge endpoint):
- Set `BRIDGE_URL`, then run: `pwsh -File .\scripts\run_server_bridge.ps1`

PowerShell helpers are available in `scripts/`:
- `scripts/run_mcp.ps1` - activates `.venv`, installs in editable mode, sets `BRIDGE_ENABLED=false`, and starts the server.
- `scripts/run_blender_bridge.ps1` - same as above but sets `BRIDGE_ENABLED=true` to activate the live bridge.
- `scripts/reset_all.ps1` - terminates MCP-related Python or Blender processes and clears typical MCP ports.

Legacy env vars: `BLENDER_BRIDGE_ENABLED` and `BLENDER_BRIDGE_URL` are still supported but deprecated; prefer `BRIDGE_ENABLED` and `BRIDGE_URL`.

## Developer notes

- The tool registry automatically selects stub tools when `BRIDGE_ENABLED` is false and the full Blender toolset when it is true.
- Stub scene snapshots are stored in-memory; real snapshots flow through the live scenegraph when the bridge is enabled.
- Keep `MCP_HOST`/`MCP_PORT`/`MCP_WORKSPACE` environment variables consistent across modes if you override defaults.
- If the bridge fails to configure, `/bridge/event` returns HTTP 503 and bridge-only tools may report `BRIDGE_NOT_CONFIGURED`.
