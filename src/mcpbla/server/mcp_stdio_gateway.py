import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx


HTTP_URL = os.environ.get("MCPBLA_HTTP_URL", "http://127.0.0.1:8000").rstrip("/")
LOG_PATH = os.environ.get("MCPBLA_GATEWAY_LOG", "")


def _log(msg: str) -> None:
    if not LOG_PATH:
        return
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        ts = datetime.utcnow().isoformat() + "Z"
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{ts} {msg}\n")
    except Exception:
        pass


def _send(obj: Dict[str, Any]) -> None:
    s = json.dumps(obj, ensure_ascii=False)
    _log("OUT " + s)
    sys.stdout.write(s + "\n")
    sys.stdout.flush()


def _err(req_id: Any, code: int, message: str, data: Optional[Dict[str, Any]] = None) -> None:
    payload: Dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
    if data is not None:
        payload["error"]["data"] = data
    _send(payload)


def _ok(req_id: Any, result: Any) -> None:
    _send({"jsonrpc": "2.0", "id": req_id, "result": result})


def _http_get_tools() -> Any:
    with httpx.Client(timeout=10.0) as client:
        r = client.get(f"{HTTP_URL}/tools")
        r.raise_for_status()
        return r.json()


def _http_invoke_tool(name: str, arguments: Dict[str, Any]) -> Any:
    with httpx.Client(timeout=60.0) as client:
        r = client.post(f"{HTTP_URL}/tools/{name}/invoke", json={"arguments": arguments})
        r.raise_for_status()
        return r.json()


def _normalize_tools(tools_json: Any) -> List[Dict[str, Any]]:
    tools = tools_json.get("tools") if isinstance(tools_json, dict) else tools_json
    if not isinstance(tools, list):
        return []

    norm: List[Dict[str, Any]] = []
    for t in tools:
        if not isinstance(t, dict):
            continue
        schema = t.get("inputSchema")
        if schema is None:
            schema = t.get("input_schema") or {"type": "object", "properties": {}}

        norm.append(
            {
                "name": t.get("name", ""),
                "description": t.get("description", ""),
                "inputSchema": schema,
            }
        )
    return norm


def _as_mcp_content(result: Any) -> Dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}


def main() -> None:
    _log(f"START http_url={HTTP_URL} python={sys.executable} cwd={os.getcwd()}")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        _log("IN  " + line)

        try:
            msg = json.loads(line)
        except Exception:
            continue

        req_id = msg.get("id", None)
        method = msg.get("method", "")
        params = msg.get("params", {}) or {}

        if req_id is None:
            # notification (e.g., "initialized")
            continue

        try:
            if method == "initialize":
                _ok(
                    req_id,
                    {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "mcpbla-http-gateway", "version": "0.3.0"},
                        "capabilities": {"tools": {}, "resources": {}, "prompts": {}},
                    },
                )
                continue

            if method in ("ping", "server/ping"):
                _ok(req_id, {"ok": True})
                continue

            if method in ("shutdown", "server/shutdown"):
                _ok(req_id, {"ok": True})
                return

            if method in ("resources/list", "resources.list"):
                _ok(req_id, {"resources": []})
                continue

            if method in ("prompts/list", "prompts.list"):
                _ok(req_id, {"prompts": []})
                continue

            if method in ("tools/list", "tools.list"):
                tools = _normalize_tools(_http_get_tools())
                _ok(req_id, {"tools": tools})
                continue

            if method in ("tools/call", "tools.call"):
                name = params.get("name")
                arguments = params.get("arguments") or {}
                if not isinstance(name, str) or not name:
                    _err(req_id, -32602, "Invalid params: missing tool name")
                    continue
                if not isinstance(arguments, dict):
                    _err(req_id, -32602, "Invalid params: arguments must be an object")
                    continue

                result = _http_invoke_tool(name, arguments)
                _ok(req_id, _as_mcp_content(result))
                continue

            _err(req_id, -32601, f"Method not found: {method}")

        except httpx.HTTPError as e:
            _err(req_id, -32002, "HTTP gateway error", {"detail": str(e), "http_url": HTTP_URL})
        except Exception as e:
            _err(req_id, -32000, "Gateway internal error", {"detail": str(e)})


if __name__ == "__main__":
    main()
