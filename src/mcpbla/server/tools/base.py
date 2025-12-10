from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict


Handler = Callable[[Dict[str, Any]], Awaitable[Any]]


@dataclass
class Tool:
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Handler
