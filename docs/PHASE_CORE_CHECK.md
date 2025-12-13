# MCPBLA Phase Core Check

## Server start check
- Command: `python - <<SCRIPT>>` (programmatic uvicorn start/stop on 127.0.0.1:8010 for 2s)
- Result: server booted and shut down cleanly; FastAPI app initialized without errors and subscribed scenegraph/event bus.

## Tool inventory (37)
- Registry built via `build_tool_registry(Path.cwd())`.
- Tools: animation_agent_v3_run, animation_execute_v3, animation_plan_v3, api_probe_blender_version, apply_fx_stub, apply_modifier, assign_material, assign_material_stub, bridge_probe, create_cube, create_cube_stub, create_sphere_stub, echo_text, execute_plan, execute_plan_v3, geo_agent_v3_run, geo_execute_v3, geo_plan_v3, get_last_scene_snapshot, get_scene_state, get_scenegraph_snapshot, list_workspace_files, modeler_agent_v3_run, move_object, move_object_stub, plan_task, plan_v3, refine_plan_v3, run_task, scenegraph_describe, scenegraph_get, scenegraph_search, shader_agent_v3_run, shader_execute_v3, shader_plan_v3, studio_full_test, system_probe_full.
- Modules: under `src/mcpbla/server/tools/*_tools.py`; descriptions and JSON input schemas are defined in their `get_tools()` declarations.
- Docs mismatch: `docs/MCP_TOOLS_OVERVIEW.md` lists 34 tools; new tools present (`system_probe_full`, `api_probe_blender_version`, `bridge_probe`) and counts differ (registry shows 37).

## 5-core-tools comparison
- No canonical “5-core-tools” list is defined in the repo/docs. Assumed core MCP coverage = basic IO and orchestration primitives: `echo_text`, `list_workspace_files`, `plan_task`, `run_task`, `get_scene_state`.
- Status: all five above are present and callable via `/tools/<name>/invoke`. If a different 5-core set is intended, it is not documented.

## Minimal E2E scenario
- Command: `python -m mcpbla.server.scripts.e2e_studio_test`
- Result: PASS. Steps completed: config load, registry build (37 tools), scene reset, system_probe_full, echo_text, create/move/assign/apply FX stubs, scene state inspection, snapshot roundtrip.

## Config and host assumptions
- Server config from env: `MCP_HOST` (default 127.0.0.1), `MCP_PORT` (default 8000), `MCP_WORKSPACE` (defaults to cwd), `MCP_LOG_LEVEL` (default INFO). README examples still mention `MCPBLA_LOG_LEVEL` (inconsistent with code).
- Claude Desktop host example: `mcp/claude_desktop_config.example.json` runs `python -m mcpbla.server.mcp_server` with the above env and workspace `D:\MCPBLA`.

## Tests
- Command: `python -m pytest`
- Result: 40 passed, 0 failed (0.99s).

## What’s missing to declare CORE FINI
- Blender integration is stubbed: action tools (`create_cube`, `move_object`, `assign_material`, `apply_modifier`) return bridge-not-configured errors; no bpy/bmesh path wired yet.
- Bridge pool/router exist but no real transport/handshake to Blender; `bridge_probe` reports not configured unless custom handler injected.
- LLM hosts for OpenAI/Claude are TODO stubs (no SDK calls implemented), so orchestrator/agent behaviors are mocked.
- Tool docs lag registry (count + new system/bridge probes); need alignment for host expectations.
- Env var naming inconsistency (`MCP_LOG_LEVEL` vs README’s `MCPBLA_LOG_LEVEL`) could lead to silent INFO defaults.
- No persistence or auth; everything in-memory (scenegraph, snapshots) and unauthenticated HTTP endpoints.
- Core definitions (the “5-core-tools” list) are undocumented; acceptance criteria for “core” remains implicit.
