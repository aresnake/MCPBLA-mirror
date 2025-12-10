from __future__ import annotations

from typing import Any, Dict, List


def validate_assign_material(payload: Dict[str, Any]) -> Dict[str, Any]:
    obj = payload.get("object")
    mat = payload.get("material")
    color = payload.get("color", [])
    if not obj or not mat:
        return {"ok": False, "error": "Object and material are required"}
    if not isinstance(color, list) or len(color) < 3:
        return {"ok": False, "error": "Color must be an RGB array"}
    return {"ok": True}
