"""
Task 08 — Layered water waves (IN SCOPE).

Two pen-tool wave paths with bezier handles, in different blues, with rounded stroke caps.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayerAspectRatioGreaterThan, VectorsCurvedCountAtLeast
from verifier.checks.stroke_checks import DistinctStrokeColors, AllStrokeWeightsEqual
from verifier.checks.structure_checks import LayerInsideFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

task = Task(
    id="task_08_water_waves",
    description="Two pen-tool S-curve waves with bezier handles in different blue shades.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("vector", equals=2),                                                     # 0 ★ prompt: "two ... waves"
        ], weight=0.20, critical=[0]),

        AlignmentRubric([
            LayerAspectRatioGreaterThan(layer_type="vector", ratio=2.0, axis="horizontal"),     # 0 ★ prompt: "horizontal wave"
            VectorsCurvedCountAtLeast(minimum=2),                                               # 1 ★ prompt: "smooth Bezier curves ... with bezier handles"
        ], weight=0.35, critical=[0, 1]),

        ColorRubric([
            DistinctStrokeColors(minimum=2, tolerance=0.12),                                    # 0 ★ prompt: "different blue shades"
            AllStrokeWeightsEqual(layer_type="vector", weight=4.0, tolerance=2.5),              # 1 ★ prompt: "4px blue stroke"
        ], weight=0.25, critical=[0, 1]),

        StructureRubric([
            LayerInsideFrame("vector"),                                                         # 0 ★ prompt: "Create a 1000x300 frame"
        ], weight=0.10, critical=[0]),

        EventRubric([
            ToolUsed("pen"),                                                                    # 0 ★ prompt: "Use the Pen tool"
            EventTypeCountAtLeast("create_vector", minimum=2),                                  # 1
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=40),
)
