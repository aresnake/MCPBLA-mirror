from mcpbla.server.tools import studio_tools


def test_studio_tool_stub():
    tools = studio_tools.get_tools()
    assert any(t.name == "studio_full_test" for t in tools)
    handler = next(t.handler for t in tools if t.name == "studio_full_test")
    import asyncio

    result = asyncio.run(handler({}))
    assert "ok" in result

