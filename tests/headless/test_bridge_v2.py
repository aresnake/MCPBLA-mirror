from server.bridge.pool_v2 import BridgePoolV2
from server.bridge.messages import ActionMessage


def test_bridge_pool_v2_without_handler():
    pool = BridgePoolV2()
    msg = ActionMessage(route="noop", payload={})
    try:
        pool.send_action(msg)
    except RuntimeError:
        assert True
    else:
        assert False
