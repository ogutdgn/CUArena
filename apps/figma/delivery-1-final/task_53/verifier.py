"""
Task 53 [DELETE] — Delete all red shapes; preserve all blue shapes.

Tests attribute-based filtering + batch deletion + preservation of non-targets.
Red = #FF0000, Blue = #0000FF. Shape types are mixed to ensure filtering by
color, not shape type.

Starting state is defined in fixture.json (loaded by the runner).
"""
from __future__ import annotations

from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.structure_checks import (
    NamedLayerDeleted, NamedLayerExists, LayerTotalCount,
)

task = Task(
    id="task_53_delete_all_red",
    description="Delete all 5 red shapes; preserve all 5 blue shapes.",

    rubrics=[
        FundamentalsRubric([
            NamedLayerDeleted(name="red_01"),
            NamedLayerDeleted(name="red_02"),
            NamedLayerDeleted(name="red_03"),
            NamedLayerDeleted(name="red_04"),
            NamedLayerDeleted(name="red_05"),
        ], weight=0.50, critical=[0, 1, 2, 3, 4]),

        StructureRubric([
            NamedLayerExists(name="blue_01"),
            NamedLayerExists(name="blue_02"),
            NamedLayerExists(name="blue_03"),
            NamedLayerExists(name="blue_04"),
            NamedLayerExists(name="blue_05"),
            # End-state only: frame + 5 blue layers should be all that remains.
            LayerTotalCount(equals=6),
        ], weight=0.50, critical=[0, 1, 2, 3, 4, 5]),
    ],
    efficiency=EfficiencyRubric(target_turns=1, lambda_=0.0),
)
