from __future__ import annotations
import math
from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import (
    find_layers_by_type, find_all_layers, layers_aligned, layers_symmetric_x, layer_center
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


@dataclass
class LayersConcentric:
    """All layers of layer_type share the same center point (x AND y) within tolerance."""
    layer_type: str
    tolerance: float = 5.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥2 {self.layer_type} layers, found {len(layers)}")
        x_passed, x_diff = layers_aligned(layers, "center_x", self.tolerance)
        y_passed, y_diff = layers_aligned(layers, "center_y", self.tolerance)
        passed = x_passed and y_passed
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type} concentric: max diff x={x_diff:.1f}px y={y_diff:.1f}px (tolerance {self.tolerance}px)",
        )


@dataclass
class LayersStacked:
    """
    Layers of layer_type are stacked along axis, with each adjacent edge separated by gap_px.

    axis="y": sorted top-to-bottom; checks (next.top − prev.bottom) ≈ gap_px for each pair.
    axis="x": sorted left-to-right; checks (next.left − prev.right) ≈ gap_px.

    gap_px=0 forces flush stacking (no gap, no overlap).
    gap_px>0 forces consistent positive spacing.
    """
    layer_type: str
    axis: str            # "x" | "y"
    gap_px: float = 0.0
    tolerance: float = 4.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥2 {self.layer_type} layers, found {len(layers)}")
        if self.axis == "y":
            sorted_layers = sorted(layers, key=lambda l: l["y"])
            gaps = [sorted_layers[i + 1]["y"] - (sorted_layers[i]["y"] + sorted_layers[i]["h"])
                    for i in range(len(sorted_layers) - 1)]
        elif self.axis == "x":
            sorted_layers = sorted(layers, key=lambda l: l["x"])
            gaps = [sorted_layers[i + 1]["x"] - (sorted_layers[i]["x"] + sorted_layers[i]["w"])
                    for i in range(len(sorted_layers) - 1)]
        else:
            raise ValueError(f"axis must be 'x' or 'y', got '{self.axis}'")
        max_dev = max(abs(g - self.gap_px) for g in gaps)
        passed = max_dev <= self.tolerance
        gap_str = "flush" if self.gap_px == 0 else f"gap={self.gap_px}px"
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type} stacked on {self.axis} ({gap_str}): max deviation {max_dev:.1f}px (tolerance {self.tolerance}px)",
        )


@dataclass
class LayersOverlap:
    """At least one (type_a, type_b) pair has overlapping bounding boxes."""
    type_a: str
    type_b: str

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        a_layers = find_layers_by_type(doc, self.type_a)
        b_layers = find_layers_by_type(doc, self.type_b)
        if not a_layers or not b_layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need both {self.type_a} and {self.type_b} layers")
        for a in a_layers:
            for b in b_layers:
                if a is b:
                    continue
                if (a["x"] < b["x"] + b["w"] and a["x"] + a["w"] > b["x"]
                        and a["y"] < b["y"] + b["h"] and a["y"] + a["h"] > b["y"]):
                    return CheckResult(passed=True, score=1.0, max_score=1.0,
                                       message=f"{self.type_a} overlaps {self.type_b}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.type_a} overlaps any {self.type_b}",
        )


@dataclass
class LayerBoundsInside:
    """At least one inner_type's bbox fits entirely inside an outer_type's bbox."""
    inner_type: str
    outer_type: str
    tolerance: float = 2.0       # tolerated overhang in px

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        inners = find_layers_by_type(doc, self.inner_type)
        outers = find_layers_by_type(doc, self.outer_type)
        if not inners or not outers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need both {self.inner_type} and {self.outer_type} layers")
        for inner in inners:
            for outer in outers:
                if inner is outer:
                    continue
                t = self.tolerance
                if (inner["x"] >= outer["x"] - t
                        and inner["y"] >= outer["y"] - t
                        and inner["x"] + inner["w"] <= outer["x"] + outer["w"] + t
                        and inner["y"] + inner["h"] <= outer["y"] + outer["h"] + t):
                    return CheckResult(passed=True, score=1.0, max_score=1.0,
                                       message=f"{self.inner_type} bounds fit inside {self.outer_type}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.inner_type} fits inside any {self.outer_type}",
        )


@dataclass
class LayerAspectRatioGreaterThan:
    """
    All layers of layer_type have an aspect ratio above the threshold.

    axis="horizontal": w/h ≥ ratio   (forces wider-than-tall, e.g. sunset bands)
    axis="vertical":   h/w ≥ ratio   (forces taller-than-wide, e.g. sidebars, stripes)
    """
    layer_type: str
    ratio: float
    axis: str = "horizontal"       # "horizontal" | "vertical"

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            w, h = l["w"], l["h"]
            if w == 0 or h == 0:
                failures.append(f"{l['id'][:8]}: zero dimension")
                continue
            actual = w / h if self.axis == "horizontal" else h / w
            if actual < self.ratio:
                failures.append(f"{l['id'][:8]}: ratio={actual:.2f} < {self.ratio}")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} aspect ratio ≥ {self.ratio} ({self.axis})" if passed
                    else "; ".join(failures),
        )


