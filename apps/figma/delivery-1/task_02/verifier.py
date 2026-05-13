"""
Task 02 — Sunset stripe band (in-scope replacement).

5 horizontal rectangle bands stacked top-to-bottom in sunset colors:
deep purple → pink → orange → yellow → pale yellow.
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    LayersSameDimensions, LayersStacked, LayerAspectRatioGreaterThan,
)
from verifier.checks.fill_checks   import NthLayerByAxisInColorRange
from verifier.checks.structure_checks import LayerInsideFrame
from verifier.checks.event_checks  import ToolUsed

# Per-slot color ranges. Each {r,g,b} channel must land inside [min, max]
# (plus a small slop, set on the check). Ranges are authored to:
#   • be wide enough for human-eye variance in what counts as "deep purple", etc.
#   • be tight enough that default canvas grey (0.85,0.85,0.85) falls out.
#   • not overlap between adjacent slots (yellow.b max < pale_yellow.b min, etc.).
DEEP_PURPLE_RANGE = {"r": (0.15, 0.85), "g": (0.00, 0.40), "b": (0.35, 0.95)}  # includes magenta-violet
PINK_RANGE        = {"r": (0.80, 1.00), "g": (0.00, 0.75), "b": (0.50, 0.95)}  # includes hot magenta-pink
ORANGE_RANGE      = {"r": (0.85, 1.00), "g": (0.35, 0.75), "b": (0.00, 0.45)}
YELLOW_RANGE      = {"r": (0.80, 1.00), "g": (0.70, 1.00), "b": (0.00, 0.50)}
PALE_YELLOW_RANGE = {"r": (0.85, 1.00), "g": (0.85, 1.00), "b": (0.55, 0.95)}

task = Task(
    id="task_02_sunset_gradient",
    description="5 horizontal rectangle bands in sunset colors (purple, pink, orange, yellow, pale yellow).",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=5),                                       # 0 ★ prompt: "5 horizontal rectangles"
        ], weight=0.20, critical=[0]),

        AlignmentRubric([
            LayersStacked(layer_type="rectangle", axis="y", gap_px=0.0,
                          tolerance=8.0),                                             # 0 ★ prompt: "flush against each other" — strict (a 20px gap = visible band)
            LayerAspectRatioGreaterThan(layer_type="rectangle", ratio=2.0,
                                        axis="horizontal"),                           # 1 ★ prompt: "5 horizontal rectangle bands"
            LayersSameDimensions(layer_type="rectangle", tolerance=25.0),              # 2 ★ prompt: "Each rectangle is the same width and a similar height"
        ], weight=0.30, critical=[0, 1, 2]),

        ColorRubric([                                                                # ★ prompt: per-slot range check; partial credit per color
            NthLayerByAxisInColorRange("rectangle", index=0, rgb_range=DEEP_PURPLE_RANGE, sort_axis="y", label="deep purple"),
            NthLayerByAxisInColorRange("rectangle", index=1, rgb_range=PINK_RANGE,        sort_axis="y", label="pink"),
            NthLayerByAxisInColorRange("rectangle", index=2, rgb_range=ORANGE_RANGE,      sort_axis="y", label="orange"),
            NthLayerByAxisInColorRange("rectangle", index=3, rgb_range=YELLOW_RANGE,      sort_axis="y", label="yellow"),
            NthLayerByAxisInColorRange("rectangle", index=4, rgb_range=PALE_YELLOW_RANGE, sort_axis="y", label="pale yellow"),
        ], weight=0.30, critical=[]),

        StructureRubric([
            LayerInsideFrame("rectangle"),                                            # 0 ★ prompt: "Create a frame and inside it stack 5 ..."
        ], weight=0.10, critical=[]),

        EventRubric([
            ToolUsed("rectangle"),                                                    # 0 ★ prompt: "Click Rectangle tool" — duplicate/paste paths covered by ShapeCount outcome check
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=24),
)
