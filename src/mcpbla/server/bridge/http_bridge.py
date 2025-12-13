from __future__ import annotations

import json
import os
import uuid
from typing import Any, Callable, Dict, Optional
from urllib import error, request


class HttpBridgeHandler:
    """HTTP bridge handler that forwards bridge routes to a Blender addon listener."""

    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def __call__(self, route: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/bridge/route"
        req_id = str(uuid.uuid4())
        body = {
            "route": route,
            "payload": payload,
            "request_id": req_id,
        }
        data = json.dumps(body).encode("utf-8")
        req = request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                text = resp.read().decode("utf-8")
                if not text:
                    return {"ok": False, "error": {"code": "EMPTY_RESPONSE", "message": "No response body"}}
                parsed = json.loads(text)
                if "request_id" not in parsed:
                    parsed["request_id"] = req_id
                return parsed
        except error.HTTPError as exc:
            return {"ok": False, "error": {"code": "HTTP_ERROR", "message": f"{exc.code}: {exc.reason}"}}
        except error.URLError as exc:
            return {"ok": False, "error": {"code": "HTTP_ERROR", "message": str(exc.reason)}}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": {"code": "HTTP_ERROR", "message": str(exc)}}


def _resolve_bridge_url_from_env(force_enabled: bool = False) -> Optional[str]:
    """Return a bridge URL from env, with sensible defaults when enabled."""
    # Explicit URL wins
    explicit = os.getenv("BLENDER_BRIDGE_URL") or os.getenv("BRIDGE_URL") or ""
    if explicit.strip():
        return explicit.strip()

    # Construct from host/port if provided or if bridge explicitly enabled
    enabled_env = str(os.getenv("BRIDGE_ENABLED") or os.getenv("BLENDER_BRIDGE_ENABLED") or "").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    enabled = enabled_env or force_enabled
    host = os.getenv("BRIDGE_HOST") or os.getenv("BLENDER_BRIDGE_HOST") or "127.0.0.1"
    port = os.getenv("BRIDGE_PORT") or os.getenv("BLENDER_BRIDGE_PORT") or "9876"
    scheme = os.getenv("BRIDGE_SCHEME") or "http"

    if enabled:
        return f"{scheme}://{host}:{port}"
    return None


def get_http_handler_from_env(force_enabled: bool = False) -> Optional[Callable[[str, dict], Dict[str, Any]]]:
    """Return an HTTP handler if bridge env configuration is available."""
    base = _resolve_bridge_url_from_env(force_enabled=force_enabled)
    if not base:
        return None
    timeout = float(os.getenv("BLENDER_BRIDGE_TIMEOUT", os.getenv("BRIDGE_TIMEOUT", "5")))
    return HttpBridgeHandler(base, timeout=timeout)
