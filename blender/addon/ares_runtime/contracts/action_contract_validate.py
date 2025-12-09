from __future__ import annotations

from typing import Any, Dict


def validate_action(payload: Dict[str, Any]) -> Dict[str, Any]:
    if "action" not in payload:
        return {"ok": False, "error": "Missing action"}
    if "params" not in payload or not isinstance(payload["params"], dict):
        return {"ok": False, "error": "Missing params"}
    return {"ok": True}
