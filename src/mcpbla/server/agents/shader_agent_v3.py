from __future__ import annotations

from typing import Any, Dict

from mcpbla.server.orchestrator.shader_orchestrator_v3 import ShaderOrchestratorV3

MAX_ITER = 3


class ShaderAgentV3:
    def __init__(self) -> None:
        self.orchestrator = ShaderOrchestratorV3()

    def run(self, instruction: str, material: str) -> Dict[str, Any]:
        plan = self.orchestrator.plan(instruction, material)
        for _ in range(MAX_ITER):
            ok, results = self.orchestrator.execute(plan)
            delta = self.orchestrator.verify(plan)
            if delta.get("ok", False):
                return {"ok": True, "plan": plan.to_dict(), "results": results, "message": "Success"}
            plan = self.orchestrator.replan(plan, delta)
        return {"ok": False, "message": "Max iterations reached", "plan": plan.to_dict()}

