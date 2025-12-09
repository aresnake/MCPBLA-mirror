# MCP Blender Orchestrator

A Model Context Protocol (MCP) server that hosts multiple LLM providers (Claude, OpenAI, etc.), exposes Blender-focused tools, and orchestrates agents to automate Blender jobs. The project also ships a Blender bridge client/add-on to keep a live scenegraph and exchange actions with the MCP server.

## Features (initial)
- FastAPI-based MCP-compatible server with healthcheck and dummy tools
- Pluggable LLM hosts and provider abstraction stubs
- Blender bridge placeholders (addon + scripts) designed for headless/background Blender
- Orchestrator/agent scaffolding for modeling, shading, FX roles

## Getting Started

### Requirements
- Python 3.10+
- (Optional) Blender 4.5+ for the addon/bridge parts

### Installation
```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows
pip install -e .[dev]
```

### Run the MCP server
```bash
python scripts/start_mcp_server.py
# server will listen on http://127.0.0.1:8000 by default
```

### Demo: connect and send a snapshot (no Blender required)
```bash
python blender/scripts/demo_connect.py
python blender/scripts/demo_scene_snapshot.py
```
Set `MCP_SERVER_URL` if your server is running elsewhere (default `http://127.0.0.1:8000`).

### Running tests
```bash
python -m pytest
```

## Orchestrator & Agents

The orchestrator plans and executes tasks using MCP tools. Key MCP tools:
- `plan_task`: create a plan from an instruction.
- `execute_plan`: run a provided plan.
- `run_task`: plan + execute in one call.

Example HTTP payloads (FastAPI endpoints):
- `POST /tools/plan_task/invoke` with body:
```json
{ "arguments": { "instruction": "create a cube and move it up" } }
```
- `POST /tools/run_task/invoke` with body:
```json
{ "arguments": { "instruction": "shade the cube with a red material" } }
```

### Running Orchestrator Demos
```bash
python -m scripts.start_mcp_server  # terminal 1
# in another terminal:
python -m blender.scripts.demo_run_task
```
The Blender addon (N-panel, MCP category) also has a "Run Demo Task" button that triggers the same orchestrator flow.

### Scene state (virtual)
Stub tools now maintain an in-memory logical scene on the MCP server (objects, locations, materials, fx). Use the MCP tool `get_scene_state` (via `/tools/get_scene_state/invoke`) to inspect the current state after running tasks.

### Blender-side execution
- The addon panel now includes **"Run Demo Task in Blender"**, which calls `plan_task` on the MCP server and executes the resulting steps locally in Blender (creates a cube at the origin and moves it up by 2m). Ensure the MCP server is running before clicking.

## Packaging the Blender addon
```bash
cd D:\MCPBLA
python scripts/package_addon.py
# output: dist/<addon_name>.zip
```
Optional cleanup of old installs:
```bash
python scripts/purge_installed_addon.py --dry-run
python scripts/purge_installed_addon.py
```
Install in Blender: Preferences → Add-ons → Install… → select the generated zip.

### Project layout
See the repository tree for server/, blender/, and scripts/ folders. Each area is modular so we can grow toolsets, providers, and agents over time.

