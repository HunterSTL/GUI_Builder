class EventBus:
    def __init__(self):
        """
        maps events (e.g. widget.move) to a list of subscribers

        self._subscribers = {
            "widget.move":      [function1, function2],
            "widget.delete":    [function3],
            "project.save":     [function4]
        }
        """
        self._subscribers = {}

    def subscribe(self, event_name, function):
        """register a function to be called when the given event is emitted"""
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

        subscribers = self._subscribers.get(event_name)

        for function in subscribers:
            try:
                function(**kwargs)
            except Exception as e:
                print(f"[EventBus] Error in handler for \"{event_name}\": {e}")