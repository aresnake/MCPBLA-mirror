from __future__ import annotations

import json
import uuid
from typing import Any, Dict

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None


class BlenderEventEmitter:
    def __init__(self, bridge_client=None) -> None:
        self.bridge_client = bridge_client

    def emit(self, event_name: str, data: Dict[str, Any]) -> None:
        if self.bridge_client is None:
            return
        message = {
            "event": event_name,
            "data": data,
            "correlation_id": str(uuid.uuid4()),
            "type": "event",
        }
        try:
            # using bridge_client run_tool to send an event envelope over existing channel
            self.bridge_client._request("POST", "/bridge/event", message)
        except Exception:
            return
