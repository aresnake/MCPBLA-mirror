from __future__ import annotations

from typing import Any, Dict

try:
    from . import actions
    from blender.addon.ares_runtime.datafirst import actions_datafirst, materials_datafirst, geometry_datafirst, nodes_datafirst
except Exception:  # pragma: no cover
    actions = None
    actions_datafirst = None
    materials_datafirst = None
    geometry_datafirst = None
    nodes_datafirst = None


def handle_route(route: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if route == "action.execute.v2":
        return actions.execute_action(payload) if actions else {"ok": False, "error": "actions not available"}
    if route == "create_cube.v2":
        params = payload.get("payload") or payload.get("params") or payload
        return actions_datafirst.create_cube(params.get("name"), params.get("size")) if actions_datafirst else {"ok": False, "error": "runtime not available"}
    if route == "move_object.v2":
        params = payload.get("payload") or payload.get("params") or payload
        return actions_datafirst.move_object(params.get("name"), params.get("translation", {})) if actions_datafirst else {"ok": False, "error": "runtime not available"}
    if route == "assign_material.v2":
        params = payload.get("payload") or payload.get("params") or payload
        return materials_datafirst.assign_material(params.get("object"), params.get("material"), params.get("color", [])) if materials_datafirst else {"ok": False, "error": "runtime not available"}
    if route == "apply_modifier.v2":
        params = payload.get("payload") or payload.get("params") or payload
        return geometry_datafirst.apply_modifier(params.get("object"), params.get("type"), params.get("settings", {})) if geometry_datafirst else {"ok": False, "error": "runtime not available"}
    if route == "node.operation.v2":
        params = payload.get("payload") or payload.get("params") or payload
        return nodes_datafirst.add_node(params.get("material"), params.get("operation", "ShaderNodeTexNoise")) if nodes_datafirst else {"ok": False, "error": "runtime not available"}
    if route == "batch.execute":
        actions_list = payload.get("actions", [])
        results = []
        for item in actions_list:
            route_name = item.get("route")
            pl = item.get("payload", {})
            results.append(handle_route(route_name, pl))
        return {"ok": all(r.get("ok") for r in results), "data": results}
    return {"ok": False, "error": f"Unknown route '{route}'"}
