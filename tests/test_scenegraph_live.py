import pytest

from mcpbla.server.bridge.scenegraph_live import SceneSnapshot, ScenegraphLive, clear_registry, get_snapshot, store_snapshot
from mcpbla.server.tools.blender_tools import _get_scenegraph_snapshot_handler


@pytest.fixture(autouse=True)
def reset_registry():
    clear_registry()
    yield
    clear_registry()


def test_scenegraph_apply_and_snapshot():
    sg = ScenegraphLive()
    sg.apply({"objects": ["Cube"]})
    snap = sg.snapshot()
    assert snap["objects"] == ["Cube"]


def test_store_and_get_snapshot():
    snapshot = SceneSnapshot(session_id="demo", objects=[{"name": "Cube"}], metadata={"source": "test"})
    store_snapshot(snapshot)
    fetched = get_snapshot("demo")
    assert fetched is not None
    assert fetched.session_id == "demo"
    assert fetched.objects[0]["name"] == "Cube"


def test_get_scenegraph_snapshot_tool_handler():
    snapshot = SceneSnapshot(session_id="demo2", objects=[{"name": "Cube"}], metadata={"source": "test"})
    store_snapshot(snapshot)
    result = _get_scenegraph_snapshot_handler({"session_id": "demo2"})
    assert result["ok"] is True
    payload = result["result"]
    assert payload["session_id"] == "demo2"
    assert payload["objects"][0]["name"] == "Cube"
