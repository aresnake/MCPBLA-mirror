from fastapi.testclient import TestClient

from mcpbla.server.bridge import lifecycle
from mcpbla.server.bridge.pool_v2 import get_bridge_pool_v2
from mcpbla.server.mcp_server import create_app


def setup_function(_):
    lifecycle.reset_state()


def test_lifecycle_no_handler_probe():
    lifecycle.reset_state()
    client = TestClient(create_app(bridge_enabled=True))
    resp = client.post("/tools/bridge_probe/invoke", json={"arguments": {}})
    assert resp.status_code == 200
    data = resp.json().get("result", {}).get("data", {})
    assert data.get("configured") is True
    assert data.get("reachable") is False
    assert data.get("last_error", {}).get("code") in {"BRIDGE_NOT_CONFIGURED", "BRIDGE_UNREACHABLE", "HTTP_ERROR", "BRIDGE_ERROR"}
    state = lifecycle.get_state()
    assert state["configured"] is True
    assert state["reachable"] is False


def test_lifecycle_unreachable_handler():
    lifecycle.reset_state()
    pool = get_bridge_pool_v2()
    original = pool.router.handler

    def failing_handler(route, payload):
        raise ConnectionError("offline")

    pool.set_handler(failing_handler)
    client = TestClient(create_app(bridge_enabled=True))
    resp = client.post("/tools/bridge_probe/invoke", json={"arguments": {}})
    assert resp.status_code == 200
    data = resp.json().get("result", {}).get("data", {})
    assert data.get("configured") is True
    assert data.get("reachable") is False
    assert data.get("last_error", {}).get("code") in {"BRIDGE_UNREACHABLE", "BRIDGE_ERROR"}
    state = lifecycle.get_state()
    assert state["configured"] is True
    assert state["reachable"] is False
    pool.set_handler(original)


def test_lifecycle_success_handler_records_seen():
    lifecycle.reset_state()
    pool = get_bridge_pool_v2()
    original = pool.router.handler

    def ok_handler(route, payload):
        return {"ok": True, "data": {"pong": True}}

    pool.set_handler(ok_handler)
    client = TestClient(create_app(bridge_enabled=True))
    resp = client.post("/tools/bridge_probe/invoke", json={"arguments": {}})
    assert resp.status_code == 200
    data = resp.json().get("result", {}).get("data", {})
    assert data.get("configured") is True
    assert data.get("reachable") is True
    assert data.get("last_seen") is not None
    state = lifecycle.get_state()
    assert state["reachable"] is True
    assert state["last_seen"] is not None
    pool.set_handler(original)
