from __future__ import annotations

from typing import Any, Dict


def ok(result: Any) -> Dict[str, Any]:
    return {"ok": True, "result": result}


def err(code: str, error: str, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {"ok": False, "code": code, "error": error, "details": details or {}}


MISSING_ARG = "MISSING_ARG"
INVALID_ARG = "INVALID_ARG"
BRIDGE_UNREACHABLE = "BRIDGE_UNREACHABLE"
INTERNAL_ERROR = "INTERNAL_ERROR"
BRIDGE_TIMEOUT = "BRIDGE_TIMEOUT"
BRIDGE_BAD_RESPONSE = "BRIDGE_BAD_RESPONSE"
