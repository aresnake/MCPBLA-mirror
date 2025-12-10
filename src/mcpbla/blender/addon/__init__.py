from .mcp_blender_addon import (
    MCP_OT_PingServer,
    MCP_OT_SendDummySnapshot,
    MCP_OT_RunDemoTask,
    MCP_OT_RunDemoTaskInBlender,
    MCP_PT_Panel,
)

bl_info = {
    "name": "MCP Blender Bridge",
    "author": "Adrien / ARES",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > MCP",
    "description": "Connects Blender to the MCP orchestrator server (scene snapshot, orchestrator tools, demo tasks).",
    "category": "3D View",
}


def register():  # pragma: no cover - Blender runtime only
    import bpy  # type: ignore

    for cls in (MCP_OT_PingServer, MCP_OT_SendDummySnapshot, MCP_OT_RunDemoTask, MCP_OT_RunDemoTaskInBlender, MCP_PT_Panel):
        bpy.utils.register_class(cls)


def unregister():  # pragma: no cover - Blender runtime only
    import bpy  # type: ignore

    for cls in reversed(
        (MCP_OT_PingServer, MCP_OT_SendDummySnapshot, MCP_OT_RunDemoTask, MCP_OT_RunDemoTaskInBlender, MCP_PT_Panel)
    ):
        bpy.utils.unregister_class(cls)
