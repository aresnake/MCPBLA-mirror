from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from server.core.contracts.common_types import ContractResult


@dataclass
class AssignMaterialContract:
    object: str
    material: str
    color: List[float]

    def validate(self) -> ContractResult:
        if not self.object:
            return ContractResult(ok=False, error="Object is required")
        if not self.material:
            return ContractResult(ok=False, error="Material is required")
        if not isinstance(self.color, list) or len(self.color) < 3:
            return ContractResult(ok=False, error="Color must be an RGB array")
        return ContractResult(ok=True, data={"object": self.object, "material": self.material, "color": self.color})
