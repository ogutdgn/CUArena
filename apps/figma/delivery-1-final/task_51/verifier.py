"""
Task 51 [READ] — Count blue rectangles, click matching number label.

Tests visual identification (color + shape type) + counting + selection.
Distractors: red rects, yellow rects, red circles, pink stars.
Two distractors overlap blue rectangles to force disambiguation.
The correct answer is 4 blue rectangles → agent must click "label_4".

Starting state is defined in fixture.json (loaded by the runner, not the verifier).
"""
from __future__ import annotations

from verifier.types import Task
from verifier.types import CheckResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.structure_checks import NamedLayerExists, LayerTotalCount
from verifier.math_utils import find_all_layers

CORRECT_LABEL = "label_4"
ALL_LABELS = [f"label_{i}" for i in range(1, 9)]
REQUIRED_TOP_LEVELS = [
    "blue_rect_01", "blue_rect_02", "blue_rect_03", "blue_rect_04",
    "red_rect_01", "red_rect_02",
    "red_circle_01", "red_circle_02", "red_circle_03",
    "pink_star_01", "pink_star_02", "pink_star_03",
    "yellow_rect_01", "yellow_rect_02",
] + ALL_LABELS


def _find_layer_by_name(document: dict, name: str) -> dict | None:
    for layer in find_all_layers(document):
        if layer.get("name") == name:
            return layer
    return None


def _iter_layer_tree(layer: dict):
    yield layer
    for child in layer.get("children", []):
        yield from _iter_layer_tree(child)


def _is_greenish(color: dict) -> bool:
    r = float(color.get("r", 0.0))
    g = float(color.get("g", 0.0))
    b = float(color.get("b", 0.0))
    return g >= 0.45 and (g - r) >= 0.12 and (g - b) >= 0.12


class LayerHasGreenFill:
    """Pass if the named layer (or any descendant) has a visible solid green-ish fill."""
    def __init__(self, layer_name: str):
        self.layer_name = layer_name

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        target = _find_layer_by_name(doc, self.layer_name)
        if not target:
            return CheckResult(
                passed=False,
                score=0.0,
                max_score=1.0,
                message=f"Layer '{self.layer_name}' not found in document",
            )

        for node in _iter_layer_tree(target):
            for fill in node.get("fills", []):
                if fill.get("kind") != "solid":
                    continue
                if not fill.get("visible", True):
                    continue
                if float(fill.get("opacity", 1.0)) <= 0.01:
                    continue
                if _is_greenish(fill.get("color", {})):
                    return CheckResult(
                        passed=True,
                        score=1.0,
                        max_score=1.0,
                        message=f"Layer '{self.layer_name}' has green fill",
                    )

        return CheckResult(
            passed=False,
            score=0.0,
            max_score=1.0,
            message=f"Layer '{self.layer_name}' is not filled with green",
        )


class LayerNotGreenFill:
    """Pass if the named layer has no visible solid green-ish fill."""
    def __init__(self, layer_name: str):
        self.layer_name = layer_name

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        target = _find_layer_by_name(doc, self.layer_name)
        if not target:
            return CheckResult(
                passed=False,
                score=0.0,
                max_score=1.0,
                message=f"Layer '{self.layer_name}' not found in document",
            )

        for node in _iter_layer_tree(target):
            for fill in node.get("fills", []):
                if fill.get("kind") != "solid":
                    continue
                if not fill.get("visible", True):
                    continue
                if float(fill.get("opacity", 1.0)) <= 0.01:
                    continue
                if _is_greenish(fill.get("color", {})):
                    return CheckResult(
                        passed=False,
                        score=0.0,
                        max_score=1.0,
                        message=f"Layer '{self.layer_name}' is also green",
                    )

        return CheckResult(
            passed=True,
            score=1.0,
            max_score=1.0,
            message=f"Layer '{self.layer_name}' is not green",
        )

task = Task(
    id="task_51_read_count_blue_rects",
    description="Count blue rectangles in scene (answer: 4) and fill only label_4 with green.",

    rubrics=[
        # End-state correctness: only the answer label is green.
        FundamentalsRubric([
            LayerHasGreenFill(layer_name=CORRECT_LABEL),
            LayerNotGreenFill(layer_name="label_1"),
            LayerNotGreenFill(layer_name="label_2"),
            LayerNotGreenFill(layer_name="label_3"),
            LayerNotGreenFill(layer_name="label_5"),
            LayerNotGreenFill(layer_name="label_6"),
            LayerNotGreenFill(layer_name="label_7"),
            LayerNotGreenFill(layer_name="label_8"),
        ], weight=0.70, critical=[0]),

        StructureRubric(
            [NamedLayerExists(name=n) for n in REQUIRED_TOP_LEVELS]
            + [
                # End-state fixture invariants:
                # frame (1) + top-level layers (22) + label children (16) = 39
                LayerTotalCount(equals=39),
            ],
            weight=0.30,
            critical=list(range(len(REQUIRED_TOP_LEVELS))),
        ),
    ],
    efficiency=EfficiencyRubric(target_turns=1, lambda_=0.0),
)
