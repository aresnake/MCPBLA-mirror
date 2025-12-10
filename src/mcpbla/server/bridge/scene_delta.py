from __future__ import annotations

from typing import Any, Dict, List


def compute_delta(old_snapshot: Dict[str, Any], new_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    old_objs = {obj.get("name"): obj for obj in old_snapshot.get("objects", [])} if old_snapshot else {}
    new_objs = {obj.get("name"): obj for obj in new_snapshot.get("objects", [])} if new_snapshot else {}

    changed: List[str] = []
    added: List[str] = []
    removed: List[str] = []

    for name in new_objs:
        if name not in old_objs:
            added.append(name)
        elif old_objs[name] != new_objs[name]:
            changed.append(name)
    for name in old_objs:
        if name not in new_objs:
            removed.append(name)

    return {"objects_added": added, "objects_removed": removed, "objects_changed": changed}
