from verifier.rubrics._base import Rubric


def PropertyRubric(checks: list, weight: float = 0.5) -> Rubric:
    """Checks layer properties: opacity, visibility, corner radius, flip."""
    return Rubric(name="property", checks=checks, weight=weight)
