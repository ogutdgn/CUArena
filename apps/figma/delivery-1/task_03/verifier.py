"""Task 03 — Radial flower with petals (end-state only)."""

from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.color        import ColorRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks  import ShapeCount
from verifier.checks.geometry_checks import (
    RadialDistributionExcludeCentral,
    LayersSameDimensionsExcludeCentral,
    LayersTouchCentralLayer,
    LayersElongatedExcludeCentral,
    LayersSmallerThanCentralLayer,
    CentralLayerIsCircular,
)
from verifier.checks.fill_checks   import (
    DistinctTypedSolidColorsExcludeCentral, CentermostLayerHasColor,
)
from verifier.checks.structure_checks import LayerInsideFrame
from verifier.checks.event_checks  import ToolUsed

task = Task(
    id="task_03_glowing_orb",
    description="1 yellow center circle + 8 elliptical petals arranged radially around it.",
    rubrics=[
        FundamentalsRubric([
            ShapeCount("ellipse", equals=9),
        ], weight=0.25, critical=[0]),

        AlignmentRubric([
            RadialDistributionExcludeCentral(layer_type="ellipse", n=8,
                                             tolerance_deg=15.0),                     # 0 ★ prompt: "8 colored petals arranged radially around it"
            LayersSameDimensionsExcludeCentral(layer_type="ellipse",
                                               tolerance=6.0),                         # 1 ★ prompt: "All 8 petals are the same size"
            LayersTouchCentralLayer(layer_type="ellipse",
                                    tolerance=18.0),                                   # 2 ★ prompt: "each petal's inner end touches the outside of the center circle"
            CentralLayerIsCircular(layer_type="ellipse", tolerance=4.0),               # 3 ★ prompt: "center is a true circle (width ≈ height)"
            LayersElongatedExcludeCentral(layer_type="ellipse", min_ratio=1.5),        # 4 ★ prompt: "each petal is elongated — long axis ≥ 1.5× short axis"
            LayersSmallerThanCentralLayer(layer_type="ellipse", max_ratio=0.95),       # 5 ★ prompt: "each petal is smaller than the center circle"
        ], weight=0.30, critical=[0, 1, 2, 3, 4, 5]),

        ColorRubric([
            CentermostLayerHasColor(layer_type="ellipse",                             # 0 ★ prompt: "1 yellow center circle"
                                    expected_rgb={"r": 1.0, "g": 0.9, "b": 0.2},
                                    tolerance=0.28),
            DistinctTypedSolidColorsExcludeCentral(layer_type="ellipse", minimum=8,
                                                   tolerance=0.12),                   # 1 ★ prompt: "Each petal is a different color" — center excluded so it can match a petal
        ], weight=0.40, critical=[0, 1]),

        EventRubric([
            ToolUsed("ellipse"),                                                      # 0 ★ prompt: "Click Ellipse tool" — duplicate/paste paths covered by ShapeCount outcome check
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=1, lambda_=0.0),
)
