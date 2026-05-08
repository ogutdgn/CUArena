"""
Task 47 — Sunburst stamp badge (SIMPLIFIED Medium → Easy).

8-point warm-orange star + smaller centered cream circle on top.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount, StarPointsEquals, StarInnerRatioEquals
from verifier.checks.geometry_checks import (
    LayerBoundsInside, LayerCenteredOnLayer, LayerIsCircular,
    LayerRotationEquals, LayerSizeAtLeast, LayerSmallerThanLayer,
    LayerShortDimensionAtMost, LayerInFrontOf,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
from verifier.checks.property_checks import NoLayerFlipped, LayerVisible

WARM_ORANGE = {"r": 1.0, "g": 0.50, "b": 0.10}
CREAM       = {"r": 1.0, "g": 0.95, "b": 0.80}

task = Task(
    id="task_47_sunburst_badge",
    description="8-point warm-orange star + smaller centered cream circle on top.",
    rubrics=[
        # critical: 1 star with 8 points + 1 circle
        FundamentalsRubric([
            ShapeCount("star",    equals=1),    # 0 ★ prompt: "8-point ... star"
            StarPointsEquals(points=8),         # 1 ★ prompt: "8-point star"
            ShapeCount("ellipse", equals=1),    # 2 prompt: "circle" (covered by 0/1 + alignment)
        ], weight=0.25, critical=[0, 1]),

        # critical: circle centered on star, inside bounds, round, smaller than star,
        # both upright and not flipped, star not too tiny/giant, ellipse on top
        AlignmentRubric([
            LayerCenteredOnLayer(type_a="ellipse", type_b="star", tolerance=20.0),          # 0 ★ prompt: "centered cream circle"
            LayerBoundsInside(inner_type="ellipse", outer_type="star", tolerance=10.0),     # 1 ★ prompt: "circle on top" (inside star)
            LayerIsCircular(layer_type="ellipse", tolerance=8.0),                           # 2 ★ prompt: "circle"
            LayerSmallerThanLayer(smaller_type="ellipse", larger_type="star",
                                  max_frac=0.85),                                           # 3 ★ prompt: "smaller centered ... circle"
            LayerRotationEquals(layer_type="star",    degrees=0, tolerance=5.0),            # 4 star upright
            LayerRotationEquals(layer_type="ellipse", degrees=0, tolerance=5.0),            # 5 circle upright
            NoLayerFlipped(layer_type="star"),                                              # 6 no mirror
            NoLayerFlipped(layer_type="ellipse"),                                           # 7 no mirror
            LayerSizeAtLeast(layer_type="star",    min_w=40, min_h=40),                     # 8 no degenerate star
            LayerSizeAtLeast(layer_type="ellipse", min_w=15, min_h=15),                     # 9 no degenerate circle
            LayerShortDimensionAtMost(layer_type="star",    max_value=900),                 # 10 star not absurdly huge
            StarInnerRatioEquals(ratio=0.5, tolerance=0.3),                                 # 11 reasonable spike profile
            LayerInFrontOf(type_a="ellipse", type_b="star"),                                # 12 ★ prompt: "on top"
        ], weight=0.25, critical=[0, 1, 2, 3, 12]),

        # critical: warm orange star + cream circle (specific colors), all visible
        ColorRubric([
            AllFillTypeIs("star",    kind="solid"),                                              # 0 ★ every shape needs visible fill
            AllFillTypeIs("ellipse", kind="solid"),                                              # 1 (combined w/ #0)
            SolidColorEquals(layer_type="star",    expected_rgb=WARM_ORANGE, tolerance=0.28),    # 2 ★ prompt: "warm-orange star"
            SolidColorEquals(layer_type="ellipse", expected_rgb=CREAM,       tolerance=0.28),    # 3 ★ prompt: "cream circle"
            FillCountAtMost("star",    max_count=1),                                             # 4 no stacked
            FillCountAtMost("ellipse", max_count=1),                                             # 5
            FillOpacityAtLeast("star",    min_opacity=0.5),                                      # 6
            FillOpacityAtLeast("ellipse", min_opacity=0.5),                                      # 7
            LayerVisible("star"),                                                                # 8
            LayerVisible("ellipse"),                                                             # 9
        ], weight=0.25, critical=[0, 2, 3]),

        # critical: star + ellipse tools used
        EventRubric([
            ToolUsed("star"),                               # 0 ★ prompt: "Star tool"
            ToolUsed("ellipse"),                            # 1
            EventTypeCount("create_star",    equals=1),     # 2
            EventTypeCount("create_ellipse", equals=1),     # 3
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
