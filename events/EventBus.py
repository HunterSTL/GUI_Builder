class EventBus:
    """Calls the handler for an emitted event."""
    def __init__(self):
        self._handlers = {}

    def subscribe(self, event, handler):
        """register a handler to be called when the given event is emitted"""
        if not callable(handler):
            raise ValueError(f"EventBus - subscription failed: handler must be callable [event: {event}]")

        self._handlers[event] = handler

    def emit(self, event, **kwargs):
        """call the handler for the given event"""
        if event not in self._handlers:
            return  #key doesn't exist → nothing to call

        handler = self._handlers[event]

        try:
            handler(**kwargs)
        except Exception as error:
            raise ValueError(f"EventBus - handler execution failed for event \"{event}\": {error}")
