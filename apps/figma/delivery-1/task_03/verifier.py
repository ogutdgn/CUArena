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
from verifier.checks.fill_checks   import (
    DistinctTypedSolidColors, CentermostLayerHasColor,
)
from verifier.checks.structure_checks import LayerInsideFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

task = Task(
    id="task_03_glowing_orb",
    description="1 yellow center circle + 8 elliptical petals arranged radially around it.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=9),                                          # 0 ★ prompt: "1 yellow center circle and ... 8 elliptical petals"
        ], weight=0.20, critical=[0]),

        AlignmentRubric([
            RadialDistributionExcludeCentral(layer_type="ellipse", n=8,
                                             tolerance_deg=15.0),                     # 0 ★ prompt: "8 colored petals arranged radially around it"

        ], weight=0.30, critical=[0, 1]),

        ColorRubric([
            CentermostLayerHasColor(layer_type="ellipse",                             # 0 ★ prompt: "1 yellow center circle"
                                    expected_rgb={"r": 1.0, "g": 0.9, "b": 0.2},
                                    tolerance=0.28),
            DistinctTypedSolidColors(layer_type="ellipse", minimum=8,
                                     tolerance=0.12),                                 # 1 ★ prompt: "Each petal is a different color"
        ], weight=0.40, critical=[0, 1]),

        EventRubric([
            ToolUsed("ellipse"),                                                      # 0 ★ prompt: "Click Ellipse tool"
            EventTypeCountAtLeast("create_ellipse", minimum=9),                       # 1
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
