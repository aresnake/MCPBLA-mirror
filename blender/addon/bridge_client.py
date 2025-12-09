from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional
from urllib import request, error


class BridgeClient:
    def __init__(self, base_url: Optional[str] = None, timeout: float = 10.0) -> None:
        # Base URL du serveur MCP
        base = base_url or os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000")
        self.base_url = base.rstrip("/")
        self.timeout = timeout

    # -----------------------
    # HTTP helper stdlib-only
    # -----------------------
    def _request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        data = None
        headers = {"Content-Type": "application/json"}

        if method.upper() == "POST":
            data = json.dumps(payload or {}).encode("utf-8")

        req = request.Request(url, data=data, headers=headers, method=method.upper())
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body) if body else {}
        except error.HTTPError as e:  # pragma: no cover (runtime in Blender)
            raise RuntimeError(f"HTTP error {e.code} for {url}: {e.reason}") from e
        except error.URLError as e:  # pragma: no cover (runtime in Blender)
            raise RuntimeError(f"Connection error for {url}: {e.reason}") from e

    # -------------
    # Public methods
    # -------------
    def ping(self) -> Dict[str, Any]:
        # Le serveur expose un healthcheck (souvent /health)
        return self._request("GET", "/health")

    def list_tools(self) -> Dict[str, Any]:
        return self._request("GET", "/tools")

    def send_dummy_snapshot(self) -> Dict[str, Any]:
        payload = {
            "session_id": "demo_session",
            "objects": [
                {
                    "name": "Cube",
                    "type": "MESH",
                    "location": [0.0, 0.0, 0.0],
                }
            ],
            "metadata": {"source": "blender_addon_stub"},
        }
        return self._request("POST", "/blender/scene_snapshot", payload)

    def send_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Send a data-first snapshot to the MCP server."""
        return self._request("POST", "/blender/scene_snapshot", snapshot)

    def run_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"arguments": arguments or {}}
        return self._request("POST", f"/tools/{tool_name}/invoke", payload)

    def plan_task(self, instruction: str) -> Dict[str, Any]:
        payload = {"arguments": {"instruction": instruction}}
        return self._request("POST", "/tools/plan_task/invoke", payload)

    def run_task(self, instruction: str) -> Dict[str, Any]:
        payload = {"arguments": {"instruction": instruction}}
        return self._request("POST", "/tools/run_task/invoke", payload)

    def send_event(self, event_name: str, data: Dict[str, Any], correlation_id: Optional[str] = None) -> Dict[str, Any]:
        message = {"type": "event", "event": event_name, "data": data}
        if correlation_id:
            message["correlation_id"] = correlation_id
        return self._request("POST", "/bridge/event", message)
