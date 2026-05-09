"""
Task 50 — Star inside square (in-scope replacement, no image fill/mask).

1 large square + 1 5-point star centered on top, contrasting fills,
4px white stroke around the star (substitute for the masked-region border).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, StarPointsEquals, StarInnerRatioEquals
from verifier.checks.geometry_checks import (
    LayerBoundsInside, LayerCenteredOnLayer, LayerIsSquare,
    LayerRotationEquals, LayerSizeAtLeast, LayerSmallerThanLayer,
    LayerShortDimensionAtMost, LayerInFrontOf,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, DistinctSolidColors, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.stroke_checks import (
    StrokeWeightEquals,
    AllStrokeExists, AllStrokeColorEquals,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
from verifier.checks.property_checks import (
    NoLayerFlipped, LayerVisible, CornerRadiusFractionAtMost,
)

WHITE = {"r": 1.0, "g": 1.0, "b": 1.0}

task = Task(
    id="task_50_album_cover",
    description="1 large square + 1 5-point star centered on top, contrasting fills, 4px white stroke on star.",
    rubrics=[
        # critical: 1 square + 1 5-point star (counts + points are explicit)
        FundamentalsRubric([
            ShapeCount("rectangle", equals=1),    # 0 ★ prompt: "a square"
            ShapeCount("star",      equals=1),    # 1 ★ prompt: "a centered 5-point star"
            StarPointsEquals(points=5),           # 2 ★ prompt: "5-point star"
        ], weight=0.25, critical=[1, 2]),

        # critical: square is square, star centered on it, smaller, on top.
        AlignmentRubric([
            LayerCenteredOnLayer(type_a="star", type_b="rectangle", tolerance=20.0),        # 0 ★ prompt: "a centered 5-point star"
            LayerIsSquare(layer_type="rectangle", tolerance=10.0),                          # 1 ★ prompt: "a square"
            LayerInFrontOf(type_a="star", type_b="rectangle"),                              # 2 ★ prompt: "5-point star on top"
            LayerSmallerThanLayer(smaller_type="star", larger_type="rectangle",
                                  max_frac=0.85),                                            # 3 star smaller (implies "centered ... on top")
            LayerBoundsInside(inner_type="star", outer_type="rectangle", tolerance=10.0),   # 4 star bounds inside square
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=5.0),          # 5 square upright
            LayerRotationEquals(layer_type="star",      degrees=0, tolerance=10.0),         # 6 star upright (some lean ok)
            NoLayerFlipped(layer_type="rectangle"),                                         # 7 no mirror
            NoLayerFlipped(layer_type="star"),                                              # 8 no mirror
            LayerSizeAtLeast(layer_type="rectangle", min_w=40, min_h=40),                   # 9 no degenerate
            LayerSizeAtLeast(layer_type="star", min_w=20, min_h=20),                        # 10 no degenerate
            LayerShortDimensionAtMost(layer_type="rectangle", max_value=2000),              # 11 not absurd
            StarInnerRatioEquals(ratio=0.4, tolerance=0.3),                                 # 12 reasonable spike
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.5),               # 13 not round-rect
        ], weight=0.25, critical=[0, 1, 2]),

        # critical: contrasting (distinct) colors + white stroke around star + visibility
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                       # 0 ★ shape needs visible fill
            AllFillTypeIs("star",      kind="solid"),                                       # 1 (combined w/ #0)
            DistinctSolidColors(minimum=2, tolerance=0.15),                                 # 2 ★ prompt: "contrasting colors"
            AllStrokeExists("star"),                                                        # 3 star stroke (substitute prop)
            StrokeWeightEquals("star", weight=4.0, tolerance=2.5),                          # 4 4px
            AllStrokeColorEquals("star", expected_rgb=WHITE, tolerance=0.28),               # 5 white stroke
            FillCountAtMost("rectangle", max_count=1),                                      # 6 no stacked fills
            FillOpacityAtLeast("rectangle", min_opacity=0.5),                               # 7 visible
            LayerVisible("rectangle"),                                                       # 8
        ], weight=0.25, critical=[0, 2]),

        # critical: rectangle + star tools used
        EventRubric([
            ToolUsed("rectangle"),                              # 0 ★ prompt: "Rectangle tool"
            ToolUsed("star"),                                   # 1 ★ prompt: "Star tool"
            EventTypeCount("create_rectangle", equals=1),       # 2
            EventTypeCount("create_star",      equals=1),       # 3
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
