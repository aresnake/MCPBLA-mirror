from fastapi.testclient import TestClient

from mcpbla.server.mcp_server import create_app


def test_bridge_tool_unreachable_contract(monkeypatch):
    for var in ["BLENDER_BRIDGE_URL", "BLENDER_BRIDGE_ENABLED"]:
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("BRIDGE_ENABLED", "true")
    monkeypatch.setenv("BRIDGE_URL", "http://127.0.0.1:59996")
    monkeypatch.setenv("BRIDGE_TIMEOUT_SECONDS", "0.1")

    client = TestClient(create_app())
    resp = client.post("/tools/create_cube/invoke_v2", json={"arguments": {"size": 1.0, "name": "NoBridge"}})
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("ok") is False
    assert body.get("code") in {"BRIDGE_UNREACHABLE", "BRIDGE_TIMEOUT"}
    assert body.get("details", {}).get("attempts") in {1, 2}
