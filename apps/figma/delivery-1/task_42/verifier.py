"""
Task 42 — Notification bell with badge (SIMPLIFIED Medium → Easy).

Pen-tool bell silhouette (yellow-gold) + small clapper circle + red badge with
2px white stroke.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCountAtLeast
from verifier.checks.geometry_checks import (
    LayerIsCircular, AllLayersAreCircular, FrameSizeEquals,
    AllLayerBoundsInside, LayerSizeAtLeast, LayerRotationEquals,
    LayersOverlap, LayerSmallerThanLayer, AllLayerWidthFraction,
    FrameCountAtMost, LayerNextTo,
)
from verifier.checks.fill_checks   import (
    AllFillTypeIs, AllSolidColorEquals, DistinctSolidColors,
    DistinctTypedSolidColors, FillCountAtMost, FillOpacityAtLeast,
)
from verifier.checks.stroke_checks import StrokeExists, StrokeWeightEquals, StrokeColorEquals, StrokeRendersVisible
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast
from verifier.checks.property_checks import NoLayerFlipped, LayerVisible
from verifier.checks.structure_checks import LayerGroupAllInSameFrame
from verifier.checks.page_checks   import LayerOnPage

GOLD  = {"r": 1.0, "g": 0.80, "b": 0.10}
WHITE = {"r": 1.0, "g": 1.0,  "b": 1.0}

task = Task(
    id="task_42_bell_icon",
    description="Pen bell (yellow-gold) + clapper circle + red badge circle with 2px white stroke.",
    rubrics=[
        # critical: pen-drawn bell vector + clapper/badge ellipses are prompt-mandated
        FundamentalsRubric([
            ShapeCountAtLeast("vector",  minimum=1),   # 0 ★ prompt: "pen-drawn bell silhouette"
            ShapeCountAtLeast("ellipse", minimum=2),   # 1 ★ prompt: "small clapper circle" + "red badge circle"
        ], weight=0.20, critical=[0, 1]),

        # critical: clapper-below-bell + ellipses are circles (prompt-explicit).
        # Order note: LayerNextTo placed AFTER LayersOverlap so its position handler wins.
        AlignmentRubric([
            LayerIsCircular(layer_type="ellipse", tolerance=3.0),                                   # 0 ★ prompt: "clapper circle" / "badge circle"
            AllLayersAreCircular(layer_type="ellipse", tolerance=4.0),                              # 1 EVERY ellipse round
            FrameSizeEquals(width=1280, height=832, tolerance=25.0),                                # 2 frame size
            AllLayerBoundsInside(inner_type="vector",  outer_type="frame", tolerance=10.0),         # 3 bell inside frame
            AllLayerBoundsInside(inner_type="ellipse", outer_type="frame", tolerance=10.0),         # 4 ellipses inside frame
            LayerSizeAtLeast(layer_type="vector",  min_w=40, min_h=40),                             # 5 bell not degenerate
            LayerSizeAtLeast(layer_type="ellipse", min_w=8,  min_h=8),                              # 6 ellipses not degenerate
            AllLayerWidthFraction(inner_type="vector", parent_type="frame",                          # 7 bell sane vs frame
                                   min_frac=0.05, max_frac=0.50),
            AllLayerWidthFraction(inner_type="ellipse", parent_type="frame",                         # 8 ellipses sane vs frame
                                   min_frac=0.005, max_frac=0.10),
            LayerRotationEquals(layer_type="vector",  degrees=0, tolerance=5.0),                    # 9 bell upright
            LayerRotationEquals(layer_type="ellipse", degrees=0, tolerance=5.0),                    # 10 ellipses upright
            LayerRotationEquals(layer_type="frame",   degrees=0, tolerance=5.0),                    # 11 frame upright
            NoLayerFlipped(layer_type="vector"),                                                    # 12 bell not mirrored
            NoLayerFlipped(layer_type="ellipse"),                                                   # 13 ellipses not mirrored
            LayersOverlap(type_a="ellipse", type_b="vector"),                                       # 14 ellipses sit on bell
            LayerSmallerThanLayer(smaller_type="ellipse", larger_type="vector", max_frac=0.85),     # 15 ellipses smaller than bell
            FrameCountAtMost(maximum=1),                                                            # 16 exactly one top-level frame
            LayerNextTo(type_a="ellipse", type_b="vector", side="below", tolerance=20.0),           # 17 ★ prompt: "clapper circle below"
        ], weight=0.20, critical=[0, 17]),

        # critical: gold bell, white badge stroke (prompt-explicit colors).
        ColorRubric([
            AllSolidColorEquals(layer_type="vector", expected_rgb=GOLD, tolerance=0.28),     # 0 ★ prompt: "yellow-gold fill"
            StrokeColorEquals("ellipse", expected_rgb=WHITE, tolerance=0.28),                # 1 ★ prompt: "white stroke"
            DistinctTypedSolidColors(layer_type="ellipse", minimum=2, tolerance=0.12),       # 2 clapper vs red badge
            AllFillTypeIs("vector",  kind="solid"),                                          # 3 visible solid bell
            AllFillTypeIs("ellipse", kind="solid"),                                          # 4 visible solid ellipses
            DistinctSolidColors(minimum=3, tolerance=0.15),                                  # 5 overall distinct
            FillCountAtMost("vector",  max_count=1),                                         # 6 no stacked fills on bell
            FillCountAtMost("ellipse", max_count=1),                                         # 7 no stacked fills on ellipses
            FillOpacityAtLeast("vector",  min_opacity=0.5),                                  # 8 visible bell fill
            FillOpacityAtLeast("ellipse", min_opacity=0.5),                                  # 9 visible ellipse fills
            LayerVisible("vector"),                                                           # 10 alpha+visible+opacity for bell
            LayerVisible("ellipse"),                                                          # 11 alpha+visible+opacity for ellipses
            StrokeExists("ellipse"),                                                         # 12 stroke around badge
            StrokeWeightEquals("ellipse", weight=2.0, tolerance=2.5),                        # 13 prompt: "2px white stroke"
            StrokeRendersVisible("ellipse"),                                                  # 14 stroke actually renders
        ], weight=0.20, critical=[0, 1]),

        # structure: bell + ellipses live inside one frame on page 0 (implicit, soft)
        StructureRubric([
            LayerGroupAllInSameFrame(layer_type="vector",  minimum=1),  # 0 shapes share one frame
            LayerGroupAllInSameFrame(layer_type="ellipse", minimum=2),  # 1 ellipses inside the frame
            LayerOnPage(layer_type="vector",  page_index=0),            # 2 bell on page 0
            LayerOnPage(layer_type="ellipse", page_index=0),            # 3 ellipses on page 0
        ], weight=0.20, critical=[]),

        # critical: pen + ellipse tools must be used (prompt-mandated)
        EventRubric([
            ToolUsed("pen"),                                            # 0 pen tool used
            ToolUsed("ellipse"),                                        # 1 ellipse tool used
            EventTypeCountAtLeast("create_vector",  minimum=1),         # 2
            EventTypeCountAtLeast("create_ellipse", minimum=2),         # 3
        ], weight=0.20, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
