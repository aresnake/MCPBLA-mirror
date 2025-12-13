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


def get_http_handler_from_env() -> Optional[Callable[[str, dict], Dict[str, Any]]]:
    """Return an HTTP handler if BLENDER_BRIDGE_URL is configured."""
    base = os.getenv("BLENDER_BRIDGE_URL") or ""
    if not base.strip():
        return None
    timeout = float(os.getenv("BLENDER_BRIDGE_TIMEOUT", "5"))
    return HttpBridgeHandler(base, timeout=timeout)
