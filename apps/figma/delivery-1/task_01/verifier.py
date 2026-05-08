"""
Comprehensive Task 1 verifier (two-story house) — normalized to max score 1.0.

5 rubrics, each weighted to 0.2 (sum = 1.0):
  1. Fundamentals — shape primitive counts
  2. Alignment    — geometric relationships between layers
  3. Color        — fill type and distinct color count
  4. Structure    — layer organization (inside frame, child counts)
  5. Event        — action log: tools used, creation events emitted

Score:
  base_score = sum of rubric scores             (max 1.0)
  final      = base_score × efficiency_mult     (max 1.0)

Run:
  python run.py --task house_task_comprehensive --log logs/house_sample.json
"""

from verifier.types  import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric

from verifier.checks.shape_checks    import ShapeCount, PolygonSidesEquals
from verifier.checks.geometry_checks import (
    LayersAligned, LayersSymmetricX, LayersSameDimensions, LayerEdgesAligned,
    LayersOverlap, FrameSizeEquals, LayersFlankLayer,
    LayerIsCircular, LayerCenteredOnLayer, LayerRotationEquals,
    LayerSizeAtLeast, AllLayerWidthFraction, SmallerLayerInsideLarger,
    AllLayerBoundsInside, LayerAreaRatioAtLeast,
    SmallerLayerCenteredOnLargerEdge, LayerAboveLargestLayer,
    LayerInFrontOfLargestLayer, PolygonCornersAligned,
)
from verifier.checks.fill_checks     import (
    AllFillTypeIs, DistinctSolidColors, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.structure_checks import LayerInsideFrame, ChildCountAtLeast
from verifier.checks.event_checks    import ToolUsed, EventTypeCount, EventTypeCountAtLeast
from verifier.checks.property_checks import NoLayerFlipped, CornerRadiusFractionAtMost, LayerVisible

task = Task(
    id="house_task_comprehensive",
    description=(
        "Two-story house: 2 rectangles (body + door), 2 ellipses (windows), 1 polygon (roof). "
        "Windows aligned, same size, symmetric. Roof bottom touches body top. "
        "Distinct colors used. Shapes inside one frame. Correct tools used in action log."
    ),

    # 5 rubrics, each weighted to 0.2 → sum maxes at 1.0
    rubrics=[
        # ── END-STATE: Fundamentals (weight 0.2) ────────────
        # critical: roof is a triangle (3 sides) — prompt-explicit
        FundamentalsRubric([
            ShapeCount("rectangle", equals=2),         # 0
            ShapeCount("ellipse",   equals=2),         # 1
            ShapeCount("polygon",   equals=1),         # 2
            PolygonSidesEquals(sides=3),               # 3 ★ prompt: "triangle roof"
        ], weight=0.2, critical=[3]),

        # ── END-STATE: Alignment / Geometry (weight 0.2) ────
        AlignmentRubric([
            LayersAligned(layer_type="ellipse", axis="center_y", tolerance=12.0),    # 0
            LayersSameDimensions(layer_type="ellipse", tolerance=8.0),                # 1
            LayerIsCircular(layer_type="ellipse", tolerance=8.0),                     # 2 ★ prompt: "2 small round windows"
            LayersFlankLayer(flanker_type="ellipse", pivot_type="rectangle",
                             axis="x", tolerance=15.0),                               # 3 ★ prompt: "on either side of the door"
            PolygonCornersAligned(polygon_type="polygon", rect_type="rectangle",      # 4 ★ prompt: "spanning the body width"
                                  tolerance=18.0),
            SmallerLayerInsideLarger(layer_type="rectangle", tolerance=10.0),         # 5 ★ prompt: "front door rectangle on the body"
            LayersOverlap(type_a="ellipse", type_b="rectangle"),                      # 6
            FrameSizeEquals(width=1280, height=832, tolerance=25.0),                  # 7
            LayerCenteredOnLayer(type_a="polygon", type_b="rectangle",                # 8
                                 tolerance=20.0, axis="x"),
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=5.0),    # 9
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=5.0),        # 10
            AllLayerWidthFraction(inner_type="rectangle", parent_type="frame",        # 11
                                  min_frac=0.04, max_frac=0.80),
            AllLayerWidthFraction(inner_type="ellipse", parent_type="frame",          # 12
                                  min_frac=0.02, max_frac=0.20),
            AllLayerWidthFraction(inner_type="polygon", parent_type="frame",          # 13
                                  min_frac=0.10, max_frac=0.80),
            LayerSizeAtLeast(layer_type="ellipse", min_w=10, min_h=10),               # 14
            LayerRotationEquals(layer_type="polygon", degrees=0, tolerance=5.0),      # 15
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",          # 16
                                 tolerance=10.0),
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame",            # 17
                                 tolerance=10.0),
            AllLayerBoundsInside(inner_type="polygon", outer_type="frame",            # 18
                                 tolerance=10.0),
            NoLayerFlipped(layer_type="rectangle"),                                   # 19
            LayerAreaRatioAtLeast(layer_type="rectangle", min_ratio=2.0),             # 20
            SmallerLayerCenteredOnLargerEdge(                                         # 21
                layer_type="rectangle", edge="bottom",
                edge_tolerance=20.0, axis_tolerance=80.0,
            ),
            LayerAboveLargestLayer(top_type="polygon", bottom_type="rectangle",       # 22 ★ prompt: "triangle roof on top"
                                   tolerance=25.0),
            AllLayerBoundsInside(inner_type="ellipse", outer_type="rectangle",        # 23
                                 tolerance=10.0),
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.5),         # 24
            LayerInFrontOfLargestLayer(type_a="polygon", type_b="rectangle"),         # 25
        ], weight=0.2, critical=[2, 3, 4, 5, 22]),

        # ── END-STATE: Color (weight 0.2) ───────────────────
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),             # 0 ★ prompt: "different fill color to the body, roof, door, and windows"
            AllFillTypeIs("polygon",   kind="solid"),             # 1 ★ prompt: "different fill color to the body, roof, door, and windows"
            AllFillTypeIs("ellipse",   kind="solid"),             # 2 ★ prompt: "different fill color to the body, roof, door, and windows"
            DistinctSolidColors(minimum=4, tolerance=0.12),       # 3 ★ prompt: "different fill color to the body, roof, door, and windows"
            FillCountAtMost("rectangle", max_count=1),            # 4
            FillCountAtMost("polygon",   max_count=1),            # 5
            FillCountAtMost("ellipse",   max_count=1),            # 6
            FillOpacityAtLeast("rectangle", min_opacity=0.5),     # 7
            FillOpacityAtLeast("polygon",   min_opacity=0.5),     # 8
            FillOpacityAtLeast("ellipse",   min_opacity=0.5),     # 9
            LayerVisible("rectangle"),                            # 10
            LayerVisible("polygon"),                              # 11
            LayerVisible("ellipse"),                              # 12
        ], weight=0.2, critical=[0, 1, 2, 3]),

        # ── END-STATE: Structure (weight 0.2) ───────────────
        StructureRubric([
            LayerInsideFrame("rectangle"),                        # 0 ★ prompt: "Inside the frame, build a simple house"
            LayerInsideFrame("polygon"),                          # 1
            LayerInsideFrame("ellipse"),                          # 2
            ChildCountAtLeast("frame", minimum=5),                # 3 ★ prompt: "Inside the frame, build a simple house: ... body ... roof ... door ... 2 small round windows"
        ], weight=0.2, critical=[0, 3]),

        # ── ACTION-LOG: Event (weight 0.2) ──────────────────
        EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("ellipse"),
            ToolUsed("polygon"),
            EventTypeCountAtLeast("create_rectangle", minimum=2),
            EventTypeCountAtLeast("create_ellipse",   minimum=2),
            EventTypeCountAtLeast("create_polygon",   minimum=1),
            EventTypeCountAtLeast("set_fill_color", minimum=4),
        ], weight=0.2),
    ],

    # ── ACTION-LOG: Efficiency multiplier ────────────────────
    efficiency=EfficiencyRubric(target_turns=30),
)
