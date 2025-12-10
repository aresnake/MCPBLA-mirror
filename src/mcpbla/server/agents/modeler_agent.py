from __future__ import annotations

from typing import List

from mcpbla.server.orchestrator.plan import PlanStep


def plan_modeling(instruction: str) -> List[PlanStep]:
    """Very simple modeling planner based on keywords."""
    lower = instruction.lower()
    steps: List[PlanStep] = []
    if "cube" in lower and not any(s.tool_name == "create_cube_stub" for s in steps):
        steps.append(PlanStep(tool_name="create_cube_stub", arguments={}, description="Create cube"))
    if "sphere" in lower:
        steps.append(PlanStep(tool_name="create_sphere_stub", arguments={}, description="Create sphere"))
    if "move" in lower and not any(s.tool_name == "move_object_stub" for s in steps):
        steps.append(
            PlanStep(
                tool_name="move_object_stub",
                arguments={"object_name": "Cube", "delta": [0, 0, 2]},
                description="Move object",
            )
        )
    return steps

