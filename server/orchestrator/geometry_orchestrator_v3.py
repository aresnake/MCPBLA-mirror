from __future__ import annotations

from typing import Any, Dict, List, Tuple

from server.bridge.scenegraph import SCENEGRAPH
from server.core.engines.action_engine_v3 import ActionEngineV3
from server.orchestrator.geometry_plan_v3 import GeoNodeAction, GeometryPlanV3


class GeometryOrchestratorV3:
    def __init__(self, engine: ActionEngineV3 | None = None) -> None:
        self.engine = engine or ActionEngineV3(wait_for_ack=False)

    def plan(self, instruction: str, object_name: str) -> GeometryPlanV3:
        nodes: List[GeoNodeAction] = []
        lower = instruction.lower()
        if "noise" in lower:
            nodes.append(GeoNodeAction(node_type="GeometryNodeNoiseTexture", params={"object": object_name}))
        else:
            nodes.append(GeoNodeAction(node_type="GeometryNodeSetPosition", params={"object": object_name}))
        return GeometryPlanV3(instruction=instruction, object_name=object_name, nodes=nodes)

    def execute(self, plan: GeometryPlanV3) -> Tuple[bool, List[Dict[str, Any]]]:
        results: List[Dict[str, Any]] = []
        ok_all = True
        for node in plan.nodes:
            params = {"object": plan.object_name, "operation": node.node_type, **node.params}
            res = self.engine.execute("node.operation", params)
            results.append({"node": node.node_type, "ok": res.ok, "data": res.data, "error": res.error})
            if not res.ok:
                ok_all = False
                break
        return ok_all, results

    def verify(self, plan: GeometryPlanV3) -> Dict[str, Any]:
        sg = SCENEGRAPH.describe()
        nodes = sg.get("nodes", [])
        missing = []
        for node in plan.nodes:
            if not any(n.get("type") == node.node_type and n.get("material") == plan.object_name for n in nodes):
                missing.append(node.node_type)
        return {"ok": len(missing) == 0, "missing": missing}

    def replan(self, plan: GeometryPlanV3, delta: Dict[str, Any]) -> GeometryPlanV3:
        missing = delta.get("missing", [])
        new_nodes = []
        for n in missing:
            new_nodes.append(GeoNodeAction(node_type=n, params={"object": plan.object_name}))
        if not new_nodes:
            new_nodes = plan.nodes
        return GeometryPlanV3(
            instruction=plan.instruction + " (replan)", object_name=plan.object_name, nodes=new_nodes
        )
