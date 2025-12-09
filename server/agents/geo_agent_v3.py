from __future__ import annotations

from typing import Any, Dict

from server.orchestrator.geometry_orchestrator_v3 import GeometryOrchestratorV3

MAX_ITER = 3


class GeoAgentV3:
    def __init__(self) -> None:
        self.orchestrator = GeometryOrchestratorV3()

    def run(self, instruction: str, object_name: str) -> Dict[str, Any]:
        plan = self.orchestrator.plan(instruction, object_name)
        for _ in range(MAX_ITER):
            ok, results = self.orchestrator.execute(plan)
            delta = self.orchestrator.verify(plan)
            if delta.get("ok", False):
                return {"ok": True, "plan": plan.to_dict(), "results": results}
            plan = self.orchestrator.replan(plan, delta)
        return {"ok": False, "plan": plan.to_dict()}
