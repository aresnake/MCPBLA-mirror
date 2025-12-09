from __future__ import annotations

from typing import Any, Dict

try:
    from . import actions
    from blender.addon.ares_runtime.datafirst import (
        actions_datafirst,
        materials_datafirst,
        geometry_datafirst,
        nodes_datafirst,
        scene_datafirst,
        render_datafirst,
    )
    from blender.addon.bridge.events import BlenderEventEmitter
    from blender.addon.bridge_client import BridgeClient
except Exception:  # pragma: no cover
    actions = None
    actions_datafirst = None
    materials_datafirst = None
    geometry_datafirst = None
    nodes_datafirst = None
    scene_datafirst = None
    render_datafirst = None
    BlenderEventEmitter = None
    BridgeClient = None


def handle_route(route: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    emitter = BlenderEventEmitter(BridgeClient()) if BlenderEventEmitter and BridgeClient else None
    if route == "action.execute.v2":
        result = actions.execute_action(payload) if actions else {"ok": False, "error": "actions not available"}
        if emitter and result.get("ok"):
            emitter.emit("action.completed", {"route": route, "result": result, "timestamp": None})
        return result
    if route == "create_cube.v2":
        params = payload.get("payload") or payload.get("params") or payload
        resp = (
            actions_datafirst.create_cube(params.get("name"), params.get("size"))
            if actions_datafirst
            else {"ok": False, "error": "runtime not available"}
        )
        if emitter and resp.get("ok"):
            emitter.emit("object.created", {"name": resp.get("data", {}).get("name")})
        return resp
    if route == "move_object.v2":
        params = payload.get("payload") or payload.get("params") or payload
        resp = (
            actions_datafirst.move_object(params.get("name"), params.get("translation", {}))
            if actions_datafirst
            else {"ok": False, "error": "runtime not available"}
        )
        if emitter and resp.get("ok"):
            emitter.emit("action.completed", {"route": route, "result": resp, "timestamp": None})
        return resp
    if route == "assign_material.v2":
        params = payload.get("payload") or payload.get("params") or payload
        resp = (
            materials_datafirst.assign_material(params.get("object"), params.get("material"), params.get("color", []))
            if materials_datafirst
            else {"ok": False, "error": "runtime not available"}
        )
        if emitter and resp.get("ok"):
            emitter.emit("material.updated", {"object": params.get("object"), "material": params.get("material")})
        return resp
    if route == "apply_modifier.v2":
        params = payload.get("payload") or payload.get("params") or payload
        resp = (
            geometry_datafirst.apply_modifier(params.get("object"), params.get("type"), params.get("settings", {}))
            if geometry_datafirst
            else {"ok": False, "error": "runtime not available"}
        )
        if emitter and resp.get("ok"):
            emitter.emit("modifier.applied", {"object": params.get("object"), "modifier": params.get("type")})
        return resp
    if route == "node.operation.v2":
        params = payload.get("payload") or payload.get("params") or payload
        resp = (
            nodes_datafirst.add_node(params.get("material"), params.get("operation", "ShaderNodeTexNoise"))
            if nodes_datafirst
            else {"ok": False, "error": "runtime not available"}
        )
        if emitter and resp.get("ok"):
            emitter.emit("node.created", {"material": params.get("material"), "type": params.get("operation")})
        return resp
    if route == "scene.snapshot.v2":
        params = payload.get("payload") or payload.get("params") or payload
        resp = scene_datafirst.snapshot(params.get("session_id")) if scene_datafirst else {"ok": False, "error": "runtime not available"}
        if emitter and resp.get("ok"):
            emitter.emit("scene.snapshot.completed", {"session_id": params.get("session_id")})
        return resp
    if route == "render.preview.v2":
        params = payload.get("payload") or payload.get("params") or payload
        resp = render_datafirst.render_preview(params or {}) if render_datafirst else {"ok": False, "error": "runtime not available"}
        if emitter and resp.get("ok"):
            emitter.emit("render.preview.completed", {"scene": resp.get("data", {}).get("scene")})
        return resp
    if route == "batch.execute":
        actions_list = payload.get("actions", [])
        results = []
        for item in actions_list:
            route_name = item.get("route")
            pl = item.get("payload", {})
            results.append(handle_route(route_name, pl))
        return {"ok": all(r.get("ok") for r in results), "data": results}
    return {"ok": False, "error": f"Unknown route '{route}'"}
