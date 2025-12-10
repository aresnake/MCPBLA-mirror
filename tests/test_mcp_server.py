from fastapi.testclient import TestClient

from mcpbla.server.bridge.scenegraph_live import clear_registry
from mcpbla.server.bridge import scene_state
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
    assert "echo_text" in tools
    assert "list_workspace_files" in tools
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
    client = TestClient(create_app())
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
    client = TestClient(create_app())
    resp = client.post("/tools/run_task/invoke", json={"arguments": {"instruction": "create a cube"}})
    assert resp.status_code == 200
    body = resp.json()
    result = body.get("result", {})
    assert result.get("success") is True
    assert result.get("steps")


def test_get_scene_state_tool_http():
    scene_state.reset_scene_state()
    client = TestClient(create_app())
    client.post("/tools/run_task/invoke", json={"arguments": {"instruction": "create a cube"}})
    resp = client.post("/tools/get_scene_state/invoke", json={"arguments": {}})
    assert resp.status_code == 200
    state = resp.json().get("result", {})
    assert "objects" in state
    assert "Cube" in state.get("objects", {})

