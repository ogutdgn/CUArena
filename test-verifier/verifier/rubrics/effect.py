from verifier.rubrics._base import Rubric


def EffectRubric(checks: list, weight: float = 0.5) -> Rubric:
    """Checks effects: drop shadows and blurs."""
    return Rubric(name="effect", checks=checks, weight=weight)
