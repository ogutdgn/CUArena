"""Task 05 — Plus-sign emblem (end-state only)."""

from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment import AlignmentRubric
from verifier.rubrics.color import ColorRubric
from verifier.rubrics.structure import StructureRubric
from verifier.rubrics.efficiency import EfficiencyRubric

from verifier.checks.shape_checks import ShapeCount
from verifier.checks.geometry_checks import LayersAligned, LayersHaveAspectMix
from verifier.checks.fill_checks import LayersAllSameColor
from verifier.checks.structure_checks import NoUnexpectedLayerTypes


task = Task(
    id="task_05_red_heart_union",
    description="2 perpendicular rectangles crossed at center forming a plus sign, same color.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=2),
        ], weight=0.25, critical=[0]),

        AlignmentRubric([
            LayersAligned(layer_type="rectangle", axis="center_x", tolerance=25.0),
            LayersAligned(layer_type="rectangle", axis="center_y", tolerance=25.0),
            LayersHaveAspectMix(
                layer_type="rectangle",
                horizontal_count=1,
                vertical_count=1,
                ratio=2.0,
            ),
        ], weight=0.25, critical=[0, 1, 2]),

        ColorRubric([
            LayersAllSameColor(layer_type="rectangle", tolerance=0.12),
        ], weight=0.25, critical=[0]),

        StructureRubric([
            NoUnexpectedLayerTypes(allowed_types=["rectangle"], allow_frame=True),
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=1, lambda_=0.0),
)
