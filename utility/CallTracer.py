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
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[39m"


class CallTracer:
    def __init__(
        self
    ) -> None:
        self._enabled: bool = False
        self._depth: int = 0

    def toggle(
        self
    ) -> None:
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
        if event not in {"call", "return"}:
            return

        module = frame.f_globals.get("__name__", "")
        if not module.startswith(_TRACE_TARGETS):
            return

        function_name = frame.f_code.co_qualname

        if event == "call":
            print(GREEN + f"→{_INDENTATION * self._depth}{function_name}" + RESET)
            self._depth += 1
        elif self._depth > 0:
            self._depth -= 1
            print(RED + f"←{_INDENTATION * self._depth}{function_name}" + RESET)

call_tracer = CallTracer()
