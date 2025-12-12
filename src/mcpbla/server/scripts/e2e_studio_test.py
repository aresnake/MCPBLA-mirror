from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List

from mcpbla.server.bridge import scene_state, scenegraph_live
from mcpbla.server.tools.base import Tool
from mcpbla.server.tools.registry import build_tool_registry
from mcpbla.server.utils.config import load_config


@dataclass
class StepResult:
    name: str
    ok: bool
    detail: str = ""


def _format_steps(steps: List[StepResult]) -> str:
    lines = []
    for step in steps:
        prefix = "OK" if step.ok else "FAIL"
        suffix = f" - {step.detail}" if step.detail else ""
        lines.append(f"{prefix} {step.name}{suffix}")
    return "\n".join(lines)


def _run_tool(registry: Dict[str, Tool], name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    tool = registry.get(name)
    if tool is None:
        raise RuntimeError(f"tool '{name}' is not registered")
    return asyncio.run(tool.handler(arguments))


def main() -> int:
    steps: List[StepResult] = []

    try:
        config = load_config()
        registry = build_tool_registry(config.workspace_root)
        steps.append(StepResult("load config", True, f"workspace={config.workspace_root}"))
        steps.append(StepResult("build tool registry", True, f"{len(registry)} tools"))
    except Exception as exc:  # pragma: no cover - script level guard
        steps.append(StepResult("initialize", False, str(exc)))
        print(_format_steps(steps))
        return 1

    try:
        scene_state.reset_scene_state()
        scenegraph_live.clear_registry()
        steps.append(StepResult("reset in-memory state", True, "scene + snapshots cleared"))
    except Exception as exc:  # pragma: no cover - script level guard
        steps.append(StepResult("reset in-memory state", False, str(exc)))
        print(_format_steps(steps))
        return 1

    try:
        probe = _run_tool(registry, "system_probe_full", {"include_env": False})
        probe_ok = bool(probe.get("ok", True)) if isinstance(probe, dict) else False
        steps.append(StepResult("system probe", probe_ok, "python/platform reachable"))
    except Exception as exc:  # pragma: no cover - script level guard
        steps.append(StepResult("system probe", False, str(exc)))

    try:
        echo_payload = "studio-e2e-check"
        echo_resp = _run_tool(registry, "echo_text", {"text": echo_payload})
        echoed = echo_resp.get("text") if isinstance(echo_resp, dict) else None
        steps.append(StepResult("echo text", echoed == echo_payload, f"echoed={echoed}"))
    except Exception as exc:  # pragma: no cover - script level guard
        steps.append(StepResult("echo text", False, str(exc)))

    try:
        cube = _run_tool(registry, "create_cube_stub", {})
        cube_ok = isinstance(cube, dict) and cube.get("status") == "created"
        steps.append(StepResult("create cube stub", cube_ok, str(cube)))

        move = _run_tool(registry, "move_object_stub", {"object_name": "Cube", "delta": [0, 0, 1]})
        move_ok = isinstance(move, dict) and move.get("status") == "moved" and move.get("location") == [0.0, 0.0, 1.0]
        steps.append(StepResult("move cube stub", move_ok, str(move)))

        material = _run_tool(registry, "assign_material_stub", {"object_name": "Cube", "material": "TestMat"})
        mat_ok = isinstance(material, dict) and material.get("status") == "material_assigned"
        steps.append(StepResult("assign material stub", mat_ok, str(material)))

        fx = _run_tool(registry, "apply_fx_stub", {"object_name": "Cube", "fx": "Glow"})
        fx_ok = isinstance(fx, dict) and fx.get("status") == "fx_applied"
        steps.append(StepResult("apply fx stub", fx_ok, str(fx)))

        state = _run_tool(registry, "get_scene_state", {})
        objects = state.get("objects") if isinstance(state, dict) else {}
        cube_state = objects.get("Cube") if isinstance(objects, dict) else None
        cube_state_ok = bool(cube_state) and cube_state.get("material") == "TestMat" and cube_state.get("location") == [0.0, 0.0, 1.0]
        steps.append(StepResult("inspect scene state", cube_state_ok, str(cube_state)))
    except Exception as exc:  # pragma: no cover - script level guard
        steps.append(StepResult("data-first actions", False, str(exc)))

    try:
        snapshot = scenegraph_live.SceneSnapshot(
            session_id="studio_e2e",
            objects=[{"name": "Cube", "location": [0.0, 0.0, 1.0]}],
            metadata={"source": "studio_e2e"},
        )
        scenegraph_live.store_snapshot(snapshot)
        snap_resp = _run_tool(registry, "get_last_scene_snapshot", {"session_id": "studio_e2e"})
        snap_ok = isinstance(snap_resp, dict) and snap_resp.get("session_id") == "studio_e2e"
        steps.append(StepResult("snapshot roundtrip", snap_ok, str(snap_resp)))
    except Exception as exc:  # pragma: no cover - script level guard
        steps.append(StepResult("snapshot roundtrip", False, str(exc)))

    all_ok = all(step.ok for step in steps)
    print(_format_steps(steps))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
