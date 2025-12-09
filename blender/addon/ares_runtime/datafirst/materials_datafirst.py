from __future__ import annotations

from typing import Any, Dict, List

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None

from blender.addon.ares_runtime.helpers import material_utils


def assign_material(obj_name: str, material_name: str, color: List[float]) -> Dict[str, Any]:
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        return {"ok": False, "error": f"Object '{obj_name}' not found"}
    mat = material_utils.ensure_material(material_name)
    if isinstance(mat, dict):  # error response
        return mat
    principled = material_utils.ensure_principled(mat)
    material_utils.set_base_color(principled, color)
    material_utils.ensure_material_output(mat)
    material_utils.link_principled_to_output(mat, principled)
    material_utils.assign_material_to_object(obj, mat)
    return {"ok": True, "data": {"object": obj.name, "material": mat.name, "color": color}}
