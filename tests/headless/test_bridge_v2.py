from mcpbla.server.bridge.pool_v2 import BridgePoolV2
from mcpbla.server.bridge.messages import ActionMessage


def test_bridge_pool_v2_without_handler():
    pool = BridgePoolV2()
    msg = ActionMessage(route="noop", payload={})
    resp = pool.send_action(msg)
    assert isinstance(resp, dict)
    assert resp.get("ok") is False
    assert resp.get("error", {}).get("code") == "BRIDGE_NOT_CONFIGURED"
