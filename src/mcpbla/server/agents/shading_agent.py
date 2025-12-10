from __future__ import annotations

from typing import List

from mcpbla.server.orchestrator.plan import PlanStep


def plan_shading(instruction: str) -> List[PlanStep]:
    steps: List[PlanStep] = []
    lower = instruction.lower()
    if any(keyword in lower for keyword in ("material", "shade", "color")):
        steps.append(
            PlanStep(
                tool_name="assign_material_stub",
                arguments={"object_name": "Cube", "material": "mat_stub"},
                description="Assign material",
            )
        )
    return steps

