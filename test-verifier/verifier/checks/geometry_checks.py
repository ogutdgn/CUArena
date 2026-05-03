from __future__ import annotations
from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import (
    find_layers_by_type, layers_aligned, layers_symmetric_x, layer_center
)


@dataclass
class LayersAligned:
    """All layers of layer_type share the same coordinate on axis (within tolerance)."""
    layer_type: str
    axis: str           # "x" | "y" | "center_x" | "center_y"
    tolerance: float = 5.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥2 {self.layer_type} layers, found {len(layers)}")
        passed, max_diff = layers_aligned(layers, self.axis, self.tolerance)
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type} aligned on {self.axis}: max diff {max_diff:.1f}px (tolerance {self.tolerance}px)",
        )


@dataclass
class LayersSymmetricX:
    """Layers of layer_type are symmetric around their collective center X."""
    layer_type: str
    tolerance: float = 10.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥2 {self.layer_type} layers, found {len(layers)}")
        passed, max_dev = layers_symmetric_x(layers, self.tolerance)
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type} symmetric on X: max deviation {max_dev:.1f}px (tolerance {self.tolerance}px)",
        )


@dataclass
class LayerSizeEquals:
    """All layers of layer_type have approximately the given dimensions."""
    layer_type: str
    width: float | None = None
    height: float | None = None
    tolerance: float = 2.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            if self.width is not None and abs(l["w"] - self.width) > self.tolerance:
                failures.append(f"{l['id'][:8]}: w={l['w']} ≠ {self.width}")
            if self.height is not None and abs(l["h"] - self.height) > self.tolerance:
                failures.append(f"{l['id'][:8]}: h={l['h']} ≠ {self.height}")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message="; ".join(failures) if failures else f"{self.layer_type} size correct",
        )


@dataclass
class LayerPosition:
    """At least one layer of layer_type is at approximately (x, y)."""
    layer_type: str
    x: float | None = None
    y: float | None = None
    tolerance: float = 5.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        for l in layers:
            x_ok = self.x is None or abs(l["x"] - self.x) <= self.tolerance
            y_ok = self.y is None or abs(l["y"] - self.y) <= self.tolerance
            if x_ok and y_ok:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} found at ({l['x']}, {l['y']})")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} at ({self.x}, {self.y}) ±{self.tolerance}px",
        )


@dataclass
class LayerRotationEquals:
    """All layers of layer_type have approximately `degrees` rotation."""
    layer_type: str
    degrees: float
    tolerance: float = 2.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            rot = l.get("rotation", 0)
            if abs(rot - self.degrees) > self.tolerance:
                failures.append(f"{l['id'][:8]}: rotation={rot}")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message="; ".join(failures) if failures else f"{self.layer_type} rotation {self.degrees}° correct",
        )


@dataclass
class DistanceBetween:
    """Distance between the nearest pair of (type_a, type_b) layers ≈ expected_px."""
    type_a: str
    type_b: str
    expected_px: float
    tolerance: float = 5.0

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        a_layers = find_layers_by_type(doc, self.type_a)
        b_layers = find_layers_by_type(doc, self.type_b)
        if not a_layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.type_a} layers found")
        if not b_layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.type_b} layers found")
        best = float("inf")
        for a in a_layers:
            ax, ay = layer_center(a)
            for b in b_layers:
                bx, by = layer_center(b)
                dist = ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
                best = min(best, dist)
        passed = abs(best - self.expected_px) <= self.tolerance
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"distance {self.type_a}↔{self.type_b}: {best:.1f}px (expected {self.expected_px}±{self.tolerance}px)",
        )


@dataclass
class LayerContains:
    """At least one outer_type layer has an inner_type layer as a direct child."""
    outer_type: str
    inner_type: str

    def run(self, log: dict) -> CheckResult:
        outers = find_layers_by_type(log["outcome"]["document"], self.outer_type)
        for outer in outers:
            children = outer.get("children", [])
            if any(c.get("type") == self.inner_type for c in children):
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.inner_type} found inside {self.outer_type}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.inner_type} found as direct child of any {self.outer_type}",
        )


@dataclass
class LayersSameDimensions:
    """All layers of layer_type have the same width and height as each other."""
    layer_type: str
    tolerance: float = 2.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥2 {self.layer_type} layers, found {len(layers)}")
        ref_w, ref_h = layers[0]["w"], layers[0]["h"]
        failures = [
            f"{l['id'][:8]}: {l['w']}×{l['h']} ≠ {ref_w}×{ref_h}"
            for l in layers[1:]
            if abs(l["w"] - ref_w) > self.tolerance or abs(l["h"] - ref_h) > self.tolerance
        ]
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} same size ({ref_w}×{ref_h})" if passed
                    else "; ".join(failures),
        )


@dataclass
class LayerEdgesAligned:
    """
    An edge of type_a aligns with an edge of type_b (within tolerance).

    edge values: "top" | "bottom" | "left" | "right" | "center_x" | "center_y"

    Checks all pairs — passes if at least one pair aligns.
    Useful for: "roof bottom edge == house body top edge"
    """
    type_a: str
    edge_a: str
    type_b: str
    edge_b: str
    tolerance: float = 5.0

    def _edge(self, layer: dict, edge: str) -> float:
        if edge == "top":      return layer["y"]
        if edge == "bottom":   return layer["y"] + layer["h"]
        if edge == "left":     return layer["x"]
        if edge == "right":    return layer["x"] + layer["w"]
        if edge == "center_x": return layer["x"] + layer["w"] / 2
        if edge == "center_y": return layer["y"] + layer["h"] / 2
        raise ValueError(f"Unknown edge '{edge}'")

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        a_layers = find_layers_by_type(doc, self.type_a)
        b_layers = find_layers_by_type(doc, self.type_b)
        if not a_layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.type_a} layers found")
        if not b_layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.type_b} layers found")
        for a in a_layers:
            for b in b_layers:
                ea = self._edge(a, self.edge_a)
                eb = self._edge(b, self.edge_b)
                if abs(ea - eb) <= self.tolerance:
                    return CheckResult(
                        passed=True, score=1.0, max_score=1.0,
                        message=f"{self.type_a}.{self.edge_a} ({ea:.0f}px) ≈ {self.type_b}.{self.edge_b} ({eb:.0f}px)",
                    )
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.type_a}.{self.edge_a} aligns with any {self.type_b}.{self.edge_b} (tolerance {self.tolerance}px)",
        )


@dataclass
class LayersDistributed:
    """Layers of layer_type are evenly spaced on axis (within tolerance)."""
    layer_type: str
    axis: str       # "x" | "y" | "center_x" | "center_y"
    tolerance: float = 5.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 3:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥3 {self.layer_type} layers for distribution check, found {len(layers)}")

        if self.axis in ("x", "center_x"):
            coords = sorted([l["x"] + (l["w"] / 2 if "center" in self.axis else 0) for l in layers])
        else:
            coords = sorted([l["y"] + (l["h"] / 2 if "center" in self.axis else 0) for l in layers])

        gaps = [coords[i + 1] - coords[i] for i in range(len(coords) - 1)]
        max_gap_diff = max(gaps) - min(gaps)
        passed = max_gap_diff <= self.tolerance
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type} distribution on {self.axis}: gap variance {max_gap_diff:.1f}px (tolerance {self.tolerance}px)",
        )
