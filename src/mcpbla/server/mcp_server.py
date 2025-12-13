from __future__ import annotations

import os
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from mcpbla.server.bridge.env import resolve_bridge_enabled, resolve_bridge_url
from mcpbla.server.bridge.http_bridge import HttpBridgeHandler
from mcpbla.server.bridge.messages import ActionMessage
from mcpbla.server.bridge.events import EVENT_BUS
from mcpbla.server.tools.base import Tool
from mcpbla.server.tools.registry import build_tool_registry
from mcpbla.server.utils.config import ServerConfig, load_config
from mcpbla.server.utils.logging_utils import setup_logging


class ToolMetadata(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]


class ToolInvokeRequest(BaseModel):
    arguments: Dict[str, Any] = Field(default_factory=dict)


class SceneSnapshotModel(BaseModel):
    session_id: str
    objects: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BridgeEventModel(BaseModel):
    event: str
    data: Dict[str, Any] = Field(default_factory=dict)
    type: str | None = None
    correlation_id: str | None = None


_SCENEGRAPH_SUBSCRIBED = False


def create_app(config: ServerConfig | None = None, bridge_enabled: bool | None = None) -> FastAPI:
    cfg = config or load_config()
    bridge_is_enabled = resolve_bridge_enabled(explicit=bridge_enabled)
    logger = setup_logging(cfg.log_level, __name__)

    app = FastAPI(title="MCP Blender Orchestrator", version="0.2.0")

    tools: Dict[str, Tool] = build_tool_registry(cfg.workspace_root, bridge_enabled=bridge_is_enabled)

    scenegraph_live = None

    if bridge_is_enabled:
        from mcpbla.server.bridge import scenegraph_live as bridge_scenegraph_live
        from mcpbla.server.bridge.scenegraph import SCENEGRAPH
        from mcpbla.server.bridge.startup import configure_bridge_from_env

        # Optionally wire real bridge handler if explicitly enabled via env.
        configure_bridge_from_env(enabled_override=bridge_is_enabled)

        global _SCENEGRAPH_SUBSCRIBED
        if not _SCENEGRAPH_SUBSCRIBED:
            EVENT_BUS.subscribe("*", SCENEGRAPH.on_event)
            _SCENEGRAPH_SUBSCRIBED = True

        scenegraph_live = bridge_scenegraph_live
    else:
        logger.info("BRIDGE_ENABLED is false; running in stub mode without the Blender bridge.")

    @app.get("/health")
    async def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.get("/tools", response_model=List[ToolMetadata])
    async def list_tools() -> List[ToolMetadata]:
        return [
            ToolMetadata(name=tool.name, description=tool.description, input_schema=tool.input_schema)
            for tool in tools.values()
        ]

    @app.post("/tools/{tool_name}/invoke")
    async def invoke_tool(tool_name: str, payload: ToolInvokeRequest) -> Dict[str, Any]:
        tool = tools.get(tool_name)
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        try:
            result = await tool.handler(payload.arguments)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Tool execution failed")
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        return {"tool": tool_name, "result": result}

    @app.post("/tools/{tool_name}/invoke_v2")
    async def invoke_tool_v2(tool_name: str, payload: ToolInvokeRequest) -> Dict[str, Any]:
        tool = tools.get(tool_name)
        if not tool:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "code": "NOT_FOUND",
                    "error": "Tool not found",
                    "details": {"tool_name": tool_name},
                },
            )
        try:
            return await tool.handler(payload.arguments)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Tool execution failed")
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "code": "INTERNAL_ERROR",
                    "error": "Tool execution failed",
                    "details": {"exception": str(exc)},
                },
            )

    @app.post("/blender/scene_snapshot")
    async def ingest_scene_snapshot(snapshot: SceneSnapshotModel) -> Dict[str, Any]:
        if not snapshot.session_id:
            raise HTTPException(status_code=400, detail="session_id is required")

        if not bridge_is_enabled or scenegraph_live is None:
            stub_tool = tools.get("scene_snapshot_stub")
            if stub_tool is None:
                raise HTTPException(status_code=503, detail="Bridge disabled")
            try:
                snapshot_data = snapshot.model_dump() if hasattr(snapshot, "model_dump") else snapshot.dict()
                return await stub_tool.handler(snapshot_data)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Stub scene snapshot handling failed")
                raise HTTPException(status_code=500, detail=str(exc)) from exc

        scene_snapshot = scenegraph_live.SceneSnapshot(
            session_id=snapshot.session_id, objects=snapshot.objects, metadata=snapshot.metadata
        )
        scenegraph_live.store_snapshot(scene_snapshot)
        return {
            "status": "stored",
            "session_id": snapshot.session_id,
            "objects_count": len(snapshot.objects),
            "metadata": snapshot.metadata,
        }

    @app.post("/bridge/event")
    async def ingest_event(event: BridgeEventModel) -> Dict[str, Any]:
        EVENT_BUS.emit(event.event, event.data)
        return {"ok": True, "event": event.event, "correlation_id": event.correlation_id}

    @app.get("/bridge/status")
    async def bridge_status() -> Dict[str, Any]:
        enabled = resolve_bridge_enabled()
        url = resolve_bridge_url()
        configured = bool(enabled and url)
        reachable = False
        last_error = None

        if not enabled:
            return {
                "enabled": False,
                "url": url,
                "configured": False,
                "reachable": False,
                "last_error": None,
            }

        if not configured:
            return {
                "enabled": True,
                "url": None,
                "configured": False,
                "reachable": False,
                "last_error": "BRIDGE_URL is missing",
            }

        try:
            handler = HttpBridgeHandler(url, timeout=1.0)
            resp = handler("system.ping", ActionMessage(route="system.ping", payload={}).to_dict())
            reachable = bool(isinstance(resp, dict) and resp.get("ok"))
            if not reachable:
                err = resp.get("error") if isinstance(resp, dict) else None
                if isinstance(err, dict):
                    last_error = err.get("message") or str(err)
                elif err:
                    last_error = str(err)
                else:
                    last_error = "Bridge unreachable"
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)

        return {
            "enabled": True,
            "url": url,
            "configured": True,
            "reachable": reachable,
            "last_error": last_error,
        }

    return app


app = create_app()

def main() -> None:
    """Run the MCP Blender Orchestrator HTTP server via uvicorn.

    This is used both for local CLI runs:

        python -m mcpbla.server.mcp_server

    and for MCP clients (Claude Desktop / Claude Code) that start the
    server by calling this module as a script.
    """
    import os
    import uvicorn

    # Same env vars que ce qu’on utilise déjà dans la doc / scripts
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port_str = os.getenv("MCP_PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        port = 8000

    uvicorn.run(
        "mcpbla.server.mcp_server:app",
        host=host,
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
