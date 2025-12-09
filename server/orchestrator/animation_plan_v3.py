from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class KeyframeAction:
    operation: str
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"operation": self.operation, "params": self.params}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "KeyframeAction":
        return KeyframeAction(operation=data.get("operation", ""), params=data.get("params", {}) or {})


@dataclass
class AnimationPlanV3:
    instruction: str
    object_name: str
    actions: List[KeyframeAction]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instruction": self.instruction,
            "object_name": self.object_name,
            "actions": [a.to_dict() for a in self.actions],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "AnimationPlanV3":
        actions = [KeyframeAction.from_dict(a) for a in data.get("actions", [])]
        return AnimationPlanV3(
            instruction=data.get("instruction", ""), object_name=data.get("object_name", ""), actions=actions
        )
