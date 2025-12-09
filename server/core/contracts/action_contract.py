from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from server.core.contracts.common_types import ContractResult, Vector3


@dataclass
class ActionRequestContract:
    action: str
    params: Dict[str, Any]

    def validate(self) -> ContractResult:
        if not self.action:
            return ContractResult(ok=False, error="Action is required")
        if not isinstance(self.params, dict):
            return ContractResult(ok=False, error="Params must be an object")
        return ContractResult(ok=True, data={"action": self.action, "params": self.params})


def validate_translation(translation: Dict[str, Any]) -> ContractResult:
    for key in ("x", "y", "z"):
        if key not in translation:
            return ContractResult(ok=False, error=f"Missing translation component '{key}'")
        try:
            float(translation[key])
        except Exception:  # noqa: BLE001
            return ContractResult(ok=False, error=f"Invalid translation component '{key}'")
    return ContractResult(ok=True, data=translation)