@dataclass
class RadialDistribution:
    """
    n layers of layer_type arranged at equal angular steps around their collective center.

    Computes each layer's center, then its angle from the group's collective center,
    and checks consecutive sorted angular gaps ≈ 360°/n.
    """
    layer_type: str
    n: int
    tolerance_deg: float = 10.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) != self.n:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need exactly {self.n} {self.layer_type} layers, found {len(layers)}")
        cx = sum(l["x"] + l["w"] / 2 for l in layers) / len(layers)
        cy = sum(l["y"] + l["h"] / 2 for l in layers) / len(layers)
        angles = sorted(
            (math.degrees(math.atan2(l["y"] + l["h"] / 2 - cy, l["x"] + l["w"] / 2 - cx)) % 360)
            for l in layers
        )
        gaps = [angles[i + 1] - angles[i] for i in range(len(angles) - 1)]
        gaps.append(360 - angles[-1] + angles[0])
        expected = 360 / self.n
        max_dev = max(abs(g - expected) for g in gaps)
        passed = max_dev <= self.tolerance_deg
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.n} {self.layer_type} radial: max gap deviation {max_dev:.1f}° (expected {expected:.1f}°, tolerance {self.tolerance_deg}°)",
        )


@dataclass
class LayersEvenlyRotated:
    """
    n layers of layer_type have rotation values evenly stepped by step_deg.

    Sorts the rotation property of each layer and checks consecutive differences ≈ step_deg.
    Works for any starting angle (offset is allowed).
    """
    layer_type: str
    n: int
    step_deg: float
    tolerance_deg: float = 5.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) != self.n:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need exactly {self.n} {self.layer_type} layers, found {len(layers)}")
        rotations = sorted((l.get("rotation", 0) % 360) for l in layers)
        diffs = [rotations[i + 1] - rotations[i] for i in range(len(rotations) - 1)]
        diffs.append(360 - rotations[-1] + rotations[0])
        max_dev = max(abs(d - self.step_deg) for d in diffs)
        passed = max_dev <= self.tolerance_deg
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type} rotations stepped by {self.step_deg}°: max deviation {max_dev:.1f}° (tolerance {self.tolerance_deg}°)",
        )


@dataclass
class LayersInGrid:
    """
    rows × cols layers of layer_type arranged on a regular grid lattice.

    Algorithm:
      1. Cluster layer centers into rows by Y (within tolerance).
      2. Verify exactly `rows` clusters, each with `cols` items.
      3. Sort each row by X; verify ith items across rows share a column (X within tolerance).
    """
    layer_type: str
    rows: int
    cols: int
    tolerance: float = 8.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        expected = self.rows * self.cols
        if len(layers) != expected:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need exactly {expected} {self.layer_type} layers, found {len(layers)}")
        by_y = sorted(layers, key=lambda l: l["y"] + l["h"] / 2)
        row_groups: list[list[dict]] = []
        for l in by_y:
            cy = l["y"] + l["h"] / 2
            placed = False
            for g in row_groups:
                if abs((g[0]["y"] + g[0]["h"] / 2) - cy) <= self.tolerance:
                    g.append(l)
                    placed = True
                    break
            if not placed:
                row_groups.append([l])
        if len(row_groups) != self.rows:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Found {len(row_groups)} row clusters, expected {self.rows}")
        for i, g in enumerate(row_groups):
            if len(g) != self.cols:
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"Row {i} has {len(g)} items, expected {self.cols}")
        rows_sorted = [sorted(g, key=lambda l: l["x"] + l["w"] / 2) for g in row_groups]
        for col_idx in range(self.cols):
            col_xs = [g[col_idx]["x"] + g[col_idx]["w"] / 2 for g in rows_sorted]
            if max(col_xs) - min(col_xs) > self.tolerance:
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"Column {col_idx} not aligned: spread {max(col_xs) - min(col_xs):.1f}px")
        return CheckResult(
            passed=True, score=1.0, max_score=1.0,
            message=f"{self.rows}x{self.cols} grid of {self.layer_type} confirmed",
        )


@dataclass
class LayerCenteredInFrame:
    """
    At least one layer of layer_type is centered within its parent frame.

    Walks all frames; for each direct child of the requested type, checks
    its center matches the frame's geometric center within tolerance.
    Note: layer x,y are in parent space (per scene.ts), so frame center is (w/2, h/2).
    """
    layer_type: str
    tolerance: float = 8.0

    def run(self, log: dict) -> CheckResult:
        for parent in find_all_layers(log["outcome"]["document"]):
            if parent.get("type") != "frame":
                continue
            for child in parent.get("children", []):
                if child.get("type") != self.layer_type:
                    continue
                cx_child = child["x"] + child["w"] / 2
                cy_child = child["y"] + child["h"] / 2
                cx_frame = parent["w"] / 2
                cy_frame = parent["h"] / 2
                if abs(cx_child - cx_frame) <= self.tolerance and abs(cy_child - cy_frame) <= self.tolerance:
                    return CheckResult(passed=True, score=1.0, max_score=1.0,
                                       message=f"{self.layer_type} centered in frame")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} centered in any frame",
        )
