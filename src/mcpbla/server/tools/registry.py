from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base import Tool

# -------------------------------------------------------------------
# Global registry (name -> Tool)
# -------------------------------------------------------------------

_REGISTRY: Dict[str, Tool] = {}
_WORKSPACE_ROOT: Optional[Path] = None
_CACHE_KEY: Optional[Tuple[Path, bool]] = None


def clear_registry() -> None:
    """
    Clear the global tool registry.

    Utilisé par les tests (test_mcp_server.clear_registry()) pour repartir
    d'un état propre entre deux runs.
    """
    global _REGISTRY, _WORKSPACE_ROOT, _CACHE_KEY
    _REGISTRY = {}
    _WORKSPACE_ROOT = None
    _CACHE_KEY = None


# -------------------------------------------------------------------
# Internal collection helper
# -------------------------------------------------------------------


def _env_bridge_enabled() -> bool:
    raw = os.getenv("BRIDGE_ENABLED")
    if raw is None:
        raw = os.getenv("BLENDER_BRIDGE_ENABLED", "")
    return str(raw).lower() in {"1", "true", "yes", "on"}


def _collect_bridge_tools(workspace_root: Path) -> List[Tool]:
    """
    Collect all Tool instances exposed by the various tool modules.

    Import local pour éviter tout risque de circular import avec
    orchestrator_tools / orchestrator_v3_tools qui, eux, peuvent importer
    registry.py.
    """
    from .blender_tools import get_tools as blender_get_tools
    from .stub_tools import get_tools as stub_get_tools
    from .action_tools import get_tools as action_get_tools
    from .scenegraph_tools import get_tools as scenegraph_get_tools
    from .orchestrator_tools import get_tools as orch_get_tools
    from .orchestrator_v3_tools import get_tools as orch_v3_get_tools
    from .modeler_agent_v3_tools import get_tools as modeler_get_tools
    from .shader_agent_v3_tools import get_tools as shader_get_tools
    from .geo_agent_v3_tools import get_tools as geo_get_tools
    from .animation_agent_v3_tools import get_tools as anim_get_tools
    from .studio_tools import get_tools as studio_get_tools
    from .system_tools import get_tools as system_get_tools
    from .bridge_tools import get_tools as bridge_get_tools

    tools: List[Tool] = []

    # Tools “stub” & scène logique
    tools.extend(blender_get_tools(workspace_root))

    # Actions data-first (bridge / action engine)
    tools.extend(action_get_tools())

    # Scenegraph live (describe/search/get)
    tools.extend(scenegraph_get_tools())

    # Orchestrateur v1 (plan_task / run_task / execute_plan)
    tools.extend(orch_get_tools())

    # Orchestrateur v3 (plan_v3 / execute_plan_v3 / refine_plan_v3)
    tools.extend(orch_v3_get_tools())

    # Agents v3 (modeler / shader / geo / animation)
    tools.extend(modeler_get_tools())
    tools.extend(shader_get_tools())
    tools.extend(geo_get_tools())
    tools.extend(anim_get_tools())

    # Outils studio (tests end-to-end)
    tools.extend(studio_get_tools())

    # Nouveaux outils système (probes, version, etc.)
    tools.extend(system_get_tools())

    # Bridge health tools
    tools.extend(bridge_get_tools())

    # Core lightweight tools should always be available (bridge or not)
    core_names = {"ping", "echo"}
    core_tools = [tool for tool in stub_get_tools(workspace_root) if tool.name in core_names]
    tools.extend(core_tools)

    return tools


def _collect_stub_tools(workspace_root: Path) -> List[Tool]:
    """
    Collect a minimal set of tools when the bridge is disabled.
    """
    from .stub_tools import get_tools as stub_get_tools

    tools: List[Tool] = []

    tools.extend(stub_get_tools(workspace_root))

    return tools


# -------------------------------------------------------------------
# Public API used by mcp_server & orchestrators
# -------------------------------------------------------------------


def build_tool_registry(workspace_root: Path, bridge_enabled: bool | None = None) -> Dict[str, Tool]:
    """
    Build (or return cached) registry mapping names -> Tool.

    - mcp_server.create_app() appelle cette fonction et conserve
      le dict retourné dans une variable locale `tools`.
    - Les tests appellent clear_registry() avant create_app()
      pour forcer un rebuild propre.
    """
    global _REGISTRY, _WORKSPACE_ROOT, _CACHE_KEY

    if bridge_enabled is None:
        bridge_enabled = _env_bridge_enabled()

    # Cache simple : si même workspace_root et registry déjà construit,
    # on réutilise.
    cache_key = (workspace_root, bridge_enabled)
    if _REGISTRY and _WORKSPACE_ROOT == workspace_root and _CACHE_KEY == cache_key:
        return _REGISTRY

    tools = _collect_bridge_tools(workspace_root) if bridge_enabled else _collect_stub_tools(workspace_root)

    # En cas de doublon de nom, le dernier gagne.
    _REGISTRY = {tool.name: tool for tool in tools}
    _WORKSPACE_ROOT = workspace_root
    _CACHE_KEY = cache_key
    return _REGISTRY


def get_registry() -> Dict[str, Tool]:
    """
    Retourne le dict actuel (name -> Tool) sans rebuild.
    """
    return _REGISTRY


def list_registered_tools() -> List[Tool]:
    """
    Retourne la liste des Tool enregistrés.
    """
    return list(_REGISTRY.values())


async def invoke_tool(registry: Dict[str, Tool], name: str, arguments: Dict[str, Any]) -> Any:
    """
    Invocation générique d'un tool MCP par son nom.

    Signature compatible avec les tests existants :

        await invoke_tool(registry, "create_cube_stub", {})

    et avec l’orchestrateur qui passe explicitement le registry.
    """
    tool = registry.get(name)
    if tool is None:
        raise KeyError(f"Unknown tool: {name}")

    return await tool.handler(arguments)
