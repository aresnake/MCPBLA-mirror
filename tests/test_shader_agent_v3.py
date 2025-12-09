from server.agents.shader_agent_v3 import ShaderAgentV3
from server.bridge.scenegraph import SCENEGRAPH
from server.core.engines.action_engine_v3 import ActionEngineV3
from server.core.contracts.common_types import ContractResult
from server.orchestrator.shader_orchestrator_v3 import ShaderOrchestratorV3


class DummyEngine(ActionEngineV3):
    def __init__(self, script):
        super().__init__(wait_for_ack=False)
        self.script = script

    def execute(self, action: str, params: dict) -> ContractResult:
        behavior = self.script.get(action, {"ok": True})
        return ContractResult(ok=behavior.get("ok", True), data=behavior.get("data"), error=behavior.get("error"))


def test_shader_agent_success():
    SCENEGRAPH.apply_snapshot({"nodes": [{"material": "AutoMat", "type": "ShaderNodeTexNoise"}]})
    agent = ShaderAgentV3()
    agent.orchestrator.engine = DummyEngine({"node.operation": {"ok": True}})
    res = agent.run("add noise", "AutoMat")
    assert res["ok"] is True


def test_shader_agent_replan():
    SCENEGRAPH.apply_snapshot({"nodes": []})
    agent = ShaderAgentV3()
    agent.orchestrator.engine = DummyEngine({"node.operation": {"ok": False}})
    res = agent.run("add noise", "AutoMat")
    assert res["ok"] is False
