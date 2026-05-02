from dataclasses import dataclass
from verifier.types import CheckResult


def _events(log: dict, name: str) -> list[dict]:
    return [e for e in log["semantic"] if e.get("name") == name]


@dataclass
class EventTypeUsed:
    """The given semantic event was emitted at least once during the session."""
    event_name: str

    def run(self, log: dict) -> CheckResult:
        found = bool(_events(log, self.event_name))
        return CheckResult(
            passed=found, score=1.0 if found else 0.0, max_score=1.0,
            message=f"event '{self.event_name}': {'used' if found else 'never used'}",
        )


@dataclass
class EventTypeCount:
    """The given semantic event was emitted exactly `equals` times."""
    event_name: str
    equals: int

    def run(self, log: dict) -> CheckResult:
        count = len(_events(log, self.event_name))
        passed = count == self.equals
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"event '{self.event_name}': expected {self.equals}, got {count}",
        )


@dataclass
class EventTypeCountAtLeast:
    """The given semantic event was emitted at least `minimum` times."""
    event_name: str
    minimum: int

    def run(self, log: dict) -> CheckResult:
        count = len(_events(log, self.event_name))
        passed = count >= self.minimum
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"event '{self.event_name}': expected ≥{self.minimum}, got {count}",
        )


@dataclass
class AlignToolUsed:
    """The agent used the align tool at least once (align_layers event)."""

    def run(self, log: dict) -> CheckResult:
        found = bool(_events(log, "align_layers"))
        return CheckResult(
            passed=found, score=1.0 if found else 0.0, max_score=1.0,
            message=f"align_layers: {'used' if found else 'never used'}",
        )


@dataclass
class UndoUsed:
    """The agent used undo at least once."""

    def run(self, log: dict) -> CheckResult:
        found = bool(_events(log, "undo"))
        return CheckResult(
            passed=found, score=1.0 if found else 0.0, max_score=1.0,
            message=f"undo: {'used' if found else 'never used'}",
        )


@dataclass
class ToolUsed:
    """The agent switched to the given tool at least once (tool_change event)."""
    tool_id: str   # e.g. "pen", "frame", "rectangle", "ellipse"

    def run(self, log: dict) -> CheckResult:
        found = any(
            e.get("name") == "tool_change" and
            (e.get("after") == self.tool_id or e.get("before") == self.tool_id)
            for e in log["semantic"]
        )
        return CheckResult(
            passed=found, score=1.0 if found else 0.0, max_score=1.0,
            message=f"tool '{self.tool_id}': {'used' if found else 'never used'}",
        )
