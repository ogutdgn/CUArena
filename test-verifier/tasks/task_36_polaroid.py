"""
Task 36 — Vintage frame: outer rectangle + smaller inner rectangle, both centered.

Per the prompt: "Draw an outer rectangle and a smaller inner rectangle inside it.
Both rectangles share the same center. Each can have its own fill color."

The legacy implementation also tilted the outer ~5° with a drop shadow; those
remain as soft (non-critical) bonus checks but the simpler prompt requires only
2 rectangles, inner-inside-outer, same center, both with solid fills.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.effect       import EffectRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    SmallerLayerInsideLarger, LayerRotationEquals, LayersConcentric,
    LayerAreaRatioAtLeast, LayerSizeAtLeast, LayerSmallerThanLayer,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.effect_checks import DropShadowExists
from verifier.checks.property_checks import (
    LayerVisible, NoLayerFlipped, CornerRadiusFractionAtMost,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount

WHITE = {"r": 1.0, "g": 1.0, "b": 1.0}

task = Task(
    id="task_36_polaroid",
    description="2 rectangles, smaller inner inside outer, both share the same center, each with own solid fill.",
    rubrics=[
        # critical: prompt mandates exactly 2 rectangles
        FundamentalsRubric([
            ShapeCount("rectangle", equals=2),   # 0 ★ "outer ... smaller inner"
        ], weight=0.2, critical=[0]),

        # critical: smaller-inside-larger is prompt-explicit ("inside it"),
        # both share same center, inner is smaller, non-degenerate, not flipped,
        # no extreme corner-radius (still rectangles).
        AlignmentRubric([
            SmallerLayerInsideLarger(layer_type="rectangle", tolerance=8.0),               # 0 ★ "inside it"
            LayersConcentric(layer_type="rectangle", tolerance=15.0),                      # 1 ★ "share the same center"
            LayerAreaRatioAtLeast(layer_type="rectangle", min_ratio=1.05),                 # 2 ★ inner truly smaller
            LayerSmallerThanLayer(smaller_type="rectangle", larger_type="rectangle",       # 3 ★ inner < 95% of outer
                                  max_frac=0.95),
            LayerSizeAtLeast(layer_type="rectangle", min_w=20, min_h=20),                  # 4 ★ no degenerate rects
            NoLayerFlipped(layer_type="rectangle"),                                        # 5 ★ rects not flipped
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.4),              # 6 ★ rectangles not circles
            LayerRotationEquals(layer_type="rectangle", degrees=5.0, tolerance=3.0),       # 7  legacy tilt (soft)
        ], weight=0.2, critical=[0, 1, 2, 3, 4, 5, 6]),

        # critical: solid fills, visible, no stacking, no opacity tricks
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                       # 0 ★ both solid
            SolidColorEquals(layer_type="rectangle", expected_rgb=WHITE, tolerance=0.15),   # 1  legacy outer-white (soft)
            FillCountAtMost("rectangle", max_count=1),                                      # 2 ★ no stacked fills
            FillOpacityAtLeast("rectangle", min_opacity=0.5),                               # 3 ★ visible fills
            LayerVisible("rectangle"),                                                      # 4 ★ visible layers
        ], weight=0.2, critical=[0, 2, 3, 4]),

        EffectRubric([
            DropShadowExists("rectangle"),                                                  # 0  legacy shadow (soft)
        ], weight=0.2),

        # critical: must use rectangle tool
        EventRubric([
            ToolUsed("rectangle"),                          # 0 ★
            EventTypeCount("create_rectangle", equals=2),   # 1
        ], weight=0.2, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
