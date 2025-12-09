from __future__ import annotations

import json
import os
import sys

from blender.addon.bridge_client import BridgeClient


def main() -> int:
    base_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000").rstrip("/")
    print(f"[demo] Using MCP server at {base_url}")
    client = BridgeClient(base_url=base_url)
    try:
        response = client.send_dummy_snapshot()
    except Exception as exc:  # noqa: BLE001
        print(f"[demo] Failed to send dummy snapshot: {exc}", file=sys.stderr)
        return 1
    print("[demo] Snapshot response:")
    print(json.dumps(response, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
