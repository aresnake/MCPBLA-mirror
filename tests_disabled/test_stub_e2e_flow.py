from fastapi.testclient import TestClient

from mcpbla.server.bridge.scenegraph_live import clear_registry
from mcpbla.server.bridge import scene_state
from mcpbla.server.mcp_server import create_app


def test_stub_e2e_flow():
    clear_registry()
    scene_state.reset_scene_state()
    client = TestClient(create_app())

    resp = client.post("/tools/create_cube_stub/invoke_v2", json={"arguments": {}})
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("ok") is True

    resp = client.post(
        "/tools/move_object_stub/invoke_v2",
        json={"arguments": {"object_name": "Cube", "delta": [0, 0, 2]}},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("ok") is True
    result = body.get("result", {})
    assert result.get("location") == [0.0, 0.0, 2.0]

    resp = client.post(
        "/tools/get_scene_state/invoke_v2",
        json={"arguments": {}},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("ok") is True
    snapshot = body.get("result", {})
    assert "objects" in snapshot
