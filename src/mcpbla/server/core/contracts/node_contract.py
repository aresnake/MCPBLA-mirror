from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from mcpbla.server.core.contracts.common_types import ContractResult


@dataclass
class NodeOperationContract:
    operation: str
    params: Dict[str, Any]

    def validate(self) -> ContractResult:
        if not self.operation:
            return ContractResult(ok=False, error="Node operation required")
        if not isinstance(self.params, dict):
            return ContractResult(ok=False, error="Params must be object")
        return ContractResult(ok=True, data={"operation": self.operation, "params": self.params})

