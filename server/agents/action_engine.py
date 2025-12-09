from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from server.bridge.bridge_pool import get_bridge_pool


@dataclass
class ActionRequest:
    action: str
    params: Dict[str, Any]

    def to_payload(self) -> Dict[str, Any]:
        return {"action": self.action, "params": self.params}


@dataclass
class ActionResult:
    ok: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ActionEngine:
    """ActionEngine dispatches structured actions to Blender via the bridge pool."""

    def __init__(self) -> None:
        self.bridge_pool = get_bridge_pool()

    def execute(self, action: str, params: Dict[str, Any]) -> ActionResult:
        request = ActionRequest(action=action, params=params or {})
        try:
            response = self.bridge_pool.route("action.execute", request.to_payload())
            if not isinstance(response, dict):
                return ActionResult(ok=False, error="Invalid response from bridge")
            ok = bool(response.get("ok", False))
            data = response.get("data")
            error = response.get("error")
            return ActionResult(ok=ok, data=data if isinstance(data, dict) else None, error=error)
        except Exception as exc:  # noqa: BLE001
            return ActionResult(ok=False, error=str(exc))
