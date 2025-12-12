from __future__ import annotations

from typing import Callable, Optional

from mcpbla.server.bridge.bridge_pool import get_bridge_pool  # backward compat
from mcpbla.server.bridge.pool_v2 import get_bridge_pool_v2
from mcpbla.server.bridge.router_v2 import RouterV2
from mcpbla.server.bridge.scenegraph_live_v3 import SCENEGRAPH
from mcpbla.server.bridge.events import EVENT_BUS


def configure_bridge_pool(handler: Optional[Callable[[str, dict], dict]] = None):
    pool = get_bridge_pool_v2()
    if handler:
        pool.set_handler(handler)
    EVENT_BUS.subscribe("*", SCENEGRAPH.on_event)
    return pool
