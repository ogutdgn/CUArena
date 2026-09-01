"""Task 06 — Asterisk burst (end-state only)."""

from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment import AlignmentRubric
from verifier.rubrics.color import ColorRubric
from verifier.rubrics.structure import StructureRubric
from verifier.rubrics.efficiency import EfficiencyRubric

from verifier.checks.shape_checks import ShapeCount
from verifier.checks.geometry_checks import LinesRadialFromSharedEndpoint
from verifier.checks.stroke_checks import AllStrokesSameColor, StrokeExists
from verifier.checks.structure_checks import NoUnexpectedLayerTypes


task = Task(
    id="task_06_gold_star_exclude",
    description="8 lines radiating from a center point at 45° intervals.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("line", equals=8),
        ], weight=0.25, critical=[0]),

        AlignmentRubric([
            LinesRadialFromSharedEndpoint(
                n=8,
                center_tolerance_px=20.0,
                angle_tolerance_deg=12.0,
                min_length_px=10.0,
                length_tolerance_px=80.0,
            ),
        ], weight=0.25, critical=[0]),

        ColorRubric([
            StrokeExists(layer_type="line"),
            AllStrokesSameColor(layer_type="line", tolerance=0.10),
        ], weight=0.25, critical=[0, 1]),

        StructureRubric([
            NoUnexpectedLayerTypes(allowed_types=["line"], allow_frame=True),
        ], weight=0.25, critical=[0]),
    ],
    efficiency=EfficiencyRubric(target_turns=1, lambda_=0.0),
)
