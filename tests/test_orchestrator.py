import asyncio

from mcpbla.server.orchestrator import orchestrator
from mcpbla.server.orchestrator.plan import Plan, PlanStep


def test_plan_task_basic():
    plan = orchestrator.plan_task("create a cube")
    assert plan.steps
    assert plan.steps[0].tool_name == "create_cube_stub"


def test_execute_plan_runs_steps():
    plan = Plan(task_id="test", steps=[PlanStep(tool_name="create_cube_stub", arguments={})])

    async def fake_invoker(tool_name: str, arguments: dict):
        return {"tool": tool_name, "arguments": arguments}

    result = asyncio.run(orchestrator.execute_plan(plan, invoker=fake_invoker))
    assert result.success is True
    assert len(result.steps) == 1
    assert result.steps[0].success is True


def test_run_task_end_to_end():
    async def fake_invoker(tool_name: str, arguments: dict):
        return {"tool": tool_name, "arguments": arguments}

    result = asyncio.run(orchestrator.run_task("create a cube and move it 2 meters up", invoker=fake_invoker))
    assert result.success is True
    assert len(result.steps) >= 2

