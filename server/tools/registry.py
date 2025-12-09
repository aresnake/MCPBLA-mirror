from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, Iterable, List

from server.tools import blender_tools
from server.tools.base import Tool


def build_tool_registry(workspace_root: Path) -> Dict[str, Tool]:
    """Aggregate tools from submodules into a single registry."""
    registry: Dict[str, Tool] = {}
    from server.tools import (
        action_tools,
        orchestrator_tools,
        scenegraph_tools,
        orchestrator_v3_tools,
        modeler_agent_v3_tools,
        shader_agent_v3_tools,
        geo_agent_v3_tools,
        animation_agent_v3_tools,
        studio_tools,
    )

    modules: Iterable[Iterable[Tool]] = [
        blender_tools.get_tools(workspace_root),
        orchestrator_tools.get_tools(),
        action_tools.get_tools(),
        scenegraph_tools.get_tools(),
        orchestrator_v3_tools.get_tools(),
        modeler_agent_v3_tools.get_tools(),
        shader_agent_v3_tools.get_tools(),
        geo_agent_v3_tools.get_tools(),
        animation_agent_v3_tools.get_tools(),
        studio_tools.get_tools(),
    ]
    for tool_list in modules:
        for tool in tool_list:
            registry[tool.name] = tool
    return registry


async def invoke_tool(registry: Dict[str, Tool], tool_name: str, arguments: Dict[str, Any]) -> Any:
    tool = registry.get(tool_name)
    if not tool:
        raise ValueError(f"Tool '{tool_name}' not found")
    result = tool.handler(arguments)
    if asyncio.iscoroutine(result):
        return await result
    return result
