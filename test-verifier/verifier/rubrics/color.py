from verifier.rubrics._base import Rubric


def ColorRubric(checks: list, weight: float = 0.5) -> Rubric:
    """Checks fill and stroke color correctness."""
    return Rubric(name="color", checks=checks, weight=weight)
