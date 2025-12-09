from __future__ import annotations

from typing import Any, Callable, Dict, Optional


class RouterV2:
    """Configurable router for bridge v2 with retry support."""

    def __init__(self, handler: Optional[Callable[[str, dict], Any]] = None, max_retries: int = 1) -> None:
        self.handler = handler
        self.max_retries = max_retries

    def route(self, route: str, payload: dict) -> Any:
        if not self.handler:
            raise RuntimeError("RouterV2 handler not configured")
        attempts = 0
        last_exc: Optional[Exception] = None
        while attempts <= self.max_retries:
            try:
                return self.handler(route, payload)
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                attempts += 1
                if attempts > self.max_retries:
                    raise
        if last_exc:
            raise last_exc
