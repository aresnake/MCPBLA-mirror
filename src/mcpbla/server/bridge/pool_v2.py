from __future__ import annotations

from typing import Any, Dict, Optional

from mcpbla.server.bridge.messages import ActionBatch, ActionMessage
from mcpbla.server.bridge.router_v2 import RouterV2


class BridgePoolV2:
    """Bridge pool v2 supporting batching and correlation-aware routing."""

    def __init__(self, router: Optional[RouterV2] = None) -> None:
        self.router = router or RouterV2()

    def set_handler(self, handler) -> None:
        self.router.handler = handler

    def has_handler(self) -> bool:
        return self.router.handler is not None

    def send_action(self, message: ActionMessage) -> Dict[str, Any]:
        if not self.router.handler:
            return {
                "ok": False,
                "error": {"code": "BRIDGE_NOT_CONFIGURED", "message": "Bridge handler not configured"},
            }
        try:
            return self.router.route(message.route, message.to_dict())
        except (TimeoutError, OSError, ConnectionError) as exc:
            return {"ok": False, "error": {"code": "BRIDGE_UNREACHABLE", "message": str(exc)}}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": {"code": "BRIDGE_ERROR", "message": str(exc)}}

    def send_batch(self, batch: ActionBatch) -> Dict[str, Any]:
        payload = batch.to_dict()
        if not self.router.handler:
            return {
                "ok": False,
                "error": {"code": "BRIDGE_NOT_CONFIGURED", "message": "Bridge handler not configured"},
            }
        try:
            return self.router.route("batch.execute", payload)
        except (TimeoutError, OSError, ConnectionError) as exc:
            return {"ok": False, "error": {"code": "BRIDGE_UNREACHABLE", "message": str(exc)}}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": {"code": "BRIDGE_ERROR", "message": str(exc)}}

    def receive_event(self, payload: dict) -> None:
        self.router.receive(payload)


_DEFAULT_POOL_V2: Optional[BridgePoolV2] = None


def get_bridge_pool_v2() -> BridgePoolV2:
    global _DEFAULT_POOL_V2
    if _DEFAULT_POOL_V2 is None:
        _DEFAULT_POOL_V2 = BridgePoolV2()
    return _DEFAULT_POOL_V2
