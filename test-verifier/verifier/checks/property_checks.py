from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import find_layers_by_type


@dataclass
class OpacityEquals:
    """All layers of layer_type have opacity ≈ expected (0..1)."""
    layer_type: str
    opacity: float
    tolerance: float = 0.02

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = [l for l in layers if abs(l.get("opacity", 1.0) - self.opacity) > self.tolerance]
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type} opacity correct" if passed
                    else f"{len(failures)} {self.layer_type} layers have wrong opacity",
        )


@dataclass
class VisibilityIs:
    """All layers of layer_type have the given visibility state."""
    layer_type: str
    visible: bool

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = [l for l in layers if l.get("visible", True) != self.visible]
        passed = not failures
        state = "visible" if self.visible else "hidden"
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} are {state}" if passed
                    else f"{len(failures)} {self.layer_type} layers have wrong visibility",
        )


@dataclass
class CornerRadiusEquals:
    """At least one layer of layer_type has cornerRadius ≈ expected."""
    layer_type: str
    radius: float
    tolerance: float = 1.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            cr = l.get("cornerRadius", 0)
            # cornerRadius can be a scalar or a 4-tuple — check scalar case
            if isinstance(cr, (int, float)) and abs(cr - self.radius) <= self.tolerance:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} cornerRadius {cr} ≈ {self.radius}")
            # 4-tuple: all corners match
            if isinstance(cr, list) and all(abs(v - self.radius) <= self.tolerance for v in cr):
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} cornerRadius {cr} ≈ {self.radius}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} with cornerRadius {self.radius}±{self.tolerance}",
        )


@dataclass
class IsFlippedH:
    """At least one layer of layer_type is horizontally flipped (scaleX == -1)."""
    layer_type: str

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            if l.get("scaleX") == -1:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} is flipped horizontally")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No {self.layer_type} flipped horizontally")


@dataclass
class IsFlippedV:
    """At least one layer of layer_type is vertically flipped (scaleY == -1)."""
    layer_type: str

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            if l.get("scaleY") == -1:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} is flipped vertically")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No {self.layer_type} flipped vertically")
