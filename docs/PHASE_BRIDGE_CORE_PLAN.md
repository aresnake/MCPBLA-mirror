# Phase Bridge Core — Plan & Wiring

Goal: enable a real Blender bridge transport (HTTP) while keeping stubs as default.

## 1) Where things live
- Action tools (server): `src/mcpbla/server/tools/action_tools.py` -> ActionEngine (now wraps ActionEngineV2) -> bridge pool v2.
- Bridge pools: `src/mcpbla/server/bridge/bridge_pool.py` (legacy) and `src/mcpbla/server/bridge/pool_v2.py` (current). Both return `BRIDGE_NOT_CONFIGURED` when no handler is set; lifecycle tracking in `bridge/lifecycle.py`.
- Bridge startup hook: `src/mcpbla/server/bridge/startup.py` (new `configure_bridge_from_env()` wires handler when env is set).
- Addon bridge handlers: `src/mcpbla/blender/addon/bridge/handlers_v2.py` (routes: create_cube.v2, move_object.v2, assign_material.v2, apply_modifier.v2, node.operation.v2, scene.snapshot.v2, render.preview.v2, system.ping, batch.execute) using data-first runtime.

## 2) Transport contract (HTTP)
- Request (server -> Blender addon):
  ```json
  {"route": "create_cube.v2", "payload": {"name": "Cube", "size": 1.0}, "request_id": "uuid"}
  ```
  - Fields accepted: `route` (or `action` alias), `payload` (or `params`), optional `request_id`/`correlation_id`.
- Response (Blender -> server):
  ```json
  {"ok": true, "data": {...}, "error": null, "request_id": "uuid"}
  ```
  - On error: `{"ok": false, "error": {"code": "BRIDGE_ERROR", "message": "..."}, "request_id": "uuid"}`.
  - Path: POST `${BLENDER_BRIDGE_URL}/bridge/route`.

## 3) Minimal real bridge implementation
- Server side:
  - New HTTP handler `HttpBridgeHandler` in `src/mcpbla/server/bridge/http_bridge.py` (stdlib urllib) posts to `/bridge/route`.
  - Env-gated wiring: `configure_bridge_from_env()` in `bridge/startup.py` binds handler to both bridge pools (v1/v2) when `BLENDER_BRIDGE_URL` is set; called from `mcp_server.create_app()`.
  - ActionEngine now uses ActionEngineV2 so tool routes match `.v2` handlers.
- Blender addon side:
  - New lightweight HTTP listener `src/mcpbla/blender/addon/bridge/http_server.py`, started on addon register (guarded by `MCP_BRIDGE_HTTP_ENABLED`, defaults on). Listens on `http://<host>:<port>/bridge/route` (env: `MCP_BRIDGE_HOST`, `MCP_BRIDGE_PORT`, defaults 127.0.0.1:8765), forwards to `handlers_v2.handle_route`.
  - Responses include `request_id` passthrough and `ok/data/error` fields.
- Stubs remain default: without `BLENDER_BRIDGE_URL`, bridge pools stay unconfigured and tools return `BRIDGE_NOT_CONFIGURED` as before.

## 4) Real-mode E2E script
- New script `scripts/dev/e2e_bridge_real.py` exercises real bridge: create_cube -> move_object -> assign_material via MCP tools, then calls `scene.snapshot.v2` directly on the bridge to verify `BridgeRealCube` exists.
- Preconditions: MCP server running with `BLENDER_BRIDGE_URL=http://127.0.0.1:8765` (or your port), Blender addon loaded (starts HTTP listener), and bpy available for data-first ops.

## 5) How to run
1) Start Blender addon (ensures HTTP listener up on 127.0.0.1:8765 unless overridden). Env overrides in Blender: `MCP_BRIDGE_HOST`, `MCP_BRIDGE_PORT`, `MCP_BRIDGE_HTTP_ENABLED` (set to `0` to disable).
2) Start MCP server with bridge enabled:
   ```bash
   set BLENDER_BRIDGE_URL=http://127.0.0.1:8765
   set MCP_HOST=127.0.0.1
   set MCP_PORT=8000
   set MCP_WORKSPACE=D:\MCPBLA
   python -m mcpbla.server.mcp_server
   ```
3) Run real bridge check from repo root (separate shell):
   ```bash
   set MCP_SERVER_URL=http://127.0.0.1:8000
   set BLENDER_BRIDGE_URL=http://127.0.0.1:8765
   python scripts/dev/e2e_bridge_real.py
   ```
   Expected: prints each step with `ok: true`, snapshot contains `BridgeRealCube`.

## 6) Files touched
- `src/mcpbla/server/agents/action_engine.py` (use v2 engine so routes match bridge v2).
- `src/mcpbla/server/bridge/http_bridge.py` (new HTTP handler).
- `src/mcpbla/server/bridge/startup.py` (env wiring helper).
- `src/mcpbla/server/mcp_server.py` (auto-configure bridge when env set).
- `src/mcpbla/blender/addon/bridge/http_server.py` (new HTTP listener inside Blender).
- `src/mcpbla/blender/addon/mcp_blender_addon.py` (start/stop HTTP listener on register/unregister).
- `scripts/dev/e2e_bridge_real.py` (real-mode verification script).

## 7) Next minimal steps (optional)
- Log bridge responses on server side for troubleshooting (debug level).
- Add a server-side MCP tool for `scene.snapshot.v2` to avoid direct bridge call in scripts.
- Align docs (`README`, `BRIDGE_BLENDER_OVERVIEW`) with new env vars and contract.
