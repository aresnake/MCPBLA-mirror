from __future__ import annotations

from typing import Any


class ModelsProviderStub:
    name = "models_stub"

    def fetch(self, query: str, **kwargs: Any) -> Any:
        return {"query": query, "result": "stubbed-model"}
