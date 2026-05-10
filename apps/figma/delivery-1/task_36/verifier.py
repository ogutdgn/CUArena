"""
Task 36 — Vintage frame: outer rectangle + smaller inner rectangle, both centered.

Per the prompt: "Draw an outer rectangle and a smaller inner rectangle inside it.
Both rectangles share the same center. Each can have its own fill color."
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersConcentric, LayersStrictlyNested, LayerSizeAtLeast,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.property_checks import (
    LayerVisible, NoLayerFlipped, CornerRadiusFractionAtMost,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount


task = Task(
    id="task_36_polaroid",
    description="2 rectangles, smaller inner inside outer, both share the same center, each with own solid fill.",
    rubrics=[
        # critical: prompt mandates exactly 2 rectangles
        FundamentalsRubric([
            ShapeCount("rectangle", equals=2),   # 0 ★ prompt: "an outer rectangle and a smaller inner rectangle"
        ], weight=0.25, critical=[0]),

        # critical: 2 rectangles strictly nested (smaller inside larger) AND
        # sharing the same center. LayersStrictlyNested maps directly to the
        # "smaller inner rectangle inside it" prompt phrase, replacing the older
        # SmallerLayerInsideLarger + LayerAreaRatioAtLeast + LayerSmallerThanLayer
        # combo.
        AlignmentRubric([
            LayersStrictlyNested(layer_type="rectangle", equals=2,                       # 0 ★ prompt: "smaller inner rectangle inside it"
                                 tolerance_px=10.0, min_size_drop_px=10.0),
            LayersConcentric(layer_type="rectangle", tolerance=15.0),                    # 1 ★ prompt: "share the same center"
            LayerSizeAtLeast(layer_type="rectangle", min_w=20, min_h=20),                # 2 no degenerate rects
            NoLayerFlipped(layer_type="rectangle"),                                      # 3
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.5),            # 4 still rectangles, not pills
        ], weight=0.25, critical=[0, 1]),

        # critical: solid fills (prompt: "Each can have its own fill color")
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),                                    # 0 ★ prompt: "Each can have its own fill color"
            FillCountAtMost("rectangle", max_count=1),                                   # 1 no stacked fills
            FillOpacityAtLeast("rectangle", min_opacity=0.5),                            # 2 visible fills
            LayerVisible("rectangle"),                                                   # 3 visible layers
        ], weight=0.25, critical=[0]),

        # event: must use rectangle tool (kept soft per playbook)
        EventRubric([
            ToolUsed("rectangle"),                          # 0
            EventTypeCount("create_rectangle", equals=2),   # 1
        ], weight=0.25, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=15),
)
