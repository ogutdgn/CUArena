"""
Task 03 — Glowing cyan orb.

# BLOCKED: requires radial gradient fill emission. Add ColorRubric with
# FillTypeIs(kind="gradient_radial") once implemented.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
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
    id="task_03_glowing_orb",
    description="600x600 dark navy frame containing 1 circle with radial gradient (cyan center → translucent edge).",
    rubrics=[
        WeightedRubric(FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),
            ShapeCount("ellipse", equals=1),
        ]), max_score=0.5),

        WeightedRubric(EventRubric([
            ToolUsed("frame"),
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=1),
        ]), max_score=0.5),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
