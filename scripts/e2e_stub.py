from __future__ import annotations

import sys
import time
import httpx


BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 2.0
RETRY_SECONDS = 5.0


def fail(msg: str) -> int:
    print(msg)
    return 1


def main() -> int:
    start = time.time()
    health_ok = False
    while time.time() - start < RETRY_SECONDS:
        try:
            resp = httpx.get(f"{BASE_URL}/health", timeout=TIMEOUT)
            if resp.status_code == 200 and resp.json().get("status") == "ok":
                health_ok = True
                break
        except Exception:
            pass
        time.sleep(0.2)
    if not health_ok:
        return fail("Health check failed; is the server running?")

    try:
        resp = httpx.post(
            f"{BASE_URL}/tools/create_cube_stub/invoke_v2",
            json={"arguments": {}},
            timeout=TIMEOUT,
        )
        body = resp.json()
        if resp.status_code != 200 or not body.get("ok"):
            return fail("create_cube_stub failed")
    except Exception as exc:  # noqa: BLE001
        return fail(f"create_cube_stub error: {exc}")

    try:
        resp = httpx.post(
            f"{BASE_URL}/tools/move_object_stub/invoke_v2",
            json={"arguments": {"object_name": "Cube", "delta": [0, 0, 2]}},
            timeout=TIMEOUT,
        )
        body = resp.json()
        if resp.status_code != 200 or not body.get("ok"):
            return fail("move_object_stub failed")
    except Exception as exc:  # noqa: BLE001
        return fail(f"move_object_stub error: {exc}")

    try:
        resp = httpx.post(
            f"{BASE_URL}/tools/get_scene_state/invoke_v2",
            json={"arguments": {}},
            timeout=TIMEOUT,
        )
        body = resp.json()
        if resp.status_code != 200 or not body.get("ok"):
            return fail("get_scene_state failed")
        print("Scene state:", body.get("result"))
    except Exception as exc:  # noqa: BLE001
        return fail(f"get_scene_state error: {exc}")

    print("E2E stub flow passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
