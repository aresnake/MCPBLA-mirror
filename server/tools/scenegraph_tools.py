from __future__ import annotations

from typing import Any, Dict, List

from server.bridge.scenegraph import SCENEGRAPH
from server.tools.base import Tool


def _async_wrapper(func):
    async def wrapped(arguments):
        return func(arguments)

    return wrapped


def _describe_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    return SCENEGRAPH.describe()


def _search_handler(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    query = arguments.get("query", "")
    return SCENEGRAPH.find(query)


def _get_handler(arguments: Dict[str, Any]) -> Dict[str, Any] | None:
    key = arguments.get("key", "")
    return SCENEGRAPH.get(key)


def get_tools() -> List[Tool]:
    return [
        Tool(
            name="scenegraph_describe",
            description="Describe the current SceneGraphLiveV3 state.",
            input_schema={"type": "object", "properties": {}},
            handler=_async_wrapper(_describe_handler),
        ),
        Tool(
            name="scenegraph_search",
            description="Search SceneGraphLiveV3 entries.",
            input_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            handler=_async_wrapper(_search_handler),
        ),
        Tool(
            name="scenegraph_get",
            description="Get a SceneGraphLiveV3 entry by key.",
            input_schema={
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": ["key"],
            },
            handler=_async_wrapper(_get_handler),
        ),
    ]
