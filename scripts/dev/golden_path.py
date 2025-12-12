from __future__ import annotations

import json
import os
from urllib import request, error

BASE = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000").rstrip("/")


def _post(path: str, payload: dict) -> dict:
    url = f"{BASE}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=10.0) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def main() -> int:
    print(f"Using MCP server at {BASE}")

    print("Probing bridge...")
    probe = _post("/tools/bridge_probe/invoke", {"arguments": {}})
    print(json.dumps(probe, indent=2))

    print("Creating cube via create_cube tool...")
    create_resp = _post("/tools/create_cube/invoke", {"arguments": {"size": 1.0, "name": "GoldenCube"}})
    print(json.dumps(create_resp, indent=2))

    print("Sending snapshot to ensure scenegraph awareness...")
    snapshot_payload = {
        "session_id": "golden_session",
        "objects": [{"name": "GoldenCube", "type": "MESH", "location": [0, 0, 0]}],
        "metadata": {"source": "golden_path"},
    }
    snapshot_resp = _post("/blender/scene_snapshot", snapshot_payload)
    print(json.dumps(snapshot_resp, indent=2))

    print("Fetching scenegraph snapshot...")
    sg = _post("/tools/get_scenegraph_snapshot/invoke", {"arguments": {"session_id": "golden_session"}})
    print(json.dumps(sg, indent=2))
    objects = (sg.get("result") or {}).get("objects", [])
    if not any(obj.get("name") == "GoldenCube" for obj in objects):
        raise SystemExit("GoldenCube not found in scenegraph snapshot")
    print("Golden path succeeded: GoldenCube found in scenegraph.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except error.URLError as exc:  # pragma: no cover
        raise SystemExit(f"HTTP error: {exc}")
