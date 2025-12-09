# Tests in MCPBLA

## How to run
- From repo root: `python -m pytest`
- Set `PYTHONPATH` to include the repo root if running from another directory.
- Tests are designed to be headless; no Blender runtime is required. If you add Blender-dependent tests, mark them with `pytest.mark.skipif` on missing `bpy`.

## Coverage map
- `tests/test_mcp_server.py`: FastAPI endpoints (health, tools metadata, tool invocation, snapshot ingestion).
- `tests/test_blender_tools_stub.py`: Stubbed Blender tool behaviors (`list_workspace_files`, etc.).
- `tests/test_scene_state.py` and `tests/test_scenegraph_live.py`: In-memory scene state helpers.
- `tests/test_agents.py`, `tests/test_orchestrator.py`, `tests/test_orchestrator_v3.py`, `tests/test_modeler_agent_v3.py`, `tests/test_shader_agent_v3.py`: Planning/execution logic for orchestrators and agents.
- `tests/test_studio_tools_stub.py`: Studio-level stub tool coverage.
- `tests/headless/*`: Router/event/engine headless checks (action/material/render/scene engines, bridge event roundtrip, router receive).

## Adding tests
- Prefer pure-Python, headless tests to keep CI green without Blender.
- For Blender-only behaviors, isolate data shaping logic into helpers that can be tested headless, and guard Blender imports with `try/except ImportError`.
- Use explicit skips (`pytest.mark.skip` / `skipif`) instead of `sys.exit` or brittle environment assumptions.
