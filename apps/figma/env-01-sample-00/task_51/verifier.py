"""
Task 51 [READ] — Count blue rectangles, click matching number label.

Tests visual identification (color + shape type) + counting + selection.
Distractors: red rects, yellow rects, red circles, pink stars.
Two distractors overlap blue rectangles to force disambiguation.
The correct answer is 4 blue rectangles → agent must click "label_4".

Starting state is defined in fixture.json (loaded by the runner, not the verifier).
"""
from verifier.types import Task
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.selection_checks import LayerSelected, ClickedLayer
from verifier.checks.structure_checks import NoLayerCreated, NoLayerDeleted, NoLayerMoved
from verifier.checks.event_checks    import EventTypeCountAtLeast

CORRECT_LABEL = "label_4"

task = Task(
    id="task_51_read_count_blue_rects",
    description="Count blue rectangles in scene (answer: 4) and click the matching number label.",

    rubrics=[
        # ── Correctness: agent clicked / selected label_4 ──
        FundamentalsRubric([
            ClickedLayer(layer_name=CORRECT_LABEL),
            LayerSelected(layer_name=CORRECT_LABEL),
        ], weight=0.70, critical=[0]),

        # ── Read tasks: scene must remain unchanged (no edits) ──
        StructureRubric([
            NoLayerCreated(),
            NoLayerDeleted(),
            NoLayerMoved(tolerance=2.0),
        ], weight=0.20, critical=[0, 1, 2]),

        # ── Event hygiene ──
        EventRubric([
            EventTypeCountAtLeast("click_select", minimum=1),
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=1, lambda_=0.0),
)
