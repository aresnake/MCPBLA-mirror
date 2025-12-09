from __future__ import annotations

from typing import Any, Dict, List

from server.orchestrator.orchestrator_v3 import OrchestratorV3
from server.orchestrator.plan_v3 import TaskPlan
from server.tools.base import Tool


def _async_wrapper(func):
    async def wrapped(arguments: Dict[str, Any]) -> Any:
        return func(arguments)

    return wrapped


def _plan_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    instruction = arguments.get("instruction", "")
    orchestrator = OrchestratorV3()
    plan = orchestrator.plan(instruction)
    return plan.to_dict()


def _execute_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    plan_dict = arguments.get("plan", {})
    plan = TaskPlan.from_dict(plan_dict)
    orchestrator = OrchestratorV3()
    ok, results = orchestrator.execute(plan)
    verify = orchestrator.verify(plan, results)
    return {"ok": ok, "results": results, "verify": verify}


def _refine_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    plan_dict = arguments.get("plan", {})
    diff = arguments.get("diff", {})
    plan = TaskPlan.from_dict(plan_dict)
    orchestrator = OrchestratorV3()
    new_plan = orchestrator.replan(plan, diff)
    return new_plan.to_dict()


def get_tools() -> List[Tool]:
    return [
        Tool(
            name="plan_v3",
            description="Plan an instruction into a TaskPlan v3.",
            input_schema={
                "type": "object",
                "properties": {"instruction": {"type": "string"}},
                "required": ["instruction"],
            },
            handler=_async_wrapper(_plan_handler),
        ),
        Tool(
            name="execute_plan_v3",
            description="Execute a TaskPlan v3.",
            input_schema={
                "type": "object",
                "properties": {"plan": {"type": "object"}},
                "required": ["plan"],
            },
            handler=_async_wrapper(_execute_handler),
        ),
        Tool(
            name="refine_plan_v3",
            description="Refine/replan a TaskPlan v3 based on a diff.",
            input_schema={
                "type": "object",
                "properties": {"plan": {"type": "object"}, "diff": {"type": "object"}},
                "required": ["plan", "diff"],
            },
            handler=_async_wrapper(_refine_handler),
        ),
    ]
