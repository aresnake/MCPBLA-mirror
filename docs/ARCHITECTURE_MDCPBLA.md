# MCPBLA Architecture

## High-level layout
- `src/mcpbla/server/`: FastAPI MCP-style server exposing tools, orchestrators, and bridge endpoints.
- `src/mcpbla/blender/addon/`: Blender add-on and bridge client used to talk to the MCP server.
- `src/mcpbla/blender/scripts/`: Small demo scripts that hit the MCP HTTP endpoints.
- `scripts/`: Local utilities (start server, package add-on, run live demos).
- `tests/`: Pytest suites (unit + headless bridge checks).

## Server composition
- Entry point: `scripts/start_mcp_server.py` boots `server.mcp_server:create_app()` with env-driven config (`MCP_HOST`, `MCP_PORT`, `MCP_WORKSPACE`, `MCP_LOG_LEVEL`).
- Tool registry: `server.tools.registry.build_tool_registry(workspace_root)` aggregates all MCP tools from `server/tools/*_tools.py`; FastAPI exposes `/tools` and `/tools/{name}/invoke`.
- Bridge ingestion: `/blender/scene_snapshot` receives snapshots and stores them via `server.bridge.scenegraph_live`.
- Orchestrators: `server/orchestrator/*.py` build plans and dispatch tool calls; v3 variants add more detailed geometry/shader/animation flows.
- Agents: `server/agents/*.py` wrap specialized behaviors (modeler/shader/animation) used by orchestrators and tools.
- Core engines/contracts: `server/core/*` hold reusable data contracts and engine implementations for actions, geometry, materials, nodes, render/scene.
- Providers/hosts: `server/hosts/*` stub LLM hosts; `server/providers/*` stub asset/model sources.
- Utilities: `server/utils/config.py` (env config), `server/utils/logging_utils.py`.

## Bridge pipeline (server-side)
1. Blender (addon or script) POSTs a data-first snapshot to `/blender/scene_snapshot`.
2. FastAPI converts it to `scenegraph_live.SceneSnapshot` and stores it in-memory (`store_snapshot`, retrievable by session or last-seen).
3. Tools `get_last_scene_snapshot` and `get_scenegraph_snapshot` expose this data to LLMs/agents.
4. `scene_state` maintains a logical scene for stubbed create/move/material/fx operations so orchestrator demos work without Blender.

## End-to-end flow (LLM → MCP → Blender)
1. Host/LLM sends an instruction to MCP over HTTP (`/tools/run_task/invoke` or `/tools/plan_task/invoke`).
2. Orchestrator builds a `Plan` (sequence of tool calls) and executes via the tool registry.
3. Blender-facing tools either mutate the logical `scene_state` (stub) or, when running inside Blender, are mirrored by addon handlers (`blender/addon/bridge/actions.py` and UI operators) that perform data-first edits.
4. Blender can push live state back via `BridgeClient.send_snapshot`, keeping MCP aware of current scene objects.

## Phases present in code
- v1 stubbed MCP server with echo/listing tools and logical scene state.
- v2/v3 bridge/router/event plumbing for headless tests (`server.bridge.router_v2`, `server.bridge.events`).
- v3 orchestrators and agents for geometry/shader/animation with richer plan structures.
- Blender add-on with diagnostic panel and demo task runners.

## Limitations / TODO
- LLM hosts and asset/model providers are stubs (no real Anthropic/OpenAI/asset APIs wired).
- Transport is HTTP-only; no stdio/socket MCP transport yet for hosts that expect the official protocol.
- Bridge event ingestion endpoint (`/bridge/event`) is not exposed in FastAPI; addon `send_event` is placeholder.
- No persistence for snapshots/scene state; process memory only.
- Blender-side data-first actions cover a small subset (cube, move, material, modifier); more verbs needed for parity with tool names.
