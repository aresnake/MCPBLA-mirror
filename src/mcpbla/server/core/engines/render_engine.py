from __future__ import annotations

from mcpbla.server.bridge.messages import ActionMessage
from mcpbla.server.bridge.pool_v2 import get_bridge_pool_v2
from mcpbla.server.core.contracts.common_types import ContractResult


class RenderEngine:
    def __init__(self) -> None:
        self.pool = get_bridge_pool_v2()

    def render_preview(self, settings: dict) -> ContractResult:
        msg = ActionMessage(route="render.preview.v2", payload=settings)
        try:
            resp = self.pool.send_action(msg)
            if isinstance(resp, dict) and resp.get("ok"):
                return ContractResult(ok=True, data=resp.get("data"))
            return ContractResult(ok=False, error=(resp.get("error") if isinstance(resp, dict) else "Unknown error"))
        except Exception as exc:  # noqa: BLE001
            return ContractResult(ok=False, error=str(exc))

