from verifier.rubrics._base import Rubric


def FundamentalsRubric(checks: list, weight: float = 0.5) -> Rubric:
    """Checks that the agent used the correct shape primitives."""
    return Rubric(name="fundamentals", checks=checks, weight=weight)
