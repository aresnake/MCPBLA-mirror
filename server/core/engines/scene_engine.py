from __future__ import annotations

from typing import Any, Dict

from server.bridge.messages import ActionMessage
from server.bridge.pool_v2 import get_bridge_pool_v2
from server.core.contracts.common_types import ContractResult


class SceneEngine:
    def __init__(self) -> None:
        self.pool = get_bridge_pool_v2()

    def snapshot(self, session_id: str | None = None) -> ContractResult:
        msg = ActionMessage(route="scene.snapshot.v2", payload={"session_id": session_id})
        try:
            resp = self.pool.send_action(msg)
            if isinstance(resp, dict) and resp.get("ok"):
                return ContractResult(ok=True, data=resp.get("data"))
            return ContractResult(ok=False, error=(resp.get("error") if isinstance(resp, dict) else "Unknown error"))
        except Exception as exc:  # noqa: BLE001
            return ContractResult(ok=False, error=str(exc))
