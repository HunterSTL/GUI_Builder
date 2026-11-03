from events import EventBus

def test_subscribe_uncallable_to_event_bus() -> None:
    event_bus = EventBus()
    event_bus.subscribe("EVENT", "UNCALLABLE")

def test_fail_handler_execution() -> None:
    def _handler() -> None:
        raise ValueError("ERROR")

    event_bus = EventBus()
    event_bus.subscribe("EVENT", _handler)
    event_bus.emit("EVENT")
