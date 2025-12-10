from __future__ import annotations

import math
from typing import Any, Dict

import bpy  # type: ignore


def _response(ok: bool, data: Dict[str, Any] | None = None, error: str | None = None) -> Dict[str, Any]:
    return {"ok": ok, "data": data or {}, "error": error}


def execute_action(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action")
    params = payload.get("params", {}) or {}
    try:
        if action == "create_cube":
            return handle_create_cube(params)
        if action == "move_object":
            return handle_move_object(params)
        if action == "assign_material":
            return handle_assign_material(params)
        if action == "apply_modifier":
            return handle_apply_modifier(params)
        return _response(False, error=f"Unknown action '{action}'")
    except Exception as exc:  # noqa: BLE001
        return _response(False, error=str(exc))


def handle_create_cube(params: Dict[str, Any]) -> Dict[str, Any]:
    name = params.get("name") or "Cube"
    size = float(params.get("size", 1.0))
    half = size / 2.0
    verts = [
        (-half, -half, -half),
        (-half, -half, half),
        (-half, half, -half),
        (-half, half, half),
        (half, -half, -half),
        (half, -half, half),
        (half, half, -half),
        (half, half, half),
    ]
    faces = [
        (0, 1, 3, 2),
        (4, 6, 7, 5),
        (0, 4, 5, 1),
        (2, 3, 7, 6),
        (1, 5, 7, 3),
        (0, 2, 6, 4),
    ]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return _response(True, {"name": obj.name, "size": size})


def handle_move_object(params: Dict[str, Any]) -> Dict[str, Any]:
    name = params.get("name")
    translation = params.get("translation", {}) or {}
    if not name:
        return _response(False, error="Missing object name")
    obj = bpy.data.objects.get(name)
    if obj is None:
        return _response(False, error=f"Object '{name}' not found")
    dx = float(translation.get("x", 0.0))
    dy = float(translation.get("y", 0.0))
    dz = float(translation.get("z", 0.0))
    obj.location.x += dx
    obj.location.y += dy
    obj.location.z += dz
    return _response(True, {"name": obj.name, "location": list(obj.location)})


def handle_assign_material(params: Dict[str, Any]) -> Dict[str, Any]:
    obj_name = params.get("object")
    material_name = params.get("material")
    color = params.get("color", [1.0, 1.0, 1.0]) or [1.0, 1.0, 1.0]
    if not obj_name or not material_name:
        return _response(False, error="Missing object or material name")
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        return _response(False, error=f"Object '{obj_name}' not found")
    mat = bpy.data.materials.get(material_name)
    if mat is None:
        mat = bpy.data.materials.new(material_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        r = float(color[0]) if len(color) > 0 else 1.0
        g = float(color[1]) if len(color) > 1 else 1.0
        b = float(color[2]) if len(color) > 2 else 1.0
        principled.inputs["Base Color"].default_value = (r, g, b, 1.0)
    if len(obj.data.materials) == 0:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat
    return _response(True, {"object": obj.name, "material": mat.name, "color": color})


def handle_apply_modifier(params: Dict[str, Any]) -> Dict[str, Any]:
    obj_name = params.get("object")
    mod_type = params.get("type")
    settings = params.get("settings", {}) or {}
    if not obj_name or not mod_type:
        return _response(False, error="Missing object or modifier type")
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        return _response(False, error=f"Object '{obj_name}' not found")
    mod = obj.modifiers.new(name=f"{mod_type}_auto", type=str(mod_type).upper())
    for key, value in settings.items():
        if hasattr(mod, key):
            try:
                setattr(mod, key, value)
            except Exception:
                continue
    return _response(True, {"object": obj.name, "modifier": mod.name, "type": mod.type})
