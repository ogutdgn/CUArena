"""Task 03 — Radial flower with petals (end-state only)."""

from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment import AlignmentRubric
from verifier.rubrics.color import ColorRubric
from verifier.rubrics.structure import StructureRubric
from verifier.rubrics.efficiency import EfficiencyRubric

from verifier.checks.shape_checks import ShapeCount
from verifier.checks.geometry_checks import RadialDistributionExcludeCentral
from verifier.checks.fill_checks import DistinctTypedSolidColors, CentermostLayerHasColor
from verifier.checks.structure_checks import (
    LayerInsideFrame,
    ChildCount,
    LayerTotalCount,
    NoUnexpectedLayerTypes,
)


task = Task(
    id="task_03_glowing_orb",
    description="1 yellow center circle + 8 elliptical petals arranged radially around it.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=9),
        ], weight=0.25, critical=[0]),

        AlignmentRubric([
            RadialDistributionExcludeCentral(layer_type="ellipse", n=8, tolerance_deg=15.0),
        ], weight=0.25, critical=[0]),

        ColorRubric([
            CentermostLayerHasColor(
                layer_type="ellipse",
                expected_rgb={"r": 1.0, "g": 0.9, "b": 0.2},
                tolerance=0.28,
            ),
            DistinctTypedSolidColors(layer_type="ellipse", minimum=8, tolerance=0.12),
        ], weight=0.25, critical=[0, 1]),

        StructureRubric([
            LayerInsideFrame("ellipse"),
            ChildCount("frame", equals=9),
            LayerTotalCount(equals=10),
            NoUnexpectedLayerTypes(allowed_types=["ellipse"]),
        ], weight=0.25, critical=[0, 1, 2, 3]),
    ],
    efficiency=EfficiencyRubric(target_turns=1, lambda_=0.0),
)
