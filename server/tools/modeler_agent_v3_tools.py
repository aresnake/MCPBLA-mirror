from __future__ import annotations

from typing import Any, Dict, List

from server.agents.modeler_agent_v3 import ModelerAgentV3
from server.tools.base import Tool


def _async_wrapper(func):
    async def wrapped(arguments: Dict[str, Any]) -> Any:
        return func(arguments)

    return wrapped


def _run_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    instruction = arguments.get("instruction", "")
    agent = ModelerAgentV3()
    return agent.run(instruction)


def get_tools() -> List[Tool]:
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
