"""
Task 07 — Layered mountain range (IN SCOPE).

Two pen-tool paths in different gray shades — closer mountain in front,
overlapping the farther one.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCountAtLeast
from verifier.checks.geometry_checks import LayersOverlap
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

task = Task(
    id="task_07_mountain_range",
    description="Two overlapping pen-tool mountain paths in different gray shades.",
    rubrics=[
        FundamentalsRubric([
            ShapeCountAtLeast("vector", minimum=2),
        ], weight=0.25),

        AlignmentRubric([
            LayersOverlap(type_a="vector", type_b="vector"),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("vector", kind="solid"),
            DistinctSolidColors(minimum=2, tolerance=0.05),
        ], weight=0.25),

        EventRubric([
            ToolUsed("pen"),
            EventTypeCountAtLeast("create_vector", minimum=2),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
