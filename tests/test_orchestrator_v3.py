from server.bridge.scenegraph import SCENEGRAPH
from server.orchestrator.orchestrator_v3 import OrchestratorV3
from server.orchestrator.plan_v3 import TaskPlan, TaskAction
from server.core.engines.action_engine_v3 import ActionEngineV3
from server.core.contracts.common_types import ContractResult


class DummyEngine(ActionEngineV3):
    def __init__(self, script):
        super().__init__(wait_for_ack=False)
        self.script = script
        self.calls = []

    def execute(self, action: str, params: dict) -> ContractResult:
        self.calls.append(action)
        behavior = self.script.get(action, {"ok": True})
        return ContractResult(ok=behavior.get("ok", True), data=behavior.get("data"), error=behavior.get("error"))


def test_plan_execute_verify_success():
    SCENEGRAPH.apply_snapshot({"objects": [{"name": "AutoCube"}]})
    engine = DummyEngine({"create_cube": {"ok": True, "data": {"name": "AutoCube"}}})
    orch = OrchestratorV3(engine=engine)
    plan = orch.plan("create cube")
    ok, results = orch.execute(plan)
    assert ok is True
    verify = orch.verify(plan, results)
    assert verify["ok"] is True


def test_replan_after_failure():
    SCENEGRAPH.apply_snapshot({"objects": []})
    engine = DummyEngine({"create_cube": {"ok": False, "error": "fail"}})
    orch = OrchestratorV3(engine=engine)
    plan = TaskPlan(instruction="create cube", actions=[TaskAction(name="create_cube", params={"name": "AutoCube"})])
    ok, results = orch.execute(plan)
    assert ok is False
    verify = orch.verify(plan, results)
    new_plan = orch.replan(plan, verify)
    assert isinstance(new_plan, TaskPlan)
    assert new_plan.actions
