from __future__ import annotations

import json
import os
from urllib import request


BASE_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000")


def _post(path: str, payload: dict) -> dict:
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=10.0) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def run():
    steps = [
        ("/tools/create_cube/invoke", {"arguments": {"size": 2.0, "name": "DemoCube"}}),
        ("/tools/move_object/invoke", {"arguments": {"name": "DemoCube", "translation": {"x": 0, "y": 0, "z": 2}}}),
        ("/tools/assign_material/invoke", {"arguments": {"object": "DemoCube", "material": "DemoMat", "color": [1, 0, 0]}}),
        ("/tools/apply_modifier/invoke", {"arguments": {"object": "DemoCube", "type": "BEVEL", "settings": {"width": 0.1}}}),
        ("/tools/get_scenegraph_snapshot/invoke", {"arguments": {}}),
    ]
    results = []
    for path, payload in steps:
        result = _post(path, payload)
        results.append({"path": path, "response": result})
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    run()
