"""Stub-only MCP tools exposed when the Blender bridge is disabled."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

from mcpbla.server.bridge import scene_state
from mcpbla.server.tools.base import Tool
from mcpbla.server.tools.tool_response import (
    INVALID_ARG,
    MISSING_ARG,
    ok,
    err,
)

_STUB_SNAPSHOTS: List[Dict[str, Any]] = []


def clear_stub_snapshots() -> None:
    """Reset the in-memory snapshot list (test helper)."""
    _STUB_SNAPSHOTS.clear()


def record_stub_snapshot(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Persist an in-memory snapshot without hitting the bridge."""
    session_id = payload.get("session_id") or ""
    if not session_id:
        raise ValueError("session_id is required")

    snapshot = {
        "session_id": session_id,
        "objects": payload.get("objects") or [],
        "metadata": payload.get("metadata") or {},
    }
    _STUB_SNAPSHOTS.append(deepcopy(snapshot))
    return {
        "status": "stored",
        "session_id": session_id,
        "objects": deepcopy(snapshot["objects"]),
        "objects_count": len(snapshot["objects"]),
        "metadata": deepcopy(snapshot["metadata"]),
    }


def get_stub_snapshot(session_id: str | None) -> Dict[str, Any]:
    """Return the last stored snapshot or one matching the session id."""
    if not _STUB_SNAPSHOTS:
        return {"error": "No snapshots stored"}
    if session_id:
        for snap in reversed(_STUB_SNAPSHOTS):
            if snap.get("session_id") == session_id:
                return deepcopy(snap)
        return {"error": f"No snapshot for session_id '{session_id}'"}

    return deepcopy(_STUB_SNAPSHOTS[-1])


def _async_wrapper(func):
    async def wrapped(arguments: Dict[str, Any]) -> Any:
        return func(arguments)

    return wrapped


def _ping_handler(_: Dict[str, Any]) -> Dict[str, Any]:
    return ok({"ok": True})


def _echo_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    return ok({"text": str(arguments.get("text", ""))})


def _scene_snapshot_stub_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    if not arguments.get("session_id"):
        return err(MISSING_ARG, "session_id is required")
    return ok(record_stub_snapshot(arguments))


def _list_workspace_files_handler(workspace_root: Path) -> Dict[str, Any]:
    entries = []
    for item in workspace_root.iterdir():
        entries.append(item.name + ("/" if item.is_dir() else ""))
    return ok({"files": sorted(entries)})


def _create_cube_handler(_: Dict[str, Any]) -> Dict[str, Any]:
    scene_state.upsert_object("Cube", type="MESH", location=[0.0, 0.0, 0.0])
    return ok({"status": "created", "object": "Cube"})


def _move_object_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    name = arguments.get("object_name")
    if not name:
        return err(MISSING_ARG, "object_name is required")
    delta = arguments.get("delta")
    if not isinstance(delta, list) or len(delta) != 3:
        return err(INVALID_ARG, "delta must be a length-3 array")
    updated = scene_state.move_object(name, delta)
    return ok({"status": "moved", "object": name, "delta": delta, "location": updated["location"]})


def _assign_material_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    name = arguments.get("object_name")
    material = arguments.get("material")
    if not name:
        return err(MISSING_ARG, "object_name is required")
    if material is None or material == "":
        return err(MISSING_ARG, "material is required")
    scene_state.assign_material(name, material)
    return ok({"status": "material_assigned", "object": name, "material": material})


def _apply_fx_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    name = arguments.get("object_name")
    fx = arguments.get("fx")
    if not name:
        return err(MISSING_ARG, "object_name is required")
    if fx is None or fx == "":
        return err(MISSING_ARG, "fx is required")
    scene_state.apply_fx(name, fx)
    return ok({"status": "fx_applied", "object": name, "fx": fx})


def _get_scene_state_handler(_: Dict[str, Any]) -> Dict[str, Any]:
    return ok(scene_state.get_scene_state())


def get_tools(workspace_root: Path) -> List[Tool]:
    """Expose stub-friendly tool set when the Blender bridge is disabled."""
    return [
        Tool(
            name="ping",
            description="Lightweight ping to verify the MCP server is reachable.",
            input_schema={"type": "object", "properties": {}},
            handler=_async_wrapper(_ping_handler),
        ),
        Tool(
            name="echo",
            description="Echo back the provided text (canonical).",
            input_schema={
                "type": "object",
                "properties": {"text": {"type": "string"}},
            },
            handler=_async_wrapper(_echo_handler),
        ),
        Tool(
            name="echo_text",
            description="[ALIAS of echo] Echo a piece of text.",
            input_schema={
                "type": "object",
                "properties": {"text": {"type": "string"}},
            },
            handler=_async_wrapper(_echo_handler),
        ),
        Tool(
            name="scene_snapshot_stub",
            description="Store a scene snapshot without requiring the Blender bridge.",
            input_schema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "objects": {"type": "array", "items": {"type": "object"}},
                    "metadata": {"type": "object"},
                },
            },
            handler=_async_wrapper(_scene_snapshot_stub_handler),
        ),
        Tool(
            name="list_workspace_files",
            description="List files in the MCP workspace root (non-recursive or shallow).",
            input_schema={"type": "object", "properties": {}},
            handler=_async_wrapper(lambda _=None: _list_workspace_files_handler(workspace_root)),
        ),
        Tool(
            name="create_cube_stub",
            description="Create a cube in the scene (stub).",
            input_schema={"type": "object", "properties": {}},
            handler=_async_wrapper(_create_cube_handler),
        ),
        Tool(
            name="move_object_stub",
            description="Move an object by delta (stub).",
            input_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "delta": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
                },
                "required": ["object_name", "delta"],
            },
            handler=_async_wrapper(_move_object_handler),
        ),
        Tool(
            name="assign_material_stub",
            description="Assign a material to an object (stub).",
            input_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "material": {"type": "string"},
                },
                "required": ["object_name", "material"],
            },
            handler=_async_wrapper(_assign_material_handler),
        ),
        Tool(
            name="apply_fx_stub",
            description="Apply a simple FX to an object (stub).",
            input_schema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "fx": {"type": "string"},
                },
                "required": ["object_name", "fx"],
            },
            handler=_async_wrapper(_apply_fx_handler),
        ),
        Tool(
            name="get_scene_state",
            description="Get the current in-memory logical scene state.",
            input_schema={"type": "object", "properties": {}},
            handler=_async_wrapper(_get_scene_state_handler),
        ),
    ]
