from __future__ import annotations

import logging
import os

_warned_enabled = False
_warned_url = False


def _as_bool(value: str | None) -> bool:
    if value is None:
        return False
    return str(value).lower() in {"1", "true", "yes", "on"}


def resolve_bridge_enabled(explicit: bool | None = None) -> bool:
    global _warned_enabled

    if explicit is not None:
        return bool(explicit)

    primary = os.getenv("BRIDGE_ENABLED")
    if primary is not None:
        return _as_bool(primary)

    legacy = os.getenv("BLENDER_BRIDGE_ENABLED")
    if legacy is not None:
        if not _warned_enabled:
            logging.warning("BLENDER_BRIDGE_ENABLED is deprecated; use BRIDGE_ENABLED")
            _warned_enabled = True
        return _as_bool(legacy)

    return False


def resolve_bridge_url() -> str | None:
    global _warned_url

    primary = os.getenv("BRIDGE_URL")
    if primary and primary.strip():
        return primary.strip()

    legacy = os.getenv("BLENDER_BRIDGE_URL")
    if legacy and legacy.strip():
        if not _warned_url:
            logging.warning("BLENDER_BRIDGE_URL is deprecated; use BRIDGE_URL")
            _warned_url = True
        return legacy.strip()

    return None
