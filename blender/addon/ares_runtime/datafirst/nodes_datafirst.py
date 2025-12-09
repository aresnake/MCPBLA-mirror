from __future__ import annotations

from typing import Any, Dict

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None


def add_node(material_name: str, node_type: str) -> Dict[str, Any]:
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    mat = bpy.data.materials.get(material_name)
    if mat is None:
        mat = bpy.data.materials.new(material_name)
        mat.use_nodes = True
    nodes = mat.node_tree.nodes
    node = nodes.new(node_type)
    return {"ok": True, "data": {"material": mat.name, "node": node.name, "type": node.bl_idname}}
