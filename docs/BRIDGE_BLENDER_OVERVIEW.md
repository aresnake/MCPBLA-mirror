# Blender Bridge Overview

## What talks to what?
- **Client:** `blender/addon/bridge_client.py` sends HTTP requests to the MCP server (default `http://127.0.0.1:8000` or `MCP_SERVER_URL` env).
- **Addon UI:** `blender/addon/mcp_blender_addon.py` defines operators (ping, send snapshots, run demo task, run task in Blender) and a 3D View panel.
- **Server ingress:** FastAPI endpoint `/blender/scene_snapshot` ingests snapshots and stores them in `server.bridge.scenegraph_live`.
- **Server tools:** `get_last_scene_snapshot` / `get_scenegraph_snapshot` expose stored snapshots to LLMs; stub tools in `server.tools.blender_tools` mutate the logical scene state for headless demos.

## Data-first conventions
- Snapshots sent to MCP are plain dicts: `{"session_id": str, "objects": [...], "metadata": {...}}`.
- BridgeClient uses `send_snapshot` (real data) or `send_dummy_snapshot` (quick stub) to POST this payload.
- Actions inside Blender avoid `bpy.ops` when possible; `blender/addon/bridge/actions.py` directly edits meshes/objects/materials.
- Headless router/event bus (`server.bridge.router_v2`, `server.bridge.events`) keeps payloads minimal: `{type: "event", event: str, data: dict}`.

## Adding a new Blender tool (quick checklist)
1. Define a data-first handler in `blender/addon/bridge/actions.py` (avoid global state, return `{ok, data, error}`).
2. Expose an MCP tool on the server side (e.g., in `server/tools/blender_tools.py` or a dedicated module) with a clear JSON schema and async handler.
3. If the tool needs a roundtrip from Blender → server, add a BridgeClient method or reuse `send_snapshot`.
4. Wire a UI operator in `blender/addon/mcp_blender_addon.py` only if it must be clickable; otherwise rely on MCP tool calls.
5. Add a headless test in `tests/headless/` if the logic is testable without Blender; skip with markers when Blender runtime is required.

## Known gaps / TODO
- No FastAPI route currently mounts `/bridge/event`; addon `send_event` is placeholder until the route is exposed.
- Router/pool versions (`bridge_pool.py`, `pool_v2.py`, `router_v2.py`) are experimental; align before adding more message types.
- Snapshots are stored in-memory only; restart drops state.
