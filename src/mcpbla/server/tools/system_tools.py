"""
System-level diagnostic tools for MCP hosts.
Provides information about environment, versions, and Blender capabilities.
"""

from __future__ import annotations
from typing import Any, Dict, List
import platform
import sys
import json

try:
    import bpy  # Blender runtime
except Exception:
    bpy = None


def _async_wrapper(func):
    async def wrapped(arguments: Dict[str, Any]) -> Any:
        return func(arguments)
    return wrapped


def _system_probe_handler(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return a full diagnostic dump of the MCP server environment."""
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "implementation": platform.python_implementation(),
        "executable": sys.executable,
        "argv": sys.argv,
        "env_ok": True,
    }


def _blender_version_handler(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return Blender version if running inside Blender, else unavailable."""
    if bpy is None:
        return {
            "blender": None,
            "ok": False,
            "error": "bpy not available (server running outside Blender)"
        }

    version = bpy.app.version  # (major, minor, patch)
    return {
        "blender": {
            "major": version[0],
            "minor": version[1],
            "patch": version[2],
        },
        "ok": True,
    }


from .base import Tool


def get_tools() -> List[Tool]:
    """Expose system-diagnostic tools."""
    return [
        Tool(
            name="system_probe_full",
            description="Return full diagnostic information about Python and host environment.",
            handler=_async_wrapper(_system_probe_handler),
        ),
        Tool(
            name="api_probe_blender_version",
            description="Return Blender version (if server is running inside Blender).",
            handler=_async_wrapper(_blender_version_handler),
        ),
    ]
