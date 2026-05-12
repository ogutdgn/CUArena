"""
Task 53 [DELETE] — Delete all red shapes; preserve all blue shapes.

Tests attribute-based filtering + batch deletion + preservation of non-targets.
Red = #FF0000, Blue = #0000FF. Shape types are mixed to ensure filtering by
color, not shape type.

Starting state is defined in fixture.json (loaded by the runner).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.structure_checks import (
    NamedLayerDeleted, NamedLayerExists, NoLayerCreated,
)
from verifier.checks.event_checks import EventTypeCountAtLeast

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
            NoLayerCreated(),
        ], weight=0.40, critical=[0, 1, 2, 3, 4]),

        EventRubric([
            EventTypeCountAtLeast("delete", minimum=1),
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=18),
)
