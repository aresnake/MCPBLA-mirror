from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from server.tools.base import Tool


def _async_wrapper(func):
    async def wrapped(arguments: Dict[str, Any]) -> Any:
        return func(arguments)

    return wrapped


def _run_e2e(_: Dict[str, Any]) -> Dict[str, Any]:
    root = Path(__file__).resolve().parent.parent
    script = root / "scripts" / "e2e_studio_test.py"
    if not script.exists():
        return {"ok": False, "error": "e2e script not found"}
    try:
        proc = subprocess.Popen([sys.executable, str(script)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output, _ = proc.communicate(timeout=20)
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": str(exc)}
    return {"ok": proc.returncode == 0, "output": output}


def get_tools() -> List[Tool]:
    return [
        Tool(
            name="studio_full_test",
            description="Run the end-to-end studio test suite.",
            input_schema={"type": "object", "properties": {}},
            handler=_async_wrapper(_run_e2e),
        )
    ]
