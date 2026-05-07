from verifier.rubrics._base import Rubric


def TextRubric(checks: list, weight: float = 0.5) -> Rubric:
    """Checks text content and typography."""
    return Rubric(name="text", checks=checks, weight=weight)
