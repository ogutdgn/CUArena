from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import find_layers_by_type, channel_distance


def _first_stroke(layer: dict) -> dict | None:
    strokes = layer.get("strokes", [])
    return strokes[0] if strokes else None


@dataclass
class StrokeExists:
    """At least one layer of layer_type has a stroke."""
    layer_type: str

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            if l.get("strokes"):
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} has a stroke")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No {self.layer_type} with a stroke found")


@dataclass
class StrokeWeightEquals:
    """At least one layer of layer_type has stroke weight ≈ expected."""
    layer_type: str
    weight: float
    tolerance: float = 0.5

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            s = _first_stroke(l)
            if s and abs(s.get("weight", 0) - self.weight) <= self.tolerance:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} stroke weight {s['weight']} ≈ {self.weight}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} with stroke weight {self.weight}±{self.tolerance}",
        )


@dataclass
class StrokeColorEquals:
    """At least one layer of layer_type has stroke color matching expected_rgb."""
    layer_type: str
    expected_rgb: dict
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            s = _first_stroke(l)
            if s:
                paint = s.get("paint", {})
                if paint.get("kind") == "solid":
                    dist = channel_distance(paint.get("color", {}), self.expected_rgb)
                    if dist <= self.tolerance:
                        return CheckResult(passed=True, score=1.0, max_score=1.0,
                                           message=f"{self.layer_type} stroke color matches")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} with stroke color {self.expected_rgb}",
        )


@dataclass
class StrokeAlignmentIs:
    """At least one layer of layer_type has stroke alignment matching `alignment`."""
    layer_type: str
    alignment: str   # "inside" | "center" | "outside"

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            s = _first_stroke(l)
            if s and s.get("alignment") == self.alignment:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} stroke alignment is '{self.alignment}'")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} with stroke alignment '{self.alignment}'",
        )


@dataclass
class StrokeIsDashed:
    """At least one layer of layer_type has a dashed stroke."""
    layer_type: str

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            s = _first_stroke(l)
            if s and s.get("dash") is not None:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} has dashed stroke")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No {self.layer_type} with dashed stroke found")
