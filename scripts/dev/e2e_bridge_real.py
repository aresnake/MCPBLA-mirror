from __future__ import annotations

import json
import os
import sys
from urllib import request, error


BASE = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000").rstrip("/")
BRIDGE = os.getenv("BLENDER_BRIDGE_URL", "").rstrip("/")


def _post(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=10.0) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def call_tool(name: str, arguments: dict) -> dict:
    return _post(f"{BASE}/tools/{name}/invoke", {"arguments": arguments})


def bridge_route(route: str, payload: dict) -> dict:
    if not BRIDGE:
        raise RuntimeError("BLENDER_BRIDGE_URL is not set; cannot contact Blender bridge.")
    return _post(f"{BRIDGE}/bridge/route", {"route": route, "payload": payload})


def main() -> int:
    if not BRIDGE:
        print("BLENDER_BRIDGE_URL not set; set it to your Blender HTTP bridge (e.g. http://127.0.0.1:8765).")
        return 1

    print(f"Using MCP server: {BASE}")
    print(f"Using Blender bridge: {BRIDGE}")

    print("Step 1: create cube via MCP tool -> bridge")
    create_resp = call_tool("create_cube", {"size": 1.0, "name": "BridgeRealCube"})
    print("create_cube:", json.dumps(create_resp, indent=2))
    if not (create_resp.get("result") or {}).get("ok"):
        raise SystemExit("create_cube failed")

    print("Step 2: move cube via MCP tool -> bridge")
    move_resp = call_tool("move_object", {"name": "BridgeRealCube", "translation": {"x": 0, "y": 0, "z": 1}})
    print("move_object:", json.dumps(move_resp, indent=2))
    if not (move_resp.get("result") or {}).get("ok"):
        raise SystemExit("move_object failed")

    print("Step 3: assign material via MCP tool -> bridge")
    mat_resp = call_tool("assign_material", {"object": "BridgeRealCube", "material": "BridgeMat", "color": [1.0, 0.2, 0.2]})
    print("assign_material:", json.dumps(mat_resp, indent=2))
    if not (mat_resp.get("result") or {}).get("ok"):
        raise SystemExit("assign_material failed")

    print("Step 4: snapshot directly from Blender bridge")
    snap = bridge_route("scene.snapshot.v2", {"session_id": "bridge_real"})
    print("scene.snapshot.v2:", json.dumps(snap, indent=2))
    if not snap.get("ok"):
        raise SystemExit("scene.snapshot.v2 failed")

    objects = (snap.get("data") or {}).get("objects", [])
    if not any(obj.get("name") == "BridgeRealCube" for obj in objects):
        raise SystemExit("BridgeRealCube not present in snapshot")

    print("Bridge real-mode cycle succeeded.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except error.URLError as exc:  # pragma: no cover
        raise SystemExit(f"HTTP error: {exc}")
