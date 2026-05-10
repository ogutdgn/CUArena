"""
Task 43 — Compass rose (IN SCOPE).

Sand-colored circle + 4 triangles arranged 90° apart (cardinal directions, distinct colors)
+ small gold center pivot circle.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, PolygonSidesEquals
from verifier.checks.geometry_checks import (
    LayersSameDimensions, LayersEvenlyRotated, LayerIsCircular,
    AllLayersAreCircular, FrameSizeEquals, AllLayerBoundsInside,
    LayerSizeAtLeast, LayerRotationEquals, AllLayerWidthFraction,
    LayerSmallerThanLayer, FrameCountAtMost, LayerAreaRatioAtLeast,
    LayerCenteredOnLayer, RadialDistribution,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, DistinctSolidColors, DistinctTypedSolidColors,
    FillCountAtMost, FillOpacityAtLeast, SolidColorEquals,
)
from verifier.checks.event_checks  import ToolUsed, EventTypeCount
from verifier.checks.property_checks import NoLayerFlipped, LayerVisible
from verifier.checks.structure_checks import LayerGroupAllInSameFrame
from verifier.checks.page_checks   import LayerOnPage

GOLD = {"r": 0.85, "g": 0.65, "b": 0.13}
SAND = {"r": 0.90, "g": 0.80, "b": 0.60}

task = Task(
    id="task_43_compass_rose",
    description="Sand circle + 4 N/E/S/W triangles (90° apart, distinct colors) + gold center pivot.",
    rubrics=[
        # critical: prompt mandates exactly 2 ellipses (sand + gold center) and 4 triangles.
        FundamentalsRubric([
            ShapeCount("ellipse", equals=2),    # 0 ★ prompt: "sand-colored circle" + "small gold center circle"
            ShapeCount("polygon", equals=4),    # 1 ★ prompt: "4 thin triangles pointing N/E/S/W"
            PolygonSidesEquals(sides=3),        # 2 ★ prompt: "triangles"
        ], weight=0.20, critical=[0, 1, 2]),

        # critical: triangles same size + 90° apart, ellipses round, frame size, in-frame, sane sizing.
        AlignmentRubric([
            LayersEvenlyRotated(layer_type="polygon", n=4, step_deg=90.0, tolerance_deg=10.0),   # 0 ★ prompt: "pointing N/E/S/W"
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),                                # 1 ★ prompt: "sand-colored circle" / "gold center circle"
            RadialDistribution(layer_type="polygon", n=4, tolerance_deg=18.0,                    # 2 ★ prompt: "from center"
                                radius_tolerance_frac=0.5),
            LayersSameDimensions(layer_type="polygon", tolerance=8.0),                           # 3 matched triangles
            AllLayersAreCircular(layer_type="ellipse", tolerance=4.0),                           # 4 EVERY ellipse round
            FrameSizeEquals(width=1280, height=832, tolerance=25.0),                             # 5 frame size
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame", tolerance=10.0),      # 6 ellipses inside frame
            AllLayerBoundsInside(inner_type="polygon", outer_type="frame", tolerance=10.0),      # 7 triangles inside frame
            LayerSizeAtLeast(layer_type="ellipse", min_w=10, min_h=10),                          # 8 no degenerate ellipse
            LayerSizeAtLeast(layer_type="polygon", min_w=10, min_h=20),                          # 9 no degenerate triangle
            AllLayerWidthFraction(inner_type="ellipse", parent_type="frame",                      # 10 ellipses sane vs frame
                                  min_frac=0.005, max_frac=0.50),
            AllLayerWidthFraction(inner_type="polygon", parent_type="frame",                      # 11 triangles sane
                                  min_frac=0.005, max_frac=0.50),
            LayerRotationEquals(layer_type="ellipse", degrees=0, tolerance=5.0),                 # 12 ellipses upright
            LayerRotationEquals(layer_type="frame",   degrees=0, tolerance=5.0),                 # 13 frame upright
            NoLayerFlipped(layer_type="ellipse"),                                                # 14 ellipses not mirrored
            NoLayerFlipped(layer_type="polygon"),                                                # 15 triangles not mirrored
            LayerSmallerThanLayer(smaller_type="ellipse", larger_type="ellipse", max_frac=0.85), # 16 center much smaller than sand
            LayerAreaRatioAtLeast(layer_type="ellipse", min_ratio=2.0),                          # 17 sand dominates center
            LayerCenteredOnLayer(type_a="ellipse", type_b="ellipse", tolerance=30.0, axis="both"),# 18 gold center sits on sand
            FrameCountAtMost(maximum=1),                                                         # 19 exactly one top-level frame
        ], weight=0.20, critical=[0, 1, 2]),

        # critical: distinct colors, gold center, sane fills.
        ColorRubric([
            DistinctTypedSolidColors(layer_type="polygon", minimum=2, tolerance=0.12),           # 0 ★ prompt: "N triangle is red; E/S/W are gray"
            SolidColorEquals(layer_type="ellipse", expected_rgb=GOLD, tolerance=0.28),           # 1 ★ prompt: "gold center"
            AllFillTypeIs("polygon", kind="solid"),                                              # 2 visible solid triangles
            AllFillTypeIs("ellipse", kind="solid"),                                              # 3 visible solid ellipses
            DistinctSolidColors(minimum=4, tolerance=0.15),                                      # 4 sand+gold+red+gray (4 distinct)
            DistinctTypedSolidColors(layer_type="ellipse", minimum=2, tolerance=0.12),           # 5 sand vs gold center
            FillCountAtMost("polygon", max_count=1),                                             # 6 no stacked fills
            FillCountAtMost("ellipse", max_count=1),                                             # 7 no stacked fills
            FillOpacityAtLeast("polygon", min_opacity=0.5),                                      # 8 visible fills
            FillOpacityAtLeast("ellipse", min_opacity=0.5),                                      # 9 visible fills
            LayerVisible("polygon"),                                                              # 10 alpha+visible+opacity
            LayerVisible("ellipse"),                                                              # 11
        ], weight=0.20, critical=[0, 1]),

        # structure: shapes share a frame (implicit, soft)
        StructureRubric([
            LayerGroupAllInSameFrame(layer_type="ellipse", minimum=2),  # 0 ellipses in one frame
            LayerGroupAllInSameFrame(layer_type="polygon", minimum=4),  # 1 triangles in same frame
            LayerOnPage(layer_type="ellipse", page_index=0),            # 2 ellipses on page 0
            LayerOnPage(layer_type="polygon", page_index=0),            # 3 polygons on page 0
        ], weight=0.20, critical=[]),

        # critical: ellipse + polygon tools mandated by prompt
        EventRubric([
            ToolUsed("ellipse"),                            # 0 ellipse tool used
            ToolUsed("polygon"),                            # 1 polygon tool used
            EventTypeCount("create_ellipse", equals=2),     # 2
            EventTypeCount("create_polygon", equals=4),     # 3
        ], weight=0.20, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
