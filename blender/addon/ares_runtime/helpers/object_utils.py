from __future__ import annotations

from typing import Any, Dict, Iterable, List

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None


def ensure_mesh_object(name: str, verts: Iterable, faces: Iterable) -> Any:
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def set_object_location(obj, loc3) -> Dict[str, Any]:
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    if obj is None:
        return {"ok": False, "error": "Object is None"}
    if isinstance(loc3, dict):
        obj.location.x = float(loc3.get("x", obj.location.x))
        obj.location.y = float(loc3.get("y", obj.location.y))
        obj.location.z = float(loc3.get("z", obj.location.z))
    elif isinstance(loc3, (list, tuple)) and len(loc3) >= 3:
        obj.location.x = float(loc3[0])
        obj.location.y = float(loc3[1])
        obj.location.z = float(loc3[2])
    return {"ok": True, "data": {"location": list(obj.location)}}


def apply_modifier(obj, mod_type: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    if obj is None:
        return {"ok": False, "error": "Object is None"}
    mod = obj.modifiers.new(name=f"{mod_type}_auto", type=str(mod_type).upper())
    for key, value in settings.items():
        if hasattr(mod, key):
            try:
                setattr(mod, key, value)
            except Exception:
                continue
    return {"ok": True, "data": {"modifier": mod.name, "type": mod.type}}
