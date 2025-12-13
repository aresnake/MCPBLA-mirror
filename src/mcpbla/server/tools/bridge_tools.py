"""Bridge health MCP tools."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcpbla.server.bridge.messages import ActionMessage
from mcpbla.server.bridge import lifecycle
from mcpbla.server.bridge.pool_v2 import get_bridge_pool_v2
from mcpbla.server.tools.base import Tool


def _async_wrapper(func):
    async def wrapped(arguments: Dict[str, Any]) -> Any:
        return func(arguments)

    return wrapped


def _bridge_probe_handler(_: Dict[str, Any]) -> Dict[str, Any]:
    pool = get_bridge_pool_v2()
    configured = pool.has_handler()
    handler_info: Optional[Dict[str, Any]] = None
    handler = getattr(pool, "router", None) and getattr(pool.router, "handler", None)
    if handler and getattr(handler, "__class__", None).__name__ == "HttpBridgeHandler":
        handler_info = {"type": "http", "base_url": getattr(handler, "base_url", None)}
    reachable = False
    last_error: Optional[Dict[str, Any]] = None
    lifecycle.set_configured(configured)

    if not configured:
        last_error = {"code": "BRIDGE_NOT_CONFIGURED", "message": "Bridge handler not configured"}
        lifecycle.record_error(last_error["code"], last_error["message"])
    else:
        try:
            resp = pool.send_action(ActionMessage(route="system.ping", payload={}))
            if isinstance(resp, dict) and resp.get("ok"):
                reachable = True
                lifecycle.record_success()
            else:
                err = resp.get("error") if isinstance(resp, dict) else None
                if isinstance(err, dict):
                    last_error = {"code": err.get("code"), "message": err.get("message")}
                else:
                    last_error = {"code": "BRIDGE_UNREACHABLE", "message": "Bridge unreachable"}
                lifecycle.record_error(last_error["code"], last_error["message"])
        except Exception as exc:  # noqa: BLE001
            reachable = False
            last_error = {"code": "BRIDGE_ERROR", "message": str(exc)}
            lifecycle.record_error(last_error["code"], last_error["message"])

    state = lifecycle.get_state()
    return {
        "ok": True,
        "data": {
            "configured": state.get("configured", configured),
            "reachable": state.get("reachable", reachable),
            "last_seen": state.get("last_seen"),
            "last_error": state.get("last_error") if state.get("last_error") else last_error,
            "handler": handler_info,
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
