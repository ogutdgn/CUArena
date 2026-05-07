"""
Task 03 — Radial flower with petals (in-scope replacement).

1 yellow center circle + 8 elliptical petals arranged radially around it,
each petal a different color.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import RadialDistributionExcludeCentral
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors, CentermostLayerHasColor
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_03_glowing_orb",
    description="1 yellow center circle + 8 elliptical petals arranged radially around it.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=9),
        ], weight=0.25),

        AlignmentRubric([
            RadialDistributionExcludeCentral(layer_type="ellipse", n=8, tolerance_deg=15.0),
        ], weight=0.25),

        ColorRubric([
            FillTypeIs("ellipse", kind="solid"),
            DistinctSolidColors(minimum=8, tolerance=0.05),
            CentermostLayerHasColor(layer_type="ellipse",
                                    expected_rgb={"r": 1.0, "g": 0.9, "b": 0.2},
                                    tolerance=0.20),
        ], weight=0.25),

        EventRubric([
            ToolUsed("ellipse"),
            EventTypeCount("create_ellipse", equals=9),
        ], weight=0.25),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
