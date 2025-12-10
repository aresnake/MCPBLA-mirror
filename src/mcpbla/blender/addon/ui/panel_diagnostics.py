from __future__ import annotations

import json
from typing import Any, Dict

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None

from mcpbla.blender.addon.bridge_client import BridgeClient
from mcpbla.blender.addon.mcp_blender_addon import build_scene_snapshot

_EVENT_MONITOR_ENABLED = False


class ARES_OT_ping(bpy.types.Operator):  # type: ignore[misc]
    bl_idname = "ares.ping"
    bl_label = "MCP Ping"
    bl_description = "Ping MCP server"

    def execute(self, context):  # noqa: ANN001
        client = BridgeClient()
        try:
            resp = client.ping()
            self.report({"INFO"}, f"Ping OK: {resp}")
        except Exception as exc:  # noqa: BLE001
            self.report({"ERROR"}, f"Ping failed: {exc}")
            return {"CANCELLED"}
        return {"FINISHED"}


class ARES_OT_snapshot(bpy.types.Operator):  # type: ignore[misc]
    bl_idname = "ares.snapshot"
    bl_label = "Send Snapshot"
    bl_description = "Send real scene snapshot to MCP server"

    def execute(self, context):  # noqa: ANN001
        client = BridgeClient()
        try:
            payload = build_scene_snapshot(session_id="diagnostics")
            resp = client.send_snapshot(payload)
            self.report({"INFO"}, f"Snapshot sent: {resp}")
        except Exception as exc:  # noqa: BLE001
            self.report({"ERROR"}, f"Snapshot failed: {exc}")
            return {"CANCELLED"}
        return {"FINISHED"}


class ARES_OT_studio_test(bpy.types.Operator):  # type: ignore[misc]
    bl_idname = "ares.studio_test"
    bl_label = "Run Studio Test"
    bl_description = "Run studio full test via MCP server"

    def execute(self, context):  # noqa: ANN001
        client = BridgeClient()
        try:
            resp = client.run_tool("studio_full_test", {})
            self.report({"INFO"}, f"Studio test: {resp}")
        except Exception as exc:  # noqa: BLE001
            self.report({"ERROR"}, f"Studio test failed: {exc}")
            return {"CANCELLED"}
        return {"FINISHED"}


class ARES_OT_event_monitor(bpy.types.Operator):  # type: ignore[misc]
    bl_idname = "ares.event_monitor"
    bl_label = "Toggle Event Monitor"
    bl_description = "Toggle event monitor (client-side)"

    def execute(self, context):  # noqa: ANN001
        global _EVENT_MONITOR_ENABLED
        _EVENT_MONITOR_ENABLED = not _EVENT_MONITOR_ENABLED
        state = "ON" if _EVENT_MONITOR_ENABLED else "OFF"
        self.report({"INFO"}, f"Event monitor {state}")
        return {"FINISHED"}


class ARES_PT_Diagnostics(bpy.types.Panel):  # type: ignore[misc]
    bl_label = "ARES Diagnostics"
    bl_idname = "ARES_PT_diagnostics"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MCP"

    def draw(self, context):  # noqa: ANN001
        layout = self.layout
        layout.operator("ares.ping", text="MCP Ping")
        layout.operator("ares.snapshot", text="Snapshot")
        layout.operator("ares.studio_test", text="Run Studio Test")
        layout.operator("ares.event_monitor", text="Toggle Event Monitor")


CLASSES = (
    ARES_OT_ping,
    ARES_OT_snapshot,
    ARES_OT_studio_test,
    ARES_OT_event_monitor,
    ARES_PT_Diagnostics,
)


def register():
    if bpy is None:
        return
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    if bpy is None:
        return
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

