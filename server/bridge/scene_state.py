from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


# Simple in-memory scene representation
SCENE_STATE: Dict[str, Any] = {"objects": {}}


def reset_scene_state() -> None:
    SCENE_STATE["objects"] = {}


def get_scene_state() -> Dict[str, Any]:
    return deepcopy(SCENE_STATE)


def upsert_object(name: str, *, type: str = "MESH", location: List[float] | None = None, material: str | None = None) -> Dict[str, Any]:
    if location is None:
        location = [0.0, 0.0, 0.0]
    obj = SCENE_STATE["objects"].get(
        name,
        {
            "name": name,
            "type": type,
            "location": location,
            "material": material,
            "fx": [],
        },
    )
    obj["name"] = name
    obj["type"] = type
    obj["location"] = location
    obj["material"] = material if material is not None else obj.get("material")
    obj.setdefault("fx", [])
    SCENE_STATE["objects"][name] = obj
    return deepcopy(obj)


def _require_object(name: str) -> Dict[str, Any]:
    if name not in SCENE_STATE["objects"]:
        raise ValueError(f"Object '{name}' not found in scene")
    return SCENE_STATE["objects"][name]


def move_object(name: str, delta: List[float]) -> Dict[str, Any]:
    obj = _require_object(name)
    current = obj.get("location", [0.0, 0.0, 0.0])
    if len(current) != 3 or len(delta) != 3:
        raise ValueError("Location and delta must be length-3 lists")
    new_loc = [current[i] + float(delta[i]) for i in range(3)]
    obj["location"] = new_loc
    return deepcopy(obj)


def assign_material(name: str, material: str) -> Dict[str, Any]:
    obj = _require_object(name)
    obj["material"] = material
    return deepcopy(obj)


def apply_fx(name: str, fx: str) -> Dict[str, Any]:
    obj = _require_object(name)
    fx_list = obj.setdefault("fx", [])
    if fx not in fx_list:
        fx_list.append(fx)
    return deepcopy(obj)
