"""
Task 10 — Concentric squares (in-scope replacement).

4 nested squares of decreasing size, alternating two colors, all sharing the same center.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import LayersConcentric, LayersStrictlyNested
from verifier.checks.fill_checks   import LayersAlternatingColorsByArea
from verifier.checks.event_checks  import ToolUsed, EventTypeCountAtLeast

task = Task(
    id="task_10_apple_avatar",
    description="4 nested squares of decreasing size, alternating two colors, sharing center.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=4),                                                  # 0 ★ prompt: "4 ... nested squares"
        ], weight=0.15, critical=[0]),

        AlignmentRubric([
            LayersConcentric(layer_type="rectangle", tolerance=25.0),                           # 0 ★ prompt: "shared center"
            LayersStrictlyNested(layer_type="rectangle", equals=4,
                                 tolerance_px=25.0, min_size_drop_px=4.0),                       # 1 ★ prompt: "nested ... decreasing size"
        ], weight=0.25, critical=[0, 1]),

        ColorRubric([
            LayersAlternatingColorsByArea(layer_type="rectangle", n_colors=2,
                                          tolerance=0.12),                                      # 0 ★ prompt: "alternating two colors"
        ], weight=0.50, critical=[0]),

        EventRubric([
            ToolUsed("rectangle"),                                                              # 0 ★ prompt: "Click Rectangle tool"
            EventTypeCountAtLeast("create_rectangle", minimum=4),                               # 1
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
