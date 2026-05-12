"""
Task 51 [READ] — Count jeans, click matching number label.

Tests visual identification + counting + targeted selection.
The correct answer is 4 jeans → agent must click the layer named "label_4".

This is the first task to use a Fixture (starting state).
"""
from verifier.types import Task, Fixture
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.event        import EventRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.selection_checks import LayerSelected, ClickedLayer
from verifier.checks.structure_checks import NoLayerCreated, NoLayerDeleted, NoLayerMoved
from verifier.checks.event_checks    import EventTypeCountAtLeast

CORRECT_LABEL = "label_4"

task = Task(
    id="task_51_read_count_jeans",
    description="Count jeans in scene (answer: 4) and click the matching number label.",

    fixture=Fixture(
        frame={"width": 1200, "height": 800, "name": "scene"},
        layers=[
            # ── Clothing items (scattered across top 2/3 of frame) ──
            # 4 jeans (correct count)
            {"name": "jeans_01", "type": "vector", "asset": "jeans",   "x": 120, "y": 100, "w": 90,  "h": 140, "fill": "#3B5998"},
            {"name": "jeans_02", "type": "vector", "asset": "jeans",   "x": 480, "y": 220, "w": 90,  "h": 140, "fill": "#5878A8"},
            {"name": "jeans_03", "type": "vector", "asset": "jeans",   "x": 820, "y": 140, "w": 90,  "h": 140, "fill": "#2E4A7A"},
            {"name": "jeans_04", "type": "vector", "asset": "jeans",   "x": 320, "y": 420, "w": 90,  "h": 140, "fill": "#4A6FA5"},
            # 3 shirts
            {"name": "shirt_01", "type": "vector", "asset": "shirt",   "x": 240, "y": 240, "w": 110, "h": 110, "fill": "#E74C3C"},
            {"name": "shirt_02", "type": "vector", "asset": "shirt",   "x": 620, "y": 80,  "w": 110, "h": 110, "fill": "#2ECC71"},
            {"name": "shirt_03", "type": "vector", "asset": "shirt",   "x": 940, "y": 380, "w": 110, "h": 110, "fill": "#F39C12"},
            # 2 hats
            {"name": "hat_01",   "type": "vector", "asset": "hat",     "x": 380, "y": 80,  "w": 80,  "h": 60,  "fill": "#8E44AD"},
            {"name": "hat_02",   "type": "vector", "asset": "hat",     "x": 720, "y": 440, "w": 80,  "h": 60,  "fill": "#1ABC9C"},
            # 2 jackets
            {"name": "jacket_01","type": "vector", "asset": "jacket",  "x": 60,  "y": 320, "w": 130, "h": 160, "fill": "#34495E"},
            {"name": "jacket_02","type": "vector", "asset": "jacket",  "x": 1020,"y": 180, "w": 130, "h": 160, "fill": "#16A085"},
            # 1 dress
            {"name": "dress_01", "type": "vector", "asset": "dress",   "x": 540, "y": 380, "w": 100, "h": 180, "fill": "#C0392B"},

            # ── Number labels along bottom (y ≈ 700) ──
            {"name": "label_1", "type": "group", "x": 120,  "y": 700, "w": 60, "h": 60,
             "children": [
                 {"type": "ellipse",   "w": 60, "h": 60, "fill": "#FFFFFF", "stroke": "#000000", "stroke_weight": 2},
                 {"type": "text",      "text": "1", "font_size": 32, "fill": "#000000"},
             ]},
            {"name": "label_2", "type": "group", "x": 250,  "y": 700, "w": 60, "h": 60,
             "children": [
                 {"type": "ellipse",   "w": 60, "h": 60, "fill": "#FFFFFF", "stroke": "#000000", "stroke_weight": 2},
                 {"type": "text",      "text": "2", "font_size": 32, "fill": "#000000"},
             ]},
            {"name": "label_3", "type": "group", "x": 380,  "y": 700, "w": 60, "h": 60,
             "children": [
                 {"type": "ellipse",   "w": 60, "h": 60, "fill": "#FFFFFF", "stroke": "#000000", "stroke_weight": 2},
                 {"type": "text",      "text": "3", "font_size": 32, "fill": "#000000"},
             ]},
            {"name": "label_4", "type": "group", "x": 510,  "y": 700, "w": 60, "h": 60,
             "children": [
                 {"type": "ellipse",   "w": 60, "h": 60, "fill": "#FFFFFF", "stroke": "#000000", "stroke_weight": 2},
                 {"type": "text",      "text": "4", "font_size": 32, "fill": "#000000"},
             ]},
            {"name": "label_5", "type": "group", "x": 640,  "y": 700, "w": 60, "h": 60,
             "children": [
                 {"type": "ellipse",   "w": 60, "h": 60, "fill": "#FFFFFF", "stroke": "#000000", "stroke_weight": 2},
                 {"type": "text",      "text": "5", "font_size": 32, "fill": "#000000"},
             ]},
            {"name": "label_6", "type": "group", "x": 770,  "y": 700, "w": 60, "h": 60,
             "children": [
                 {"type": "ellipse",   "w": 60, "h": 60, "fill": "#FFFFFF", "stroke": "#000000", "stroke_weight": 2},
                 {"type": "text",      "text": "6", "font_size": 32, "fill": "#000000"},
             ]},
            {"name": "label_7", "type": "group", "x": 900,  "y": 700, "w": 60, "h": 60,
             "children": [
                 {"type": "ellipse",   "w": 60, "h": 60, "fill": "#FFFFFF", "stroke": "#000000", "stroke_weight": 2},
                 {"type": "text",      "text": "7", "font_size": 32, "fill": "#000000"},
             ]},
            {"name": "label_8", "type": "group", "x": 1030, "y": 700, "w": 60, "h": 60,
             "children": [
                 {"type": "ellipse",   "w": 60, "h": 60, "fill": "#FFFFFF", "stroke": "#000000", "stroke_weight": 2},
                 {"type": "text",      "text": "8", "font_size": 32, "fill": "#000000"},
             ]},
        ],
    ),

    rubrics=[
        # ── Correctness: agent clicked / selected label_4 ──
        FundamentalsRubric([
            ClickedLayer(layer_name=CORRECT_LABEL),                                   # 0 ★ "click the number label that matches"
            LayerSelected(layer_name=CORRECT_LABEL),                                  # 1
        ], weight=0.70, critical=[0]),

        # ── Read tasks: scene must remain unchanged (no edits) ──
        StructureRubric([
            NoLayerCreated(),                                                         # 0 ★ Read task: agent should not create anything
            NoLayerDeleted(),                                                         # 1 ★ Read task: agent should not delete anything
            NoLayerMoved(tolerance=2.0),                                              # 2 ★ Read task: scene should be untouched
        ], weight=0.20, critical=[0, 1, 2]),

        # ── Event hygiene ──
        EventRubric([
            EventTypeCountAtLeast("click", minimum=1),                                # 0 — at least one click event
        ], weight=0.10, critical=[]),
    ],
    efficiency=EfficiencyRubric(target_turns=6),
)
