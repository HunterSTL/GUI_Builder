from .EventBus import EventBus

class EventRouter:
    """
    Routes emitted events to the appropriate EventBus based on the event namespace:

    1. App events (e.g. "project.open", "project.save", "app.exit"):
        *Owned by the AppController
        *Persist for the entire application lifetime
        *App events must start with "app." or "project."
    2. Designer events (e.g. "selection.rectangle.start", "widget.nudge"):
        *Owned by a single Designer instance
        *Must be discarded when the Designer window is destroyed

    The EventRouter provides a single interface for emitting events
    so controllers do not need to know which EventBus an event belongs to.
    """
    def __init__(
        self,
        app_event_bus: EventBus,
        designer_event_bus: EventBus
    ):
        self._app_event_bus = app_event_bus
        self._designer_event_bus = designer_event_bus

    def emit(self, event_name, **kwargs):
        """emit an event and forward the event to the correct EventBus"""
        if event_name.startswith(("app.", "project.")):
            self._app_event_bus.emit(event_name, **kwargs)
        else:
            self._designer_event_bus.emit(event_name, **kwargs)