from __future__ import annotations

from typing import Any, Dict

from server.orchestrator.orchestrator_v3 import OrchestratorV3

MAX_ITER = 3


class ModelerAgentV3:
    def __init__(self) -> None:
        self.orchestrator = OrchestratorV3()

    def run(self, instruction: str) -> Dict[str, Any]:
        plan = self.orchestrator.plan(instruction)
        for _ in range(MAX_ITER):
            ok, results = self.orchestrator.execute(plan)
            delta = self.orchestrator.verify(plan, results)
            if delta.get("ok", False):
                return {
                    "ok": True,
                    "plan": plan.to_dict(),
                    "results": results,
                    "message": "Success",
                }
            plan = self.orchestrator.replan(plan, delta)
        return {
            "ok": False,
            "message": "Max iterations reached",
            "plan": plan.to_dict(),
        }
