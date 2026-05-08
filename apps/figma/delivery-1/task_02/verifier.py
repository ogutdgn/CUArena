"""
Task 02 — Sunset stripe band (in-scope replacement).

5 horizontal rectangle bands stacked top-to-bottom in sunset colors:
deep purple → pink → orange → yellow → pale yellow.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersSameDimensions, LayersAligned, LayersStacked, LayerAspectRatioGreaterThan,
    AllLayerBoundsInside, LayerSizeAtLeast, LayerRotationEquals,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, DistinctSolidColors, LayersHaveColorOrder,
    FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.property_checks import (
    LayerVisible, NoLayerFlipped, CornerRadiusFractionAtMost,
)
from verifier.checks.structure_checks import LayerInsideFrame, LayerGroupAllInSameFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
task = Task(
    id="task_02_sunset_gradient",
    description="5 horizontal rectangle bands in sunset colors (purple, pink, orange, yellow, pale yellow).",
    rubrics=[
        # critical: exact count of 5 — prompt-explicit
        FundamentalsRubric([
            ShapeCount("rectangle", equals=5),                                       # 0 ★ prompt: "5 horizontal rectangles"
        ], weight=0.25, critical=[0]),

        AlignmentRubric([
            LayersSameDimensions(layer_type="rectangle", tolerance=8.0),             # 0 ★ prompt: "Each rectangle is the same width and a similar height"
            LayersAligned(layer_type="rectangle", axis="center_x", tolerance=12.0),  # 1 ★ prompt: "click Align horizontal centers"
            LayersStacked(layer_type="rectangle", axis="y", gap_px=0.0, tolerance=12.0),  # 2 ★ prompt: "stack 5 horizontal rectangles top-to-bottom" + "flush against each other"
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=2.0, axis="horizontal"),  # 3 ★ prompt: "5 horizontal rectangles"
            LayerInsideFrame("rectangle"),                                           # 4
            LayerGroupAllInSameFrame("rectangle", minimum=5),                        # 5
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame", tolerance=10.0),  # 6
            LayerSizeAtLeast(layer_type="rectangle", min_w=80.0, min_h=20.0),        # 7
            LayerRotationEquals(layer_type="rectangle", degrees=0.0, tolerance=5.0), # 8
            NoLayerFlipped(layer_type="rectangle"),                                  # 9
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.5),        # 10
            LayerRotationEquals(layer_type="frame", degrees=0.0, tolerance=5.0),     # 11
        ], weight=0.25, critical=[0, 1, 2, 3]),

        # critical: solid fills + 5 distinct colors + sunset color order — prompt-explicit
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                # 0 ★ prompt: solid fill bands
            DistinctSolidColors(minimum=5, tolerance=0.12),                          # 1 ★ prompt: "sunset colors: deep purple, pink, orange, yellow, pale yellow"
            LayersHaveColorOrder(                                                    # 2 ★ prompt: "purple, pink, orange, yellow, pale yellow" top-to-bottom
                layer_type="rectangle",
                expected_rgbs=[
                    {"r": 0.30, "g": 0.10, "b": 0.50},   # deep purple
                    {"r": 1.00, "g": 0.50, "b": 0.70},   # pink
                    {"r": 1.00, "g": 0.60, "b": 0.20},   # orange
                    {"r": 1.00, "g": 0.90, "b": 0.20},   # yellow
                    {"r": 1.00, "g": 1.00, "b": 0.70},   # pale yellow
                ],
                sort_axis="y",
                tolerance=0.25,
            ),
            LayerVisible(layer_type="rectangle", min_opacity=0.5, min_alpha=0.5),    # 3
            FillCountAtMost(layer_type="rectangle", max_count=1),                    # 4
            FillOpacityAtLeast(layer_type="rectangle", min_opacity=0.5),             # 5
        ], weight=0.25, critical=[0, 1, 2]),

        # critical: rectangle tool used — prompt-explicit
        EventRubric([
            ToolUsed("rectangle"),                                                   # 0 ★ prompt: "Click Rectangle tool"
            EventTypeCount("create_rectangle", equals=5),                            # 1
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
