from __future__ import annotations

from typing import Any, Dict, List

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None


def assign_material(obj_name: str, material_name: str, color: List[float]) -> Dict[str, Any]:
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        return {"ok": False, "error": f"Object '{obj_name}' not found"}
    mat = bpy.data.materials.get(material_name)
    if mat is None:
        mat = bpy.data.materials.new(material_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        r = float(color[0]) if len(color) > 0 else 1.0
        g = float(color[1]) if len(color) > 1 else 1.0
        b = float(color[2]) if len(color) > 2 else 1.0
        principled.inputs["Base Color"].default_value = (r, g, b, 1.0)
    if len(obj.data.materials) == 0:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat
    return {"ok": True, "data": {"object": obj.name, "material": mat.name, "color": color}}
