"""Bridge health MCP tools."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcpbla.server.bridge.messages import ActionMessage
from mcpbla.server.bridge.pool_v2 import get_bridge_pool_v2
from mcpbla.server.tools.base import Tool


def _async_wrapper(func):
    async def wrapped(arguments: Dict[str, Any]) -> Any:
        return func(arguments)

    return wrapped


def _bridge_probe_handler(_: Dict[str, Any]) -> Dict[str, Any]:
    pool = get_bridge_pool_v2()
    configured = pool.has_handler()
    reachable = False
    last_error: Optional[Dict[str, Any]] = None

    if not configured:
        last_error = {"code": "BRIDGE_NOT_CONFIGURED", "message": "Bridge handler not configured"}
    else:
        resp = pool.send_action(ActionMessage(route="bridge.ping", payload={}))
        if isinstance(resp, dict) and resp.get("ok"):
            reachable = True
        else:
            err = resp.get("error") if isinstance(resp, dict) else None
            if isinstance(err, dict):
                last_error = {"code": err.get("code"), "message": err.get("message")}
            else:
                last_error = {"code": "BRIDGE_UNREACHABLE", "message": "Bridge unreachable"}

    return {
        "ok": True,
        "data": {
            "configured": configured,
            "reachable": reachable,
            "last_error": last_error,
        },
    }


def get_tools() -> List[Tool]:
    return [
        Tool(
            name="bridge_probe",
            description="Report bridge handler status and reachability.",
            input_schema={"type": "object", "properties": {}},
            handler=_async_wrapper(_bridge_probe_handler),
        )
    ]
