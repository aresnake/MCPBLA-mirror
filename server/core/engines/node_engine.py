from __future__ import annotations

from server.bridge.messages import ActionMessage
from server.bridge.pool_v2 import get_bridge_pool_v2
from server.core.contracts.common_types import ContractResult
from server.core.contracts.node_contract import NodeOperationContract


class NodeEngine:
    def __init__(self) -> None:
        self.pool = get_bridge_pool_v2()

    def operate(self, operation: str, params: dict) -> ContractResult:
        contract = NodeOperationContract(operation=operation, params=params).validate()
        if not contract.ok:
            return contract
        msg = ActionMessage(route="node.operation.v2", payload=contract.data)
        try:
            resp = self.pool.send_action(msg)
            if isinstance(resp, dict) and resp.get("ok"):
                return ContractResult(ok=True, data=resp.get("data"))
            return ContractResult(ok=False, error=(resp.get("error") if isinstance(resp, dict) else "Unknown error"))
        except Exception as exc:  # noqa: BLE001
            return ContractResult(ok=False, error=str(exc))
