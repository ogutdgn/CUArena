"""
Task 16 — Speech bubble via Union.

# BLOCKED: requires boolean Union operation.
"""
from dataclasses import dataclass
from typing import Any
from verifier.types import Task, RubricResult
from verifier.rubrics.event import EventRubric
from verifier.rubrics.efficiency import EfficiencyRubric
from verifier.checks.event_checks import ToolUsed, EventTypeCount


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
    id="task_16_speech_bubble",
    description="Rounded rectangle + small triangle tail unioned into a speech bubble.",
    rubrics=[
        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("polygon"),
            EventTypeCount("create_rectangle", equals=1),
            EventTypeCount("create_polygon", equals=1),
        ]), max_score=1.0),
    ],
    efficiency=EfficiencyRubric(target_turns=20),
)
