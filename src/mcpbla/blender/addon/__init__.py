# src/mcpbla/blender/addon/__init__.py

bl_info = {
    "name": "MCP Blender Orchestrator",
    "author": "Adrien / ARES",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > MCP",
    "description": "Connects Blender to the MCPBLA orchestration server (HTTP bridge + tools).",
    "category": "3D View",
}


def register() -> None:
    """
    Entry point for Blender's add-on system.

    We import the heavy module (operators, panels, bridge wiring)
    *inside* this function so that simply importing
    `mcpbla.blender.addon` (e.g. from headless scripts) does NOT
    require Blender runtime or any UI classes.
    """
    from . import mcp_blender_addon

    mcp_blender_addon.register()


def unregister() -> None:
    """
    Mirror of `register()`. Keeps the import local so importing the
    package stays lightweight outside Blender.
    """
    from . import mcp_blender_addon

    mcp_blender_addon.unregister()
