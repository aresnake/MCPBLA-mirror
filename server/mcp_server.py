from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from server.bridge import scenegraph_live
from server.tools.base import Tool
from server.tools.registry import build_tool_registry
from server.utils.config import ServerConfig, load_config
from server.utils.logging_utils import setup_logging


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


def create_app(config: ServerConfig | None = None) -> FastAPI:
    cfg = config or load_config()
    logger = setup_logging(cfg.log_level, __name__)

    app = FastAPI(title="MCP Blender Orchestrator", version="0.2.0")

    tools: Dict[str, Tool] = build_tool_registry(cfg.workspace_root)

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

    @app.post("/blender/scene_snapshot")
    async def ingest_scene_snapshot(snapshot: SceneSnapshotModel) -> Dict[str, Any]:
        if not snapshot.session_id:
            raise HTTPException(status_code=400, detail="session_id is required")
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

    return app


app = create_app()
