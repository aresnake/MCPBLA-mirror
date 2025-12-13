from __future__ import annotations

import json
import os
import socket
import uuid
from typing import Any, Callable, Dict, Optional
from urllib import error, request

from mcpbla.server.bridge.env import resolve_bridge_enabled, resolve_bridge_url
from mcpbla.server.tools.tool_response import BRIDGE_BAD_RESPONSE, BRIDGE_TIMEOUT, BRIDGE_UNREACHABLE, err

DEFAULT_TIMEOUT = 5.0
DEFAULT_PING_TIMEOUT = 1.0


def _float_from_env(keys: list[str], default: float) -> float:
    for key in keys:
        raw = os.getenv(key)
        if raw is None or raw == "":
            continue
        try:
            return float(raw)
        except (TypeError, ValueError):
            continue
    return default


def get_bridge_timeout_seconds() -> float:
    return _float_from_env(
        ["BRIDGE_TIMEOUT_SECONDS", "BLENDER_BRIDGE_TIMEOUT", "BRIDGE_TIMEOUT"],
        DEFAULT_TIMEOUT,
    )


def get_bridge_ping_timeout_seconds() -> float:
    return _float_from_env(
        ["BRIDGE_PING_TIMEOUT_SECONDS"],
        DEFAULT_PING_TIMEOUT,
    )


class HttpBridgeHandler:
    """HTTP bridge handler that forwards bridge routes to a Blender addon listener."""

    def __init__(self, base_url: str, timeout: float | None = None, max_attempts: int = 2) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout if timeout is not None else get_bridge_timeout_seconds()
        self.max_attempts = max(1, max_attempts)

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
        attempt = 0
        while attempt < self.max_attempts:
            attempt += 1
            try:
                with request.urlopen(req, timeout=self.timeout) as resp:
                    text = resp.read().decode("utf-8")
                    if not text:
                        return err(
                            BRIDGE_BAD_RESPONSE,
                            "No response body",
                            {"attempts": attempt},
                        )
                    try:
                        parsed = json.loads(text)
                    except json.JSONDecodeError as decode_exc:
                        return err(
                            BRIDGE_BAD_RESPONSE,
                            "Invalid JSON response",
                            {"exception": str(decode_exc), "attempts": attempt},
                        )
                    if "request_id" not in parsed:
                        parsed["request_id"] = req_id
                    return parsed
            except error.HTTPError as exc:
                return err(
                    BRIDGE_BAD_RESPONSE,
                    f"{exc.code}: {exc.reason}",
                    {"exception": str(exc), "attempts": attempt},
                )
            except error.URLError as exc:
                reason = getattr(exc, "reason", exc)
                is_timeout = isinstance(reason, (TimeoutError, socket.timeout))
                code = BRIDGE_TIMEOUT if is_timeout else BRIDGE_UNREACHABLE
                if attempt < self.max_attempts and code in {BRIDGE_TIMEOUT, BRIDGE_UNREACHABLE}:
                    continue
                return err(
                    code,
                    str(reason),
                    {"exception": str(reason), "attempts": attempt},
                )
            except socket.timeout as exc:
                if attempt < self.max_attempts:
                    continue
                return err(BRIDGE_TIMEOUT, "Bridge timeout", {"exception": str(exc), "attempts": attempt})
            except Exception as exc:  # noqa: BLE001
                if attempt < self.max_attempts:
                    continue
                return err(
                    BRIDGE_UNREACHABLE,
                    "Bridge error",
                    {"exception": str(exc), "attempts": attempt},
                )


def _resolve_bridge_url_from_env(force_enabled: bool = False) -> Optional[str]:
    """Return a bridge URL from env, with sensible defaults when enabled."""
    explicit = resolve_bridge_url()
    if explicit:
        return explicit

    enabled = resolve_bridge_enabled() or force_enabled
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
    timeout = get_bridge_timeout_seconds()
    return HttpBridgeHandler(base, timeout=timeout)
