from __future__ import annotations

from typing import List

from mcpbla.server.orchestrator.plan import PlanStep


def plan_fx(instruction: str) -> List[PlanStep]:
    steps: List[PlanStep] = []
    lower = instruction.lower()
    if any(keyword in lower for keyword in ("fx", "effect", "glow")):
        steps.append(
            PlanStep(
                tool_name="apply_fx_stub",
                arguments={"object_name": "Cube", "fx": "glow_stub"},
                description="Apply FX",
            )
        )
    return steps

