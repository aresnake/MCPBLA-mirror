from __future__ import annotations

from mcpbla.server.bridge.bridge_pool import get_bridge_pool  # backward compat
from mcpbla.server.bridge.pool_v2 import get_bridge_pool_v2
from mcpbla.server.bridge.router_v2 import RouterV2
from mcpbla.server.bridge.scenegraph_live_v3 import SCENEGRAPH
from mcpbla.server.bridge.events import EVENT_BUS
from mcpbla.blender.addon.bridge.handlers_v2 import handle_route  # type: ignore


def configure_bridge_pool():
    pool = get_bridge_pool_v2()
    pool.set_handler(handle_route)
    EVENT_BUS.subscribe("*", SCENEGRAPH.on_event)
    return pool

