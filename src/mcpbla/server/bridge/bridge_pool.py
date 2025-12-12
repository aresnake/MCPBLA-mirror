from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from mcpbla.server.bridge import lifecycle


class BridgePool:
    """Lightweight routing layer to communicate with Blender bridge."""

    def __init__(self, router: Optional[Callable[[str, dict], Any]] = None) -> None:
        self._router = router

    def set_router(self, router: Callable[[str, dict], Any]) -> None:
        self._router = router
        lifecycle.set_configured(True)

    def has_handler(self) -> bool:
        return self._router is not None

    def route(self, route: str, payload: dict) -> Any:
        if not self._router:
            lifecycle.set_configured(False)
            lifecycle.record_error("BRIDGE_NOT_CONFIGURED", "Bridge handler not configured")
            return {
                "ok": False,
                "error": {"code": "BRIDGE_NOT_CONFIGURED", "message": "Bridge handler not configured"},
            }
        try:
            resp = self._router(route, payload)
            if isinstance(resp, dict) and resp.get("ok"):
                lifecycle.record_success()
            else:
                err = resp.get("error") if isinstance(resp, dict) else None
                if isinstance(err, dict):
                    lifecycle.record_error(err.get("code", "BRIDGE_ERROR"), err.get("message", "Bridge error"))
                else:
                    lifecycle.record_error("BRIDGE_ERROR", "Bridge handler returned invalid response")
            return resp
        except (TimeoutError, OSError, ConnectionError) as exc:
            lifecycle.record_error("BRIDGE_UNREACHABLE", str(exc))
            return {"ok": False, "error": {"code": "BRIDGE_UNREACHABLE", "message": str(exc)}}
        except Exception as exc:  # noqa: BLE001
            lifecycle.record_error("BRIDGE_ERROR", str(exc))
            return {"ok": False, "error": {"code": "BRIDGE_ERROR", "message": str(exc)}}


_DEFAULT_POOL: Optional[BridgePool] = None


def get_bridge_pool() -> BridgePool:
    global _DEFAULT_POOL
    if _DEFAULT_POOL is None:
        _DEFAULT_POOL = BridgePool()
    return _DEFAULT_POOL
