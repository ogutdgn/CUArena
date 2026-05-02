from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import find_layers_by_type


@dataclass
class ShapeCount:
    """Passes when the document contains exactly `equals` layers of `layer_type`."""
    layer_type: str
    equals: int

    def run(self, log: dict) -> CheckResult:
        count = log["outcome"]["summary"]["shapeCounts"].get(self.layer_type, 0)
        passed = count == self.equals
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type}: expected {self.equals}, got {count}",
        )


@dataclass
class ShapeCountAtLeast:
    """Passes when the document contains at least `minimum` layers of `layer_type`."""
    layer_type: str
    minimum: int

    def run(self, log: dict) -> CheckResult:
        count = log["outcome"]["summary"]["shapeCounts"].get(self.layer_type, 0)
        passed = count >= self.minimum
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type}: expected ≥{self.minimum}, got {count}",
        )


@dataclass
class PolygonSidesEquals:
    """Passes when all polygon layers have exactly `sides` sides."""
    sides: int

    def run(self, log: dict) -> CheckResult:
        polygons = find_layers_by_type(log["outcome"]["document"], "polygon")
        if not polygons:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message="No polygon layers found")
        wrong = [p for p in polygons if p.get("sides") != self.sides]
        passed = len(wrong) == 0
        got = polygons[0].get("sides", "?") if polygons else "?"
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"polygon sides: expected {self.sides}, got {got}" + (
                f" ({len(wrong)} wrong)" if wrong else ""),
        )


@dataclass
class StarPointsEquals:
    """Passes when all star layers have exactly `points` points."""
    points: int

    def run(self, log: dict) -> CheckResult:
        stars = find_layers_by_type(log["outcome"]["document"], "star")
        if not stars:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message="No star layers found")
        wrong = [s for s in stars if s.get("points") != self.points]
        passed = len(wrong) == 0
        got = stars[0].get("points", "?")
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"star points: expected {self.points}, got {got}" + (
                f" ({len(wrong)} wrong)" if wrong else ""),
        )


@dataclass
class StarInnerRatioEquals:
    """Passes when all star layers have approximately `ratio` innerRatio (0..1)."""
    ratio: float
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        stars = find_layers_by_type(log["outcome"]["document"], "star")
        if not stars:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message="No star layers found")
        wrong = [s for s in stars
                 if abs(s.get("innerRatio", 0) - self.ratio) > self.tolerance]
        passed = len(wrong) == 0
        got = stars[0].get("innerRatio", "?")
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"star innerRatio: expected {self.ratio}±{self.tolerance}, got {got}",
        )
