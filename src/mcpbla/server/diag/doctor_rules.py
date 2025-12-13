from __future__ import annotations

from typing import Dict, Tuple, Any


def evaluate_status(status: Dict[str, Any], health_ok: bool = True) -> Tuple[bool, str | None]:
    """
    Return (passes, hint) based on server/bridge status.
    """
    if not health_ok:
        return False, "Health check failed."

    if not status or status.get("ok") is not True:
        return False, "Status not ok."

    bridge = status.get("bridge", {}) or {}
    if bridge.get("enabled") is True and bridge.get("configured") is False:
        return False, "Bridge enabled but not configured."

    if bridge.get("enabled") is True and bridge.get("configured") is True and bridge.get("reachable") is False:
        return False, "Bridge unreachable."

    return True, None
