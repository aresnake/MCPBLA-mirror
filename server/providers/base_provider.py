from __future__ import annotations

from typing import Protocol, Any


class Provider(Protocol):
    name: str

    def fetch(self, query: str, **kwargs: Any) -> Any:
        ...
