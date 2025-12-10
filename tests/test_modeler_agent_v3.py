from mcpbla.server.agents.modeler_agent_v3 import ModelerAgentV3, MAX_ITER
from mcpbla.server.bridge.scenegraph import SCENEGRAPH
from mcpbla.server.core.engines.action_engine_v3 import ActionEngineV3
from mcpbla.server.core.contracts.common_types import ContractResult
from mcpbla.server.orchestrator.plan_v3 import TaskAction, TaskPlan


class DummyEngine(ActionEngineV3):
    def __init__(self, script):
        super().__init__(wait_for_ack=False)
        self.script = script

    def execute(self, action: str, params: dict) -> ContractResult:
        behavior = self.script.get(action, {"ok": True})
        return ContractResult(ok=behavior.get("ok", True), data=behavior.get("data"), error=behavior.get("error"))


def test_modeler_agent_v3_success():
    SCENEGRAPH.apply_snapshot({"objects": [{"name": "AutoCube"}]})
    agent = ModelerAgentV3()
    agent.orchestrator.engine = DummyEngine({"create_cube": {"ok": True}})
    res = agent.run("create cube")
    assert res["ok"] is True


def test_modeler_agent_v3_replan():
    SCENEGRAPH.apply_snapshot({"objects": []})
    agent = ModelerAgentV3()
    agent.orchestrator.engine = DummyEngine({"create_cube": {"ok": False}})
    res = agent.run("create cube")
    assert res["ok"] is False
    assert res["message"] == "Max iterations reached"

