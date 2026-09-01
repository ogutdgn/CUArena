from verifier.rubrics._base import Rubric


def ColorRubric(checks: list, weight: float = 0.5, critical: list = None) -> Rubric:
    """Checks fill and stroke color correctness."""
    return Rubric(name="color", checks=checks, weight=weight, critical=critical or [])
