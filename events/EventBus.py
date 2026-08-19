from collections.abc import Callable


class EventBus:
    """Dispatches emitted events to their handlers."""
    def __init__(
        self
    ) -> None:
        self._handlers: dict[str, Callable[..., object]] = {}

    def subscribe(
        self,
        event: str,
        handler: Callable
    ) -> None:
        """Register a handler to be called when the given event is emitted."""
        if not callable(handler):
            raise ValueError(f"EventBus - subscription failed: handler must be callable [event: {event}]")

        self._handlers[event] = handler

    def emit(
        self,
        event: str,
        **kwargs
    ) -> None:
        """Call the handler for the given event."""
        if event not in self._handlers:
            return

        handler = self._handlers[event]

        try:
            handler(**kwargs)
        except Exception as error:
            raise ValueError(f"EventBus - handler execution failed for event \"{event}\": {error}")
