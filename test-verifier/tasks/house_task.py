from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.alignment    import AlignmentRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.shape_checks    import ShapeCount
from verifier.checks.geometry_checks import (
    LayersAligned, LayersSymmetricX, LayersSameDimensions, LayerEdgesAligned
)

task = Task(
    id="house_task",
    description=(
        "1 polygon (roof), 2 ellipses (windows), 2 rectangles (body + door). "
        "Windows aligned, same size, symmetric. Roof bottom touches house body top."
    ),
    rubrics=[
        FundamentalsRubric([
            ShapeCount("polygon",   equals=1),
            ShapeCount("ellipse",   equals=2),
            ShapeCount("rectangle", equals=2),
        ]),
        AlignmentRubric([
            # windows on the same horizontal line
            LayersAligned(layer_type="ellipse", axis="center_y", tolerance=8.0),
            # windows are the same size as each other
            LayersSameDimensions(layer_type="ellipse", tolerance=3.0),
            # windows placed symmetrically left-right
            LayersSymmetricX(layer_type="ellipse", tolerance=15.0),
            # roof bottom edge meets house body top edge
            LayerEdgesAligned(
                type_a="polygon", edge_a="bottom",
                type_b="rectangle", edge_b="top",
                tolerance=10.0,
            ),
        ]),
    ],
    efficiency=EfficiencyRubric(target_turns=30),
)
