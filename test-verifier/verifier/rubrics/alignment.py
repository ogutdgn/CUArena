from verifier.rubrics._base import Rubric


def AlignmentRubric(checks: list, weight: float = 0.5) -> Rubric:
    """Checks geometric relationships between layers."""
    return Rubric(name="alignment", checks=checks, weight=weight)
