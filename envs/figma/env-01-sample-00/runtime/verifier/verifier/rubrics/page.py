from verifier.rubrics._base import Rubric


def PageRubric(checks: list, weight: float = 0.5, critical: list = None) -> Rubric:
    """Checks page count and layer presence across pages."""
    return Rubric(name="page", checks=checks, weight=weight, critical=critical or [])
