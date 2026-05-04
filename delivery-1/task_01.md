# Task 1 — Build a simple house inside a MacBook Air frame with a body, triangle roof, door, and 2 round windows.

**Difficulty:** Easy  •  **Time horizon:** 10 min

## Thorough description

Use the Frame tool from the toolbar and select the MacBook Air preset (1280x832) from the right-panel preset list. Inside the frame, build a simple house: draw a rectangle for the body, add a triangle roof on top spanning the body width with a small overhang on each side, add a front door rectangle on the body, and include 2 small round windows (ellipses) on either side of the door. Apply a different fill color to the body, roof, door, and windows.

## Simplified prompt

> Build a simple house inside a MacBook Air frame with a body, triangle roof, door, and 2 round windows.

## Step-by-step

1. Click Frame tool. 2. Click MacBook Air preset. 3. Click Rectangle tool. 4. Drag body. 5. Pick body color. 6. Click Polygon tool. 7. Drag roof triangle. 8. Pick roof color. 9. Click Rectangle tool. 10. Drag door. 11. Pick door color. 12. Click Ellipse tool. 13. Drag left window. 14. Pick window color. 15. Right-click then Duplicate. 16. Drag duplicate to right side of door.

## Verifier

File: `test-verifier/tasks/task_01_house_task_comprehensive.py`

```python
"""
Comprehensive Task 1 verifier (two-story house) — normalized to max score 1.0.

Extends the basic house_task.py with:
  - ColorRubric      — fill type and color variety checks
  - StructureRubric  — frame containment and grouping
  - EventRubric      — action-log usage of correct tools and creation events
  - DistinctSolidColors — custom check (defined inline) for color variety
  - WeightedRubric   — wrapper that rescales any rubric to a custom max_score

Architecture:
  5 rubrics, each rescaled via WeightedRubric to max 0.2 (sum = 1.0):
    1. Fundamentals (3 checks)  — shape primitive counts
    2. Alignment    (4 checks)  — geometric relationships between layers
    3. Color        (4 checks)  — fill type and distinct color count
    4. Structure    (4 checks)  — layer organization (inside frame, child counts)
    5. Event        (6 checks)  — action log: tools used, creation events emitted
  Efficiency multiplier (0.5..1.0) based on semantic event count vs target.

Score:
  base_score = sum of rubric scores             (max 5 × 0.2 = 1.0)
  final      = base_score × efficiency_mult     (max 1.0)

Run:
  python run.py --task house_task_comprehensive --log logs/house_sample.json
"""

from dataclasses import dataclass
from typing import Any

from verifier.types  import Task, RubricResult

from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric

from verifier.checks.shape_checks    import ShapeCount
from verifier.checks.geometry_checks import (
    LayersAligned, LayersSymmetricX, LayersSameDimensions, LayerEdgesAligned,
    LayerBoundsInside, LayersOverlap, FrameSizeEquals,
)
from verifier.checks.fill_checks     import FillTypeIs, DistinctSolidColors
from verifier.checks.structure_checks import LayerInsideFrame, ChildCountAtLeast
from verifier.checks.event_checks    import ToolUsed, EventTypeCount


# ─────────────────────────────────────────────────────────────
# WeightedRubric — wraps any rubric and rescales its score
# Lets us keep their library rubric classes (each native max=0.5)
# while normalizing the task total to 1.0.
# ─────────────────────────────────────────────────────────────

@dataclass
class WeightedRubric:
    rubric: Any           # any object with a .run(log) -> RubricResult
    max_score: float      # the desired max for this slot

    def run(self, log: dict) -> RubricResult:
        r = self.rubric.run(log)
        scale = self.max_score / r.max_score if r.max_score else 1.0
        return RubricResult(
            name=r.name,
            score=round(r.score * scale, 4),
            max_score=self.max_score,
            checks=r.checks,
        )


# ─────────────────────────────────────────────────────────────
# The comprehensive task
# ─────────────────────────────────────────────────────────────

task = Task(
    id="house_task_comprehensive",
    description=(
        "Two-story house: 2 rectangles (body + door), 2 ellipses (windows), 1 polygon (roof). "
        "Windows aligned, same size, symmetric. Roof bottom touches body top. "
        "Distinct colors used. Shapes inside one frame. Correct tools used in action log."
    ),

    # 5 rubrics, each weighted to 0.2 → sum maxes at 1.0
    rubrics=[
        # ── END-STATE: Fundamentals (weight 0.2) ────────────
        WeightedRubric(FundamentalsRubric([
            ShapeCount("rectangle", equals=2),
            ShapeCount("ellipse",   equals=2),
            ShapeCount("polygon",   equals=1),
        ]), max_score=0.2),

        # ── END-STATE: Alignment / Geometry (weight 0.2) ────
        WeightedRubric(AlignmentRubric([
            LayersAligned(layer_type="ellipse", axis="center_y", tolerance=8.0),
            LayersSameDimensions(layer_type="ellipse", tolerance=3.0),
            LayersSymmetricX(layer_type="ellipse", tolerance=15.0),
            LayerEdgesAligned(
                type_a="polygon", edge_a="bottom",
                type_b="rectangle", edge_b="top",
                tolerance=10.0,
            ),
            LayerBoundsInside(inner_type="rectangle", outer_type="rectangle", tolerance=4.0),
            LayersOverlap(type_a="ellipse", type_b="rectangle"),
            FrameSizeEquals(width=1280, height=832, tolerance=10.0),
        ]), max_score=0.2),

        # ── END-STATE: Color (weight 0.2) ───────────────────
        WeightedRubric(ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            FillTypeIs("polygon",   kind="solid"),
            FillTypeIs("ellipse",   kind="solid"),
            DistinctSolidColors(minimum=4, tolerance=0.05),
        ]), max_score=0.2),

        # ── END-STATE: Structure (weight 0.2) ───────────────
        WeightedRubric(StructureRubric([
            LayerInsideFrame("rectangle"),
            LayerInsideFrame("polygon"),
            LayerInsideFrame("ellipse"),
            ChildCountAtLeast("frame", minimum=5),
        ]), max_score=0.2),

        # ── ACTION-LOG: Event (weight 0.2) ──────────────────
        WeightedRubric(EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("ellipse"),
            ToolUsed("polygon"),
            EventTypeCount("create_rectangle", equals=2),
            EventTypeCount("create_ellipse",   equals=2),
            EventTypeCount("create_polygon",   equals=1),
        ]), max_score=0.2),
    ],

    # ── ACTION-LOG: Efficiency multiplier ────────────────────
    efficiency=EfficiencyRubric(target_turns=30),
)
```
