"""Task 09 — 12-color swatch grid (end-state only)."""

from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment import AlignmentRubric
from verifier.rubrics.color import ColorRubric
from verifier.rubrics.structure import StructureRubric
from verifier.rubrics.efficiency import EfficiencyRubric

from verifier.checks.shape_checks import ShapeCount
from verifier.checks.geometry_checks import LayersSameDimensions, LayersInGrid, LayerAllSquare
from verifier.checks.fill_checks import DistinctTypedSolidColors
from verifier.checks.structure_checks import (
    LayerInsideFrame,
    ChildCount,
    LayerTotalCount,
    NoUnexpectedLayerTypes,
)


task = Task(
    id="task_09_brand_palette",
    description="4x3 grid of 12 same-size squares, each filled a different color.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=12),
        ], weight=0.25, critical=[0]),

        AlignmentRubric([
            LayersInGrid(layer_type="rectangle", rows=3, cols=4, tolerance=25.0),
            LayerAllSquare(layer_type="rectangle", tolerance=8.0),
            LayersSameDimensions(layer_type="rectangle", tolerance=25.0),
        ], weight=0.25, critical=[0, 1, 2]),

        ColorRubric([
            DistinctTypedSolidColors(layer_type="rectangle", minimum=12, tolerance=0.08),
        ], weight=0.25, critical=[0]),

        StructureRubric([
            LayerInsideFrame("rectangle"),
            ChildCount("frame", equals=12),
            LayerTotalCount(equals=13),
            NoUnexpectedLayerTypes(allowed_types=["rectangle"]),
        ], weight=0.25, critical=[0, 1, 2, 3]),
    ],
    efficiency=EfficiencyRubric(target_turns=1, lambda_=0.0),
)
