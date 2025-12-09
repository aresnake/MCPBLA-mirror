from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class TaskAction:
    name: str
    params: Dict[str, Any] = field(default_factory=dict)
    expected: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "params": self.params, "expected": self.expected}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TaskAction":
        return TaskAction(
            name=data.get("name", ""),
            params=data.get("params", {}) or {},
            expected=data.get("expected", {}) or {},
        )


@dataclass
class TaskPlan:
    instruction: str
    actions: List[TaskAction]

    def to_dict(self) -> Dict[str, Any]:
        return {"instruction": self.instruction, "actions": [a.to_dict() for a in self.actions]}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TaskPlan":
        actions = [TaskAction.from_dict(item) for item in data.get("actions", [])]
        return TaskPlan(instruction=data.get("instruction", ""), actions=actions)
