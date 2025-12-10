from __future__ import annotations

from typing import Any, Dict

from mcpbla.server.bridge.pool_v2 import get_bridge_pool_v2  # type: ignore
from .handlers_v2 import handle_route


def configure_bridge_pool():
    pool = get_bridge_pool_v2()
    pool.set_handler(handle_route)
    return pool

