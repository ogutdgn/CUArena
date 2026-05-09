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
class AllFillTypeIs:
    """Every layer of layer_type has fills[fill_index] of the given kind.
    Stricter than FillTypeIs (which passes on ≥1 layer)."""
    layer_type: str
    kind: str       # "solid" | "image" | "gradient"
    fill_index: int = 0

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
            if fills[self.fill_index].get("kind") != self.kind:
                failures.append(f"{l['id'][:8]}: fill kind '{fills[self.fill_index].get('kind')}' ≠ '{self.kind}'")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} have {self.kind} fill" if passed
                    else "; ".join(failures),
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
class FillCountAtMost:
    """All layers of layer_type have at most `max_count` fills.
    Catches stacked-fill workarounds where extra fills hide under the first."""
    layer_type: str
    max_count: int = 1

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = [
            f"{l['id'][:8]}: {len(l.get('fills', []))} fills > {self.max_count}"
            for l in layers if len(l.get("fills", [])) > self.max_count
        ]
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} have ≤ {self.max_count} fills" if passed
                    else "; ".join(failures),
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
class FillOpacityAtLeast:
    """Every layer of layer_type has fills[fill_index].opacity >= min_opacity.
    Catches near-invisible fills that satisfy other color checks trivially."""
    layer_type: str
    min_opacity: float       # 0..1
    fill_index: int = 0

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
            op = fills[self.fill_index].get("opacity", 1.0)
            if op < self.min_opacity:
                failures.append(f"{l['id'][:8]}: opacity {op:.2f} < {self.min_opacity}")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} fill opacity ≥ {self.min_opacity}" if passed
                    else "; ".join(failures),
        )


@dataclass
class LayersHaveColorOrder:
    """Sorted layers of layer_type have fill colors matching expected_rgbs in order.
    sort_axis: 'x' or 'y' for linear direction; 'size' to sort largest→smallest
    (useful for concentric layers where x/y all overlap)."""
    layer_type: str
    expected_rgbs: list
    sort_axis: str = "y"
    tolerance: float = 0.15

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) != len(self.expected_rgbs):
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need exactly {len(self.expected_rgbs)} {self.layer_type}, found {len(layers)}")
        if self.sort_axis == "y":
            ordered = sorted(layers, key=lambda l: l["y"] + l["h"] / 2)
        elif self.sort_axis == "size":
            ordered = sorted(layers, key=lambda l: -(l["w"] * l["h"]))  # largest first
        else:
            ordered = sorted(layers, key=lambda l: l["x"] + l["w"] / 2)
        for i, l in enumerate(ordered):
            fills = l.get("fills", [])
            if not fills or fills[0].get("kind") != "solid":
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"layer {i} has no solid fill")
            c = fills[0].get("color", {})
            expected = self.expected_rgbs[i]
            diff = max(abs(c.get(k, 0) - expected.get(k, 0)) for k in ("r", "g", "b"))
            if diff > self.tolerance:
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"layer {i}: color mismatch (diff={diff:.2f})")
        return CheckResult(
            passed=True, score=1.0, max_score=1.0,
            message=f"{self.layer_type} colors match expected sequence on {self.sort_axis}",
        )


@dataclass
class CentermostLayerHasColor:
    """Among layers of layer_type, the one closest to the layer-set centroid
    has a solid fill matching expected_rgb. Used to verify a 'center' role."""
    layer_type: str
    expected_rgb: dict
    tolerance: float = 0.15

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers")
        cx = sum(l["x"] + l["w"] / 2 for l in layers) / len(layers)
        cy = sum(l["y"] + l["h"] / 2 for l in layers) / len(layers)
        center = min(layers, key=lambda l: ((l["x"] + l["w"] / 2 - cx) ** 2 + (l["y"] + l["h"] / 2 - cy) ** 2))
        fills = center.get("fills", [])
        if not fills or fills[0].get("kind") != "solid":
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Centermost {self.layer_type} has no solid fill")
        c = fills[0].get("color", {})
        diff = max(abs(c.get(k, 0) - self.expected_rgb.get(k, 0)) for k in ("r", "g", "b"))
        passed = diff <= self.tolerance
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"centermost {self.layer_type} color diff {diff:.2f} (tol {self.tolerance})",
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
class AllLayersHaveNoFill:
    """Every layer of layer_type has no visible solid/image fill."""
    layer_type: str

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            visible = [
                f for f in l.get("fills", [])
                if f.get("visible", True) and f.get("opacity", 1.0) > 0
            ]
            if visible:
                failures.append(l["id"][:8])
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} layers have no visible fill" if passed
                    else f"{len(failures)} {self.layer_type} layers still have visible fill",
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


