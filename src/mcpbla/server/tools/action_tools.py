"""Action engine-backed MCP tools for direct modeling operations."""

from __future__ import annotations

from typing import Any, Dict, List

from mcpbla.server.agents.action_engine import ActionEngine
from mcpbla.server.tools.base import Tool


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
        return {"ok": False, "error": "name is required"}
    size = float(arguments.get("size", 1.0))
    result = engine.execute("create_cube", {"name": name, "size": size})
    return {"ok": result.ok, "data": result.data, "error": result.error}


def _move_object_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Move an object using the action engine translation op."""
    engine = _create_engine()
    name = arguments.get("name")
    if not name:
        return {"ok": False, "error": "name is required"}
    translation = arguments.get("translation")
    if not isinstance(translation, dict):
        return {"ok": False, "error": "translation must be an object"}
    for axis in ("x", "y", "z"):
        if axis not in translation:
            return {"ok": False, "error": f"translation.{axis} is required"}
    result = engine.execute("move_object", {"name": name, "translation": translation})
    return {"ok": result.ok, "data": result.data, "error": result.error}


def _assign_material_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Assign a material with color to a given object."""
    engine = _create_engine()
    obj = arguments.get("object")
    material = arguments.get("material")
    color = arguments.get("color")
    if not obj:
        return {"ok": False, "error": "object is required"}
    if material is None or material == "":
        return {"ok": False, "error": "material is required"}
    if not isinstance(color, list) or len(color) != 3:
        return {"ok": False, "error": "color must be a length-3 array"}
    result = engine.execute("assign_material", {"object": obj, "material": material, "color": color})
    return {"ok": result.ok, "data": result.data, "error": result.error}


def _apply_modifier_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Apply a modifier with provided settings to an object."""
    engine = _create_engine()
    obj = arguments.get("object")
    mod_type = arguments.get("type")
    settings = arguments.get("settings")
    if not obj:
        return {"ok": False, "error": "object is required"}
    if mod_type is None or mod_type == "":
        return {"ok": False, "error": "type is required"}
    if not isinstance(settings, dict):
        return {"ok": False, "error": "settings must be an object"}
    result = engine.execute("apply_modifier", {"object": obj, "type": mod_type, "settings": settings})
    return {"ok": result.ok, "data": result.data, "error": result.error}


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
