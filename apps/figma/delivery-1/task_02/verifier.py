"""
Task 02 — Sunset stripe band (in-scope replacement).

5 horizontal rectangle bands stacked top-to-bottom in sunset colors:
deep purple → pink → orange → yellow → pale yellow.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersSameDimensions, LayersStacked, LayerAspectRatioGreaterThan,
)
from verifier.checks.fill_checks   import LayersHaveColorOrder
from verifier.checks.structure_checks import LayerInsideFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

DEEP_PURPLE = {"r": 0.30, "g": 0.10, "b": 0.50}
PINK        = {"r": 1.00, "g": 0.50, "b": 0.70}
ORANGE      = {"r": 1.00, "g": 0.60, "b": 0.20}
YELLOW      = {"r": 1.00, "g": 0.90, "b": 0.20}
PALE_YELLOW = {"r": 1.00, "g": 1.00, "b": 0.70}

task = Task(
    id="task_02_sunset_gradient",
    description="5 horizontal rectangle bands in sunset colors (purple, pink, orange, yellow, pale yellow).",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=5),                                       # 0 ★ prompt: "5 horizontal rectangles"
        ], weight=0.20, critical=[0]),

        AlignmentRubric([
            LayersStacked(layer_type="rectangle", axis="y", gap_px=0.0,
                          tolerance=25.0),                                            # 0 ★ prompt: "stack 5 horizontal rectangles top-to-bottom" + "flush against each other"
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=2.0,
                                        axis="horizontal"),                           # 1 ★ prompt: "5 horizontal rectangle bands"
            LayersSameDimensions(layer_type="rectangle", tolerance=25.0),              # 2 ★ prompt: "Each rectangle is the same width and a similar height"
        ], weight=0.30, critical=[0, 1, 2]),

        ColorRubric([
            LayersHaveColorOrder(                                                     # 0 ★ prompt: "deep purple, pink, orange, yellow, pale yellow" top-to-bottom
                layer_type="rectangle",
                expected_rgbs=[DEEP_PURPLE, PINK, ORANGE, YELLOW, PALE_YELLOW],
                sort_axis="y",
                tolerance=0.25,
            ),
        ], weight=0.30, critical=[0]),

        StructureRubric([
            LayerInsideFrame("rectangle"),                                            # 0 ★ prompt: "Create a frame and inside it stack 5 ..."
        ], weight=0.10, critical=[]),

        EventRubric([
            ToolUsed("rectangle"),                                                    # 0 ★ prompt: "Click Rectangle tool"
            EventTypeCountAtLeast("create_rectangle", minimum=5),                     # 1
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
