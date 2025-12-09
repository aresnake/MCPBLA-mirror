from __future__ import annotations

import uuid
from typing import Any, Dict

from blender.addon.bridge_client import BridgeClient


def emit_event(event_name: str, data: Dict[str, Any]) -> None:
    """Send an event to the MCP server bridge endpoint."""
    message = {
        "type": "event",
        "event": event_name,
        "data": data,
        "correlation_id": str(uuid.uuid4()),
    }
    try:
        client = BridgeClient()
        client.send_event(event_name, data, correlation_id=message["correlation_id"])
    except Exception:
        return
