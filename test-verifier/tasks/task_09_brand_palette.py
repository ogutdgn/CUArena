"""
Task 09 — Brand palette with color styles.

# BLOCKED: requires color styles feature (save fill as style + apply by clicking swatch).
# Once implemented, check that ≥4 color styles are created and applied.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
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
    id="task_09_brand_palette",
    description="2 rows of 4 squares (8 total) with 4 distinct colors saved as styles and reapplied.",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=8),
        ]), max_score=0.5),

        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=8),
        ]), max_score=0.5),
    ],
    efficiency=EfficiencyRubric(target_turns=36),
)
