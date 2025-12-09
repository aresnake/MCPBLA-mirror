from server.bridge.router_v2 import RouterV2


def test_router_receive_event():
    captured = {}

    def event_handler(payload):
        captured["event"] = payload.get("event")
        captured["data"] = payload.get("data")

    router = RouterV2()
    router.set_event_handler(event_handler)
    router.receive({"type": "event", "event": "demo", "data": {"ok": True}})
    assert captured.get("event") == "demo"
    assert captured.get("data") == {"ok": True}
