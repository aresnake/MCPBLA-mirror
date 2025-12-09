from server.core.engines.action_engine_v2 import ActionEngineV2
from server.bridge.pool_v2 import get_bridge_pool_v2


def test_action_engine_v2_validation_only():
    engine = ActionEngineV2()
    # Without router set, expect error on execute
    res = engine.execute("create_cube", {"name": "Cube", "size": 1})
    assert res.ok is False
