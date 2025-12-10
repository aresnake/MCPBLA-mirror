from __future__ import annotations

from typing import Any, Callable, Optional


class BridgePool:
    """Lightweight routing layer to communicate with Blender bridge."""

    def __init__(self, router: Optional[Callable[[str, dict], Any]] = None) -> None:
        self._router = router

    def set_router(self, router: Callable[[str, dict], Any]) -> None:
        self._router = router

    def route(self, route: str, payload: dict) -> Any:
        if not self._router:
            raise RuntimeError("BridgePool router is not configured")
        return self._router(route, payload)


_DEFAULT_POOL: Optional[BridgePool] = None


def get_bridge_pool() -> BridgePool:
    global _DEFAULT_POOL
    if _DEFAULT_POOL is None:
        _DEFAULT_POOL = BridgePool()
    return _DEFAULT_POOL
