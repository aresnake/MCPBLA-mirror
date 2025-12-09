from __future__ import annotations

from typing import Any, Dict

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None

from blender.addon.ares_runtime.helpers.object_utils import apply_modifier
from blender.addon.ares_runtime.helpers.undo_utils import push_undo_step
from blender.addon.bridge.event_emitter import emit_event


def apply_modifier(obj_name: str, mod_type: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        return {"ok": False, "error": f"Object '{obj_name}' not found"}
    push_undo_step("apply_modifier")
    result = apply_modifier(obj, mod_type, settings)
    try:
        if isinstance(result, dict) and result.get("ok"):
            emit_event("modifier.added", {"object": obj.name, "modifier": mod_type})
    except Exception:
        pass
    return result
