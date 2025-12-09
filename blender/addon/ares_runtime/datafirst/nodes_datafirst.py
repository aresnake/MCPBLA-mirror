from __future__ import annotations

from typing import Any, Dict

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None

from blender.addon.ares_runtime.helpers.node_utils import safe_new_node
from blender.addon.bridge.event_emitter import emit_event


def add_node(material_name: str, node_type: str) -> Dict[str, Any]:
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    mat = bpy.data.materials.get(material_name)
    if mat is None:
        mat = bpy.data.materials.new(material_name)
        mat.use_nodes = True
    node = safe_new_node(mat, node_type)
    if isinstance(node, dict):
        return node
    result = {"ok": True, "data": {"material": mat.name, "node": node.name, "type": node.bl_idname}}
    try:
        emit_event("node.added", {"material": mat.name, "node": node.name, "type": node.bl_idname})
    except Exception:
        pass
    return result
