"""System-level MCP tools for Blender-Jarvis.

These tools are meant for:
- probing the Python/platform environment (system_probe_full)
- probing the Blender API/version when running inside Blender (api_probe_blender_version)
"""

from __future__ import annotations

import os
import platform
import sys
from typing import Any, Dict, List

from .base import Tool


def _async_wrapper(func):
    """Wrap sync handlers for async MCP tool compatibility."""
    async def wrapped(arguments: Dict[str, Any]) -> Any:
        return func(arguments)

    return wrapped


def _system_probe_full_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Health-check of the MCP Blender-Jarvis environment."""
    include_env = bool(arguments.get("include_env", False))
    env_keys = arguments.get("env_keys") or []

    info: Dict[str, Any] = {
        "ok": True,
        "python": {
            "version": sys.version,
            "executable": sys.executable,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "version": platform.version(),
        },
        "paths": {
            "cwd": os.getcwd(),
            "pythonpath": sys.path,
        },
    }

    if include_env:
        env_snapshot: Dict[str, str] = {}
        if env_keys:
            for key in env_keys:
                if key in os.environ:
                    env_snapshot[key] = os.environ[key]
        else:
            # Par défaut, on prend un tout petit subset safe
            for key in ("BLENDER_EXE", "BLENDER_USER_SCRIPTS", "PATH", "PYTHONPATH"):
                if key in os.environ:
                    env_snapshot[key] = os.environ[key]
        info["env"] = env_snapshot

    return info


def _api_probe_blender_version_handler(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return Blender version/build info if running inside Blender."""
    try:
        import bpy  # type: ignore
    except ImportError:
        return {
            "ok": False,
            "blender": None,
            "error": "bpy not available (server not running inside Blender)",
        }

    version = getattr(bpy.app, "version", None)
    build_hash = getattr(bpy.app, "build_hash", None)
    build_date = getattr(bpy.app, "build_date", None)

    if version is None:
        return {
            "ok": False,
            "blender": None,
            "error": "bpy.app.version not available",
        }

    major, minor, patch = version

    return {
        "ok": True,
        "blender": {
            "major": major,
            "minor": minor,
            "patch": patch,
            "build_hash": build_hash,
            "build_date": build_date,
        },
    }


def get_tools() -> List[Tool]:
    """Expose system-level tools as MCP tools."""
    return [
        Tool(
            name="system_probe_full",
            description="Health-check of the MCP Blender-Jarvis environment (Python, platform, paths, env subset).",
            input_schema={
                "type": "object",
                "properties": {
                    "include_env": {
                        "type": "boolean",
                        "description": "Include selected environment variables snapshot.",
                        "default": False,
                    },
                    "env_keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific environment variable names to include.",
                    },
                },
                "required": [],
            },
            handler=_async_wrapper(_system_probe_full_handler),
        ),
        Tool(
            name="api_probe_blender_version",
            description="Return Blender version/build information if running inside Blender.",
            input_schema={
                "type": "object",
                "properties": {},
                "required": [],
            },
            handler=_async_wrapper(_api_probe_blender_version_handler),
        ),
    ]
