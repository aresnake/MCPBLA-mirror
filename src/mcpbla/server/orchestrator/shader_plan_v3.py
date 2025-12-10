from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ShaderNodeAction:
    node_type: str
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"node_type": self.node_type, "params": self.params}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ShaderNodeAction":
        return ShaderNodeAction(node_type=data.get("node_type", ""), params=data.get("params", {}) or {})


@dataclass
class ShaderPlanV3:
    instruction: str
    material: str
    nodes: List[ShaderNodeAction]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instruction": self.instruction,
            "material": self.material,
            "nodes": [n.to_dict() for n in self.nodes],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ShaderPlanV3":
        nodes = [ShaderNodeAction.from_dict(n) for n in data.get("nodes", [])]
        return ShaderPlanV3(instruction=data.get("instruction", ""), material=data.get("material", ""), nodes=nodes)
