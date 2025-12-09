from __future__ import annotations

from typing import Any


class DummyHost:
    """A no-op LLM host placeholder for local testing."""

    name = "dummy"

    def generate(self, prompt: str, **kwargs: Any) -> str:
        return f"[dummy-host] echo: {prompt}"
