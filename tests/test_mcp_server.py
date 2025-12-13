from fastapi.testclient import TestClient

from mcpbla.server.bridge.scenegraph_live import clear_registry
from mcpbla.server.bridge import scene_state
from mcpbla.server.bridge.events import EVENT_BUS
from mcpbla.server.mcp_server import create_app


def test_healthcheck():
    client = TestClient(create_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_tools_metadata():
    client = TestClient(create_app())
    resp = client.get("/tools")
    assert resp.status_code == 200
    tools = {tool["name"]: tool for tool in resp.json()}
    assert set(tools.keys()) <= {
        "ping",
        "echo",
        "echo_text",
        "list_workspace_files",
        "scene_snapshot_stub",
        "create_cube_stub",
        "move_object_stub",
        "assign_material_stub",
        "apply_fx_stub",
        "get_scene_state",
    }
    assert "echo_text" in tools
    assert tools["echo_text"]["input_schema"]["required"] == ["text"]


def test_echo_tool_invoke():
    client = TestClient(create_app())
    payload = {"arguments": {"text": "ping"}}
    resp = client.post("/tools/echo_text/invoke", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"]["text"] == "ping"


def test_scene_snapshot_flow():
    clear_registry()
    client = TestClient(create_app(bridge_enabled=True))
    snapshot_payload = {
        "session_id": "demo_session",
        "objects": [{"name": "Cube", "type": "MESH", "location": [0, 0, 0]}],
        "metadata": {"source": "test"},
    }
    ingest_resp = client.post("/blender/scene_snapshot", json=snapshot_payload)
    assert ingest_resp.status_code == 200
    invoke_resp = client.post("/tools/get_last_scene_snapshot/invoke", json={"arguments": {"session_id": "demo_session"}})
    assert invoke_resp.status_code == 200
    data = invoke_resp.json()["result"]
    assert data["session_id"] == "demo_session"
    assert data["objects"][0]["name"] == "Cube"


def test_run_task_http():
    scene_state.reset_scene_state()
    client = TestClient(create_app(bridge_enabled=True))
    resp = client.post("/tools/run_task/invoke", json={"arguments": {"instruction": "create a cube"}})
    assert resp.status_code == 200
    body = resp.json()
    result = body.get("result", {})
    assert result.get("success") is True
    assert result.get("steps")


def test_get_scene_state_tool_http():
    scene_state.reset_scene_state()
    client = TestClient(create_app())
    client.post("/tools/create_cube_stub/invoke", json={"arguments": {}})
    resp = client.post("/tools/get_scene_state/invoke", json={"arguments": {}})
    assert resp.status_code == 200
    state = resp.json().get("result", {})
    assert "objects" in state
    assert "Cube" in state.get("objects", {})


def test_action_tool_without_bridge_handler():
    client = TestClient(create_app(bridge_enabled=True))
    resp = client.post("/tools/create_cube/invoke", json={"arguments": {"size": 1.0, "name": "NoBridge"}})
    assert resp.status_code == 200
    result = resp.json().get("result", {})
    assert result.get("ok") is False
    error = result.get("error", {})
    assert error.get("code") in {"BRIDGE_NOT_CONFIGURED", "HTTP_ERROR", "BRIDGE_UNREACHABLE", "BRIDGE_ERROR"}


def test_bridge_event_ingress_triggers_event_bus():
    client = TestClient(create_app())
    captured = {}

    def handler(event_name, data):
        captured["event"] = event_name
        captured["data"] = data

    EVENT_BUS.subscribe("ingress.test", handler)
    resp = client.post("/bridge/event", json={"event": "ingress.test", "data": {"value": 1}})
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("ok") is True
    assert captured.get("event") == "ingress.test"
    assert captured.get("data") == {"value": 1}


def test_bridge_probe_not_configured():
    client = TestClient(create_app(bridge_enabled=True))
    resp = client.post("/tools/bridge_probe/invoke", json={"arguments": {}})
    assert resp.status_code == 200
    result = resp.json().get("result", {})
    assert result.get("ok") is True
    data = result.get("data", {})
    assert data.get("configured") is True
    assert data.get("reachable") is False
    assert data.get("last_error", {}).get("code") in {"BRIDGE_NOT_CONFIGURED", "BRIDGE_UNREACHABLE", "HTTP_ERROR", "BRIDGE_ERROR"}


def test_bridge_probe_unreachable_handler():
    from mcpbla.server.bridge.pool_v2 import get_bridge_pool_v2

    pool = get_bridge_pool_v2()
    original = pool.router.handler

    def failing_handler(route, payload):
        raise ConnectionError("no bridge")

    pool.set_handler(failing_handler)
    try:
        client = TestClient(create_app(bridge_enabled=True))
        resp = client.post("/tools/bridge_probe/invoke", json={"arguments": {}})
        assert resp.status_code == 200
        result = resp.json().get("result", {})
        assert result.get("ok") is True
        data = result.get("data", {})
        assert data.get("configured") is True
        assert data.get("reachable") is False
        assert data.get("last_error", {}).get("code") in {"BRIDGE_UNREACHABLE", "BRIDGE_ERROR"}
    finally:
        pool.set_handler(original)
