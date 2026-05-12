"""
Task 52 [READ] — Find and click the gift box.

Tests visual category recognition in a cluttered scene. The gift box is
the only composite shape (group with ribbons + bow); distractors are
plain solid rectangles.

Starting state is defined in fixture.json (loaded by the runner).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.selection_checks import LayerSelected, ClickedLayer
from verifier.checks.structure_checks import NoLayerCreated, NoLayerDeleted, NoLayerMoved
from verifier.checks.event_checks    import EventTypeCountAtLeast

TARGET = "gift_box"

task = Task(
    id="task_52_read_click_giftbox",
    description="Click the gift box in a scene of plain colored shapes.",

    rubrics=[
        FundamentalsRubric([
            ClickedLayer(layer_name=TARGET),
            LayerSelected(layer_name=TARGET),
        ], weight=0.70, critical=[0]),

        StructureRubric([
            NoLayerCreated(),
            NoLayerDeleted(),
            NoLayerMoved(tolerance=2.0),
        ], weight=0.20, critical=[0, 1, 2]),

        EventRubric([
            EventTypeCountAtLeast("click_select", minimum=1),
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=4),
)
