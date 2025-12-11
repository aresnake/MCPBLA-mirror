"""Animation agent v3 MCP tool wrappers for planning and execution."""

from __future__ import annotations

from typing import Any, Dict, List

from mcpbla.server.agents.animation_agent_v3 import AnimationAgentV3
from mcpbla.server.orchestrator.animation_orchestrator_v3 import AnimationOrchestratorV3
from mcpbla.server.orchestrator.animation_plan_v3 import AnimationPlanV3
from mcpbla.server.tools.base import Tool


def _async_wrapper(func):
    """Wrap sync animation operations for async compatibility."""
    async def wrapped(arguments: Dict[str, Any]) -> Any:
        return func(arguments)

    return wrapped


def _plan_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Create an animation plan from instruction/object inputs."""
    instruction = arguments.get("instruction", "")
    obj = arguments.get("object", "AnimObj")
    orch = AnimationOrchestratorV3()
    plan = orch.plan(instruction, obj)
    return plan.to_dict()


def _execute_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an animation plan and verify it."""
    plan_dict = arguments.get("plan", {})
    plan = AnimationPlanV3.from_dict(plan_dict)
    orch = AnimationOrchestratorV3()
    ok, results = orch.execute(plan)
    verify = orch.verify(plan)
    return {"ok": ok, "results": results, "verify": verify}


def _agent_run_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Run the autonomous animation agent end-to-end."""
    instruction = arguments.get("instruction", "")
    obj = arguments.get("object", "AnimObj")
    agent = AnimationAgentV3()
    return agent.run(instruction, obj)


def get_tools() -> List[Tool]:
    """Expose animation planning/execution and agent run as MCP tools."""
    return [
        Tool(
            name="animation_plan_v3",
            description="Plan animation operations v3.",
            input_schema={
                "type": "object",
                "properties": {"instruction": {"type": "string"}, "object": {"type": "string"}},
                "required": ["instruction", "object"],
            },
            handler=_async_wrapper(_plan_handler),
        ),
        Tool(
            name="animation_execute_v3",
            description="Execute an animation plan v3.",
            input_schema={
                "type": "object",
                "properties": {"plan": {"type": "object"}},
                "required": ["plan"],
            },
            handler=_async_wrapper(_execute_handler),
        ),
        Tool(
            name="animation_agent_v3_run",
            description="Run autonomous animation agent v3.",
            input_schema={
                "type": "object",
                "properties": {"instruction": {"type": "string"}, "object": {"type": "string"}},
                "required": ["instruction", "object"],
            },
            handler=_async_wrapper(_agent_run_handler),
        ),
    ]
