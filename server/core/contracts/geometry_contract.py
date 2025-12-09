from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from server.core.contracts.common_types import ContractResult


@dataclass
class CreateCubeContract:
    name: str
    size: float

    def validate(self) -> ContractResult:
        if not self.name:
            return ContractResult(ok=False, error="Name is required")
        try:
            float(self.size)
        except Exception:  # noqa: BLE001
            return ContractResult(ok=False, error="Size must be numeric")
        return ContractResult(ok=True, data={"name": self.name, "size": float(self.size)})
