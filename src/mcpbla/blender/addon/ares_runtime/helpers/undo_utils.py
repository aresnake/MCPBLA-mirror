from __future__ import annotations


def push_undo_step(label: str):
    try:
        import bpy  # type: ignore

        bpy.ops.ed.undo_push(message=label)
    except Exception:
        return
