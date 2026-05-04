"""
Task 28 — Photo placeholder mockup (in-scope replacement, no image fill).

1 large rectangle (placeholder) + 2 diagonal lines drawn from corner to corner forming an X-cross.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LinesOnDiagonal
from verifier.checks.fill_checks   import FillTypeIs
from verifier.checks.event_checks  import ToolUsed, EventTypeCount


@dataclass
class WeightedRubric:
    rubric: Any
    max_score: float
    def run(self, log):
        r = self.rubric.run(log)
        scale = self.max_score / r.max_score if r.max_score else 1.0
        return RubricResult(name=r.name, score=round(r.score * scale, 4),
                            max_score=self.max_score, checks=r.checks)


task = Task(
    id="task_28_edited_photo",
    description="Large rectangle placeholder + 2 diagonal lines crossing through it.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=1),
            ShapeCount("line",      equals=2),
        ]), max_score=0.25),

        WeightedRubric(AlignmentRubric([
            LinesOnDiagonal(rect_type="rectangle", line_type="line", tolerance=12.0),
        ]), max_score=0.25),

        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
        ]), max_score=0.25),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("line"),
            EventTypeCount("create_rectangle", equals=1),
            EventTypeCount("create_line",      equals=2),
        ]), max_score=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
