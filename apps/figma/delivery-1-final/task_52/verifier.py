"""
Task 52 [READ] — Find the gift box and drag it outside the frame.

Tests visual category recognition in a cluttered scene. The gift box is
the only composite shape (group with ribbons + bow); distractors are
plain solid rectangles.

Starting state is defined in fixture.json (loaded by the runner).
"""
from __future__ import annotations

from verifier.types import Task
from verifier.types import CheckResult
from verifier.rubrics.fundamentals import FundamentalsRubric
from verifier.rubrics.structure    import StructureRubric
from verifier.rubrics.efficiency   import EfficiencyRubric
from verifier.checks.structure_checks import NamedLayerExists, LayerTotalCount
from verifier.math_utils import find_all_layers

TARGET = "gift_box"
FRAME_NAME = "scene"
REQUIRED_LAYERS = [
    "shape_01",
    "shape_02",
    "shape_03",
    "shape_04",
    "shape_05",
    "shape_06",
    "shape_07",
    "shape_08",
    "shape_09",
    "shape_10",
    TARGET,
]


def _find_layer_by_name(document: dict, name: str) -> dict | None:
    for layer in find_all_layers(document):
        if layer.get("name") == name:
            return layer
    return None


def _overlap_area(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x1 = max(ax, bx)
    y1 = max(ay, by)
    x2 = min(ax + aw, bx + bw)
    y2 = min(ay + ah, by + bh)
    if x2 <= x1 or y2 <= y1:
        return 0.0
    return float((x2 - x1) * (y2 - y1))


class LayerOutsideFrameByName:
    """Pass iff named layer lies mostly outside named frame (overlap <= 50%)."""
    def __init__(self, layer_name: str, frame_name: str, max_inside_frac: float = 0.50):
        self.layer_name = layer_name
        self.frame_name = frame_name
        self.max_inside_frac = max_inside_frac

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        layer = _find_layer_by_name(doc, self.layer_name)
        frame = _find_layer_by_name(doc, self.frame_name)
        if not layer:
            return CheckResult(False, 0.0, 1.0, f"Layer '{self.layer_name}' not found")
        if not frame:
            return CheckResult(False, 0.0, 1.0, f"Frame '{self.frame_name}' not found")

        lb = (float(layer.get("x", 0)), float(layer.get("y", 0)), float(layer.get("w", 0)), float(layer.get("h", 0)))
        fb = (float(frame.get("x", 0)), float(frame.get("y", 0)), float(frame.get("w", 0)), float(frame.get("h", 0)))
        layer_area = max(1.0, lb[2] * lb[3])
        inside_area = _overlap_area(lb, fb)
        inside_frac = inside_area / layer_area
        passed = inside_frac <= self.max_inside_frac
        return CheckResult(
            passed=passed,
            score=1.0 if passed else 0.0,
            max_score=1.0,
            message=(
                f"'{self.layer_name}' inside fraction {inside_frac:.2f} "
                f"(need <= {self.max_inside_frac:.2f})"
            ),
        )


class NamedLayerAtPosition:
    """Pass iff named layer remains near a target position."""
    def __init__(self, layer_name: str, x: float, y: float, tolerance: float = 2.0):
        self.layer_name = layer_name
        self.x = x
        self.y = y
        self.tolerance = tolerance

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        layer = _find_layer_by_name(doc, self.layer_name)
        if not layer:
            return CheckResult(False, 0.0, 1.0, f"Layer '{self.layer_name}' not found")
        dx = abs(float(layer.get("x", 0)) - self.x)
        dy = abs(float(layer.get("y", 0)) - self.y)
        passed = dx <= self.tolerance and dy <= self.tolerance
        return CheckResult(
            passed=passed,
            score=1.0 if passed else 0.0,
            max_score=1.0,
            message=f"'{self.layer_name}' at ({layer.get('x')}, {layer.get('y')}) vs ({self.x}, {self.y}) ±{self.tolerance}",
        )

task = Task(
    id="task_52_read_drag_giftbox_outside_frame",
    description="Find the gift box and drag it outside of the scene frame.",

    rubrics=[
        FundamentalsRubric([
            NamedLayerExists(name=TARGET),
            LayerOutsideFrameByName(layer_name=TARGET, frame_name=FRAME_NAME, max_inside_frac=0.50),
        ], weight=0.70, critical=[1]),

        StructureRubric(
            [NamedLayerExists(name=n) for n in REQUIRED_LAYERS]
            + [
                NamedLayerAtPosition(layer_name=FRAME_NAME, x=0, y=0, tolerance=2.0),
                # End-state only invariant for this fixture:
                # frame + 11 top-level shapes + 4 gift-box children = 16 total layers.
                LayerTotalCount(equals=16),
            ],
            weight=0.30,
            critical=list(range(len(REQUIRED_LAYERS))),
        ),
    ],
    efficiency=EfficiencyRubric(target_turns=1, lambda_=0.0),
)
