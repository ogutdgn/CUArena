from verifier.rubrics._base import Rubric


def TextRubric(checks: list, weight: float = 0.5, critical: list = None) -> Rubric:
    """Checks text content and typography."""
    return Rubric(name="text", checks=checks, weight=weight, critical=critical or [])
