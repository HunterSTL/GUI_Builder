from .EventBus import EventBus


class EventRouter:
    """Forwards emitted events to the appropriate event bus."""
    def __init__(
        self,
        app_event_bus: EventBus,
        designer_event_bus: EventBus
    ) -> None:
        self._app_event_bus: EventBus = app_event_bus
        self._designer_event_bus: EventBus = designer_event_bus

    def emit(
        self,
        event: str,
        **kwargs
    ) -> None:
        """Forward the event to the appropriate event bus based on the event namespace."""
        if event.startswith(("app.", "project.")):
            self._app_event_bus.emit(event, **kwargs)
        else:
            self._designer_event_bus.emit(event, **kwargs)
