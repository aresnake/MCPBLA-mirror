from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from server.bridge.messages import EventMessage


class BridgeEventEmitter:
    """Simple event emitter to broadcast bridge events."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[[EventMessage], Any]]] = {}

    def subscribe(self, event: str, handler: Callable[[EventMessage], Any]) -> None:
        self._subscribers.setdefault(event, []).append(handler)

    def emit(self, event: str, data: Dict[str, Any], correlation_id: Optional[str] = None) -> None:
        msg = EventMessage(event=event, data=data, correlation_id=correlation_id or EventMessage(event, data).correlation_id)
        for handler in self._subscribers.get(event, []):
            handler(msg)


class EventBus:
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Any]] = {}

    def subscribe(self, event_name: str, handler) -> None:
        self._subscribers.setdefault(event_name, []).append(handler)

    def emit(self, event_name: str, data: Dict[str, Any]) -> None:
        for h in self._subscribers.get(event_name, []):
            h(event_name, data)


EVENT_BUS = EventBus()
