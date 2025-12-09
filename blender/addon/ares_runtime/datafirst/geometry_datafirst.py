from __future__ import annotations

from typing import Any, Dict

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None


def apply_modifier(obj_name: str, mod_type: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        return {"ok": False, "error": f"Object '{obj_name}' not found"}
    mod = obj.modifiers.new(name=f"{mod_type}_auto", type=str(mod_type).upper())
    for key, value in settings.items():
        if hasattr(mod, key):
            try:
                setattr(mod, key, value)
            except Exception:
                continue
    return {"ok": True, "data": {"object": obj.name, "modifier": mod.name, "type": mod.type}}
