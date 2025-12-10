from __future__ import annotations

from typing import Any, Dict

from . import actions


def handle_route(route: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if route == "action.execute":
        return actions.execute_action(payload)
    return {"ok": False, "error": f"Unknown route '{route}'"}
