from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcpbla.server.bridge.scene_delta import compute_delta


class SceneGraphLiveV3:
    def __init__(self) -> None:
        self.objects: Dict[str, Dict[str, Any]] = {}
        self.materials: Dict[str, Dict[str, Any]] = {}
        self.modifiers: Dict[str, Dict[str, Any]] = {}
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.last_snapshot: Optional[Dict[str, Any]] = None

    def apply_snapshot(self, snapshot: Dict[str, Any]) -> None:
        self.objects = {obj["name"]: obj for obj in snapshot.get("objects", []) if "name" in obj}
        self.materials = {mat.get("name", f"mat_{i}"): mat for i, mat in enumerate(snapshot.get("materials", []))}
        self.modifiers = {mod.get("id", f"mod_{i}"): mod for i, mod in enumerate(snapshot.get("modifiers", []))}
        self.nodes = {node.get("id", f"node_{i}"): node for i, node in enumerate(snapshot.get("nodes", []))}
        self.last_snapshot = snapshot

    def apply_delta(self, delta: Dict[str, Any]) -> None:
        for obj in delta.get("objects_added", []):
            if isinstance(obj, dict) and "name" in obj:
                self.objects[obj["name"]] = obj
        for name in delta.get("objects_removed", []):
            if name in self.objects:
                self.objects.pop(name, None)
        for obj in delta.get("objects_changed", []):
            if isinstance(obj, dict) and "name" in obj:
                self.objects[obj["name"]] = obj

    def on_event(self, event_name: str, payload: Dict[str, Any]) -> None:
        if event_name == "object.created":
            name = payload.get("name")
            if name:
                self.objects[name] = {**self.objects.get(name, {}), "name": name, "event": "created"}
        elif event_name == "object.transformed":
            name = payload.get("name")
            if name and name in self.objects:
                self.objects[name].update({"location": payload.get("location")})
        elif event_name == "material.updated":
            name = payload.get("material") or payload.get("name")
            if name:
                self.materials[name] = {**self.materials.get(name, {}), "name": name, "event": "updated"}
        elif event_name == "modifier.added":
            obj = payload.get("object")
            mod = payload.get("modifier")
            if obj and mod:
                key = f"{obj}:{mod}"
                self.modifiers[key] = {"object": obj, "modifier": mod}
        elif event_name == "node.added":
            mat = payload.get("material")
            node_type = payload.get("type")
            node_name = payload.get("node")
            key = node_name or f"{mat}:{node_type}"
            self.nodes[key] = {"material": mat, "type": node_type, "node": node_name}
        elif event_name == "scene.snapshot.delta":
            delta = payload.get("delta", {})
            self.apply_delta(delta)
        elif event_name == "scene.snapshot.completed":
            snap = payload.get("snapshot")
            if snap:
                self.apply_snapshot(snap)

    def describe(self) -> Dict[str, Any]:
        return {
            "objects": list(self.objects.values()),
            "materials": list(self.materials.values()),
            "modifiers": list(self.modifiers.values()),
            "nodes": list(self.nodes.values()),
            "last_snapshot": self.last_snapshot,
        }

    def find(self, query: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for collection in (self.objects, self.materials, self.modifiers, self.nodes):
            for item in collection.values():
                if query.lower() in str(item).lower():
                    results.append(item)
        return results

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        return self.objects.get(key) or self.materials.get(key) or self.modifiers.get(key) or self.nodes.get(key)


SCENEGRAPH = SceneGraphLiveV3()

