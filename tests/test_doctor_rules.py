from mcpbla.server.diag.doctor_rules import evaluate_status


def test_doctor_rules_pass():
    status = {
        "ok": True,
        "bridge": {"enabled": False, "configured": False, "reachable": False},
    }
    ok, hint = evaluate_status(status, health_ok=True)
    assert ok is True
    assert hint is None


def test_doctor_rules_bridge_enabled_not_configured():
    status = {
        "ok": True,
        "bridge": {"enabled": True, "configured": False, "reachable": False},
    }
    ok, hint = evaluate_status(status, health_ok=True)
    assert ok is False
    assert "not configured" in hint.lower()


def test_doctor_rules_bridge_unreachable():
    status = {
        "ok": True,
        "bridge": {"enabled": True, "configured": True, "reachable": False},
    }
    ok, hint = evaluate_status(status, health_ok=True)
    assert ok is False
    assert "unreachable" in hint.lower()


def test_doctor_rules_health_fail():
    status = {"ok": True, "bridge": {"enabled": False}}
    ok, hint = evaluate_status(status, health_ok=False)
    assert ok is False
    assert "health" in hint.lower()
