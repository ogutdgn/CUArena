from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import find_layers_by_type, find_all_layers, channel_distance


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


@dataclass
class LayerHasNoFill:
    """At least one layer of layer_type has no visible solid/image fills.
    Used for outline-only shapes (battery body, magnifier ring, stroked hexagons)."""
    layer_type: str

    def run(self, log: dict) -> CheckResult:
        for l in find_layers_by_type(log["outcome"]["document"], self.layer_type):
            fills = l.get("fills", [])
            if not fills:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} has no fill")
            visible = [f for f in fills
                       if f.get("kind") in ("solid", "image")
                       and f.get("visible", True)
                       and f.get("opacity", 1.0) > 0]
            if not visible:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} has no visible fill")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"All {self.layer_type} layers have a visible fill",
        )


@dataclass
class SameColorAcrossTypes:
    """First-layer of each listed type all share the same solid fill color
    (within tolerance). Used when a multi-shape design must read as one color."""
    types: list
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        first_colors = []
        for t in self.types:
            layers = find_layers_by_type(log["outcome"]["document"], t)
            if not layers:
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"No {t} layer found")
            fills = layers[0].get("fills", [])
            if not fills or fills[0].get("kind") != "solid":
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"{t} has no solid fill to compare")
            c = fills[0].get("color", {})
            first_colors.append((c.get("r", 0), c.get("g", 0), c.get("b", 0)))
        ref = first_colors[0]
        for i, rgb in enumerate(first_colors[1:], start=1):
            if max(abs(a - b) for a, b in zip(rgb, ref)) > self.tolerance:
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"{self.types[i]} color differs from {self.types[0]}")
        return CheckResult(
            passed=True, score=1.0, max_score=1.0,
            message=f"All of {self.types} share the same fill color",
        )


@dataclass
class DistinctSolidColors:
    """
    Document contains at least `minimum` perceptually-distinct solid fills.

    Walks all layers, dedupes solid fill colors by per-channel tolerance, and
    asserts the count of distinct colors meets the threshold.
    """
    minimum: int
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        seen: list[tuple[float, float, float]] = []
        for layer in find_all_layers(log["outcome"]["document"]):
            for fill in layer.get("fills", []):
                if fill.get("kind") != "solid":
                    continue
                c = fill.get("color", {})
                rgb = (c.get("r", 0), c.get("g", 0), c.get("b", 0))
                close = any(
                    max(abs(rgb[0] - d[0]), abs(rgb[1] - d[1]), abs(rgb[2] - d[2])) <= self.tolerance
                    for d in seen
                )
                if not close:
                    seen.append(rgb)
        passed = len(seen) >= self.minimum
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"distinct solid colors: expected ≥{self.minimum}, got {len(seen)}",
        )
