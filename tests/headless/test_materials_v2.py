from server.core.engines.material_engine import MaterialEngine


def test_material_engine_validation():
    engine = MaterialEngine()
    res = engine.assign("", "", [])
    assert res.ok is False
