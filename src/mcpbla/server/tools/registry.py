"""
Unified MCP tool registry.
Loads tools dynamically from all tool modules.
"""

from __future__ import annotations
from typing import List
from pathlib import Path

from .base import Tool

from .blender_tools import get_tools as blender_get_tools
from .action_tools import get_tools as action_get_tools
from .orchestrator_tools import get_tools as orch_get_tools
from .scenegraph_tools import get_tools as scenegraph_get_tools
from .orchestrator_v3_tools import get_tools as orch_v3_get_tools
from .modeler_agent_v3_tools import get_tools as modeler_v3_get_tools
from .shader_agent_v3_tools import get_tools as shader_v3_get_tools
from .geo_agent_v3_tools import get_tools as geo_v3_get_tools
from .animation_agent_v3_tools import get_tools as anim_v3_get_tools
from .studio_tools import get_tools as studio_get_tools

# NEW
from .system_tools import get_tools as system_get_tools


def build_tool_registry(workspace_root: Path) -> List[Tool]:
    """Aggregate tools from all modules into a single registry."""
    tools: List[Tool] = []

    tools.extend(blender_get_tools(workspace_root))
    tools.extend(action_get_tools())
    tools.extend(orch_get_tools())
    tools.extend(scenegraph_get_tools())
    tools.extend(orch_v3_get_tools())
    tools.extend(modeler_v3_get_tools())
    tools.extend(shader_v3_get_tools())
    tools.extend(geo_v3_get_tools())
    tools.extend(anim_v3_get_tools())
    tools.extend(studio_get_tools())

    # NEW system tools
    tools.extend(system_get_tools())

    return tools
