"""Task 10 — Concentric squares (end-state only)."""

from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment import AlignmentRubric
from verifier.rubrics.color import ColorRubric
from verifier.rubrics.structure import StructureRubric
from verifier.rubrics.efficiency import EfficiencyRubric

from verifier.checks.shape_checks import ShapeCount
from verifier.checks.geometry_checks import LayersConcentric, LayersStrictlyNested
from verifier.checks.fill_checks import LayersAlternatingColorsByArea
from verifier.checks.structure_checks import NoUnexpectedLayerTypes


task = Task(
    id="task_10_apple_avatar",
    description="4 nested squares of decreasing size, alternating two colors, sharing center.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=4),
        ], weight=0.25, critical=[0]),

        AlignmentRubric([
            LayersConcentric(layer_type="rectangle", tolerance=25.0),
            LayersStrictlyNested(layer_type="rectangle", equals=4, tolerance_px=25.0, min_size_drop_px=4.0),
        ], weight=0.25, critical=[0, 1]),

        ColorRubric([
            LayersAlternatingColorsByArea(layer_type="rectangle", n_colors=2, tolerance=0.12),
        ], weight=0.25, critical=[0]),

        StructureRubric([
            NoUnexpectedLayerTypes(allowed_types=["rectangle"], allow_frame=True),
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=1, lambda_=0.0),
)
