from server.core.engines.scene_engine import SceneEngine


def test_scene_engine_snapshot_contract_result():
    engine = SceneEngine()
    res = engine.snapshot(session_id="test")
    assert hasattr(res, "ok")
