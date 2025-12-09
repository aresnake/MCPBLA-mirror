from __future__ import annotations

from typing import Any, Dict

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None

from blender.addon.ares_runtime.helpers.object_utils import apply_modifier


def apply_modifier(obj_name: str, mod_type: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        return {"ok": False, "error": f"Object '{obj_name}' not found"}
    return apply_modifier(obj, mod_type, settings)
