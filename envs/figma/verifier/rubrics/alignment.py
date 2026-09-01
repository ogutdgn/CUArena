from verifier.rubrics._base import Rubric


def AlignmentRubric(checks: list, weight: float = 0.5, critical: list = None) -> Rubric:
    """Checks geometric relationships between layers."""
    return Rubric(name="alignment", checks=checks, weight=weight, critical=critical or [])
