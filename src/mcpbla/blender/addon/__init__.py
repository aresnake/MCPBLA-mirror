# SPDX-License-Identifier: MIT
from __future__ import annotations

import os
import sys
from pathlib import Path

bl_info = {
    "name": "MCPBLA",
    "author": "aresnake",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar",
    "description": "MCP Blender Bridge + Tools",
    "category": "Development",
}

def _ensure_mcpbla_importable() -> None:
    # 1) Preferred: env var points at repo root (e.g. D:\MCPBLA)
    repo = os.environ.get("MCPBLA_REPO", "").strip().strip('"')
    candidates = []
    if repo:
        candidates.append(Path(repo) / "src")

    # 2) Fallbacks (dev-friendly)
    candidates.extend([
        Path(r"D:\MCPBLA\src"),
        Path.home() / "MCPBLA" / "src",
    ])

    for p in candidates:
        try:
            p = p.resolve()
        except Exception:
            continue
        if (p / "mcpbla").is_dir():
            if str(p) not in sys.path:
                sys.path.insert(0, str(p))
            return

    # If we reach here, we couldn't locate the package.
    print("[MCPBLA] ERROR: Could not locate repo src/. Set env MCPBLA_REPO to your repo root (e.g. D:\\MCPBLA).")
    print("[MCPBLA] sys.path head:", sys.path[:8])

_ensure_mcpbla_importable()

def register():
    from . import mcp_blender_addon
    mcp_blender_addon.register()

def unregister():
    from . import mcp_blender_addon
    mcp_blender_addon.unregister()
