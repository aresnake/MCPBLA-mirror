from __future__ import annotations

from typing import Callable, Optional

import os

from mcpbla.server.bridge.bridge_pool import get_bridge_pool  # backward compat
from mcpbla.server.bridge.pool_v2 import get_bridge_pool_v2
from mcpbla.server.bridge.router_v2 import RouterV2
from mcpbla.server.bridge.scenegraph_live_v3 import SCENEGRAPH
from mcpbla.server.bridge.events import EVENT_BUS
from mcpbla.server.bridge.http_bridge import get_http_handler_from_env


def configure_bridge_pool(handler: Optional[Callable[[str, dict], dict]] = None):
    pool = get_bridge_pool_v2()
    if handler:
        pool.set_handler(handler)
    EVENT_BUS.subscribe("*", SCENEGRAPH.on_event)
    return pool


def configure_bridge_from_env() -> bool:
    """Configure bridge pools from environment when explicitly enabled.

    Requires BLENDER_BRIDGE_ENABLED to be truthy; BLENDER_BRIDGE_URL alone
    should not auto-configure to keep tests hermetic.
    """
    enabled = os.getenv("BLENDER_BRIDGE_ENABLED", "").lower() in {"1", "true", "yes", "on"}
    if not enabled:
        return False

    handler = get_http_handler_from_env()
    if not handler:
        return False

    pool_v2 = get_bridge_pool_v2()
    pool_v2.set_handler(handler)

    legacy_pool = get_bridge_pool()
    legacy_pool.set_router(handler)

    EVENT_BUS.subscribe("*", SCENEGRAPH.on_event)
    return True
