from __future__ import annotations

from typing import Callable, Optional

from mcpbla.server.bridge.bridge_pool import get_bridge_pool  # backward compat
from mcpbla.server.bridge.env import resolve_bridge_enabled
from mcpbla.server.bridge.pool_v2 import get_bridge_pool_v2
from mcpbla.server.bridge.router_v2 import RouterV2
from mcpbla.server.bridge.scenegraph_live_v3 import SCENEGRAPH
from mcpbla.server.bridge.events import EVENT_BUS
from mcpbla.server.bridge.http_bridge import get_http_handler_from_env

import os


def configure_bridge_pool(handler: Optional[Callable[[str, dict], dict]] = None):
    pool = get_bridge_pool_v2()
    if handler:
        pool.set_handler(handler)
    EVENT_BUS.subscribe("*", SCENEGRAPH.on_event)
    return pool


def configure_bridge_from_env(enabled_override: Optional[bool] = None) -> bool:
    """Configure bridge pools from environment when explicitly enabled.

    Requires BLENDER_BRIDGE_ENABLED to be truthy; BLENDER_BRIDGE_URL alone
    should not auto-configure to keep tests hermetic.
    """
    enabled = resolve_bridge_enabled(explicit=enabled_override)
    if not enabled:
        return False

    pool_v2 = get_bridge_pool_v2()
    if pool_v2.has_handler():
        EVENT_BUS.subscribe("*", SCENEGRAPH.on_event)
        return True

    handler = get_http_handler_from_env(force_enabled=enabled)
    if not handler:
        return False

    pool_v2.set_handler(handler)

    legacy_pool = get_bridge_pool()
    if not legacy_pool.has_handler():
        legacy_pool.set_router(handler)

    EVENT_BUS.subscribe("*", SCENEGRAPH.on_event)
    return True
