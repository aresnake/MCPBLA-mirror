from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SceneSnapshot:
    """Lightweight representation of a Blender scene snapshot."""

    session_id: str
    objects: List[Dict[str, Any]]
    metadata: Dict[str, Any]


_REGISTRY: Dict[str, SceneSnapshot] = {}
_LAST_SESSION_ID: Optional[str] = None


def store_snapshot(snapshot: SceneSnapshot) -> None:
    """Store or replace the latest snapshot for a session."""
    _REGISTRY[snapshot.session_id] = snapshot
    global _LAST_SESSION_ID
    _LAST_SESSION_ID = snapshot.session_id


def get_snapshot(session_id: str) -> Optional[SceneSnapshot]:
    """Retrieve the latest snapshot for a session."""
    return _REGISTRY.get(session_id)


def get_last_snapshot() -> Optional[SceneSnapshot]:
    """Retrieve the most recently stored snapshot regardless of session."""
    if _LAST_SESSION_ID:
        return _REGISTRY.get(_LAST_SESSION_ID)
    return None


def clear_registry() -> None:
    """Utility for tests to reset state."""
    _REGISTRY.clear()
    global _LAST_SESSION_ID
    _LAST_SESSION_ID = None


class ScenegraphLive:
    """Maintains a lightweight in-memory scenegraph representation."""

    def __init__(self) -> None:
        self._state: Dict[str, Any] = {}

    def apply(self, actions: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder: merge incoming actions into state
        self._state.update(actions)
        return self._state

    def snapshot(self) -> Dict[str, Any]:
        return dict(self._state)

    def to_scene_snapshot(self, session_id: str) -> SceneSnapshot:
        """Convert internal state to a SceneSnapshot for a session."""
        return SceneSnapshot(session_id=session_id, objects=self._state.get("objects", []), metadata=self._state.get("metadata", {}))

    @staticmethod
    def serialize_snapshot(snapshot: SceneSnapshot) -> Dict[str, Any]:
        return asdict(snapshot)
