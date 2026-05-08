"""
Task 48 — Spiderweb pattern (SIMPLIFIED Medium → Easy).

Navy frame + 4 white radial lines (rotated 90° apart) + 2 concentric stroked
hexagons (white stroke).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.checks.shape_checks  import ShapeCount, ShapeCountAtLeast, PolygonSidesEquals
from verifier.checks.geometry_checks import (
    LayersConcentric, LayersEvenlyRotated, LayerRotationEquals,
    LayerAreaRatioAtLeast, LayerSizeAtLeast, AllLayerBoundsInside,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, SolidColorEquals, AllLayersHaveNoFill, FillOpacityAtLeast,
)
from verifier.checks.stroke_checks import (
    StrokeExists, StrokeColorEquals, AllStrokeExists, AllStrokeColorEquals,
    AllStrokeWeightAtMost,
)
from verifier.checks.structure_checks import LayerGroupAllInSameFrame
from verifier.checks.event_checks  import ToolUsed, EventTypeCount, EventTypeCountAtLeast
from verifier.checks.property_checks import NoLayerFlipped, LayerVisible

NAVY  = {"r": 0.05, "g": 0.10, "b": 0.45}
WHITE = {"r": 1.0,  "g": 1.0,  "b": 1.0}

task = Task(
    id="task_48_spiderweb",
    description="Navy frame + 4 white radial lines (90° apart) + 2 concentric white-stroked hexagons.",
    rubrics=[
        # critical: navy frame + 4 lines + 2 hexagons (6 sides)
        FundamentalsRubric([
            ShapeCountAtLeast("frame",   minimum=1),    # 0 ★ navy frame
            ShapeCountAtLeast("line",    minimum=4),    # 1 ★ 4 radial lines
            ShapeCount("polygon", equals=2),            # 2 ★ 2 concentric polygons
            PolygonSidesEquals(sides=6),                # 3 ★ hexagons (6 sides)
        ], weight=0.20, critical=[0, 1, 2, 3]),

        # critical: hexagons no-fill, lines 90° apart, hexagons concentric,
        # nothing flipped, frame upright, hexagons different sizes (true concentric)
        AlignmentRubric([
            AllLayersHaveNoFill(layer_type="polygon"),                                         # 0 ★ stroked-only hexagons
            LayersEvenlyRotated(layer_type="line", n=4, step_deg=90.0, tolerance_deg=10.0),   # 1 ★ 90° apart radials
            LayersConcentric(layer_type="line", tolerance=15.0),                               # radials share one center
            LayersConcentric(layer_type="polygon", tolerance=10.0),                            # 2 ★ concentric hexagons
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=2.0),                 # 3 ★ frame upright
            NoLayerFlipped(layer_type="frame"),                                                # 4 ★ frame not mirrored
            NoLayerFlipped(layer_type="line"),                                                 # 5 ★ lines not mirrored
            NoLayerFlipped(layer_type="polygon"),                                              # 6 ★ polygons not mirrored
            LayerAreaRatioAtLeast(layer_type="polygon", min_ratio=1.3),                        # 7 ★ hex sizes differ (true concentric)
            LayerSizeAtLeast(layer_type="line", min_w=20, min_h=0),                            # 8 ★ lines ≥ 20px long
            LayerSizeAtLeast(layer_type="polygon", min_w=20, min_h=20),                        # 9 ★ no degenerate hex
            AllLayerBoundsInside(inner_type="polygon", outer_type="frame", tolerance=4.0),     # 10 ★ hexagons inside frame
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),

        # critical: navy frame, white strokes on lines and hexagons (all of them),
        # everything visible, no transparency tricks
        ColorRubric([
            AllFillTypeIs("frame", kind="solid"),                                       # 0 ★
            SolidColorEquals(layer_type="frame", expected_rgb=NAVY, tolerance=0.30),    # 1 ★ navy frame
            AllStrokeExists("line"),                                                     # 2 ★ all lines stroked
            AllStrokeExists("polygon"),                                                  # 3 ★ all hexagons stroked
            AllStrokeColorEquals("line", expected_rgb=WHITE, tolerance=0.20),            # 4 ★ all line strokes white
            AllStrokeColorEquals("polygon", expected_rgb=WHITE, tolerance=0.20),         # 5 ★ all hex strokes white
            AllStrokeWeightAtMost("line", max_weight=10.0),                              # 6 ★ lines not absurd-thick
            FillOpacityAtLeast("frame", min_opacity=0.5),                                # 7 ★ frame visible fill
            LayerVisible("frame"),                                                       # 8 ★ frame visible
            LayerVisible("line"),                                                        # 9 ★ lines visible
            LayerVisible("polygon"),                                                     # 10 ★ hexagons visible
        ], weight=0.20, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),

        # critical: lines and polygons all in the same frame (catches split designs)
        StructureRubric([
            LayerGroupAllInSameFrame(layer_type="line", minimum=4),     # 0 ★ all lines in one frame
            LayerGroupAllInSameFrame(layer_type="polygon", minimum=2),  # 1 ★ all hexagons in same frame
        ], weight=0.20, critical=[0, 1]),

        # critical: line + polygon tools used
        EventRubric([
            ToolUsed("line"),                                          # 0 ★
            ToolUsed("polygon"),                                       # 1 ★
            EventTypeCountAtLeast("create_line", minimum=4),           # 2
            EventTypeCount("create_polygon", equals=2),                # 3
        ], weight=0.20, critical=[0, 1]),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
