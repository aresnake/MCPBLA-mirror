from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def generate_correlation_id() -> str:
    return str(uuid.uuid4())


@dataclass
class ActionMessage:
    route: str
    payload: Dict[str, Any]
    correlation_id: str = field(default_factory=generate_correlation_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "route": self.route,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
        }


@dataclass
class EventMessage:
    event: str
    data: Dict[str, Any]
    correlation_id: str = field(default_factory=generate_correlation_id)

    def to_dict(self) -> Dict[str, Any]:
        return {"event": self.event, "data": self.data, "correlation_id": self.correlation_id}


@dataclass
class ErrorMessage:
    error: str
    detail: Optional[str] = None
    correlation_id: str = field(default_factory=generate_correlation_id)

    def to_dict(self) -> Dict[str, Any]:
        return {"error": self.error, "detail": self.detail, "correlation_id": self.correlation_id}


@dataclass
class ActionBatch:
    actions: List[ActionMessage]
    atomic: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {"atomic": self.atomic, "actions": [a.to_dict() for a in self.actions]}


@dataclass
class EventACKMessage:
    event: str
    correlation_id: str
    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {"event": self.event, "correlation_id": self.correlation_id, "data": self.data}


@dataclass
class ActionACKMessage:
    action: str
    correlation_id: str
    status: str
    data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "data": self.data or {},
        }
