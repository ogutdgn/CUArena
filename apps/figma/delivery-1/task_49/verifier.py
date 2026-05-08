"""
Task 49 — Tied ribbon shape (in-scope replacement, no gradient/outline-stroke).

1 pen-tool S-curve drawn with a thick (12px) dashed stroke acting as the ribbon.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast
from verifier.checks.stroke_checks import (
    StrokeExists, StrokeWeightEquals, StrokeIsDashed,
    AllStrokeExists, AllStrokeWeightAtMost,
)
from verifier.checks.geometry_checks import (
    LayerRotationEquals, LayerSizeAtLeast, LayerShortDimensionAtMost,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast
from verifier.checks.property_checks import NoLayerFlipped, LayerVisible

task = Task(
    id="task_49_decorative_ribbon",
    description="1 pen-tool S-curve with a thick (12px) dashed stroke acting as the ribbon.",
    rubrics=[
        # critical: pen-drawn vector required (exactly 1, not many)
        FundamentalsRubric([
            ShapeCount("vector", equals=1),    # 0 ★ exactly 1 ribbon
        ], weight=0.25, critical=[0]),

        # critical: vector upright, not tiny, not flipped
        AlignmentRubric([
            LayerSizeAtLeast(layer_type="vector", min_w=50, min_h=20),                  # 0 ★ no degenerate (S-curve must have actual extent)
            LayerShortDimensionAtMost(layer_type="vector", max_value=1500),             # 1 not absurd
            LayerRotationEquals(layer_type="vector", degrees=0, tolerance=15.0),        # 2 roughly upright (allow some lean)
            NoLayerFlipped(layer_type="vector"),                                        # 3 no mirror
            LayerVisible(layer_type="vector"),                                          # 4 visible
        ], weight=0.25, critical=[0]),

        # critical: 12px dashed stroke (all explicit prompt requirements)
        ColorRubric([
            AllStrokeExists("vector"),                                          # 0 ★ prompt: "thick (12px) dashed stroke" (stroke required)
            StrokeWeightEquals("vector", weight=12.0, tolerance=2.5),           # 1 ★ prompt: "(12px)"
            StrokeIsDashed("vector"),                                           # 2 ★ prompt: "dashed stroke"
            AllStrokeWeightAtMost("vector", max_weight=25.0),                   # 3 stroke not absurdly thick (>25 fails)
        ], weight=0.25, critical=[0, 1, 2]),

        # critical: pen tool mandated
        EventRubric([
            ToolUsed("pen"),                                              # 0 ★ prompt: "Pen tool"
            EventTypeCountAtLeast("create_vector", minimum=1),            # 1
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
