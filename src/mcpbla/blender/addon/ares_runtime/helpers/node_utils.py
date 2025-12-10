from __future__ import annotations

from typing import Any, Dict

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None


def safe_new_node(material, node_type: str):
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    if material is None:
        return {"ok": False, "error": "Material is None"}
    material.use_nodes = True
    nodes = material.node_tree.nodes
    try:
        node = nodes.new(type=node_type)
        return node
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": str(exc)}


def link_nodes(mat, from_node, from_socket_name: str, to_node, to_socket_name: str):
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    if mat is None or from_node is None or to_node is None:
        return {"ok": False, "error": "Invalid nodes"}
    try:
        out_socket = from_node.outputs.get(from_socket_name)
        in_socket = to_node.inputs.get(to_socket_name)
        if not out_socket or not in_socket:
            return {"ok": False, "error": "Sockets not found"}
        mat.node_tree.links.new(out_socket, in_socket)
        return {"ok": True}
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": str(exc)}
