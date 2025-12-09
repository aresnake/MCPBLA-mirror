import pytest

from server.bridge import scene_state
from server.tools.registry import build_tool_registry, invoke_tool
from server.utils.config import load_config


@pytest.fixture(autouse=True)
def reset_state():
    scene_state.reset_scene_state()
    yield
    scene_state.reset_scene_state()


def test_scene_state_upsert_and_move():
    scene_state.upsert_object("Cube", type="MESH", location=[0, 0, 0])
    updated = scene_state.move_object("Cube", [0, 0, 2])
    assert updated["location"] == [0.0, 0.0, 2.0]


def test_stub_tools_update_state():
    cfg = load_config()
    registry = build_tool_registry(cfg.workspace_root)
    import asyncio

    asyncio.run(invoke_tool(registry, "create_cube_stub", {}))
    asyncio.run(invoke_tool(registry, "move_object_stub", {"object_name": "Cube", "delta": [0, 1, 0]}))
    state = scene_state.get_scene_state()
    assert "Cube" in state["objects"]
    assert state["objects"]["Cube"]["location"] == [0.0, 1.0, 0.0]
