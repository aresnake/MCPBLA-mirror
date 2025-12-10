from __future__ import annotations

from typing import Any, Dict, List, Tuple

from mcpbla.server.bridge.scenegraph import SCENEGRAPH
from mcpbla.server.core.engines.action_engine_v3 import ActionEngineV3
from mcpbla.server.orchestrator.shader_plan_v3 import ShaderNodeAction, ShaderPlanV3


class ShaderOrchestratorV3:
    def __init__(self, engine: ActionEngineV3 | None = None) -> None:
        self.engine = engine or ActionEngineV3(wait_for_ack=False)

    def plan(self, instruction: str, material: str) -> ShaderPlanV3:
        nodes: List[ShaderNodeAction] = []
        lower = instruction.lower()
        if "noise" in lower:
            nodes.append(ShaderNodeAction(node_type="ShaderNodeTexNoise", params={"material": material}))
        else:
            nodes.append(ShaderNodeAction(node_type="ShaderNodeTexMusgrave", params={"material": material}))
        return ShaderPlanV3(instruction=instruction, material=material, nodes=nodes)

    def execute(self, plan: ShaderPlanV3) -> Tuple[bool, List[Dict[str, Any]]]:
        results: List[Dict[str, Any]] = []
        ok_all = True
        for node in plan.nodes:
            params = {"material": plan.material, "operation": node.node_type, **node.params}
            res = self.engine.execute("node.operation", params)
            results.append({"node": node.node_type, "ok": res.ok, "data": res.data, "error": res.error})
            if not res.ok:
                ok_all = False
                break
        return ok_all, results

    def verify(self, plan: ShaderPlanV3) -> Dict[str, Any]:
        sg = SCENEGRAPH.describe()
        nodes = sg.get("nodes", [])
        missing = []
        for node in plan.nodes:
            if not any(n.get("type") == node.node_type and n.get("material") == plan.material for n in nodes):
                missing.append(node.node_type)
        return {"ok": len(missing) == 0, "missing": missing}

    def replan(self, plan: ShaderPlanV3, delta: Dict[str, Any]) -> ShaderPlanV3:
        missing = delta.get("missing", [])
        new_nodes = []
        for n in missing:
            new_nodes.append(ShaderNodeAction(node_type=n, params={"material": plan.material}))
        if not new_nodes:
            new_nodes = plan.nodes
        return ShaderPlanV3(instruction=plan.instruction + " (replan)", material=plan.material, nodes=new_nodes)

