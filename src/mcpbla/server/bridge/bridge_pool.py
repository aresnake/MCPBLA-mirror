from __future__ import annotations

from typing import Any, Callable, Dict, Optional


class BridgePool:
    """Lightweight routing layer to communicate with Blender bridge."""

    def __init__(self, router: Optional[Callable[[str, dict], Any]] = None) -> None:
        self._router = router

    def set_router(self, router: Callable[[str, dict], Any]) -> None:
        self._router = router

    def route(self, route: str, payload: dict) -> Any:
        if not self._router:
            return {
                "ok": False,
                "error": {"code": "BRIDGE_NOT_CONFIGURED", "message": "Bridge handler not configured"},
            }
        try:
            return self._router(route, payload)
        except (TimeoutError, OSError, ConnectionError) as exc:
            return {"ok": False, "error": {"code": "BRIDGE_UNREACHABLE", "message": str(exc)}}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": {"code": "BRIDGE_ERROR", "message": str(exc)}}


_DEFAULT_POOL: Optional[BridgePool] = None


def get_bridge_pool() -> BridgePool:
    global _DEFAULT_POOL
    if _DEFAULT_POOL is None:
        _DEFAULT_POOL = BridgePool()
    return _DEFAULT_POOL
