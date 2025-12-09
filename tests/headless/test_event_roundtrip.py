from server.bridge.events import EVENT_BUS
from server.bridge.router_v2 import RouterV2


def test_event_roundtrip():
    received = {}

    def handler(event_name, data):
        received["event"] = event_name
        received["data"] = data

    EVENT_BUS.subscribe("test", handler)
    router = RouterV2()
    router.set_event_handler(lambda payload: EVENT_BUS.emit(payload.get("event"), payload.get("data", {})))
    router.receive({"type": "event", "event": "test", "data": {"foo": "bar"}})
    assert received.get("event") == "test"
    assert received.get("data") == {"foo": "bar"}
