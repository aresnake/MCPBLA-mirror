from __future__ import annotations

from typing import Any


class OpenAIHost:
    """Stub adapter for OpenAI models."""

    name = "openai"

    def generate(self, prompt: str, **kwargs: Any) -> str:
        # TODO: integrate OpenAI SDK
        return "OpenAIHost stub – integration pending"
