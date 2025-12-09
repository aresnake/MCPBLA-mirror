from __future__ import annotations

from typing import Any, Dict, List, Tuple

from server.bridge.scenegraph import SCENEGRAPH
from server.core.engines.action_engine_v3 import ActionEngineV3
from server.orchestrator.plan_v3 import TaskAction, TaskPlan


class OrchestratorV3:
    def __init__(self, engine: ActionEngineV3 | None = None) -> None:
        self.engine = engine or ActionEngineV3(wait_for_ack=False)

    def plan(self, instruction: str) -> TaskPlan:
        actions: List[TaskAction] = []
        lower = instruction.lower()
        if "cube" in lower:
            actions.append(TaskAction(name="create_cube", params={"name": "AutoCube", "size": 1.0}))
        if "move" in lower:
            actions.append(
                TaskAction(name="move_object", params={"name": "AutoCube", "translation": {"x": 0, "y": 0, "z": 2}})
            )
        if not actions:
            actions.append(TaskAction(name="noop", params={}))
        return TaskPlan(instruction=instruction, actions=actions)

    def execute(self, plan: TaskPlan) -> Tuple[bool, List[Dict[str, Any]]]:
        results: List[Dict[str, Any]] = []
        overall_ok = True
        for action in plan.actions:
            res = self.engine.execute(action.name, action.params)
            results.append({"action": action.name, "ok": res.ok, "data": res.data, "error": res.error})
            if not res.ok:
                overall_ok = False
                break
        return overall_ok, results

    def verify(self, plan: TaskPlan, result: List[Dict[str, Any]]) -> Dict[str, Any]:
        # simple verification: check SceneGraph contains object from plan
        sg = SCENEGRAPH.describe()
        ok = True
        missing = []
        for action in plan.actions:
            if action.name == "create_cube":
                name = action.params.get("name", "")
                if not any(obj.get("name") == name for obj in sg.get("objects", [])):
                    ok = False
                    missing.append(name)
        return {"ok": ok, "missing": missing}

    def replan(self, plan: TaskPlan, diff: Dict[str, Any]) -> TaskPlan:
        # basic replan: if missing objects, retry creation
        missing = diff.get("missing", [])
        new_actions = []
        for name in missing:
            new_actions.append(TaskAction(name="create_cube", params={"name": name, "size": 1.0}))
        if not new_actions:
            new_actions = plan.actions
        return TaskPlan(instruction=plan.instruction + " (replan)", actions=new_actions)
