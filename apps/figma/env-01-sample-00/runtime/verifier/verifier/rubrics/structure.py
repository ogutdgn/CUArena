from verifier.rubrics._base import Rubric


def StructureRubric(checks: list, weight: float = 0.5, critical: list = None) -> Rubric:
    """Checks layer structure: nesting, z-order, grouping."""
    return Rubric(name="structure", checks=checks, weight=weight, critical=critical or [])
