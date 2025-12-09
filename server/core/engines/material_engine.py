from __future__ import annotations

from typing import Any, Dict, List

from server.bridge.messages import ActionMessage
from server.bridge.pool_v2 import get_bridge_pool_v2
from server.core.contracts.common_types import ContractResult
from server.core.contracts.material_contract import AssignMaterialContract


class MaterialEngine:
    def __init__(self) -> None:
        self.pool = get_bridge_pool_v2()

    def assign(self, object_name: str, material: str, color: List[float]) -> ContractResult:
        contract = AssignMaterialContract(object=object_name, material=material, color=color).validate()
        if not contract.ok:
            return contract
        msg = ActionMessage(route="assign_material.v2", payload=contract.data)
        try:
            resp = self.pool.send_action(msg)
            if isinstance(resp, dict) and resp.get("ok"):
                return ContractResult(ok=True, data=resp.get("data"))
            return ContractResult(ok=False, error=(resp.get("error") if isinstance(resp, dict) else "Unknown error"))
        except Exception as exc:  # noqa: BLE001
            return ContractResult(ok=False, error=str(exc))
