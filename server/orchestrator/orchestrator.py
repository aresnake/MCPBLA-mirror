from __future__ import annotations

import uuid
from typing import Awaitable, Callable, List

from server.agents import fx_agent, modeler_agent, shading_agent
from server.orchestrator.plan import ExecutionResult, Plan, PlanStep, StepResult


ToolInvoker = Callable[[str, dict], Awaitable[dict]]


def plan_task(instruction: str) -> Plan:
    task_id = str(uuid.uuid4())
    steps: List[PlanStep] = []
    lower = instruction.lower()

    # Basic modeling keywords
    if "cube" in lower:
        steps.append(PlanStep(tool_name="create_cube_stub", arguments={}, description="Create a cube"))
    if "sphere" in lower:
        steps.append(PlanStep(tool_name="create_sphere_stub", arguments={}, description="Create a sphere"))
    if "move" in lower:
        steps.append(
            PlanStep(
                tool_name="move_object_stub",
                arguments={"object_name": "Cube", "delta": [0, 0, 2]},
                description="Move Cube up",
            )
        )
    if any(word in lower for word in ("color", "material", "shade")):
        steps.extend(shading_agent.plan_shading(instruction))
    if any(word in lower for word in ("fx", "effect", "glow")):
        steps.extend(fx_agent.plan_fx(instruction))
    # Always defer to modeler agent for remaining modeling cues
    steps.extend(modeler_agent.plan_modeling(instruction))

    # Deduplicate by tool_name to keep the plan concise
    deduped: List[PlanStep] = []
    seen = set()
    for step in steps:
        if step.tool_name in seen:
            continue
        seen.add(step.tool_name)
        deduped.append(step)

    return Plan(task_id=task_id, steps=deduped)


async def execute_plan(plan: Plan, *, invoker: ToolInvoker) -> ExecutionResult:
    results: List[StepResult] = []
    success = True
    for step in plan.steps:
        try:
            output = await invoker(step.tool_name, step.arguments)
            results.append(StepResult(step=step, success=True, output=output))
        except Exception as exc:  # noqa: BLE001
            results.append(StepResult(step=step, success=False, output=None, error=str(exc)))
            if not step.optional:
                success = False
                break
    else:
        success = success and all(r.success for r in results)

    return ExecutionResult(task_id=plan.task_id, success=success, steps=results)


async def run_task(instruction: str, *, invoker: ToolInvoker) -> ExecutionResult:
    plan = plan_task(instruction)
    return await execute_plan(plan, invoker=invoker)
