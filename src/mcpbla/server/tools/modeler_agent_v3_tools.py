"""MCP tool wrapper for the autonomous modeling agent v3."""

from __future__ import annotations

from typing import Any, Dict, List

from mcpbla.server.agents.modeler_agent_v3 import ModelerAgentV3
from mcpbla.server.tools.base import Tool


def _async_wrapper(func):
    """Wrap sync agent calls for async execution."""
    async def wrapped(arguments: Dict[str, Any]) -> Any:
        return func(arguments)

    return wrapped


def _run_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Run the modeling agent against a natural language instruction."""
    instruction = arguments.get("instruction", "")
    agent = ModelerAgentV3()
    return agent.run(instruction)


def get_tools() -> List[Tool]:
    """Expose the modeler agent v3 run entrypoint as an MCP tool."""
    return [
        Tool(
            name="modeler_agent_v3_run",
            description="Run the autonomous modeling agent v3.",
            input_schema={
                "type": "object",
                "properties": {"instruction": {"type": "string"}},
                "required": ["instruction"],
            },
            handler=_async_wrapper(_run_handler),
        )
    ]
