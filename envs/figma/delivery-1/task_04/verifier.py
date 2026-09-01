"""Task 04 — Color hexagon ring (end-state only)."""

from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment import AlignmentRubric
from verifier.rubrics.color import ColorRubric
from verifier.rubrics.structure import StructureRubric
from verifier.rubrics.efficiency import EfficiencyRubric

from verifier.checks.shape_checks import ShapeCount
from verifier.checks.geometry_checks import LayerIsSquare, LayersOnRing
from verifier.checks.fill_checks import FillTypeIs, DistinctSolidColors
from verifier.checks.structure_checks import (
    LayerInsideFrame,
    ChildCount,
    LayerTotalCount,
    NoUnexpectedLayerTypes,
)


task = Task(
    id="task_04_color_wheel",
    description="6 same-size squares arranged in a hexagonal ring, each filled a different rainbow color.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("rectangle", equals=6),
            LayerIsSquare(layer_type="rectangle", tolerance=8.0),
        ], weight=0.25, critical=[0, 1]),

        AlignmentRubric([
            LayersOnRing(
                layer_type="rectangle",
                n=6,
                angle_tolerance_deg=10.0,
                radius_tolerance_px=5.0,
                min_radius_px=30.0,
            ),
        ], weight=0.25, critical=[0]),

        ColorRubric([
            FillTypeIs("rectangle", kind="solid"),
            DistinctSolidColors(minimum=6, tolerance=0.12),
        ], weight=0.25, critical=[0, 1]),

        StructureRubric([
            LayerInsideFrame("rectangle"),
            ChildCount("frame", equals=6),
            LayerTotalCount(equals=7),
            NoUnexpectedLayerTypes(allowed_types=["rectangle"]),
        ], weight=0.25, critical=[0, 1, 2, 3]),
    ],
    efficiency=EfficiencyRubric(target_turns=1, lambda_=0.0),
)
