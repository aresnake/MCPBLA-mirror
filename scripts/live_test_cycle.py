from __future__ import annotations

import json
import os
from urllib import request

BASE = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000")


def _post(path: str, payload: dict) -> dict:
    url = f"{BASE}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=10.0) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def main():
    steps = [
        ("/tools/create_cube/invoke", {"arguments": {"size": 1.0, "name": "LiveCube"}}),
        ("/tools/move_object/invoke", {"arguments": {"name": "LiveCube", "translation": {"x": 0, "y": 0, "z": 1}}}),
        ("/tools/assign_material/invoke", {"arguments": {"object": "LiveCube", "material": "LiveMat", "color": [0, 1, 0]}}),
        ("/tools/apply_modifier/invoke", {"arguments": {"object": "LiveCube", "type": "BEVEL", "settings": {"width": 0.05}}}),
        ("/tools/animation_plan_v3/invoke", {"arguments": {"instruction": "rotate cube", "object": "LiveCube"}}),
        ("/tools/geo_plan_v3/invoke", {"arguments": {"instruction": "noise gn", "object": "LiveCube"}}),
        ("/tools/shader_plan_v3/invoke", {"arguments": {"instruction": "add noise node", "material": "LiveMat"}}),
        ("/tools/get_scenegraph_snapshot/invoke", {"arguments": {}}),
    ]
    results = []
    for path, payload in steps:
        results.append({path: _post(path, payload)})
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
