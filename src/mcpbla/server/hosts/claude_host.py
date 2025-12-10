from __future__ import annotations

from typing import Any


class ClaudeHost:
    """Stub adapter for Anthropic Claude."""

    name = "claude"

    def generate(self, prompt: str, **kwargs: Any) -> str:
        # TODO: integrate Anthropic SDK
        return "ClaudeHost stub – integration pending"
