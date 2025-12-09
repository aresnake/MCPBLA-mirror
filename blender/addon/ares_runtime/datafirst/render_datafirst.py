from __future__ import annotations

from typing import Any, Dict

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None


def render_preview(settings: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}

    settings = settings or {}
    scene = bpy.context.scene if bpy.context else None
    if scene is None:
        return {"ok": False, "error": "No active scene"}

    res_x = int(settings.get("resolution_x", scene.render.resolution_x))
    res_y = int(settings.get("resolution_y", scene.render.resolution_y))
    engine = settings.get("engine", scene.render.engine)

    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.engine = engine

    return {
        "ok": True,
        "data": {
            "scene": scene.name,
            "resolution_x": res_x,
            "resolution_y": res_y,
            "engine": engine,
        },
    }
