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
    tools_list = resp.json()
    tools = {tool["name"]: tool for tool in tools_list}
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
    assert tools["echo_text"]["input_schema"]["properties"]["text"]["type"] == "string"
    # Ensure list is sorted by name
    names = [tool["name"] for tool in tools_list]
    assert names == sorted(names)


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


def test_bridge_status_disabled(monkeypatch):
    for var in ["BRIDGE_ENABLED", "BLENDER_BRIDGE_ENABLED", "BRIDGE_URL", "BLENDER_BRIDGE_URL"]:
        monkeypatch.delenv(var, raising=False)
    client = TestClient(create_app(bridge_enabled=False))
    resp = client.get("/bridge/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["enabled"] is False
    assert data["configured"] is False
    assert data["reachable"] is False
    assert data["last_error"] is None


def test_bridge_status_enabled_missing_url(monkeypatch):
    for var in ["BRIDGE_URL", "BLENDER_BRIDGE_URL"]:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("BRIDGE_ENABLED", "true")
    monkeypatch.delenv("BLENDER_BRIDGE_ENABLED", raising=False)

    client = TestClient(create_app())
    resp = client.get("/bridge/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["enabled"] is True
    assert data["configured"] is False
    assert data["reachable"] is False
    assert data["last_error"] == "BRIDGE_URL is missing"


def test_bridge_status_unreachable(monkeypatch):
    for var in ["BLENDER_BRIDGE_URL", "BLENDER_BRIDGE_ENABLED"]:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("BRIDGE_ENABLED", "true")
    monkeypatch.setenv("BRIDGE_URL", "http://127.0.0.1:59999")

    client = TestClient(create_app())
    resp = client.get("/bridge/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["configured"] is True
    assert data["reachable"] is False
    assert isinstance(data["last_error"], str)
    assert data["last_error"]


def test_bridge_status_legacy_enabled(monkeypatch):
    for var in ["BRIDGE_ENABLED", "BRIDGE_URL"]:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("BLENDER_BRIDGE_ENABLED", "true")
    monkeypatch.delenv("BLENDER_BRIDGE_URL", raising=False)

    client = TestClient(create_app())
    resp = client.get("/bridge/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["enabled"] is True
    assert data["configured"] is False
    assert data["reachable"] is False
    assert data["last_error"] == "BRIDGE_URL is missing"


def test_bridge_status_legacy_url(monkeypatch):
    for var in ["BRIDGE_URL"]:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("BRIDGE_ENABLED", "true")
    monkeypatch.setenv("BLENDER_BRIDGE_URL", "http://127.0.0.1:59998")

    client = TestClient(create_app())
    resp = client.get("/bridge/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["url"] == "http://127.0.0.1:59998"
    assert data["configured"] is True
    assert data["reachable"] is False
    assert isinstance(data["last_error"], str)


def test_move_object_stub_requires_name():
    client = TestClient(create_app())
    resp = client.post("/tools/move_object_stub/invoke", json={"arguments": {"delta": [0, 1, 2]}})
    assert resp.status_code == 200
    data = resp.json().get("result", {})
    assert data.get("error") == "object_name is required"


def test_echo_alias_matches_canonical():
    client = TestClient(create_app())
    payload = {"arguments": {"text": "hello"}}
    resp_echo = client.post("/tools/echo/invoke", json=payload)
    resp_alias = client.post("/tools/echo_text/invoke", json=payload)
    assert resp_echo.status_code == 200
    assert resp_alias.status_code == 200
    assert resp_echo.json()["result"] == resp_alias.json()["result"]


def test_tools_list_includes_aliases():
    client = TestClient(create_app())
    resp = client.get("/tools")
    assert resp.status_code == 200
    names = {tool["name"] for tool in resp.json()}
    assert "echo" in names
    assert "echo_text" in names


def test_alias_description_labeling():
    client = TestClient(create_app())
    resp = client.get("/tools")
    assert resp.status_code == 200
    tools = {t["name"]: t for t in resp.json()}
    assert tools["echo_text"]["description"].startswith("[ALIAS of echo]")
    assert not tools["echo"]["description"].startswith("[ALIAS")
