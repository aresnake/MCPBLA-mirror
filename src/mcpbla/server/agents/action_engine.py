from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import os

from mcpbla.server.bridge.pool_v2 import get_bridge_pool_v2
from mcpbla.server.core.engines.action_engine_v2 import ActionEngineV2


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
        self.engine = ActionEngineV2()
        self.pool = get_bridge_pool_v2()

    def execute(self, action: str, params: Dict[str, Any]) -> ActionResult:
        request = ActionRequest(action=action, params=params or {})
        # Prefer bridge pool routing when a handler is configured (BLENDER_BRIDGE_URL or manual setup).
        if self.pool.has_handler():
            resp = self.pool.route("action.execute", request.to_payload())
            if not isinstance(resp, dict):
                return ActionResult(ok=False, error="Invalid response from bridge")
            ok = bool(resp.get("ok", False))
            data = resp.get("data")
            err = resp.get("error")
            return ActionResult(ok=ok, data=data if isinstance(data, dict) else None, error=err)

        # Fallback: local v2 engine validation/runtime (stub mode).
        result = self.engine.execute(request.action, request.params)
        return ActionResult(ok=result.ok, data=result.data if isinstance(result.data, dict) else None, error=result.error)
