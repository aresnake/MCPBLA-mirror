from __future__ import annotations

from typing import Dict, Any


class ActionApplier:
    """Applies high-level actions to the scenegraph or dispatches to Blender."""

    def apply_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: route to Blender bridge or simulate result
        return {"status": "ok", "action": action}
