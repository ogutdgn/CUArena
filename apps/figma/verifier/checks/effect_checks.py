from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import find_layers_by_type, channel_distance


def _effects_of_kind(layer: dict, kind: str) -> list[dict]:
    return [e for e in layer.get("effects", []) if e.get("kind") == kind]


@dataclass
class DropShadowExists:
    """At least one layer of layer_type has a drop shadow effect."""
    layer_type: str

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            if _effects_of_kind(l, "drop_shadow"):
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} has drop shadow")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No {self.layer_type} with drop shadow found")


@dataclass
class LayerBlurExists:
    """At least one layer of layer_type has a layer blur effect."""
    layer_type: str

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            if _effects_of_kind(l, "layer_blur"):
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} has layer blur")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No {self.layer_type} with layer blur found")


@dataclass
class BlurRadiusEquals:
    """At least one layer of layer_type has layer blur radius ≈ expected."""
    layer_type: str
    radius: float
    tolerance: float = 1.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            for e in _effects_of_kind(l, "layer_blur"):
                if abs(e.get("radius", 0) - self.radius) <= self.tolerance:
                    return CheckResult(passed=True, score=1.0, max_score=1.0,
                                       message=f"{self.layer_type} blur radius {e['radius']} ≈ {self.radius}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} with blur radius {self.radius}±{self.tolerance}",
        )


@dataclass
class EffectColorEquals:
    """Drop shadow at effect_index on layer_type has color matching expected_rgb."""
    layer_type: str
    effect_index: int
    expected_rgb: dict
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            shadows = _effects_of_kind(l, "drop_shadow")
            if self.effect_index < len(shadows):
                color = shadows[self.effect_index].get("color", {})
                if channel_distance(color, self.expected_rgb) <= self.tolerance:
                    return CheckResult(passed=True, score=1.0, max_score=1.0,
                                       message=f"{self.layer_type} shadow[{self.effect_index}] color matches")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} with shadow[{self.effect_index}] color {self.expected_rgb}",
        )
