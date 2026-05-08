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
)
from verifier.checks.fill_checks     import (
    AllFillTypeIs, DistinctSolidColors, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.structure_checks import LayerInsideFrame, ChildCountAtLeast
from verifier.checks.event_checks    import ToolUsed, EventTypeCount, EventTypeCountAtLeast
from verifier.checks.property_checks import NoLayerFlipped, CornerRadiusFractionAtMost, LayerVisible
from verifier.checks.geometry_checks import LayerInFrontOf


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
            PolygonSidesEquals(sides=3),               # 3 ★ roof is a triangle
        ], weight=0.2, critical=[3]),

        # ── END-STATE: Alignment / Geometry (weight 0.2) ────
        # critical: round windows, flanking, roof-on-body, door-in-body,
        # window-on-body, frame-size, roof-x-centered, body-rotation,
        # frame-rotation, body/window/roof sizing, ellipse min-size are
        # prompt-critical (halve rubric on fail)
        AlignmentRubric([
            LayersAligned(layer_type="ellipse", axis="center_y", tolerance=8.0),     # 0
            LayersSameDimensions(layer_type="ellipse", tolerance=3.0),                # 1
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),                     # 2 ★ "round" windows
            LayersFlankLayer(flanker_type="ellipse", pivot_type="rectangle",
                             axis="x", tolerance=10.0),                               # 3 ★ "on either side"
            LayerEdgesAligned(                                                        # 4 ★ roof on body
                type_a="polygon", edge_a="bottom",
                type_b="rectangle", edge_b="top",
                tolerance=10.0,
            ),
            SmallerLayerInsideLarger(layer_type="rectangle", tolerance=4.0),          # 5 ★ door in body (largest)
            LayersOverlap(type_a="ellipse", type_b="rectangle"),                      # 6 ★ window on body
            FrameSizeEquals(width=1280, height=832, tolerance=10.0),                  # 7 ★ frame size
            LayerCenteredOnLayer(type_a="polygon", type_b="rectangle",                # 8 ★ roof x-centered on body
                                 tolerance=20.0, axis="x"),
            LayerRotationEquals(layer_type="rectangle", degrees=0, tolerance=2.0),    # 9 ★ body/door upright
            LayerRotationEquals(layer_type="frame", degrees=0, tolerance=2.0),        # 10 ★ frame upright
            AllLayerWidthFraction(inner_type="rectangle", parent_type="frame",        # 11 ★ body-vs-frame size sane
                                  min_frac=0.04, max_frac=0.80),
            AllLayerWidthFraction(inner_type="ellipse", parent_type="frame",          # 12 ★ window-vs-frame size sane
                                  min_frac=0.02, max_frac=0.20),
            AllLayerWidthFraction(inner_type="polygon", parent_type="frame",          # 13 ★ roof-vs-frame size sane
                                  min_frac=0.10, max_frac=0.80),
            LayerSizeAtLeast(layer_type="ellipse", min_w=10, min_h=10),               # 14 ★ no degenerate windows
            LayerRotationEquals(layer_type="polygon", degrees=0, tolerance=2.0),      # 15 ★ roof upright
            AllLayerBoundsInside(inner_type="rectangle", outer_type="frame",          # 16 ★ rects inside frame
                                 tolerance=4.0),
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame",            # 17 ★ ellipses inside frame
                                 tolerance=4.0),
            AllLayerBoundsInside(inner_type="polygon", outer_type="frame",            # 18 ★ roof inside frame
                                 tolerance=4.0),
            NoLayerFlipped(layer_type="rectangle"),                                   # 19 ★ body/door not mirrored
            LayerAreaRatioAtLeast(layer_type="rectangle", min_ratio=3.0),             # 20 ★ body dominates door
            SmallerLayerCenteredOnLargerEdge(                                         # 21 ★ door at body's bottom-center
                layer_type="rectangle", edge="bottom",
                edge_tolerance=20.0, axis_tolerance=80.0,
            ),
            LayerAboveLargestLayer(top_type="polygon", bottom_type="rectangle",       # 22 ★ roof on body (largest), not inside
                                   tolerance=10.0),
            AllLayerBoundsInside(inner_type="ellipse", outer_type="rectangle",        # 23 ★ windows fully inside body
                                 tolerance=4.0),
            CornerRadiusFractionAtMost(layer_type="rectangle", max_frac=0.4),         # 24 ★ no circle-like rectangles
            LayerInFrontOf(type_a="polygon", type_b="rectangle"),                     # 25 ★ roof drawn after body
        ], weight=0.2, critical=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]),

        # ── END-STATE: Color (weight 0.2) ───────────────────
        # critical: every shape has a solid fill, plus distinct-colors
        ColorRubric([
            AllFillTypeIs("rectangle", kind="solid"),             # 0 ★ every rect solid
            AllFillTypeIs("polygon",   kind="solid"),             # 1 ★ every polygon solid
            AllFillTypeIs("ellipse",   kind="solid"),             # 2 ★ every ellipse solid
            DistinctSolidColors(minimum=4, tolerance=0.05),       # 3 ★
            FillCountAtMost("rectangle", max_count=1),            # 4 ★ no stacked fills
            FillCountAtMost("polygon",   max_count=1),            # 5 ★
            FillCountAtMost("ellipse",   max_count=1),            # 6 ★
            FillOpacityAtLeast("rectangle", min_opacity=0.5),     # 7 ★ visible fills
            FillOpacityAtLeast("polygon",   min_opacity=0.5),     # 8 ★
            FillOpacityAtLeast("ellipse",   min_opacity=0.5),     # 9 ★
            LayerVisible("rectangle"),                            # 10 ★ alpha + visible + layer opacity
            LayerVisible("polygon"),                              # 11 ★
            LayerVisible("ellipse"),                              # 12 ★
        ], weight=0.2, critical=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),

        # ── END-STATE: Structure (weight 0.2) ───────────────
        # critical: shapes must all live in one frame (catches split-frame designs)
        StructureRubric([
            LayerInsideFrame("rectangle"),                        # 0 ★
            LayerInsideFrame("polygon"),                          # 1 ★
            LayerInsideFrame("ellipse"),                          # 2 ★
            ChildCountAtLeast("frame", minimum=5),                # 3 ★ all 5 shapes in one frame
        ], weight=0.2, critical=[0, 1, 2, 3]),

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
