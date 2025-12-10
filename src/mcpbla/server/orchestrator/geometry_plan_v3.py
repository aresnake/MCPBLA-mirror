from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class GeoNodeAction:
    node_type: str
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"node_type": self.node_type, "params": self.params}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "GeoNodeAction":
        return GeoNodeAction(node_type=data.get("node_type", ""), params=data.get("params", {}) or {})


@dataclass
class GeometryPlanV3:
    instruction: str
    object_name: str
    nodes: List[GeoNodeAction]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instruction": self.instruction,
            "object_name": self.object_name,
            "nodes": [n.to_dict() for n in self.nodes],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "GeometryPlanV3":
        nodes = [GeoNodeAction.from_dict(n) for n in data.get("nodes", [])]
        return GeometryPlanV3(
            instruction=data.get("instruction", ""), object_name=data.get("object_name", ""), nodes=nodes
        )
