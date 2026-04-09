from events import EventBus

class EventRouter:
    """
    Routes emitted events to the appropriate EventBus based on the event name:

    1. App events (e.g. "project.open", "project.save", "app.exit"):
        *Owned by the AppController
        *Persist for the entire application lifetime
        *App events must start with "app." or "project."
    2. UI events (e.g. "selection.handle_press", "widget.move"):
        *Owned by a single Designer instance
        *Must be discarded when the Designer window is destroyed

    The EventRouter provides a single interface for emitting events
    so controllers do not need to know which EventBus an event belongs to.
    """
    def __init__(
        self,
        app_event_bus: EventBus,
        ui_event_bus: EventBus
    ):
        self._app_event_bus = app_event_bus
        self._ui_event_bus = ui_event_bus

    def emit(self, event_name, **kwargs):
        """emit an event and forward the event to the correct EventBus"""
        if event_name.startswith(("app.", "project.")):
            self._app_event_bus.emit(event_name, **kwargs)
        else:
            self._ui_event_bus.emit(event_name, **kwargs)