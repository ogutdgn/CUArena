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

from verifier.checks.shape_checks    import ShapeCount
from verifier.checks.geometry_checks import (
    LayersAligned, LayersSymmetricX, LayersSameDimensions, LayerEdgesAligned,
    LayerBoundsInside, LayersOverlap, FrameSizeEquals, LayersFlankLayer,
)
from verifier.checks.fill_checks     import FillTypeIs, DistinctSolidColors
from verifier.checks.structure_checks import LayerInsideFrame, ChildCountAtLeast
from verifier.checks.event_checks    import ToolUsed, EventTypeCount, EventTypeCountAtLeast


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
        FundamentalsRubric([
            ShapeCount("rectangle", equals=2),
            ShapeCount("ellipse",   equals=2),
            ShapeCount("polygon",   equals=1),
        ], weight=0.2),

        # ── END-STATE: Alignment / Geometry (weight 0.2) ────
        AlignmentRubric([
            LayersAligned(layer_type="ellipse", axis="center_y", tolerance=8.0),
            LayersSameDimensions(layer_type="ellipse", tolerance=3.0),
            LayersFlankLayer(flanker_type="ellipse", pivot_type="rectangle", axis="x", tolerance=10.0),
            LayerEdgesAligned(
                type_a="polygon", edge_a="bottom",
                type_b="rectangle", edge_b="top",
                tolerance=10.0,
            ),
            LayerBoundsInside(inner_type="rectangle", outer_type="rectangle", tolerance=4.0),
            LayersOverlap(type_a="ellipse", type_b="rectangle"),
            FrameSizeEquals(width=1280, height=832, tolerance=10.0),
        ], weight=0.2),

        # ── END-STATE: Color (weight 0.2) ───────────────────
        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            FillTypeIs("polygon",   kind="solid"),
            FillTypeIs("ellipse",   kind="solid"),
            DistinctSolidColors(minimum=4, tolerance=0.05),
        ], weight=0.2),

        # ── END-STATE: Structure (weight 0.2) ───────────────
        StructureRubric([
            LayerInsideFrame("rectangle"),
            LayerInsideFrame("polygon"),
            LayerInsideFrame("ellipse"),
            ChildCountAtLeast("frame", minimum=5),
        ], weight=0.2),

        # ── ACTION-LOG: Event (weight 0.2) ──────────────────
        EventRubric([
            ToolUsed("rectangle"),
            ToolUsed("ellipse"),
            ToolUsed("polygon"),
            EventTypeCount("create_rectangle", equals=2),
            EventTypeCount("create_ellipse",   equals=2),
            EventTypeCount("create_polygon",   equals=1),
            EventTypeCountAtLeast("set_fill_color", minimum=4),
        ], weight=0.2),
    ],

    # ── ACTION-LOG: Efficiency multiplier ────────────────────
    efficiency=EfficiencyRubric(target_turns=30),
)
