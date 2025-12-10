from __future__ import annotations

from typing import Any, Dict, List

from mcpbla.server.orchestrator import orchestrator
from mcpbla.server.orchestrator.plan import ExecutionResult, Plan
from mcpbla.server.tools.base import Tool
from mcpbla.server.tools.registry import build_tool_registry, invoke_tool
from mcpbla.server.utils.config import load_config


def _make_invoker():
    cfg = load_config()
    registry = build_tool_registry(cfg.workspace_root)

    async def _invoker(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return await invoke_tool(registry, tool_name, arguments)

    return _invoker


async def _plan_task_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    instruction = arguments.get("instruction", "")
    plan = orchestrator.plan_task(instruction)
    return plan.to_dict()


async def _execute_plan_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    plan_dict = arguments.get("plan", {})
    plan = Plan.from_dict(plan_dict)
    invoker = _make_invoker()
    result: ExecutionResult = await orchestrator.execute_plan(plan, invoker=invoker)
    return result.to_dict()


async def _run_task_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    instruction = arguments.get("instruction", "")
    invoker = _make_invoker()
    result: ExecutionResult = await orchestrator.run_task(instruction, invoker=invoker)
    return result.to_dict()


def get_tools() -> List[Tool]:
    return [
        Tool(
            name="plan_task",
            description="Create an execution plan from a natural language instruction.",
            input_schema={
                "type": "object",
                "properties": {"instruction": {"type": "string"}},
                "required": ["instruction"],
            },
            handler=_plan_task_handler,
        ),
        Tool(
            name="execute_plan",
            description="Execute a previously generated plan.",
            input_schema={
                "type": "object",
                "properties": {"plan": {"type": "object"}},
                "required": ["plan"],
            },
            handler=_execute_plan_handler,
        ),
        Tool(
            name="run_task",
            description="Plan and execute an instruction in one call.",
            input_schema={
                "type": "object",
                "properties": {"instruction": {"type": "string"}},
                "required": ["instruction"],
            },
            handler=_run_task_handler,
        ),
    ]

