from server.core.engines.render_engine import RenderEngine


def test_render_engine_preview_contract_result():
    engine = RenderEngine()
    res = engine.render_preview({})
    assert hasattr(res, "ok")
