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
        # critical: 8-point star + 1 circle (counts + points)
        FundamentalsRubric([
            ShapeCount("star",    equals=1),    # 0 single-star count
            StarPointsEquals(points=8),         # 1 ★ prompt: "8-point ... star"
            ShapeCount("ellipse", equals=1),    # 2 ★ prompt: "smaller centered cream circle"
        ], weight=0.25, critical=[1, 2]),

        # critical: circle centered on star, smaller, in front (on top), round.
        AlignmentRubric([
            LayerCenteredOnLayer(type_a="ellipse", type_b="star", tolerance=20.0),          # 0 ★ prompt: "centered cream circle"
            LayerSmallerThanLayer(smaller_type="ellipse", larger_type="star",
                                  max_frac=0.85),                                            # 1 ★ prompt: "smaller centered ... circle"
            LayerInFrontOf(type_a="ellipse", type_b="star"),                                # 2 ★ prompt: "circle on top"
            LayerIsCircular(layer_type="ellipse", tolerance=8.0),                           # 3 ★ prompt: "circle"
            LayerBoundsInside(inner_type="ellipse", outer_type="star", tolerance=10.0),     # 4 circle inside star bounds
            LayerRotationEquals(layer_type="star",    degrees=0, tolerance=5.0),            # 5 star upright
            LayerRotationEquals(layer_type="ellipse", degrees=0, tolerance=5.0),            # 6 circle upright
            NoLayerFlipped(layer_type="star"),                                              # 7 no mirror
            NoLayerFlipped(layer_type="ellipse"),                                           # 8 no mirror
            LayerSizeAtLeast(layer_type="star",    min_w=40, min_h=40),                     # 9 no degenerate star
            LayerSizeAtLeast(layer_type="ellipse", min_w=15, min_h=15),                     # 10 no degenerate circle
            LayerShortDimensionAtMost(layer_type="star",    max_value=900),                 # 11 star not absurdly huge
            StarInnerRatioEquals(ratio=0.5, tolerance=0.3),                                 # 12 reasonable spike profile
        ], weight=0.25, critical=[0, 1, 2, 3]),

        # critical: warm orange star + cream circle (specific colors), all visible
        ColorRubric([
            AllFillTypeIs("star",    kind="solid"),                                              # 0 ★ visible solid star
            AllFillTypeIs("ellipse", kind="solid"),                                              # 1 visible solid ellipse
            SolidColorEquals(layer_type="star",    expected_rgb=WARM_ORANGE, tolerance=0.35),    # 2 ★ prompt: "warm-orange" — loose tol for modifier+color
            SolidColorEquals(layer_type="ellipse", expected_rgb=CREAM,       tolerance=0.35),    # 3 ★ prompt: "cream circle" — loose tol for modifier+color
            FillCountAtMost("star", max_count=1),                                                # 4 no stacked fills
            FillOpacityAtLeast("star", min_opacity=0.5),                                         # 5 visible fill
            LayerVisible("star"),                                                                # 6 alpha+visible+opacity
        ], weight=0.25, critical=[0, 2, 3]),

        # critical: star + ellipse tools used
        EventRubric([
            ToolUsed("star"),                               # 0 ★ prompt: "Star tool"
            ToolUsed("ellipse"),                            # 1 ★ prompt: "Ellipse tool"
            EventTypeCount("create_star",    equals=1),     # 2
            EventTypeCount("create_ellipse", equals=1),     # 3
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
