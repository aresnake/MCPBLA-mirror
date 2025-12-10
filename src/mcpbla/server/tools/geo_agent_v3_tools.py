from __future__ import annotations

from typing import Any, Dict, List

from mcpbla.server.agents.geo_agent_v3 import GeoAgentV3
from mcpbla.server.orchestrator.geometry_orchestrator_v3 import GeometryOrchestratorV3
from mcpbla.server.orchestrator.geometry_plan_v3 import GeometryPlanV3
from mcpbla.server.tools.base import Tool


def _async_wrapper(func):
    async def wrapped(arguments: Dict[str, Any]) -> Any:
        return func(arguments)

    return wrapped


def _plan_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    instruction = arguments.get("instruction", "")
    obj = arguments.get("object", "GeoObj")
    orch = GeometryOrchestratorV3()
    plan = orch.plan(instruction, obj)
    return plan.to_dict()


def _execute_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    plan_dict = arguments.get("plan", {})
    plan = GeometryPlanV3.from_dict(plan_dict)
    orch = GeometryOrchestratorV3()
    ok, results = orch.execute(plan)
    verify = orch.verify(plan)
    return {"ok": ok, "results": results, "verify": verify}


def _agent_run_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    instruction = arguments.get("instruction", "")
    obj = arguments.get("object", "GeoObj")
    agent = GeoAgentV3()
    return agent.run(instruction, obj)


def get_tools() -> List[Tool]:
    return [
        Tool(
            name="geo_plan_v3",
            description="Plan a geometry nodes setup from instruction.",
            input_schema={
                "type": "object",
                "properties": {"instruction": {"type": "string"}, "object": {"type": "string"}},
                "required": ["instruction", "object"],
            },
            handler=_async_wrapper(_plan_handler),
        ),
        Tool(
            name="geo_execute_v3",
            description="Execute a geometry plan v3.",
            input_schema={
                "type": "object",
                "properties": {"plan": {"type": "object"}},
                "required": ["plan"],
            },
            handler=_async_wrapper(_execute_handler),
        ),
        Tool(
            name="geo_agent_v3_run",
            description="Run autonomous geometry agent v3.",
            input_schema={
                "type": "object",
                "properties": {"instruction": {"type": "string"}, "object": {"type": "string"}},
                "required": ["instruction", "object"],
            },
            handler=_async_wrapper(_agent_run_handler),
        ),
    ]

