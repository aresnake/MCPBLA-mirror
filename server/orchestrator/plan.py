from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class PlanStep:
    tool_name: str
    arguments: Dict[str, Any]
    description: str = ""
    optional: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Plan:
    task_id: str
    steps: List[PlanStep]

    def to_dict(self) -> Dict[str, Any]:
        return {"task_id": self.task_id, "steps": [s.to_dict() for s in self.steps]}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Plan":
        steps = [PlanStep(**step) for step in data.get("steps", [])]
        return Plan(task_id=data.get("task_id", ""), steps=steps)


@dataclass
class StepResult:
    step: PlanStep
    success: bool
    output: Optional[Dict[str, Any]]
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step.to_dict(),
            "success": self.success,
            "output": self.output,
            "error": self.error,
        }


@dataclass
class ExecutionResult:
    task_id: str
    success: bool
    steps: List[StepResult]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "success": self.success,
            "steps": [s.to_dict() for s in self.steps],
        }
