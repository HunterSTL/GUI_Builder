import logging, sys, threading

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d  %(message)s",
    datefmt="%H:%M:%S"
)

log = logging.getLogger("GUIBuilder")

class CallTracer:
    def __init__(self):
        self.enabled = False
        self.local = threading.local()

    def _ensure(self):
        if not hasattr(self.local, "depth"):
            self.local.depth = 0

    def _profiler(self, frame, event, arg):
        if event not in ("call", "return"):
            return

        mod = frame.f_globals.get("__name__", "")
        if not mod.startswith(("Designer", "AppState", "view", "controller", "commands")):
            return

        self._ensure()
        func = frame.f_code.co_name

        if event == "call":
            self.local.depth += 1
            indent = "  " * (self.local.depth - 1)
            log.info(f"{indent}→ {mod}.{func}")
        else:
            indent = "  " * (self.local.depth - 1)
            log.info(f"{indent}← {mod}.{func}")
            self.local.depth -= 1

    def enable(self):
        if not self.enabled:
            sys.setprofile(self._profiler)
            self.enabled = True
            log.info("CALL TRACING ENABLED")

    def disable(self):
        if self.enabled:
            sys.setprofile(None)
            self.enabled = False
            log.info("CALL TRACING DISABLED")

    def toggle(self):
        if self.enabled:
            self.disable()
        else:
            self.enable()

    def log_event(self, message):
        if self.enabled:
            log.info(message)

call_tracer = CallTracer()