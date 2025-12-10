from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8000
    workspace_root: Path = Path.cwd()
    log_level: str = "INFO"


def load_config() -> ServerConfig:
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8000"))
    workspace_root = Path(os.getenv("MCP_WORKSPACE", Path.cwd()))
    log_level = os.getenv("MCP_LOG_LEVEL", "INFO")
    return ServerConfig(host=host, port=port, workspace_root=workspace_root, log_level=log_level)
