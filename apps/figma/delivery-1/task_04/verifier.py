"""
Task 04 — Color hexagon ring (in-scope replacement).

6 squares arranged in a hexagonal ring, each filled a different rainbow color
(red, yellow, green, cyan, blue, magenta).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayerIsSquare, LayersOnRing
from verifier.checks.fill_checks   import FillTypeIs, DistinctSolidColors
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast


task = Task(
    id="task_04_color_wheel",
    description="6 same-size squares arranged in a hexagonal ring, each filled a different rainbow color.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=6),                                                  # 0 ★ prompt: "6 same-size squares"
            LayerIsSquare(layer_type="rectangle", tolerance=8.0),                               # 1 ★ prompt: "squares"
        ], weight=0.20, critical=[0, 1]),

        AlignmentRubric([
            LayersOnRing(layer_type="rectangle", n=6,
                         angle_tolerance_deg=10.0, radius_tolerance_px=22.0,
                         min_radius_px=30.0),                                                   # 0 ★ prompt: "hexagonal ring"
        ], weight=0.50, critical=[0]),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),                                              # 0 ★ prompt: solid rainbow colors
            DistinctSolidColors(minimum=6, tolerance=0.12),                                     # 1 ★ prompt: "red, yellow, green, cyan, blue, magenta"
        ], weight=0.20, critical=[0, 1]),

        EventRubric([
            ToolUsed("rectangle"),                                                              # 0 ★ prompt: "Click Rectangle tool"
            EventTypeCountAtLeast("create_rectangle", minimum=6),                               # 1
        ], weight=0.10, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
