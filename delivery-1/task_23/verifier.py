"""
Task 23 — Sidebar layout with constraints (IN SCOPE).

1 outer frame + 1 dark-gray sidebar rectangle on the left edge with
constraints: horizontal=left, vertical=stretch (top-to-bottom).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.geometry_checks import LayerAspectRatioGreaterThan, LayerWidthFraction
from verifier.checks.fill_checks   import FillTypeIs, SolidColorEquals
from verifier.checks.property_checks import ConstraintHorizontalEquals, ConstraintVerticalEquals
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

DARK_GRAY = {"r": 0.30, "g": 0.30, "b": 0.30}

task = Task(
    id="task_23_stretchy_sidebar",
    description="Frame + dark-gray sidebar on left edge with constraints horizontal=left, vertical=stretch.",
    rubrics=[
        FundamentalsRubric([
            ShapeCountAtLeast("frame", minimum=1),
            ShapeCount("rectangle", equals=1),
        ], weight=0.25),

        AlignmentRubric([
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=2.0, axis="vertical"),
            LayerWidthFraction(inner_type="rectangle", parent_type="frame",
                               min_frac=0.08, max_frac=0.30),
            ConstraintHorizontalEquals(layer_type="rectangle", value="left"),
            ConstraintVerticalEquals(layer_type="rectangle", value="stretch"),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            SolidColorEquals(layer_type="rectangle", expected_rgb=DARK_GRAY, tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("frame"),
            ToolUsed("rectangle"),
            EventTypeCount("create_rectangle", equals=1),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
