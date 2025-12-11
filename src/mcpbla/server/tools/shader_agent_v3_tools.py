"""Shader agent v3 MCP tools for planning, executing, and running shaders."""

from __future__ import annotations

from typing import Any, Dict, List

from mcpbla.server.agents.shader_agent_v3 import ShaderAgentV3
from mcpbla.server.orchestrator.shader_orchestrator_v3 import ShaderOrchestratorV3
from mcpbla.server.orchestrator.shader_plan_v3 import ShaderPlanV3
from mcpbla.server.tools.base import Tool


def _async_wrapper(func):
    """Wrap sync shader operations for async use."""
    async def wrapped(arguments: Dict[str, Any]) -> Any:
        return func(arguments)

    return wrapped


def _plan_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Create a shader plan from instruction/material inputs."""
    instruction = arguments.get("instruction", "")
    material = arguments.get("material", "AutoMat")
    orchestrator = ShaderOrchestratorV3()
    plan = orchestrator.plan(instruction, material)
    return plan.to_dict()


def _execute_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a shader plan and report verification results."""
    plan_dict = arguments.get("plan", {})
    plan = ShaderPlanV3.from_dict(plan_dict)
    orchestrator = ShaderOrchestratorV3()
    ok, results = orchestrator.execute(plan)
    verify = orchestrator.verify(plan)
    return {"ok": ok, "results": results, "verify": verify}


def _agent_run_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Run the autonomous shader agent end-to-end."""
    instruction = arguments.get("instruction", "")
    material = arguments.get("material", "AutoMat")
    agent = ShaderAgentV3()
    return agent.run(instruction, material)


def get_tools() -> List[Tool]:
    """Expose shader planning/execution and agent run as MCP tools."""
    return [
        Tool(
            name="shader_plan_v3",
            description="Plan a shader graph from instruction.",
            input_schema={
                "type": "object",
                "properties": {"instruction": {"type": "string"}, "material": {"type": "string"}},
                "required": ["instruction", "material"],
            },
            handler=_async_wrapper(_plan_handler),
        ),
        Tool(
            name="shader_execute_v3",
            description="Execute a shader plan.",
            input_schema={
                "type": "object",
                "properties": {"plan": {"type": "object"}},
                "required": ["plan"],
            },
            handler=_async_wrapper(_execute_handler),
        ),
        Tool(
            name="shader_agent_v3_run",
            description="Run autonomous shader agent v3.",
            input_schema={
                "type": "object",
                "properties": {"instruction": {"type": "string"}, "material": {"type": "string"}},
                "required": ["instruction", "material"],
            },
            handler=_async_wrapper(_agent_run_handler),
        ),
    ]
