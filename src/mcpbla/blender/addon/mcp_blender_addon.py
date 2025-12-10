bl_info = {
    "name": "MCP Blender Bridge",
    "author": "MCPBLA",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D",
    "description": "Connects Blender to MCP server",
    "category": "3D View",
}

try:
    import bpy  # type: ignore
except ImportError:  # pragma: no cover - Blender runtime only
    bpy = None


if bpy:
    from .bridge_client import BridgeClient
    from .ui.panel_diagnostics import CLASSES as DIAG_CLASSES, register as register_diag, unregister as unregister_diag

    def get_or_create_cube(name: str = "Cube"):
        """Return an existing cube by name or create one at the origin."""
        obj = bpy.data.objects.get(name)
        if obj:
            return obj
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        obj.location = (0.0, 0.0, 0.0)
        bpy.context.scene.collection.objects.link(obj)
        return obj

    def move_object(obj, delta):
        """Move object by delta vector."""
        if not delta:
            return
        dx = float(delta[0]) if len(delta) > 0 else 0.0
        dy = float(delta[1]) if len(delta) > 1 else 0.0
        dz = float(delta[2]) if len(delta) > 2 else 0.0
        obj.location.x += dx
        obj.location.y += dy
        obj.location.z += dz

    def build_scene_snapshot(session_id: str = "blender_session") -> dict:
        """Build a data-first snapshot of the current Blender scene."""
        objects = []
        for obj in bpy.data.objects:
            if obj.type not in {"MESH", "LIGHT", "CAMERA"}:
                continue
            objects.append(
                {
                    "name": obj.name,
                    "type": obj.type,
                    "location": list(obj.location),
                }
            )
        snapshot = {
            "session_id": session_id,
            "objects": objects,
            "metadata": {
                "source": "blender_addon",
                "scene_name": bpy.context.scene.name if bpy.context and bpy.context.scene else "unknown",
            },
        }
        return snapshot

    class MCP_OT_PingServer(bpy.types.Operator):
        bl_idname = "mcp.ping_server"
        bl_label = "Ping MCP Server"
        bl_description = "Ping the MCP server health endpoint"

        def execute(self, context):  # noqa: ANN001
            client = BridgeClient()
            try:
                result = client.ping()
                self.report({"INFO"}, f"Ping ok: {result}")
            except Exception as exc:  # noqa: BLE001
                self.report({"ERROR"}, f"Ping failed: {exc}")
                return {"CANCELLED"}
            return {"FINISHED"}

    class MCP_OT_SendDummySnapshot(bpy.types.Operator):
        bl_idname = "mcp.send_dummy_snapshot"
        bl_label = "Send Dummy Snapshot"
        bl_description = "Send a stub scene snapshot to MCP server"

        def execute(self, context):  # noqa: ANN001
            client = BridgeClient()
            try:
                result = client.send_dummy_snapshot()
                self.report({"INFO"}, f"Snapshot sent: {result}")
            except Exception as exc:  # noqa: BLE001
                self.report({"ERROR"}, f"Snapshot failed: {exc}")
                return {"CANCELLED"}
            return {"FINISHED"}

    class MCP_OT_RunDemoTask(bpy.types.Operator):
        bl_idname = "mcp.run_demo_task"
        bl_label = "Run Demo Task"
        bl_description = "Run a demo orchestrator task via MCP server"

        def execute(self, context):  # noqa: ANN001
            client = BridgeClient()
            try:
                instruction = "create a cube and move it 2 meters up"
                result = client.run_task(instruction)
                self.report({"INFO"}, f"Run task success: {result.get('result', {}).get('success', True)}")
                print("MCP Run Demo Task result:", result)
            except Exception as exc:  # noqa: BLE001
                self.report({"ERROR"}, f"Run task failed: {exc}")
                return {"CANCELLED"}
            return {"FINISHED"}

    class MCP_OT_RunDemoTaskInBlender(bpy.types.Operator):
        bl_idname = "mcp.run_demo_task_in_blender"
        bl_label = "Run Demo Task in Blender"
        bl_description = "Plan via MCP and execute steps locally in Blender"

        def execute(self, context):  # noqa: ANN001
            client = BridgeClient()
            instruction = "create a cube and move it 2 meters up"
            try:
                plan_resp = client.plan_task(instruction)
                plan_data = plan_resp.get("result") or plan_resp
                steps = plan_data.get("steps", [])
                if not steps:
                    self.report({"ERROR"}, "No steps returned from planner")
                    return {"CANCELLED"}
                created = {}
                for step in steps:
                    name = step.get("tool_name")
                    args = step.get("arguments", {})
                    if name == "create_cube_stub":
                        cube_name = args.get("object_name", "Cube") or "Cube"
                        self.report({"INFO"}, f"Creating cube '{cube_name}'")
                        obj = get_or_create_cube(cube_name)
                        created[obj.name] = obj
                    elif name == "move_object_stub":
                        obj_name = args.get("object_name", "Cube")
                        delta = args.get("delta", [0, 0, 0])
                        obj = bpy.data.objects.get(obj_name) or created.get(obj_name) or get_or_create_cube(obj_name)
                        self.report({"INFO"}, f"Moving '{obj.name}' by {delta}")
                        move_object(obj, delta)
                    else:
                        self.report({"WARNING"}, f"Unknown step '{name}', skipping")
                self.report({"INFO"}, "Demo task executed in Blender")
            except Exception as exc:  # noqa: BLE001
                self.report({"ERROR"}, f"Run in Blender failed: {exc}")
                return {"CANCELLED"}
            return {"FINISHED"}

    class MCP_PT_Panel(bpy.types.Panel):
        bl_label = "MCP Bridge"
        bl_idname = "MCP_PT_bridge_panel"
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_category = "MCP"

        def draw(self, context):  # noqa: ANN001
            layout = self.layout
            layout.operator("mcp.ping_server", text="Ping MCP Server")
            layout.operator("mcp.send_dummy_snapshot", text="Send Dummy Snapshot")
            layout.operator("mcp.send_real_snapshot", text="Send Real Scene Snapshot")
            layout.operator("mcp.run_demo_task", text="Run Demo Task")
            layout.operator("mcp.run_demo_task_in_blender", text="Run Demo Task in Blender")
            layout.operator("mcp.full_reload_test", text="Run Full Studio Test")

    class ARES_OT_full_reload_test(bpy.types.Operator):
        bl_idname = "mcp.full_reload_test"
        bl_label = "Run Full Studio Test"
        bl_description = "Trigger full studio test via MCP tool"

        def execute(self, context):  # noqa: ANN001
            client = BridgeClient()
            try:
                result = client.run_tool("studio_full_test", {})
                self.report({"INFO"}, f"Studio test: {result}")
            except Exception as exc:  # noqa: BLE001
                self.report({"ERROR"}, f"Studio test failed: {exc}")
                return {"CANCELLED"}
            return {"FINISHED"}

    class ARES_MT_diagnostics(bpy.types.Menu):
        bl_label = "ARES Diagnostics"
        bl_idname = "ARES_MT_diagnostics"

        def draw(self, context):  # noqa: ANN001
            layout = self.layout
            layout.operator("mcp.ping_server", text="Ping MCP Server")
            layout.operator("mcp.send_real_snapshot", text="Send Real Scene Snapshot")
            layout.operator("mcp.full_reload_test", text="Run Full Studio Test")

    class MCP_OT_SendRealSnapshot(bpy.types.Operator):
        bl_idname = "mcp.send_real_snapshot"
        bl_label = "Send Real Scene Snapshot"
        bl_description = "Capture the current Blender scene and send it to MCP server"

        def execute(self, context):  # noqa: ANN001
            from .bridge_client import BridgeClient

            client = BridgeClient()
            payload = build_scene_snapshot(session_id="blender_session")
            try:
                resp = client.send_snapshot(payload)
                self.report({"INFO"}, f"Real snapshot sent: {resp}")
            except Exception as exc:  # noqa: BLE001
                self.report({"ERROR"}, f"Failed to send snapshot: {exc}")
                return {"CANCELLED"}
            return {"FINISHED"}

    _CLASSES = (
        MCP_OT_PingServer,
        MCP_OT_SendDummySnapshot,
        MCP_OT_SendRealSnapshot,
        MCP_OT_RunDemoTask,
        MCP_OT_RunDemoTaskInBlender,
        ARES_OT_full_reload_test,
        ARES_MT_diagnostics,
        MCP_PT_Panel,
    )

    def register():
        for cls in _CLASSES:
            bpy.utils.register_class(cls)
        register_diag()

    def unregister():
        unregister_diag()
        for cls in reversed(_CLASSES):
            bpy.utils.unregister_class(cls)

else:

    def register():  # pragma: no cover - Blender runtime only
        print("Blender not available; addon registration skipped.")

    def unregister():  # pragma: no cover - Blender runtime only
        print("Blender not available; addon unregistration skipped.")
