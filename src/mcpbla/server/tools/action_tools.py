"""Action engine-backed MCP tools for direct modeling operations."""

from __future__ import annotations

from typing import Any, Dict, List

from mcpbla.server.agents.action_engine import ActionEngine
from mcpbla.server.tools.base import Tool
from mcpbla.server.tools.tool_response import (
    BRIDGE_UNREACHABLE,
    INVALID_ARG,
    MISSING_ARG,
    INTERNAL_ERROR,
    ok,
    err,
)


def _async_wrapper(func):
    """Wrap sync handlers for async MCP tool compatibility."""
    async def wrapped(arguments: Dict[str, Any]) -> Any:
        return func(arguments)

    return wrapped


def _create_engine() -> ActionEngine:
    """Instantiate a fresh ActionEngine per call."""
    return ActionEngine()


def _create_cube_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Create a cube through the action engine."""
    engine = _create_engine()
    name = arguments.get("name")
    if not name:
        return err(MISSING_ARG, "name is required")
    size = float(arguments.get("size", 1.0))
    try:
        result = engine.execute("create_cube", {"name": name, "size": size})
    except Exception as exc:  # noqa: BLE001
        return err(BRIDGE_UNREACHABLE, "Bridge unreachable", {"error": str(exc)})
    if result.ok:
        return ok(result.data)
    error_msg = result.error if isinstance(result.error, str) else str(result.error)
    return err(INTERNAL_ERROR, "Action failed", {"error": error_msg, "data": result.data})


def _move_object_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Move an object using the action engine translation op."""
    engine = _create_engine()
    name = arguments.get("name")
    if not name:
        return err(MISSING_ARG, "name is required")
    translation = arguments.get("translation")
    if not isinstance(translation, dict):
        return err(INVALID_ARG, "translation must be an object")
    for axis in ("x", "y", "z"):
        if axis not in translation:
            return err(MISSING_ARG, f"translation.{axis} is required")
    try:
        result = engine.execute("move_object", {"name": name, "translation": translation})
    except Exception as exc:  # noqa: BLE001
        return err(BRIDGE_UNREACHABLE, "Bridge unreachable", {"error": str(exc)})
    if result.ok:
        return ok(result.data)
    error_msg = result.error if isinstance(result.error, str) else str(result.error)
    return err(INTERNAL_ERROR, "Action failed", {"error": error_msg, "data": result.data})


def _assign_material_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Assign a material with color to a given object."""
    engine = _create_engine()
    obj = arguments.get("object")
    material = arguments.get("material")
    color = arguments.get("color")
    if not obj:
        return err(MISSING_ARG, "object is required")
    if material is None or material == "":
        return err(MISSING_ARG, "material is required")
    if not isinstance(color, list) or len(color) != 3:
        return err(INVALID_ARG, "color must be a length-3 array")
    try:
        result = engine.execute("assign_material", {"object": obj, "material": material, "color": color})
    except Exception as exc:  # noqa: BLE001
        return err(BRIDGE_UNREACHABLE, "Bridge unreachable", {"error": str(exc)})
    if result.ok:
        return ok(result.data)
    error_msg = result.error if isinstance(result.error, str) else str(result.error)
    return err(INTERNAL_ERROR, "Action failed", {"error": error_msg, "data": result.data})


def _apply_modifier_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Apply a modifier with provided settings to an object."""
    engine = _create_engine()
    obj = arguments.get("object")
    mod_type = arguments.get("type")
    settings = arguments.get("settings")
    if not obj:
        return err(MISSING_ARG, "object is required")
    if mod_type is None or mod_type == "":
        return err(MISSING_ARG, "type is required")
    if not isinstance(settings, dict):
        return err(INVALID_ARG, "settings must be an object")
    try:
        result = engine.execute("apply_modifier", {"object": obj, "type": mod_type, "settings": settings})
    except Exception as exc:  # noqa: BLE001
        return err(BRIDGE_UNREACHABLE, "Bridge unreachable", {"error": str(exc)})
    if result.ok:
        return ok(result.data)
    error_msg = result.error if isinstance(result.error, str) else str(result.error)
    return err(INTERNAL_ERROR, "Action failed", {"error": error_msg, "data": result.data})


def get_tools() -> List[Tool]:
    """Expose action engine wrappers as MCP tools."""
    return [
        Tool(
            name="create_cube",
            description="Create a cube in Blender via the action engine.",
            input_schema={
                "type": "object",
                "properties": {
                    "size": {"type": "number"},
                    "name": {"type": "string"},
                },
                "required": ["name"],
            },
            handler=_async_wrapper(_create_cube_handler),
        ),
        Tool(
            name="move_object",
            description="Move an object by translation via the action engine.",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "translation": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"},
                            "z": {"type": "number"},
                        },
                        "required": ["x", "y", "z"],
                    },
                },
                "required": ["name", "translation"],
            },
            handler=_async_wrapper(_move_object_handler),
        ),
        Tool(
            name="assign_material",
            description="Assign a material with color to an object via the action engine.",
            input_schema={
                "type": "object",
                "properties": {
                    "object": {"type": "string"},
                    "material": {"type": "string"},
                    "color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 3,
                    },
                },
                "required": ["object", "material", "color"],
            },
            handler=_async_wrapper(_assign_material_handler),
        ),
        Tool(
            name="apply_modifier",
            description="Apply a modifier to an object via the action engine.",
            input_schema={
                "type": "object",
                "properties": {
                    "object": {"type": "string"},
                    "type": {"type": "string"},
                    "settings": {"type": "object"},
                },
                "required": ["object", "type", "settings"],
            },
            handler=_async_wrapper(_apply_modifier_handler),
        ),
    ]
