# MCP Tools Overview

Total tools exposed: **34**. Examples of typical calls from an MCP host:
- `plan_task` with `{"instruction": "add a red cube"}`
- `execute_plan_v3` with a previously returned `plan` object
- `shader_agent_v3_run` with `{"instruction": "glass material", "material": "GlassMat"}`
- `scenegraph_search` with `{"query": "Cube"}` for quick lookups
- `studio_full_test` with `{}` to run the bundled studio smoke test

| name | module | description | category |
| --- | --- | --- | --- |
| echo_text | blender_tools.py | Echo a text payload. | basic |
| list_workspace_files | blender_tools.py | List files/directories in the workspace root (shallow). | basic |
| get_last_scene_snapshot | blender_tools.py | Retrieve the latest scene snapshot for a session. | scenegraph |
| get_scenegraph_snapshot | blender_tools.py | Return the last stored scenegraph snapshot. | scenegraph |
| create_cube_stub | blender_tools.py | Insert a cube placeholder into the in-memory scene. | stub |
| create_sphere_stub | blender_tools.py | Insert a sphere placeholder into the in-memory scene. | stub |
| move_object_stub | blender_tools.py | Move an object by delta in the in-memory scene. | stub |
| assign_material_stub | blender_tools.py | Tag an object with a material in the in-memory scene. | stub |
| apply_fx_stub | blender_tools.py | Tag an object with a simple FX entry. | stub |
| get_scene_state | blender_tools.py | Return the current logical scene state. | scenegraph |
| create_cube | action_tools.py | Create a cube through the action engine. | action |
| move_object | action_tools.py | Move an object via the action engine translation op. | action |
| assign_material | action_tools.py | Assign a material with color using the action engine. | action |
| apply_modifier | action_tools.py | Apply a modifier with settings to an object. | action |
| plan_task | orchestrator_tools.py | Create an execution plan from a natural language instruction. | plan/execution |
| execute_plan | orchestrator_tools.py | Execute a previously generated plan. | plan/execution |
| run_task | orchestrator_tools.py | Plan and execute an instruction in one call. | plan/execution |
| scenegraph_describe | scenegraph_tools.py | Describe the current SceneGraphLiveV3 state. | scenegraph |
| scenegraph_search | scenegraph_tools.py | Search SceneGraphLiveV3 entries. | scenegraph |
| scenegraph_get | scenegraph_tools.py | Get a SceneGraphLiveV3 entry by key. | scenegraph |
| plan_v3 | orchestrator_v3_tools.py | Plan an instruction into a TaskPlan v3. | plan_v3 |
| execute_plan_v3 | orchestrator_v3_tools.py | Execute a TaskPlan v3 and verify it. | plan_v3 |
| refine_plan_v3 | orchestrator_v3_tools.py | Refine/replan a TaskPlan v3 based on a diff. | plan_v3 |
| modeler_agent_v3_run | modeler_agent_v3_tools.py | Run the autonomous modeling agent v3. | agent_v3 |
| shader_plan_v3 | shader_agent_v3_tools.py | Plan a shader graph from instruction and material. | agent_v3 |
| shader_execute_v3 | shader_agent_v3_tools.py | Execute a shader plan and verify it. | agent_v3 |
| shader_agent_v3_run | shader_agent_v3_tools.py | Run autonomous shader agent v3. | agent_v3 |
| geo_plan_v3 | geo_agent_v3_tools.py | Plan a geometry nodes setup from instruction/object. | agent_v3 |
| geo_execute_v3 | geo_agent_v3_tools.py | Execute a geometry plan v3 and verify it. | agent_v3 |
| geo_agent_v3_run | geo_agent_v3_tools.py | Run autonomous geometry agent v3. | agent_v3 |
| animation_plan_v3 | animation_agent_v3_tools.py | Plan animation operations v3. | agent_v3 |
| animation_execute_v3 | animation_agent_v3_tools.py | Execute an animation plan v3 and verify it. | agent_v3 |
| animation_agent_v3_run | animation_agent_v3_tools.py | Run autonomous animation agent v3. | agent_v3 |
| studio_full_test | studio_tools.py | Run the end-to-end studio test suite. | debug/test |
