from __future__ import annotations

from typing import Any


class AssetsProviderStub:
    name = "assets_stub"

    def fetch(self, query: str, **kwargs: Any) -> Any:
        return {"query": query, "result": "stubbed-asset"}
