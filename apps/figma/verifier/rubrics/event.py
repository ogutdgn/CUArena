from verifier.rubrics._base import Rubric


def EventRubric(checks: list, weight: float = 0.5, critical: list = None) -> Rubric:
    """Checks which semantic events were used during the session."""
    return Rubric(name="event", checks=checks, weight=weight, critical=critical or [])
