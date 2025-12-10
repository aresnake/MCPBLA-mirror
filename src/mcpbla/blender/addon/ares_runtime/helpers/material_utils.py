from __future__ import annotations

from typing import Any, Dict, List

try:
    import bpy  # type: ignore
except Exception:  # pragma: no cover
    bpy = None


def ensure_material(name: str):
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat


def ensure_principled(mat):
    if bpy is None:
        return None
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        return principled
    return nodes.new(type="ShaderNodeBsdfPrincipled")


def ensure_material_output(mat):
    if bpy is None:
        return None
    nodes = mat.node_tree.nodes
    outputs = [n for n in nodes if n.type == "OUTPUT_MATERIAL"]
    if outputs:
        return outputs[0]
    return nodes.new(type="ShaderNodeOutputMaterial")


def link_principled_to_output(mat, principled):
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    output = ensure_material_output(mat)
    if principled is None or output is None:
        return {"ok": False, "error": "Missing nodes for linking"}
    try:
        bsdf_out = principled.outputs.get("BSDF")
        surface_in = output.inputs.get("Surface")
        if bsdf_out and surface_in:
            mat.node_tree.links.new(bsdf_out, surface_in)
        return {"ok": True, "data": {"output": output.name}}
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": str(exc)}


def assign_material_to_object(obj, mat):
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    if obj is None or mat is None:
        return {"ok": False, "error": "Object or material is None"}
    if len(obj.data.materials) == 0:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat
    return {"ok": True, "data": {"object": obj.name, "material": mat.name}}


def set_base_color(principled, rgb: List[float]):
    if bpy is None:
        return {"ok": False, "error": "bpy unavailable"}
    if principled is None:
        return {"ok": False, "error": "Principled node missing"}
    r = float(max(0.0, min(1.0, rgb[0] if len(rgb) > 0 else 1.0)))
    g = float(max(0.0, min(1.0, rgb[1] if len(rgb) > 1 else 1.0)))
    b = float(max(0.0, min(1.0, rgb[2] if len(rgb) > 2 else 1.0)))
    principled.inputs["Base Color"].default_value = (r, g, b, 1.0)
    return {"ok": True, "data": {"color": [r, g, b]}}
