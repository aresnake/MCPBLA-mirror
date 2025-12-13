"""Stub-only MCP tools exposed when the Blender bridge is disabled."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

from mcpbla.server.bridge import scene_state
from mcpbla.server.tools.base import Tool

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
    return {"ok": True}


def _echo_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    return {"text": str(arguments.get("text", ""))}


def _scene_snapshot_stub_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    return record_stub_snapshot(arguments)


def _list_workspace_files_handler(workspace_root: Path) -> Dict[str, Any]:
    entries = []
    for item in workspace_root.iterdir():
        entries.append(item.name + ("/" if item.is_dir() else ""))
    return {"files": sorted(entries)}


def _create_cube_handler(_: Dict[str, Any]) -> Dict[str, Any]:
    scene_state.upsert_object("Cube", type="MESH", location=[0.0, 0.0, 0.0])
    return {"status": "created", "object": "Cube"}


def _create_sphere_handler(_: Dict[str, Any]) -> Dict[str, Any]:
    scene_state.upsert_object("Sphere", type="MESH", location=[0.0, 0.0, 0.0])
    return {"status": "created", "object": "Sphere"}


def _move_object_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    name = arguments.get("object_name")
    delta = arguments.get("delta", [0, 0, 0])
    updated = scene_state.move_object(name, delta)
    return {"status": "moved", "object": name, "delta": delta, "location": updated["location"]}


def _assign_material_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    name = arguments.get("object_name")
    material = arguments.get("material")
    scene_state.assign_material(name, material)
    return {"status": "material_assigned", "object": name, "material": material}


def _apply_fx_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    name = arguments.get("object_name")
    fx = arguments.get("fx")
    scene_state.apply_fx(name, fx)
    return {"status": "fx_applied", "object": name, "fx": fx}


def _get_scene_state_handler(_: Dict[str, Any]) -> Dict[str, Any]:
    return scene_state.get_scene_state()


def _get_last_scene_snapshot_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    session_id = arguments.get("session_id")
    return get_stub_snapshot(session_id)


def _get_scenegraph_snapshot_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    session_id = arguments.get("session_id")
    return get_stub_snapshot(session_id)


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
            description="Echo back the provided text.",
            input_schema={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
            handler=_async_wrapper(_echo_handler),
        ),
        Tool(
            name="echo_text",
            description="Echo a piece of text.",
            input_schema={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
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
                "required": ["session_id"],
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
            name="get_last_scene_snapshot",
            description="Retrieve the latest scene snapshot for a session.",
            input_schema={
                "type": "object",
                "properties": {"session_id": {"type": "string"}},
                "required": ["session_id"],
            },
            handler=_async_wrapper(_get_last_scene_snapshot_handler),
        ),
        Tool(
            name="get_scenegraph_snapshot",
            description="Return the last stored scene snapshot (scenegraph).",
            input_schema={
                "type": "object",
                "properties": {"session_id": {"type": "string"}},
            },
            handler=_async_wrapper(_get_scenegraph_snapshot_handler),
        ),
        Tool(
            name="create_cube_stub",
            description="Create a cube in the scene (stub).",
            input_schema={"type": "object", "properties": {}},
            handler=_async_wrapper(_create_cube_handler),
        ),
        Tool(
            name="create_sphere_stub",
            description="Create a sphere in the scene (stub).",
            input_schema={"type": "object", "properties": {}},
            handler=_async_wrapper(_create_sphere_handler),
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