@dataclass
class DistinctTypedSolidColors:
    """
    Layers of layer_type have at least `minimum` perceptually-distinct solid fills.

    Stricter than DistinctSolidColors because the frame (and any unrelated layers)
    are excluded — only the named layer_type's own fills are counted.
    Use to enforce "two different shades of X" prompts where the frame's
    background color must not be counted as one of the X's "distinct colors".
    """
    layer_type: str
    minimum: int
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        seen: list[tuple[float, float, float]] = []
        for l in layers:
            for fill in l.get("fills", []):
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
            message=f"distinct {self.layer_type} colors: expected ≥{self.minimum}, got {len(seen)}",
        )


@dataclass
class LayersAllSameColor:
    """Every layer of layer_type shares the same solid fill color (uniformity, not specific RGB)."""
    layer_type: str
    fill_index: int = 0
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        ref = None
        for i, l in enumerate(layers):
            fills = l.get("fills", [])
            if self.fill_index >= len(fills) or fills[self.fill_index].get("kind") != "solid":
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"{self.layer_type} #{i} missing solid fill at index {self.fill_index}")
            c = fills[self.fill_index].get("color", {})
            rgb = (c.get("r", 0), c.get("g", 0), c.get("b", 0))
            if ref is None:
                ref = rgb
            elif max(abs(rgb[0] - ref[0]), abs(rgb[1] - ref[1]), abs(rgb[2] - ref[2])) > self.tolerance:
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"{self.layer_type} #{i} fill differs from #0")
        return CheckResult(
            passed=True, score=1.0, max_score=1.0,
            message=f"All {len(layers)} {self.layer_type} share one color",
        )


@dataclass
class AllSolidColorsNearGray:
    """
    All layers of `layer_type` have a first solid fill whose RGB channels are
    close to each other (i.e. gray family color).
    """
    layer_type: str
    tolerance: float = 0.12

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        for l in layers:
            fills = l.get("fills", [])
            if not fills or fills[0].get("kind") != "solid":
                return CheckResult(
                    passed=False, score=0.0, max_score=1.0,
                    message=f"{self.layer_type} {l.get('id', '')[:8]} missing solid fill",
                )
            c = fills[0].get("color", {})
            r, g, b = c.get("r", 0.0), c.get("g", 0.0), c.get("b", 0.0)
            if max(abs(r - g), abs(g - b), abs(r - b)) > self.tolerance:
                return CheckResult(
                    passed=False, score=0.0, max_score=1.0,
                    message=f"{self.layer_type} {l.get('id', '')[:8]} not gray-like",
                )
        return CheckResult(
            passed=True, score=1.0, max_score=1.0,
            message=f"All {self.layer_type} fills are gray-like",
        )


@dataclass
class LayersAlternatingColorsByArea:
    """
    Layers of `layer_type`, sorted by area descending (outer->inner), alternate
    between exactly `n_colors` unique solid colors.
    """
    layer_type: str
    n_colors: int = 2
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < self.n_colors * 2:
            return CheckResult(
                passed=False, score=0.0, max_score=1.0,
                message=f"Need >={self.n_colors * 2} {self.layer_type} layers, found {len(layers)}",
            )

        ordered = sorted(layers, key=lambda l: l["w"] * l["h"], reverse=True)
        colors: list[tuple[float, float, float]] = []
        for l in ordered:
            fills = l.get("fills", [])
            if not fills or fills[0].get("kind") != "solid":
                return CheckResult(
                    passed=False, score=0.0, max_score=1.0,
                    message=f"{self.layer_type} missing solid fill in area order",
                )
            c = fills[0].get("color", {})
            colors.append((c.get("r", 0), c.get("g", 0), c.get("b", 0)))

        cycle = colors[: self.n_colors]
        distinct_cycle: list[tuple[float, float, float]] = []
        for rgb in cycle:
            close = any(
                max(abs(rgb[0] - d[0]), abs(rgb[1] - d[1]), abs(rgb[2] - d[2])) <= self.tolerance
                for d in distinct_cycle
            )
            if not close:
                distinct_cycle.append(rgb)
        if len(distinct_cycle) != self.n_colors:
            return CheckResult(
                passed=False, score=0.0, max_score=1.0,
                message=f"Expected exactly {self.n_colors} alternating colors, got fewer in cycle seed",
            )

        for i, rgb in enumerate(colors):
            expected = cycle[i % self.n_colors]
            diff = max(abs(rgb[0] - expected[0]), abs(rgb[1] - expected[1]), abs(rgb[2] - expected[2]))
            if diff > self.tolerance:
                return CheckResult(
                    passed=False, score=0.0, max_score=1.0,
                    message=f"{self.layer_type} color at rank {i} breaks alternating cycle",
                )
        return CheckResult(
            passed=True, score=1.0, max_score=1.0,
            message=f"{self.layer_type} colors alternate by area with {self.n_colors} colors",
        )
