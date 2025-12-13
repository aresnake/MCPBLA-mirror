from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional, Tuple

from .handlers_v2 import handle_route

_SERVER: Optional[ThreadingHTTPServer] = None
_THREAD: Optional[threading.Thread] = None


class _BridgeRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in {"/bridge/route", "/bridge/action"}:
            self._send_json(404, {"ok": False, "error": {"code": "NOT_FOUND", "message": "Unknown path"}})
            return

        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except Exception:  # noqa: BLE001
            self._send_json(400, {"ok": False, "error": {"code": "BAD_REQUEST", "message": "Invalid JSON"}})
            return

        route = payload.get("route") or payload.get("action")
        params = payload.get("payload") or payload.get("params") or {}
        req_id = payload.get("request_id") or payload.get("correlation_id")
        if not route:
            self._send_json(400, {"ok": False, "error": {"code": "MISSING_ROUTE", "message": "Route required"}})
            return

        result = handle_route(route, params)
        response = {
            "ok": bool(result.get("ok")),
            "data": result.get("data"),
            "error": result.get("error"),
            "request_id": req_id,
        }
        self._send_json(200, response)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        # Quiet server logs inside Blender UI.
        return


def _server_address() -> Tuple[str, int]:
    host = os.getenv("MCP_BRIDGE_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_BRIDGE_PORT", "8765"))
    return host, port


def start_http_bridge() -> Optional[ThreadingHTTPServer]:
    """Start a lightweight HTTP listener inside Blender for bridge calls."""
    global _SERVER, _THREAD
    if _SERVER:
        return _SERVER
    if os.getenv("MCP_BRIDGE_HTTP_ENABLED", "1") not in {"1", "true", "True"}:
        return None

    address = _server_address()
    try:
        server = ThreadingHTTPServer(address, _BridgeRequestHandler)
    except OSError as exc:  # pragma: no cover - runtime only
        print(f"[MCPBLA] Failed to bind HTTP bridge on {address}: {exc}")
        return None

    thread = threading.Thread(target=server.serve_forever, name="mcpbla-bridge-http", daemon=True)
    thread.start()
    _SERVER = server
    _THREAD = thread
    print(f"[MCPBLA] HTTP bridge listening on http://{address[0]}:{address[1]}/bridge/route")
    return server


def stop_http_bridge() -> None:
    """Stop the HTTP listener."""
    global _SERVER, _THREAD
    if _SERVER:
        _SERVER.shutdown()
        _SERVER.server_close()
    _SERVER = None
    _THREAD = None
