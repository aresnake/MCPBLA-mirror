from server.tools import blender_tools


def test_scenegraph_stub_returns_keys():
    snapshot = blender_tools.get_scenegraph_snapshot()
    assert "objects" in snapshot
    assert "materials" in snapshot
