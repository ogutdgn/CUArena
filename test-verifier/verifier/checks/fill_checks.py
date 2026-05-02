from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import find_layers_by_type, channel_distance


@dataclass
class SolidColorEquals:
    """At least one layer of layer_type has a solid fill matching expected_rgb."""
    layer_type: str
    expected_rgb: dict      # {"r": 0..1, "g": 0..1, "b": 0..1}
    fill_index: int = 0
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            fills = l.get("fills", [])
            if self.fill_index < len(fills):
                fill = fills[self.fill_index]
                if fill.get("kind") == "solid":
                    if channel_distance(fill.get("color", {}), self.expected_rgb) <= self.tolerance:
                        return CheckResult(passed=True, score=1.0, max_score=1.0,
                                           message=f"{self.layer_type} has expected color")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} with solid fill {self.expected_rgb} (tol {self.tolerance})",
        )


@dataclass
class AllSolidColorEquals:
    """Every layer of layer_type has a solid fill matching expected_rgb."""
    layer_type: str
    expected_rgb: dict
    fill_index: int = 0
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            fills = l.get("fills", [])
            if self.fill_index >= len(fills):
                failures.append(f"{l['id'][:8]}: no fill at index {self.fill_index}")
                continue
            fill = fills[self.fill_index]
            if fill.get("kind") != "solid":
                failures.append(f"{l['id'][:8]}: fill is not solid")
                continue
            dist = channel_distance(fill.get("color", {}), self.expected_rgb)
            if dist > self.tolerance:
                failures.append(f"{l['id'][:8]}: color mismatch (dist={dist:.3f})")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message="; ".join(failures) if failures else f"All {self.layer_type} have expected color",
        )


@dataclass
class FillTypeIs:
    """At least one layer of layer_type has a fill of the given kind."""
    layer_type: str
    kind: str       # "solid" | "image"
    fill_index: int = 0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            fills = l.get("fills", [])
            if self.fill_index < len(fills) and fills[self.fill_index].get("kind") == self.kind:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} has {self.kind} fill")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} with fill kind '{self.kind}'",
        )


@dataclass
class FillCount:
    """All layers of layer_type have exactly `equals` fills."""
    layer_type: str
    equals: int

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = [l for l in layers if len(l.get("fills", [])) != self.equals]
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type} fill count correct" if passed
                    else f"{len(failures)} {self.layer_type} layers have wrong fill count",
        )


@dataclass
class ImageFillExists:
    """At least one layer of layer_type has an image fill or is an image layer."""
    layer_type: str

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            if l.get("imageFill"):
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} has image fill")
            for fill in l.get("fills", []):
                if fill.get("kind") == "image":
                    return CheckResult(passed=True, score=1.0, max_score=1.0,
                                       message=f"{self.layer_type} has image fill")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} with image fill found",
        )


@dataclass
class FillOpacityEquals:
    """Fill-level opacity (fills[fill_index].opacity) on layers of layer_type."""
    layer_type: str
    opacity: float      # 0..1
    fill_index: int = 0
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            fills = l.get("fills", [])
            if self.fill_index < len(fills):
                op = fills[self.fill_index].get("opacity", 1.0)
                if abs(op - self.opacity) <= self.tolerance:
                    return CheckResult(passed=True, score=1.0, max_score=1.0,
                                       message=f"{self.layer_type} fill opacity {op:.2f} ≈ {self.opacity}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} with fill opacity {self.opacity}±{self.tolerance}",
        )
