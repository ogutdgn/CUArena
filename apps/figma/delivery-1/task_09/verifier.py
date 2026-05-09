"""
Task 09 — 12-color swatch grid (in-scope replacement).

12 same-size squares arranged in a 4x3 grid, each filled a different color.
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
    LayersSameDimensions, LayersInGrid, LayerAllSquare,
)
from verifier.checks.fill_checks   import DistinctTypedSolidColors
from verifier.checks.structure_checks import LayerInsideFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

task = Task(
    id="task_09_brand_palette",
    description="4x3 grid of 12 same-size squares, each filled a different color.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=12),                                       # 0 ★ prompt: "12 same-size squares"
        ], weight=0.15, critical=[0]),

        AlignmentRubric([
            LayersInGrid(layer_type="rectangle", rows=3, cols=4, tolerance=12.0),     # 0 ★ prompt: "4x3 grid"
            LayerAllSquare(layer_type="rectangle", tolerance=8.0),                    # 1 ★ prompt: "squares" (w≈h)
            LayersSameDimensions(layer_type="rectangle", tolerance=8.0),              # 2 ★ prompt: "12 same-size squares"
        ], weight=0.30, critical=[0, 1, 2]),

        ColorRubric([
            DistinctTypedSolidColors(layer_type="rectangle", minimum=12,
                                     tolerance=0.08),                                 # 0 ★ prompt: "Each square is filled a different color"
        ], weight=0.30, critical=[0]),

        StructureRubric([
            LayerInsideFrame(layer_type="rectangle"),                                 # 0 ★ prompt: "Inside a frame"
        ], weight=0.15, critical=[0]),

        EventRubric([
            ToolUsed("rectangle"),                                                    # 0 ★ prompt: "Click Rectangle tool"
            EventTypeCountAtLeast("create_rectangle", minimum=12),                    # 1
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=36),
)
