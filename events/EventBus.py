class EventBus:
    """
    Maps events (e.g. widget.nudge) to subscribers.

    self._subscribers = {
        "widget.nudge":     [function1, function2],
        "edit.delete":      [function3],
        "project.save":     [function4]
    }
    """
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_name, function):
        """register a function to be called when the given event is emitted"""
        if not callable(function):
            raise ValueError(f"EventBus - subscription failed: subscriber must be callable [event: {event_name}]")

        #create list of subscribers if key doesn't exist yet
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []

        self._subscribers[event_name].append(function)

    def unsubscribe(self, event_name, function):
        """remove a function from the subscribers for the given event"""
        if event_name not in self._subscribers:
            return  #key doesn't exist → nothing to remove

        subscribers = self._subscribers.get(event_name)

        if function in subscribers:
            subscribers.remove(function)

    def emit(self, event_name, **kwargs):
        """call all subscribers for the given event"""
        if event_name not in self._subscribers:
            return  #key doesn't exist → nothing to call

        subscribers = self._subscribers[event_name]
        errors = []

        for function in subscribers:
            try:
                function(**kwargs)
            except Exception as e:
                errors.append(f"\t{function.__name__}: {e}")

        if errors:
            count_errors = len(errors)
            if count_errors == 1:
                reason = "1 handler raised an error:\n"
            else:
                reason = f"{count_errors} handlers raised an error:\n"
            reason += "\n".join(errors)

            raise ValueError(f"EventBus - handler execution failed for event \"{event_name}\": {reason}")
