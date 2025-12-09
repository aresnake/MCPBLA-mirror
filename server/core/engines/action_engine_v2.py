from __future__ import annotations

from typing import Any, Dict, List

from server.bridge.messages import ActionBatch, ActionMessage
from server.bridge.pool_v2 import get_bridge_pool_v2
from server.core.contracts.action_contract import ActionRequestContract, validate_translation
from server.core.contracts.common_types import ContractResult


class ActionEngineV2:
    """Action engine v2 with batching and contract validation."""

    def __init__(self) -> None:
        self.pool = get_bridge_pool_v2()

    def execute(self, action: str, params: Dict[str, Any]) -> ContractResult:
        contract = ActionRequestContract(action=action, params=params).validate()
        if not contract.ok:
            return contract
        msg = ActionMessage(route=f"{action}.v2", payload=contract.data)
        try:
            resp = self.pool.send_action(msg)
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
