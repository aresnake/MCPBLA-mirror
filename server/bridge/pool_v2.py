from __future__ import annotations

from typing import Any, Dict, Optional

from server.bridge.messages import ActionBatch, ActionMessage
from server.bridge.router_v2 import RouterV2


class BridgePoolV2:
    """Bridge pool v2 supporting batching and correlation-aware routing."""

    def __init__(self, router: Optional[RouterV2] = None) -> None:
        self.router = router or RouterV2()

    def set_handler(self, handler) -> None:
        self.router.handler = handler

    def send_action(self, message: ActionMessage) -> Dict[str, Any]:
        return self.router.route(message.route, message.to_dict())

    def send_batch(self, batch: ActionBatch) -> Dict[str, Any]:
        payload = batch.to_dict()
        return self.router.route("batch.execute", payload)


_DEFAULT_POOL_V2: Optional[BridgePoolV2] = None


def get_bridge_pool_v2() -> BridgePoolV2:
    global _DEFAULT_POOL_V2
    if _DEFAULT_POOL_V2 is None:
        _DEFAULT_POOL_V2 = BridgePoolV2()
    return _DEFAULT_POOL_V2
