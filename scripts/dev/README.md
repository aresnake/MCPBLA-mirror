# Dev helper scripts

PowerShell helpers for local workflows (Windows):

- `start_server.ps1`: starts MCP server from repo root using `python -m mcpbla.server.mcp_server`; stores PID in `.runtime/server.pid` and echoes URL.
- `probe_bridge.ps1`: POSTs to `/tools/bridge_probe/invoke` (uses `MCP_SERVER_URL` or defaults to `http://127.0.0.1:8000`) and prints JSON.
- `reset_dev.ps1`: stops the server PID stored in `.runtime/server.pid` if present, then calls `start_server.ps1` and `probe_bridge.ps1`.
- `golden_path.py`: quick demo that probes the bridge, calls `create_cube`, posts a snapshot, and verifies `GoldenCube` appears via `get_scenegraph_snapshot`.

Usage (from repo root):
```powershell
powershell -ExecutionPolicy Bypass -File scripts/dev/start_server.ps1
powershell -ExecutionPolicy Bypass -File scripts/dev/probe_bridge.ps1
powershell -ExecutionPolicy Bypass -File scripts/dev/reset_dev.ps1
# optional: python scripts/dev/golden_path.py
```
