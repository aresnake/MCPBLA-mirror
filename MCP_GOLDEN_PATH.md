# MCP golden path

Two run modes are available for the MCP server:

- **Mode A – Stub MCP only**: `BRIDGE_ENABLED=false` (default). No Blender bridge is loaded. The server exposes `/health`, `/tools`, `/tools/{tool}/invoke`, and stub handlers for scene snapshots. Tools include `ping`, `echo`, `scene_snapshot_stub`, and the in-memory scene-state helpers (`create_cube_stub`, `get_scene_state`, etc.).
- **Mode B – Full Blender bridge**: `BRIDGE_ENABLED=true`. The live bridge, scenegraph, and event bus are wired. Endpoints `/blender/scene_snapshot` and `/bridge/event` operate against the live bridge. Requires a reachable Blender bridge handler (e.g., set `BLENDER_BRIDGE_ENABLED=true` and `BLENDER_BRIDGE_URL` when applicable).

## How to run

1) Create a virtual environment and install the project once:
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

2) Start the MCP server:
- Stub mode (default): `BRIDGE_ENABLED=false python -m mcpbla.server.mcp_server`
- Bridge mode: `BRIDGE_ENABLED=true BLENDER_BRIDGE_ENABLED=true python -m mcpbla.server.mcp_server`

PowerShell helpers are available in `scripts/`:
- `scripts/run_mcp.ps1` – activates `.venv`, installs in editable mode, sets `BRIDGE_ENABLED=false`, and starts the server.
- `scripts/run_blender_bridge.ps1` – same as above but sets `BRIDGE_ENABLED=true` (and `BLENDER_BRIDGE_ENABLED=true`) to activate the live bridge.
- `scripts/reset_all.ps1` – terminates MCP-related Python or Blender processes and clears typical MCP ports.

## Developer notes

- The tool registry automatically selects stub tools when `BRIDGE_ENABLED` is false and the full Blender toolset when it is true.
- Stub scene snapshots are stored in-memory; real snapshots flow through the live scenegraph when the bridge is enabled.
- Keep `MCP_HOST`/`MCP_PORT`/`MCP_WORKSPACE` environment variables consistent across modes if you override defaults.
- If the bridge fails to configure, `/bridge/event` returns HTTP 503 and bridge-only tools may report `BRIDGE_NOT_CONFIGURED`.
