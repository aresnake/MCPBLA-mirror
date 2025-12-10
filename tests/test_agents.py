from mcpbla.server.agents import fx_agent, modeler_agent, shading_agent


def test_modeler_agent_plans_cube():
    steps = modeler_agent.plan_modeling("create a cube")
    assert steps
    assert any(step.tool_name == "create_cube_stub" for step in steps)


def test_shading_agent_plans_material():
    steps = shading_agent.plan_shading("add a red material")
    assert steps
    assert any(step.tool_name == "assign_material_stub" for step in steps)


def test_fx_agent_plans_fx():
    steps = fx_agent.plan_fx("add glow fx")
    assert steps
    assert any(step.tool_name == "apply_fx_stub" for step in steps)

