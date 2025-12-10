from __future__ import annotations

from typing import Any, Dict, List, Tuple

from mcpbla.server.bridge.scenegraph import SCENEGRAPH
from mcpbla.server.core.engines.action_engine_v3 import ActionEngineV3
from mcpbla.server.orchestrator.animation_plan_v3 import AnimationPlanV3, KeyframeAction


class AnimationOrchestratorV3:
    def __init__(self, engine: ActionEngineV3 | None = None) -> None:
        self.engine = engine or ActionEngineV3(wait_for_ack=False)

    def plan(self, instruction: str, object_name: str) -> AnimationPlanV3:
        actions: List[KeyframeAction] = []
        lower = instruction.lower()
        if "rotate" in lower:
            actions.append(KeyframeAction(operation="rotate", params={"object": object_name, "axis": "z", "degrees": 90}))
        else:
            actions.append(KeyframeAction(operation="keyframe", params={"object": object_name, "frame": 1}))
        return AnimationPlanV3(instruction=instruction, object_name=object_name, actions=actions)

    def execute(self, plan: AnimationPlanV3) -> Tuple[bool, List[Dict[str, Any]]]:
        results: List[Dict[str, Any]] = []
        ok_all = True
        for action in plan.actions:
            params = {"object": plan.object_name, "operation": action.operation, **action.params}
            res = self.engine.execute("animation.operation", params)
            results.append({"operation": action.operation, "ok": res.ok, "data": res.data, "error": res.error})
            if not res.ok:
                ok_all = False
                break
        return ok_all, results

    def verify(self, plan: AnimationPlanV3) -> Dict[str, Any]:
        sg = SCENEGRAPH.describe()
        objects = sg.get("objects", [])
        target = next((o for o in objects if o.get("name") == plan.object_name), None)
        if target:
            return {"ok": True}
        return {"ok": False, "missing": [plan.object_name]}

    def replan(self, plan: AnimationPlanV3, delta: Dict[str, Any]) -> AnimationPlanV3:
        if not delta.get("ok", True):
            new_actions = [KeyframeAction(operation="keyframe", params={"object": plan.object_name, "frame": 1})]
            return AnimationPlanV3(instruction=plan.instruction + " (replan)", object_name=plan.object_name, actions=new_actions)
        return plan

