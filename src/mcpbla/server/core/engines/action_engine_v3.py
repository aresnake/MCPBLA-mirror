from __future__ import annotations

from typing import Any, Dict, List

from mcpbla.server.bridge.events import EVENT_BUS
from mcpbla.server.bridge.messages import ActionBatch, ActionMessage
from mcpbla.server.bridge.pool_v2 import get_bridge_pool_v2
from mcpbla.server.core.contracts.action_contract import ActionRequestContract
from mcpbla.server.core.contracts.common_types import ContractResult


class ActionEngineV3:
    """Action engine v3 with ack listening via EVENT_BUS."""

    def __init__(self, wait_for_ack: bool = False) -> None:
        self.pool = get_bridge_pool_v2()
        self.wait_for_ack = wait_for_ack
        self._last_ack: Dict[str, Any] = {}
        EVENT_BUS.subscribe("ack", self._on_ack)

    def _on_ack(self, event_name: str, data: Dict[str, Any]) -> None:
        corr = data.get("correlation_id")
        if corr:
            self._last_ack[corr] = data

    def execute(self, action: str, params: Dict[str, Any]) -> ContractResult:
        contract = ActionRequestContract(action=action, params=params).validate()
        if not contract.ok:
            return contract
        msg = ActionMessage(route=f"{action}.v2", payload=contract.data)
        try:
            resp = self.pool.send_action(msg)
            if self.wait_for_ack:
                ack = self._last_ack.get(msg.correlation_id)
                if not ack:
                    return ContractResult(ok=False, error="no ack")
                status = ack.get("status", "error")
                return ContractResult(ok=status == "success", data=ack.get("data"), error=ack.get("error"))
            if isinstance(resp, dict) and resp.get("ok"):
                return ContractResult(ok=True, data=resp.get("data"))
            return ContractResult(ok=False, error=(resp.get("error") if isinstance(resp, dict) else "Unknown error"))
        except Exception as exc:  # noqa: BLE001
            return ContractResult(ok=False, error=str(exc))

    def batch(self, actions: List[Dict[str, Any]], atomic: bool = False) -> ContractResult:
        messages: List[ActionMessage] = []
        for a in actions:
            action = a.get("action")
            params = a.get("params", {})
            contract = ActionRequestContract(action=action, params=params).validate()
            if not contract.ok:
                return contract
            messages.append(ActionMessage(route=f"{action}.v2", payload=contract.data))
        batch = ActionBatch(actions=messages, atomic=atomic)
        try:
            resp = self.pool.send_batch(batch)
            if isinstance(resp, dict) and resp.get("ok", False):
                return ContractResult(ok=True, data=resp.get("data"))
            return ContractResult(ok=False, error=(resp.get("error") if isinstance(resp, dict) else "Unknown error"))
        except Exception as exc:  # noqa: BLE001
            return ContractResult(ok=False, error=str(exc))

