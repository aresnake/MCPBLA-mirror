from __future__ import annotations

from typing import Any, Dict

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None

from blender.addon.ares_runtime.helpers.object_utils import ensure_mesh_object, set_object_location
from blender.addon.ares_runtime.helpers.undo_utils import push_undo_step


def create_cube(name: str, size: float) -> Dict[str, Any]:
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    push_undo_step("create_cube")
    half = size / 2.0
    verts = [
        (-half, -half, -half),
        (-half, -half, half),
        (-half, half, -half),
        (-half, half, half),
        (half, -half, -half),
        (half, -half, half),
        (half, half, -half),
        (half, half, half),
    ]
    faces = [
        (0, 1, 3, 2),
        (4, 6, 7, 5),
        (0, 4, 5, 1),
        (2, 3, 7, 6),
        (1, 5, 7, 3),
        (0, 2, 6, 4),
    ]
    obj = ensure_mesh_object(name, verts, faces)
    if isinstance(obj, dict) and not obj.get("ok", True):
        return obj
    return {"ok": True, "data": {"name": obj.name, "size": size}}


def move_object(name: str, translation: Dict[str, float]) -> Dict[str, Any]:
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    obj = bpy.data.objects.get(name)
    if obj is None:
        return {"ok": False, "error": f"Object '{name}' not found"}
    push_undo_step("move_object")
    obj.location.x += float(translation.get("x", 0))
    obj.location.y += float(translation.get("y", 0))
    obj.location.z += float(translation.get("z", 0))
    return {"ok": True, "data": {"name": obj.name, "location": list(obj.location)}}
