from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class BridgeLifecycleState:
    configured: bool = False
    reachable: bool = False
    last_seen: Optional[float] = None
    last_error: Optional[Dict[str, str]] = None

    def snapshot(self) -> Dict[str, object]:
        return {
            "configured": self.configured,
            "reachable": self.reachable,
            "last_seen": self.last_seen,
            "last_error": self.last_error,
        }


_STATE = BridgeLifecycleState()


def reset_state() -> None:
    global _STATE
    _STATE = BridgeLifecycleState()


def set_configured(configured: bool) -> None:
    _STATE.configured = configured
    if not configured:
        _STATE.reachable = False


def record_success() -> None:
    _STATE.reachable = True
    _STATE.last_seen = time.time()
    _STATE.last_error = None


def record_error(code: str, message: str) -> None:
    _STATE.reachable = False
    _STATE.last_error = {"code": code, "message": message}


def get_state() -> Dict[str, object]:
    return _STATE.snapshot()
