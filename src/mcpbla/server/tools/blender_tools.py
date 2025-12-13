"""Core Blender-adjacent stub tools exposed to MCP hosts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from mcpbla.server.bridge import scenegraph_live, scene_state
from mcpbla.server.tools.base import Tool
from mcpbla.server.tools.tool_response import INVALID_ARG, MISSING_ARG, ok, err


def get_scenegraph_snapshot() -> Dict[str, Any]:
    """Stub returning an empty scenegraph snapshot (legacy helper)."""
    return {"objects": [], "materials": []}


def _echo_text_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Echo the provided text payload."""
    text = arguments.get("text", "")
    return ok({"text": text})


def _list_workspace_files_handler(workspace_root: Path) -> Dict[str, Any]:
    """Return a shallow listing of the workspace root."""
    entries = []
    for item in workspace_root.iterdir():
        entries.append(item.name + ("/" if item.is_dir() else ""))
    return {"files": sorted(entries)}


def _get_last_scene_snapshot_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch the last live scene snapshot for a session if available."""
    session_id = arguments.get("session_id")
    snapshot = scenegraph_live.get_snapshot(session_id) if session_id else None
    if snapshot is None:
        snapshot = scenegraph_live.get_last_snapshot()
    if snapshot is None:
        return err(INVALID_ARG, f"No snapshot for session_id '{session_id}'")
    return ok(scenegraph_live.ScenegraphLive.serialize_snapshot(snapshot))


def _get_scenegraph_snapshot_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Return the latest stored scenegraph snapshot."""
    return _get_last_scene_snapshot_handler(arguments)


def _create_cube_handler(_: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a cube placeholder into the in-memory scene state."""
    scene_state.upsert_object("Cube", type="MESH", location=[0.0, 0.0, 0.0])
    return ok({"status": "created", "object": "Cube"})


def _create_sphere_handler(_: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a sphere placeholder into the in-memory scene state."""
    scene_state.upsert_object("Sphere", type="MESH", location=[0.0, 0.0, 0.0])
    return ok({"status": "created", "object": "Sphere"})


def _move_object_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Move an object by delta in the in-memory scene state."""
    name = arguments.get("object_name")
    if not name:
        return err(MISSING_ARG, "object_name is required")
    delta = arguments.get("delta")
    if not isinstance(delta, list) or len(delta) != 3:
        return err(INVALID_ARG, "delta must be a length-3 array")
    updated = scene_state.move_object(name, delta)
    return ok({"status": "moved", "object": name, "delta": delta, "location": updated["location"]})


def _assign_material_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Assign a material marker to an object in the in-memory state."""
    name = arguments.get("object_name")
    material = arguments.get("material")
    if not name:
        return err(MISSING_ARG, "object_name is required")
    if material is None or material == "":
        return err(MISSING_ARG, "material is required")
    scene_state.assign_material(name, material)
    return ok({"status": "material_assigned", "object": name, "material": material})


def _apply_fx_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Apply a simple FX marker to an object in the in-memory state."""
    name = arguments.get("object_name")
    fx = arguments.get("fx")
    if not name:
        return err(MISSING_ARG, "object_name is required")
    if fx is None or fx == "":
        return err(MISSING_ARG, "fx is required")
    scene_state.apply_fx(name, fx)
    return ok({"status": "fx_applied", "object": name, "fx": fx})


def _get_scene_state_handler(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return the current logical scene state."""
    return ok(scene_state.get_scene_state())


def get_tools(workspace_root) -> List[Tool]:
    """Return the list of Blender-facing MCP tools and stubs."""
    return [
        Tool(
            name="echo_text",
            description="[ALIAS of echo] Echo a piece of text.",
            input_schema={
                "type": "object",
                "properties": {"text": {"type": "string"}},
            },
            handler=_async_wrapper(_echo_text_handler),
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


def _async_wrapper(func):
    """Wrap sync handlers so they can be awaited uniformly."""

    async def wrapped(arguments: Dict[str, Any]) -> Any:
        return func(arguments)

    return wrapped
