from __future__ import annotations

from mcpbla.server.bridge.messages import ActionMessage
from mcpbla.server.bridge.pool_v2 import get_bridge_pool_v2
from mcpbla.server.core.contracts.common_types import ContractResult
from mcpbla.server.core.contracts.geometry_contract import CreateCubeContract


class GeometryEngine:
    def __init__(self) -> None:
        self.pool = get_bridge_pool_v2()

    def create_cube(self, name: str, size: float) -> ContractResult:
        contract = CreateCubeContract(name=name, size=size).validate()
        if not contract.ok:
            return contract
        msg = ActionMessage(route="create_cube.v2", payload=contract.data)
        try:
            resp = self.pool.send_action(msg)
            if isinstance(resp, dict) and resp.get("ok"):
                return ContractResult(ok=True, data=resp.get("data"))
            return ContractResult(ok=False, error=(resp.get("error") if isinstance(resp, dict) else "Unknown error"))
        except Exception as exc:  # noqa: BLE001
            return ContractResult(ok=False, error=str(exc))

