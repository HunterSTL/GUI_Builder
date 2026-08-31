import sys
from types import FrameType

_INDENTATION = "    "
_TRACE_TARGETS = (
    "actions",
    "commands",
    "components",
    "controller",
    "events",
    "model",
    "utility",
    "view",
    "AppController",
    "AppState",
    "Designer"
)

#terminal colors
_RED = "\033[31m"
_GREEN = "\033[32m"
_RESET = "\033[39m"


class CallTracer:
    """Controls diagnostic tracing of calls within application modules."""
    def __init__(
        self
    ) -> None:
        self._enabled: bool = False
        self._depth: int = 0

    def toggle(
        self
    ) -> None:
        """Enable or disable call tracing and report the resulting state."""
        if self._enabled:
            self._enabled = False
            self._depth = 0
            sys.setprofile(None)
            print("CALL TRACING DISABLED")
        else:
            self._enabled = True
            sys.setprofile(self._trace)
            print("CALL TRACING ENABLED")

    def _trace(
        self,
        frame: FrameType,
        event: str,
        _arg: object
    ) -> None:
        """Print nested call and return events for configured application modules."""
        if event not in {"call", "return"}:
            return

        module = frame.f_globals.get("__name__", "")
        if not module.startswith(_TRACE_TARGETS):
            return

        function_name = frame.f_code.co_qualname

        if event == "call":
            print(_GREEN + f"→{_INDENTATION * self._depth}{function_name}" + _RESET)
            self._depth += 1
        elif self._depth > 0:
            self._depth -= 1
            print(_RED + f"←{_INDENTATION * self._depth}{function_name}" + _RESET)

call_tracer = CallTracer()
