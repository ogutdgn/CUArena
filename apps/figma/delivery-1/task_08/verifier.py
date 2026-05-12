"""Task 08 — Layered water waves (end-state only)."""

from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment import AlignmentRubric
from verifier.rubrics.color import ColorRubric
from verifier.rubrics.structure import StructureRubric
from verifier.rubrics.efficiency import EfficiencyRubric

from verifier.checks.shape_checks import ShapeCount
from verifier.checks.geometry_checks import LayerAspectRatioGreaterThan, VectorsCurvedCountAtLeast
from verifier.checks.stroke_checks import DistinctStrokeColors, AllStrokeWeightsEqual
from verifier.checks.structure_checks import (
    LayerInsideFrame,
    ChildCount,
    LayerTotalCount,
    NoUnexpectedLayerTypes,
)


task = Task(
    id="task_08_water_waves",
    description="Two smooth Bezier wave vectors in different blue shades.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("vector", equals=2),
        ], weight=0.25, critical=[0]),

        AlignmentRubric([
            LayerAspectRatioGreaterThan(layer_type="vector", ratio=2.0, axis="horizontal"),
            VectorsCurvedCountAtLeast(minimum=2),
        ], weight=0.25, critical=[0, 1]),

        ColorRubric([
            DistinctStrokeColors(minimum=2, tolerance=0.12),
            AllStrokeWeightsEqual(layer_type="vector", weight=4.0, tolerance=2.0),
        ], weight=0.25, critical=[0, 1]),

        StructureRubric([
            LayerInsideFrame("vector"),
            ChildCount("frame", equals=2),
            LayerTotalCount(equals=3),
            NoUnexpectedLayerTypes(allowed_types=["vector"]),
        ], weight=0.25, critical=[0, 1, 2, 3]),
    ],
    efficiency=EfficiencyRubric(target_turns=1, lambda_=0.0),
)
