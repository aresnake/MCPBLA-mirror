from __future__ import annotations

import sys
import time

import httpx


BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 2.0
RETRY_SECONDS = 5.0
POLL_INTERVAL = 0.25


def fail(msg: str) -> int:
    print(msg)
    return 1


def main() -> int:
    start = time.time()
    while time.time() - start < RETRY_SECONDS:
        try:
            resp = httpx.get(f"{BASE_URL}/health", timeout=TIMEOUT)
            if resp.status_code == 200 and resp.json().get("status") == "ok":
                break
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)
    else:
        return fail("Health check failed; start the MCP server.")

    try:
        status_resp = httpx.get(f"{BASE_URL}/status", timeout=TIMEOUT)
        status_body = status_resp.json()
    except Exception as exc:  # noqa: BLE001
        return fail(f"Could not read /status: {exc}")

    if status_body.get("ok") is not True:
        return fail("Status not ok.")
    bridge = status_body.get("bridge", {}) or {}
    if not bridge.get("enabled"):
        return fail("Bridge is not enabled; set BRIDGE_ENABLED=true and BRIDGE_URL.")
    if not bridge.get("configured"):
        return fail("Bridge enabled but not configured; set BRIDGE_URL.")
    if not bridge.get("reachable"):
        return fail("Bridge unreachable: start Blender bridge or fix BRIDGE_URL.")

    try:
        resp = httpx.post(
            f"{BASE_URL}/tools/create_cube/invoke_v2",
            json={"arguments": {"name": "E2E_Cube", "size": 1.0}},
            timeout=TIMEOUT,
        )
        body = resp.json()
        if resp.status_code != 200 or not body.get("ok"):
            return fail("create_cube failed")
    except Exception as exc:  # noqa: BLE001
        return fail(f"create_cube error: {exc}")

    move_payload = {"arguments": {"name": "E2E_Cube", "translation": {"x": 0, "y": 0, "z": 2}}}
    try:
        resp = httpx.post(f"{BASE_URL}/tools/move_object/invoke_v2", json=move_payload, timeout=TIMEOUT)
        body = resp.json()
        if resp.status_code != 200 or not body.get("ok"):
            return fail("move_object failed")
    except Exception as exc:  # noqa: BLE001
        return fail(f"move_object error: {exc}")

    try:
        resp = httpx.post(f"{BASE_URL}/tools/get_scene_state/invoke_v2", json={"arguments": {}}, timeout=TIMEOUT)
        body = resp.json()
        if resp.status_code != 200 or not body.get("ok"):
            return fail("get_scene_state failed")
        print("Scene state:", body.get("result"))
    except Exception as exc:  # noqa: BLE001
        return fail(f"get_scene_state error: {exc}")

    print("E2E bridge flow passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
