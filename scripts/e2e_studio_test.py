from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
UI_DIR = ROOT / "scripts" / "ui"


def _run(cmd: list[str], timeout: int = 15) -> tuple[int, str]:
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        start = time.time()
        output_lines = []
        while proc.poll() is None:
            if time.time() - start > timeout:
                proc.kill()
                return -1, "timeout"
            line = proc.stdout.readline()
            if line:
                output_lines.append(line.strip())
        if proc.stdout:
            output_lines.extend(proc.stdout.read().splitlines())
        return proc.returncode, "\n".join(output_lines)
    except Exception as exc:  # pragma: no cover
        return -1, str(exc)


def main() -> int:
    steps = []
    def log(step: str, ok: bool, msg: str = ""):
        color_ok = "\033[92m" if ok else "\033[91m"
        steps.append(f"{color_ok}{'OK' if ok else 'FAIL'}\033[0m {step} {msg}")

    # reset scripts
    for reset in ["reset_server.ps1", "reset_bridge.ps1", "reset_blender.ps1"]:
        code, out = _run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(UI_DIR / reset)])
        log(f"run {reset}", code == 0, out)
        if code != 0:
            print("\n".join(steps))
            return 1

    # placeholder test suite (no real blender launch in CI)
    log("modeling test", True, "skipped")
    log("shading test", True, "skipped")
    log("geo nodes test", True, "skipped")
    log("animation test", True, "skipped")

    print("\n".join(steps))
    return 0


if __name__ == "__main__":
    sys.exit(main())
