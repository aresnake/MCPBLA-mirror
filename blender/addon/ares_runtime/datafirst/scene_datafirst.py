from __future__ import annotations

from typing import Any, Dict

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None


def snapshot(session_id: str | None = None) -> Dict[str, Any]:
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}

    scene = bpy.context.scene if bpy.context else None
    if scene is None:
        return {"ok": False, "error": "No active scene"}

    objects = []
    for obj in scene.objects:
        objects.append(
            {
                "name": obj.name,
                "type": obj.type,
                "location": [float(v) for v in obj.location[:]],
                "rotation_euler": [float(v) for v in obj.rotation_euler[:]],
                "scale": [float(v) for v in obj.scale[:]],
            }
        )

    metadata = {
        "scene": scene.name,
        "frame_current": scene.frame_current,
    }

    data = {
        "session_id": session_id or "default",
        "objects": objects,
        "metadata": metadata,
    }
    return {"ok": True, "data": data}
