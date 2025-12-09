from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class BlenderSession:
    """Tracks a connection to a Blender instance."""

    session_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    scene_snapshot: Dict[str, Any] = field(default_factory=dict)

    def update_snapshot(self, snapshot: Dict[str, Any]) -> None:
        self.scene_snapshot = snapshot

    def info(self) -> Dict[str, Any]:
        return {"session_id": self.session_id, "meta": self.metadata}
