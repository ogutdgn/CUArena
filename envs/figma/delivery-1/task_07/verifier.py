"""Task 07 — Layered mountain range (end-state only)."""

from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment import AlignmentRubric
from verifier.rubrics.color import ColorRubric
from verifier.rubrics.structure import StructureRubric
from verifier.rubrics.efficiency import EfficiencyRubric

from verifier.checks.shape_checks import ShapeCount
from verifier.checks.geometry_checks import LayersOverlap, LayerAspectRatioGreaterThan
from verifier.checks.fill_checks import FillTypeIs, DistinctSolidColors, AllSolidColorsNearGray
from verifier.checks.structure_checks import (
    LayerInsideFrame,
    ChildCount,
    LayerTotalCount,
    NoUnexpectedLayerTypes,
)


task = Task(
    id="task_07_mountain_range",
    description="Two overlapping mountain vector paths in different gray shades.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("vector", equals=2),
        ], weight=0.25, critical=[0]),

        AlignmentRubric([
            LayersOverlap(type_a="vector", type_b="vector"),
            LayerAspectRatioGreaterThan(layer_type="vector", ratio=1.8, axis="horizontal"),
        ], weight=0.25, critical=[0, 1]),

        ColorRubric([
            FillTypeIs("vector", kind="solid"),
            DistinctSolidColors(minimum=2, tolerance=0.12),
            AllSolidColorsNearGray(layer_type="vector", tolerance=0.14),
        ], weight=0.25, critical=[0, 1, 2]),

        StructureRubric([
            LayerInsideFrame("vector"),
            ChildCount("frame", equals=2),
            LayerTotalCount(equals=3),
            NoUnexpectedLayerTypes(allowed_types=["vector"]),
        ], weight=0.25, critical=[0, 1, 2, 3]),
    ],
    efficiency=EfficiencyRubric(target_turns=1, lambda_=0.0),
)
