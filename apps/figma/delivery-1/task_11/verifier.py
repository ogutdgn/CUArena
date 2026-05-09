"""
Task 11 — Triangle pyramid stack (in-scope replacement).

3 triangles of decreasing size all centered together (largest at back, smallest at front),
alternating two colors, forming a layered pyramid look.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount, PolygonSidesEquals
from verifier.checks.geometry_checks import LayersConcentric, LayersStrictlyNested
from verifier.checks.fill_checks   import DistinctTypedSolidColors
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

task = Task(
    id="task_11_pressed_button",
    description="3 triangles of decreasing size centered together, alternating two colors.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("polygon", equals=3),                                          # 0 ★ prompt: "3 nested triangles"
            PolygonSidesEquals(sides=3),                                              # 1 ★ prompt: "Polygon tool with 3 sides"
        ], weight=0.15, critical=[0, 1]),

        AlignmentRubric([
            LayersConcentric(layer_type="polygon", tolerance=12.0),                   # 0 ★ prompt: "same center"
            LayersStrictlyNested(layer_type="polygon", equals=3,
                                 tolerance_px=8.0, min_size_drop_px=4.0),             # 1 ★ prompt: "3 nested triangles ... decreasing size"
        ], weight=0.25, critical=[0, 1]),

        # Only 3 polygons → the alternating-by-area primitive (needs ≥4) doesn't apply.
        # Keep the simple "≥2 distinct fills" combo, ★-flagged on the prompt's color phrase.
        ColorRubric([
            DistinctTypedSolidColors(layer_type="polygon", minimum=2,
                                     tolerance=0.12),                                 # 0 ★ prompt: "alternating two colors"
        ], weight=0.50, critical=[0]),

        EventRubric([
            ToolUsed("polygon"),                                                      # 0 ★ prompt: "Click Polygon tool"
            EventTypeCountAtLeast("create_polygon", minimum=3),                       # 1
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
