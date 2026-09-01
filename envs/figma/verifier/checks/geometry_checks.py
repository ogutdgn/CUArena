from __future__ import annotations
import math
from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import (
    find_layers_by_type, find_all_layers, layers_aligned, layers_symmetric_x, layer_center,
    polygon_vertices, line_angle_degrees, line_endpoints, line_length,
)


def _world_bounds_by_id(document: dict) -> dict[str, tuple[float, float, float, float]]:
    """Return layer bounds translated into page coordinates.

    The mock stores frame children in parent-local coordinates. Some historical
    synthetic logs used page coordinates for children, so containment checks can
    still fall back to raw bounds when needed.
    """
    bounds: dict[str, tuple[float, float, float, float]] = {}

    def walk(nodes: list[dict], ox: float = 0.0, oy: float = 0.0) -> None:
        for node in nodes:
            x = ox + node.get("x", 0)
            y = oy + node.get("y", 0)
            bounds[node.get("id", "")] = (x, y, node.get("w", 0), node.get("h", 0))
            walk(node.get("children", []), x, y)

    for page in document.get("pages", []):
        walk(page.get("children", []))
    return bounds


def _raw_bounds(layer: dict) -> tuple[float, float, float, float]:
    return layer.get("x", 0), layer.get("y", 0), layer.get("w", 0), layer.get("h", 0)


def _visual_bounds(layer: dict) -> tuple[float, float, float, float]:
    if layer.get("type") == "polygon":
        verts = polygon_vertices(layer)
        xs = [v[0] for v in verts]
        ys = [v[1] for v in verts]
        return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
    return _raw_bounds(layer)


def _bounds_inside(
    inner: tuple[float, float, float, float],
    outer: tuple[float, float, float, float],
    tolerance: float,
) -> bool:
    ix, iy, iw, ih = inner
    ox, oy, ow, oh = outer
    return (
        ix >= ox - tolerance
        and iy >= oy - tolerance
        and ix + iw <= ox + ow + tolerance
        and iy + ih <= oy + oh + tolerance
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
class LayerCenterPosition:
    """At least one layer of layer_type has center approximately at (x, y)."""
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
            cx, cy = layer_center(l)
            x_ok = self.x is None or abs(cx - self.x) <= self.tolerance
            y_ok = self.y is None or abs(cy - self.y) <= self.tolerance
            if x_ok and y_ok:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} center found at ({cx}, {cy})")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} center at ({self.x}, {self.y}) +- {self.tolerance}px",
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
class LayersHaveDistinctRotations:
    """At least `minimum` distinct rotation values across layers of layer_type
    (within tolerance). Catches "all wedges at same angle" deceptions where the
    prompt requires varied rotations (e.g., pie wedges at different angles).

    Compares rotations modulo 360°; two rotations are 'distinct' iff their
    angular difference exceeds `tolerance_deg`."""
    layer_type: str
    minimum: int = 2
    tolerance_deg: float = 5.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        rotations = [l.get("rotation", 0) % 360 for l in layers]
        distinct = []
        for r in rotations:
            if all(abs(((r - d + 180) % 360) - 180) > self.tolerance_deg for d in distinct):
                distinct.append(r)
        passed = len(distinct) >= self.minimum
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type} has {len(distinct)} distinct rotations "
                    f"(need ≥{self.minimum}, tol {self.tolerance_deg}°)",
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
        if layer.get("type") == "polygon":
            verts = polygon_vertices(layer)
            xs = [v[0] for v in verts]
            ys = [v[1] for v in verts]
            if edge == "top":      return min(ys)
            if edge == "bottom":   return max(ys)
            if edge == "left":     return min(xs)
            if edge == "right":    return max(xs)
            if edge == "center_x": return (min(xs) + max(xs)) / 2
            if edge == "center_y": return (min(ys) + max(ys)) / 2
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
class PolygonCornersAligned:
    """
    The two bottom-most vertices of a polygon coincide with a rectangle's top
    corners. This checks the actual polygon vertices, not the polygon's bounding
    box, so triangle/polygon roof tasks are not distorted by extra outline space.
    """
    polygon_type: str = "polygon"
    rect_type: str = "rectangle"
    tolerance: float = 10.0

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        polygons = find_layers_by_type(doc, self.polygon_type)
        rects = find_layers_by_type(doc, self.rect_type)
        if not polygons or not rects:
            return CheckResult(
                passed=False,
                score=0.0,
                max_score=1.0,
                message=f"Need at least one {self.polygon_type} and one {self.rect_type}",
            )

        for poly in polygons:
            verts = polygon_vertices(poly)
            if len(verts) < 3:
                continue
            max_y = max(v[1] for v in verts)
            bottom = sorted([v for v in verts if abs(v[1] - max_y) <= 1.0], key=lambda v: v[0])
            if len(bottom) < 2:
                bottom = sorted(verts, key=lambda v: (-v[1], v[0]))[:2]
                bottom = sorted(bottom, key=lambda v: v[0])
            left_bottom, right_bottom = bottom[0], bottom[-1]
            for rect in rects:
                top_left = (rect["x"], rect["y"])
                top_right = (rect["x"] + rect["w"], rect["y"])
                left_ok = math.hypot(left_bottom[0] - top_left[0], left_bottom[1] - top_left[1]) <= self.tolerance
                right_ok = math.hypot(right_bottom[0] - top_right[0], right_bottom[1] - top_right[1]) <= self.tolerance
                if left_ok and right_ok:
                    return CheckResult(
                        passed=True,
                        score=1.0,
                        max_score=1.0,
                        message=f"{self.polygon_type} lower corners align with {self.rect_type} top corners",
                    )

        return CheckResult(
            passed=False,
            score=0.0,
            max_score=1.0,
            message=f"No {self.polygon_type} bottom vertices align with {self.rect_type} top corners",
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
class LayersAtDistinctPositions:
    """Layers of layer_type have at least `min_distinct` distinct (x_center, y_center)
    positions, where two centers are considered the same if both x and y differ by
    less than `tolerance` px.

    Catches degenerate "all stacked at one point" / "all duplicated at same x" patterns
    that other checks (overlap, alignment) silently accept."""
    layer_type: str
    min_distinct: int
    tolerance: float = 5.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        seen = []
        for l in layers:
            cx = l["x"] + l["w"] / 2
            cy = l["y"] + l["h"] / 2
            close = any(abs(cx - sx) < self.tolerance and abs(cy - sy) < self.tolerance
                        for sx, sy in seen)
            if not close:
                seen.append((cx, cy))
        passed = len(seen) >= self.min_distinct
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type}: {len(seen)} distinct centers (need ≥ {self.min_distinct}, tol {self.tolerance}px)",
        )


@dataclass
class LayersHaveConsistentGap:
    """
    Layers of layer_type are arranged sequentially along axis with positive,
    consistent inter-edge gaps. Catches both:
      - overlapping piles (zero/negative gaps),
      - inconsistent spacing (some pairs touch, others have wide gaps).

    axis="x": sorted left-to-right; gap[i] = sorted[i+1].left - sorted[i].right.
    axis="y": sorted top-to-bottom; gap[i] = sorted[i+1].top - sorted[i].bottom.

    Pass conditions:
      1. min(gaps) >= min_gap                         (no overlaps/touching pile)
      2. max(gaps) - min(gaps) <= variance_tolerance  (gaps roughly equal)

    Stricter than LayersStacked (which needs an exact gap value) — accepts any
    positive consistent spacing, which matches "consistent spacing" prompts.
    """
    layer_type: str
    axis: str = "x"           # "x" | "y"
    min_gap: float = 1.0
    variance_tolerance: float = 8.0

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
        if not gaps:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No gaps to compare for {self.layer_type}")
        gmin, gmax = min(gaps), max(gaps)
        positive_ok = gmin >= self.min_gap
        variance_ok = (gmax - gmin) <= self.variance_tolerance
        passed = positive_ok and variance_ok
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=(f"{self.layer_type} gaps on {self.axis}: min={gmin:.1f} max={gmax:.1f} "
                     f"(need min ≥ {self.min_gap}, variance ≤ {self.variance_tolerance})"),
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
                world = _world_bounds_by_id(doc)
                inner_bounds = world.get(inner.get("id", ""), _raw_bounds(inner))
                outer_bounds = world.get(outer.get("id", ""), _raw_bounds(outer))
                if _bounds_inside(inner_bounds, outer_bounds, t) or _bounds_inside(_raw_bounds(inner), _raw_bounds(outer), t):
                    return CheckResult(passed=True, score=1.0, max_score=1.0,
                                       message=f"{self.inner_type} bounds fit inside {self.outer_type}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.inner_type} fits inside any {self.outer_type}",
        )


@dataclass
class AllLayerBoundsInside:
    """Every inner_type layer's bbox fits entirely inside ANY outer_type layer's bbox.
    Stricter than LayerBoundsInside (which passes on ≥1 inner fitting in any outer)."""
    inner_type: str
    outer_type: str
    tolerance: float = 4.0

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        inners = find_layers_by_type(doc, self.inner_type)
        outers = find_layers_by_type(doc, self.outer_type)
        if not inners or not outers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need both {self.inner_type} and {self.outer_type} layers")
        t = self.tolerance
        world = _world_bounds_by_id(doc)
        failures = []
        for inner in inners:
            fits_any = False
            for outer in outers:
                if inner is outer:
                    continue
                inner_bounds = world.get(inner.get("id", ""), _raw_bounds(inner))
                outer_bounds = world.get(outer.get("id", ""), _raw_bounds(outer))
                if _bounds_inside(inner_bounds, outer_bounds, t) or _bounds_inside(_raw_bounds(inner), _raw_bounds(outer), t):
                    fits_any = True
                    break
            if not fits_any:
                failures.append(f"{inner['id'][:8]} ({self.inner_type}) outside all {self.outer_type}")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.inner_type} fit inside some {self.outer_type}" if passed
                    else "; ".join(failures),
        )


@dataclass
class FrameSizeEquals:
    """At least one frame in the document matches (width, height) within tolerance.
    Used to enforce a specific preset like MacBook Air (1280x832)."""
    width: float
    height: float
    tolerance: float = 5.0

    def run(self, log: dict) -> CheckResult:
        for f in find_layers_by_type(log["outcome"]["document"], "frame"):
            if abs(f["w"] - self.width) <= self.tolerance and abs(f["h"] - self.height) <= self.tolerance:
                return CheckResult(
                    passed=True, score=1.0, max_score=1.0,
                    message=f"frame matches {self.width}×{self.height}",
                )
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No frame at {self.width}×{self.height} (±{self.tolerance}px)",
        )


@dataclass
class LayerIsCircular:
    """At least one layer of layer_type has w ≈ h within tolerance.
    Distinguishes a true circle from an oval/elongated ellipse."""
    layer_type: str
    tolerance: float = 2.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            if l["w"] > 0 and l["h"] > 0 and abs(l["w"] - l["h"]) <= self.tolerance:
                return CheckResult(
                    passed=True, score=1.0, max_score=1.0,
                    message=f"{self.layer_type} circular: {l['w']}×{l['h']}",
                )
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} with w ≈ h (±{self.tolerance}px)",
        )


@dataclass
class LayerAllCircular:
    """EVERY layer of layer_type has w ≈ h within tolerance.
    Stricter than LayerIsCircular (which passes on ≥1)."""
    layer_type: str
    tolerance: float = 2.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            if not (l["w"] > 0 and l["h"] > 0 and abs(l["w"] - l["h"]) <= self.tolerance):
                failures.append(f"{l['id'][:8]}: {l['w']}×{l['h']}")
        if not failures:
            return CheckResult(passed=True, score=1.0, max_score=1.0,
                               message=f"All {len(layers)} {self.layer_type} layers circular")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"Non-circular {self.layer_type}: {failures[:3]}")


@dataclass
class LayerAllSameSize:
    """EVERY layer of layer_type has dimensions within tolerance of the first layer's.
    Stricter than LayersSameDimensions (which passes if max_w-min_w within tolerance)."""
    layer_type: str
    tolerance: float = 2.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        ref_w, ref_h = layers[0]["w"], layers[0]["h"]
        failures = []
        for l in layers[1:]:
            if abs(l["w"] - ref_w) > self.tolerance or abs(l["h"] - ref_h) > self.tolerance:
                failures.append(f"{l['id'][:8]}: {l['w']}×{l['h']} vs {ref_w}×{ref_h}")
        if not failures:
            return CheckResult(passed=True, score=1.0, max_score=1.0,
                               message=f"All {len(layers)} {self.layer_type} same size")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"Size mismatch: {failures[:3]}")


@dataclass
class LayerHeightRangeAtLeast:
    """The layer set has a visible height range of at least min_range pixels."""
    layer_type: str
    min_range: float

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need at least 2 {self.layer_type} layers")
        heights = [l["h"] for l in layers]
        height_range = max(heights) - min(heights)
        passed = height_range >= self.min_range
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type} height range {height_range:.1f}px >= {self.min_range}px" if passed
                    else f"{self.layer_type} height range {height_range:.1f}px < {self.min_range}px",
        )


@dataclass
class LayerIsSquare:
    """At least one layer of layer_type has w ≈ h within tolerance.
    Distinguishes a true square from a wide/tall rectangle."""
    layer_type: str
    tolerance: float = 2.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            if l["w"] > 0 and l["h"] > 0 and abs(l["w"] - l["h"]) <= self.tolerance:
                return CheckResult(
                    passed=True, score=1.0, max_score=1.0,
                    message=f"{self.layer_type} square: {l['w']}×{l['h']}",
                )
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} with w ≈ h (±{self.tolerance}px)",
        )


@dataclass
class LayerAllSquare:
    """EVERY layer of layer_type has w ≈ h within tolerance.
    Stricter than LayerIsSquare (which passes on ≥1)."""
    layer_type: str
    tolerance: float = 2.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            if not (l["w"] > 0 and l["h"] > 0 and abs(l["w"] - l["h"]) <= self.tolerance):
                failures.append(f"{l['id'][:8]}: {l['w']}×{l['h']}")
        if not failures:
            return CheckResult(passed=True, score=1.0, max_score=1.0,
                               message=f"All {len(layers)} {self.layer_type} square")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"Non-square {self.layer_type}: {failures[:3]}")


@dataclass
class LayersHaveAspectMix:
    """Among layers of layer_type, at least `horizontal_count` are wider-than-tall
    by `ratio` AND at least `vertical_count` are taller-than-wide by `ratio`.

    Used when a design needs orientations to mix — e.g. a plus sign needs one
    horizontal rectangle and one vertical rectangle (1+1 with ratio≈2)."""
    layer_type: str
    horizontal_count: int = 0
    vertical_count: int = 0
    ratio: float = 1.5

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        h_count, v_count = 0, 0
        for l in layers:
            w, h = l["w"], l["h"]
            if w == 0 or h == 0:
                continue
            if w / h >= self.ratio:
                h_count += 1
            elif h / w >= self.ratio:
                v_count += 1
        passed = h_count >= self.horizontal_count and v_count >= self.vertical_count
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type}: {h_count} horizontal, {v_count} vertical (need ≥{self.horizontal_count}H, ≥{self.vertical_count}V at ratio≥{self.ratio})",
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
    n layers of layer_type arranged at equal angular steps around their collective
    center, AND at approximately the same radius from that center.

    Computes each layer's center, then its angle from the group's collective center,
    and checks: (a) consecutive sorted angular gaps ≈ 360°/n, AND (b) max/min radius
    ratio ≤ 1 + radius_tolerance_frac. Without the radius check, a regular grid
    would falsely pass as "radial".
    """
    layer_type: str
    n: int
    tolerance_deg: float = 10.0
    radius_tolerance_frac: float = 0.25

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
        # Radius uniformity
        radii = [math.hypot(l["x"] + l["w"]/2 - cx, l["y"] + l["h"]/2 - cy) for l in layers]
        if min(radii) <= 0.5:  # all on top of each other
            radius_ok = False
            radius_msg = "layers degenerate (zero radius)"
        else:
            ratio = max(radii) / min(radii)
            radius_ok = ratio - 1 <= self.radius_tolerance_frac
            radius_msg = f"radius ratio {ratio:.2f}"
        passed = max_dev <= self.tolerance_deg and radius_ok
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.n} {self.layer_type} radial: angular dev {max_dev:.1f}° "
                    f"(expected {expected:.1f}°, tol {self.tolerance_deg}°), {radius_msg}",
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


# ─────────────────────────────────────────────────────────────
# CORE additions — cross-type spatial relationships
# ─────────────────────────────────────────────────────────────


def _bbox_overlap(a: dict, b: dict) -> bool:
    return (a["x"] < b["x"] + b["w"] and a["x"] + a["w"] > b["x"]
            and a["y"] < b["y"] + b["h"] and a["y"] + a["h"] > b["y"])


def _document_ordinals(doc: dict) -> dict:
    """Return {id(layer): ordinal} via DFS — later ordinal == higher in z-order."""
    ordinals: dict = {}
    counter = [0]

    def walk(nodes):
        for n in nodes:
            ordinals[id(n)] = counter[0]
            counter[0] += 1
            if "children" in n:
                walk(n["children"])

    for page in doc.get("pages", []):
        walk(page.get("children", []))
    return ordinals


@dataclass
class LayerOnTopOf:
    """At least one (type_a, type_b) pair where a is later in z-order than b
    AND their bounding boxes overlap (a is visibly stacked on top of b).

    require_overlap=False relaxes the bbox check (useful when shapes only
    touch at an edge, like roof-on-body)."""
    type_a: str
    type_b: str
    require_overlap: bool = True

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        ordinals = _document_ordinals(doc)
        a_layers = find_layers_by_type(doc, self.type_a)
        b_layers = find_layers_by_type(doc, self.type_b)
        if not a_layers or not b_layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need both {self.type_a} and {self.type_b} layers")
        for a in a_layers:
            for b in b_layers:
                if id(a) == id(b):
                    continue
                if ordinals[id(a)] > ordinals[id(b)]:
                    if not self.require_overlap or _bbox_overlap(a, b):
                        return CheckResult(passed=True, score=1.0, max_score=1.0,
                                           message=f"{self.type_a} on top of {self.type_b}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.type_a} stacked on top of any {self.type_b}",
        )


@dataclass
class LayerInFrontOf:
    """Every type_a layer is later in document z-order than every type_b layer
    (drawn last → renders on top). No bbox-overlap requirement.

    Stricter than LayerOnTopOf: catches z-order swaps even when shapes only
    touch at an edge."""
    type_a: str
    type_b: str

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        ordinals = _document_ordinals(doc)
        a_layers = find_layers_by_type(doc, self.type_a)
        b_layers = find_layers_by_type(doc, self.type_b)
        if not a_layers or not b_layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need both {self.type_a} and {self.type_b} layers")
        min_a_ord = min(ordinals[id(a)] for a in a_layers)
        max_b_ord = max(ordinals[id(b)] for b in b_layers)
        passed = min_a_ord > max_b_ord
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"all {self.type_a} drawn after all {self.type_b} (z-order ok)" if passed
                    else f"{self.type_a} z-order min {min_a_ord} ≤ {self.type_b} z-order max {max_b_ord}",
        )


@dataclass
class LayerInFrontOfLargestLayer:
    """Every type_a layer is later in z-order than the largest type_b layer."""
    type_a: str
    type_b: str

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        ordinals = _document_ordinals(doc)
        a_layers = find_layers_by_type(doc, self.type_a)
        b_layers = find_layers_by_type(doc, self.type_b)
        if not a_layers or not b_layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need both {self.type_a} and {self.type_b} layers")
        anchor = max(b_layers, key=lambda l: l["w"] * l["h"])
        anchor_ord = ordinals[id(anchor)]
        min_a_ord = min(ordinals[id(a)] for a in a_layers)
        passed = min_a_ord > anchor_ord
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"all {self.type_a} drawn after largest {self.type_b}" if passed
                    else f"{self.type_a} z-order min {min_a_ord} before largest {self.type_b} z-order {anchor_ord}",
        )


@dataclass
class LayerCenteredOnLayer:
    """At least one (type_a, type_b) cross-type pair shares a center within tolerance.

    axis="both": both x and y centers must match (default — original behavior).
    axis="x":    only x-centers must match (e.g. roof x-centered on body, regardless of y).
    axis="y":    only y-centers must match.
    """
    type_a: str
    type_b: str
    tolerance: float = 5.0
    axis: str = "both"

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        a_layers = find_layers_by_type(doc, self.type_a)
        b_layers = find_layers_by_type(doc, self.type_b)
        if not a_layers or not b_layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need both {self.type_a} and {self.type_b} layers")
        for a in a_layers:
            for b in b_layers:
                if id(a) == id(b):
                    continue
                acx, acy = a["x"] + a["w"] / 2, a["y"] + a["h"] / 2
                bcx, bcy = b["x"] + b["w"] / 2, b["y"] + b["h"] / 2
                x_ok = abs(acx - bcx) <= self.tolerance
                y_ok = abs(acy - bcy) <= self.tolerance
                if self.axis == "x" and x_ok:
                    return CheckResult(passed=True, score=1.0, max_score=1.0,
                                       message=f"{self.type_a} x-centered on {self.type_b}")
                if self.axis == "y" and y_ok:
                    return CheckResult(passed=True, score=1.0, max_score=1.0,
                                       message=f"{self.type_a} y-centered on {self.type_b}")
                if self.axis == "both" and x_ok and y_ok:
                    return CheckResult(passed=True, score=1.0, max_score=1.0,
                                       message=f"{self.type_a} centered on {self.type_b}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.type_a} center matches any {self.type_b} center on {self.axis} (tol {self.tolerance}px)",
        )


@dataclass
class LayerCenteredOnLayerSetCentroid:
    """At least one type_a layer is centered on the collective center of type_b layers."""
    type_a: str
    type_b: str
    tolerance: float = 10.0

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        anchors = find_layers_by_type(doc, self.type_a)
        satellites = find_layers_by_type(doc, self.type_b)
        if not anchors or not satellites:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need both {self.type_a} and {self.type_b} layers")
        centroid = (
            sum(layer_center(l)[0] for l in satellites) / len(satellites),
            sum(layer_center(l)[1] for l in satellites) / len(satellites),
        )
        best = min(
            math.hypot(layer_center(anchor)[0] - centroid[0], layer_center(anchor)[1] - centroid[1])
            for anchor in anchors
        )
        passed = best <= self.tolerance
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.type_a} centered on {self.type_b} centroid ({best:.1f}px)" if passed
                    else f"{self.type_a} center is {best:.1f}px from {self.type_b} centroid",
        )


@dataclass
class LayerNextTo:
    """A's bbox sits on the requested side of B's bbox (edges touching ±tolerance,
    plus overlap on the perpendicular axis so they're actually neighbors).

    side: "above" | "below" | "left" | "right"
    """
    type_a: str
    type_b: str
    side: str
    tolerance: float = 8.0

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        a_layers = find_layers_by_type(doc, self.type_a)
        b_layers = find_layers_by_type(doc, self.type_b)
        if not a_layers or not b_layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need both {self.type_a} and {self.type_b} layers")
        t = self.tolerance
        for a in a_layers:
            for b in b_layers:
                if id(a) == id(b):
                    continue
                horiz_overlap = a["x"] < b["x"] + b["w"] and a["x"] + a["w"] > b["x"]
                vert_overlap = a["y"] < b["y"] + b["h"] and a["y"] + a["h"] > b["y"]
                if self.side == "above":
                    gap = b["y"] - (a["y"] + a["h"])
                    if abs(gap) <= t and horiz_overlap:
                        return CheckResult(passed=True, score=1.0, max_score=1.0,
                                           message=f"{self.type_a} above {self.type_b}")
                elif self.side == "below":
                    gap = a["y"] - (b["y"] + b["h"])
                    if abs(gap) <= t and horiz_overlap:
                        return CheckResult(passed=True, score=1.0, max_score=1.0,
                                           message=f"{self.type_a} below {self.type_b}")
                elif self.side == "left":
                    gap = b["x"] - (a["x"] + a["w"])
                    if abs(gap) <= t and vert_overlap:
                        return CheckResult(passed=True, score=1.0, max_score=1.0,
                                           message=f"{self.type_a} left of {self.type_b}")
                elif self.side == "right":
                    gap = a["x"] - (b["x"] + b["w"])
                    if abs(gap) <= t and vert_overlap:
                        return CheckResult(passed=True, score=1.0, max_score=1.0,
                                           message=f"{self.type_a} right of {self.type_b}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.type_a} sits {self.side} of any {self.type_b} (tol {t}px)",
        )


@dataclass
class LayerWidthFraction:
    """At least one inner_type child of a parent_type layer has width in
    [min_frac, max_frac] × parent's width. Relative-size check."""
    inner_type: str
    parent_type: str
    min_frac: float
    max_frac: float

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        for parent in find_layers_by_type(doc, self.parent_type):
            if not parent.get("w"):
                continue
            for child in parent.get("children", []):
                if child.get("type") != self.inner_type:
                    continue
                frac = child["w"] / parent["w"]
                if self.min_frac <= frac <= self.max_frac:
                    return CheckResult(passed=True, score=1.0, max_score=1.0,
                                       message=f"{self.inner_type} width = {frac:.2f} × {self.parent_type}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.inner_type} with width fraction in [{self.min_frac}, {self.max_frac}]",
        )


# ─────────────────────────────────────────────────────────────
# EDGE additions
# ─────────────────────────────────────────────────────────────


@dataclass
class LayersHaveRotations:
    """Layers of layer_type collectively cover an expected set of rotation values
    with `count_per` layers at each value (any global offset is fine).

    e.g. expected=[0, 90], count_per=2 → exactly 2 layers near 0° and 2 near 90°.
    """
    layer_type: str
    expected: list
    count_per: int = 1
    tolerance_deg: float = 5.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) != len(self.expected) * self.count_per:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need exactly {len(self.expected) * self.count_per} {self.layer_type}, found {len(layers)}")
        rotations = [(l.get("rotation", 0) % 360) for l in layers]
        for expected_rot in self.expected:
            target = expected_rot % 360
            matched = sum(1 for r in rotations if abs(((r - target + 180) % 360) - 180) <= self.tolerance_deg)
            if matched < self.count_per:
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"Need {self.count_per} {self.layer_type} at {target}°, found {matched}")
        return CheckResult(
            passed=True, score=1.0, max_score=1.0,
            message=f"{self.layer_type} rotations match expected set {self.expected}",
        )


@dataclass
class LayersAlternatingColors:
    """Sorted layers of layer_type alternate between exactly `n_colors` distinct fills
    in a periodic A,B,A,B... pattern (or A,B,C,A,B,C... for n_colors=3).

    sort_axis ∈ {"x", "y", "angle"}. With "angle", layers are sorted by their angle
    around the layer-set centroid — used for radial layouts where alternation
    should cycle around the wheel, not along x/y."""
    layer_type: str
    n_colors: int
    sort_axis: str = "x"        # "x" | "y" | "angle"
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < self.n_colors * 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥{self.n_colors*2} {self.layer_type} layers, found {len(layers)}")
        if self.sort_axis == "x":
            ordered = sorted(layers, key=lambda l: l["x"] + l["w"] / 2)
        elif self.sort_axis == "angle":
            cx = sum(l["x"] + l["w"] / 2 for l in layers) / len(layers)
            cy = sum(l["y"] + l["h"] / 2 for l in layers) / len(layers)
            ordered = sorted(layers, key=lambda l: math.atan2(
                (l["y"] + l["h"] / 2) - cy, (l["x"] + l["w"] / 2) - cx))
        else:
            ordered = sorted(layers, key=lambda l: l["y"] + l["h"] / 2)
        # Capture first n_colors fill colors as the cycle
        cycle: list = []
        for l in ordered[: self.n_colors]:
            fills = l.get("fills", [])
            if not fills or fills[0].get("kind") != "solid":
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"{self.layer_type} missing solid fill in alternation cycle")
            c = fills[0].get("color", {})
            cycle.append((c.get("r", 0), c.get("g", 0), c.get("b", 0)))
        # The cycle's colors must themselves be distinct — otherwise a uniform-fill
        # set of layers would falsely satisfy the alternation pattern.
        for i in range(len(cycle)):
            for j in range(i+1, len(cycle)):
                a, b = cycle[i], cycle[j]
                if max(abs(a[k]-b[k]) for k in range(3)) <= self.tolerance:
                    return CheckResult(passed=False, score=0.0, max_score=1.0,
                                       message=f"{self.layer_type} alternation cycle uses fewer than {self.n_colors} distinct colors")
        # Check rest of layers cycle through these colors
        for i, l in enumerate(ordered):
            expected_rgb = cycle[i % self.n_colors]
            fills = l.get("fills", [])
            if not fills or fills[0].get("kind") != "solid":
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"Layer at index {i} has no solid fill")
            c = fills[0].get("color", {})
            actual = (c.get("r", 0), c.get("g", 0), c.get("b", 0))
            if max(abs(a - b) for a, b in zip(actual, expected_rgb)) > self.tolerance:
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"{self.layer_type} index {i}: color breaks {self.n_colors}-cycle")
        return CheckResult(
            passed=True, score=1.0, max_score=1.0,
            message=f"{self.layer_type} alternates {self.n_colors} colors in order on {self.sort_axis} axis",
        )


@dataclass
class OffsetGridLayout:
    """rows × cols layers of layer_type form an offset/honeycomb grid where
    every other row is shifted by ~0.5 × cell-width."""
    layer_type: str
    rows: int
    cols: int
    tolerance: float = 12.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        expected = self.rows * self.cols
        if len(layers) != expected:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need exactly {expected} {self.layer_type}, found {len(layers)}")
        by_y = sorted(layers, key=lambda l: l["y"] + l["h"] / 2)
        row_groups: list = []
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
        # Even rows align on column X; odd rows offset by ~half cell-width
        rows_sorted = [sorted(g, key=lambda l: l["x"] + l["w"] / 2) for g in row_groups]
        cell_w = rows_sorted[0][0]["w"]
        even_xs = [g[0]["x"] for g in rows_sorted[::2]]
        odd_xs = [g[0]["x"] for g in rows_sorted[1::2]]
        if odd_xs:
            offset = abs((odd_xs[0] - even_xs[0]) - cell_w / 2)
            if offset > self.tolerance:
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"Odd-row offset {offset:.1f}px ≠ half cell width ({cell_w/2:.1f}px)")
        return CheckResult(
            passed=True, score=1.0, max_score=1.0,
            message=f"{self.rows}x{self.cols} offset grid of {self.layer_type} confirmed",
        )


@dataclass
class RadialDistributionExcludeCentral:
    """n+1 layers of layer_type total: the most-central one is the 'core' (skipped),
    the remaining n must be radially distributed at equal angular steps AND at
    approximately the same radius from the core."""
    layer_type: str
    n: int
    tolerance_deg: float = 12.0
    radius_tolerance_frac: float = 0.25

    def run(self, log: dict) -> CheckResult:
        import math
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) != self.n + 1:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need exactly {self.n + 1} {self.layer_type}, found {len(layers)}")
        cx = sum(l["x"] + l["w"] / 2 for l in layers) / len(layers)
        cy = sum(l["y"] + l["h"] / 2 for l in layers) / len(layers)
        # The core is the layer closest to the centroid
        core = min(layers, key=lambda l: ((l["x"] + l["w"] / 2 - cx) ** 2 + (l["y"] + l["h"] / 2 - cy) ** 2))
        ring = [l for l in layers if l is not core]
        rcx = core["x"] + core["w"] / 2
        rcy = core["y"] + core["h"] / 2
        angles = sorted(
            (math.degrees(math.atan2(l["y"] + l["h"] / 2 - rcy, l["x"] + l["w"] / 2 - rcx)) % 360)
            for l in ring
        )
        gaps = [angles[i + 1] - angles[i] for i in range(len(angles) - 1)]
        gaps.append(360 - angles[-1] + angles[0])
        expected = 360 / self.n
        max_dev = max(abs(g - expected) for g in gaps)
        radii = [math.hypot(l["x"] + l["w"]/2 - rcx, l["y"] + l["h"]/2 - rcy) for l in ring]
        if min(radii) <= 0.5:
            radius_ok = False
            radius_msg = "ring layers degenerate"
        else:
            ratio = max(radii) / min(radii)
            radius_ok = ratio - 1 <= self.radius_tolerance_frac
            radius_msg = f"radius ratio {ratio:.2f}"
        passed = max_dev <= self.tolerance_deg and radius_ok
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.n} {self.layer_type} radial around core: gap dev {max_dev:.1f}° "
                    f"(tol {self.tolerance_deg}°), {radius_msg}",
        )


@dataclass
class LayersSameDimensionsExcludeCentral:
    """Among layers of layer_type (≥3 total), the layer closest to the centroid
    is the 'core' and is skipped. The remaining layers must all have the same
    w/h within tolerance. Use for petal-and-core flowers where petals must be
    uniform but the core is a different element."""
    layer_type: str
    tolerance: float = 6.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 3:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥3 {self.layer_type}, found {len(layers)}")
        cx = sum(l["x"] + l["w"] / 2 for l in layers) / len(layers)
        cy = sum(l["y"] + l["h"] / 2 for l in layers) / len(layers)
        core = min(layers, key=lambda l: (l["x"] + l["w"] / 2 - cx) ** 2 + (l["y"] + l["h"] / 2 - cy) ** 2)
        ring = [l for l in layers if l is not core]
        ref_w, ref_h = ring[0]["w"], ring[0]["h"]
        failures = [
            f"{l['id'][:8]}: {l['w']:.0f}×{l['h']:.0f} ≠ {ref_w:.0f}×{ref_h:.0f}"
            for l in ring[1:]
            if abs(l["w"] - ref_w) > self.tolerance or abs(l["h"] - ref_h) > self.tolerance
        ]
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=(f"All {len(ring)} non-central {self.layer_type} same size "
                     f"({ref_w:.0f}×{ref_h:.0f}, tol {self.tolerance:.0f}px)") if passed
                    else f"non-central {self.layer_type} mismatched: " + "; ".join(failures),
        )


@dataclass
class LayersElongatedExcludeCentral:
    """Among layers of layer_type (≥3 total), the centermost is treated as 'core'
    and skipped. Every other layer must have max(w,h)/min(w,h) ≥ min_ratio.
    Orientation-agnostic — works for petals at any rotation."""
    layer_type: str
    min_ratio: float = 1.5

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 3:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥3 {self.layer_type}, found {len(layers)}")
        cx = sum(l["x"] + l["w"] / 2 for l in layers) / len(layers)
        cy = sum(l["y"] + l["h"] / 2 for l in layers) / len(layers)
        core = min(layers, key=lambda l: (l["x"] + l["w"] / 2 - cx) ** 2 + (l["y"] + l["h"] / 2 - cy) ** 2)
        ring = [l for l in layers if l is not core]
        failures = []
        for l in ring:
            w, h = l["w"], l["h"]
            if w == 0 or h == 0:
                failures.append(f"{l['id'][:8]}: zero dimension")
                continue
            ratio = max(w, h) / min(w, h)
            if ratio < self.min_ratio:
                failures.append(f"{l['id'][:8]}: ratio={ratio:.2f} < {self.min_ratio}")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=(f"All {len(ring)} non-central {self.layer_type} elongated "
                     f"(long/short ≥ {self.min_ratio})") if passed
                    else "non-central {self.layer_type} not elongated enough: " + "; ".join(failures),
        )


@dataclass
class LayersSmallerThanCentralLayer:
    """Among layers of layer_type (≥2 total), the centermost is the 'core' and
    every other layer must have area (w*h) ≤ core_area * max_ratio. Defaults to
    0.95 — small buffer for measurement noise but still enforces visibly-smaller."""
    layer_type: str
    max_ratio: float = 0.95

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥2 {self.layer_type}, found {len(layers)}")
        cx = sum(l["x"] + l["w"] / 2 for l in layers) / len(layers)
        cy = sum(l["y"] + l["h"] / 2 for l in layers) / len(layers)
        core = min(layers, key=lambda l: (l["x"] + l["w"] / 2 - cx) ** 2 + (l["y"] + l["h"] / 2 - cy) ** 2)
        core_area = core["w"] * core["h"]
        if core_area <= 0:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"central {self.layer_type} has zero area")
        max_allowed = core_area * self.max_ratio
        ring = [l for l in layers if l is not core]
        failures = []
        for l in ring:
            a = l["w"] * l["h"]
            if a > max_allowed:
                failures.append(f"{l['id'][:8]}: area {a:.0f} > {max_allowed:.0f} ({a / core_area:.0%} of core)")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=(f"All {len(ring)} non-central {self.layer_type} smaller than core "
                     f"(≤ {self.max_ratio:.0%} of {core_area:.0f}px²)") if passed
                    else "non-central {self.layer_type} too large: " + "; ".join(failures),
        )


@dataclass
class CentralLayerIsCircular:
    """Among layers of layer_type (≥2 total), the centermost has w ≈ h within
    tolerance. Use to enforce a round center against ring elements that are
    intentionally not round."""
    layer_type: str
    tolerance: float = 4.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥2 {self.layer_type}, found {len(layers)}")
        cx = sum(l["x"] + l["w"] / 2 for l in layers) / len(layers)
        cy = sum(l["y"] + l["h"] / 2 for l in layers) / len(layers)
        core = min(layers, key=lambda l: (l["x"] + l["w"] / 2 - cx) ** 2 + (l["y"] + l["h"] / 2 - cy) ** 2)
        diff = abs(core["w"] - core["h"])
        passed = diff <= self.tolerance
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=(f"central {self.layer_type} circular ({core['w']:.0f}×{core['h']:.0f})") if passed
                    else f"central {self.layer_type} not circular: "
                         f"{core['w']:.0f}×{core['h']:.0f} (diff {diff:.1f}px > {self.tolerance:.0f})",
        )


@dataclass
class LayersTouchCentralLayer:
    """Among layers of layer_type (≥2 total), the layer closest to the centroid
    is the 'core'. Every other layer's inner tip must approximately touch the
    core's outer edge.

    Geometry: petal_center_distance ≈ core_radius + petal_long_half_axis.
    Treats the core as a circle (radius = avg of w/2, h/2). Treats each ring
    petal as oriented with its long axis pointing radially outward (which is
    the standard rotate-duplicate flower construction).

    tolerance: allowed gap in pixels (both inward overlap and outward space).
    """
    layer_type: str
    tolerance: float = 18.0

    def run(self, log: dict) -> CheckResult:
        import math
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥2 {self.layer_type}, found {len(layers)}")
        cx_all = sum(l["x"] + l["w"] / 2 for l in layers) / len(layers)
        cy_all = sum(l["y"] + l["h"] / 2 for l in layers) / len(layers)
        core = min(layers, key=lambda l: (l["x"] + l["w"] / 2 - cx_all) ** 2 + (l["y"] + l["h"] / 2 - cy_all) ** 2)
        ring = [l for l in layers if l is not core]
        ccx = core["x"] + core["w"] / 2
        ccy = core["y"] + core["h"] / 2
        core_r = (core["w"] + core["h"]) / 4
        misses = []
        for l in ring:
            pcx = l["x"] + l["w"] / 2
            pcy = l["y"] + l["h"] / 2
            actual_d = math.hypot(pcx - ccx, pcy - ccy)
            long_half = max(l["w"], l["h"]) / 2
            expected_d = core_r + long_half
            gap = actual_d - expected_d
            if abs(gap) > self.tolerance:
                misses.append(f"{l['id'][:8]}: gap {gap:+.0f}px from core edge")
        passed = not misses
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=(f"All {len(ring)} ring {self.layer_type} touch core edge "
                     f"(tol {self.tolerance:.0f}px)") if passed
                    else "petal-to-core gap mismatch: " + "; ".join(misses),
        )


@dataclass
class LinesOnDiagonal:
    """Two lines run corner-to-corner across a rectangle (one TL→BR, one TR→BL),
    forming an X. Uses Line.p1, p2 in absolute canvas coordinates."""
    rect_type: str = "rectangle"
    line_type: str = "line"
    tolerance: float = 12.0

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        rects = find_layers_by_type(doc, self.rect_type)
        lines = find_layers_by_type(doc, self.line_type)
        if not rects or len(lines) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥1 {self.rect_type} and ≥2 {self.line_type}")
        for r in rects:
            tl = (r["x"], r["y"])
            tr = (r["x"] + r["w"], r["y"])
            bl = (r["x"], r["y"] + r["h"])
            br = (r["x"] + r["w"], r["y"] + r["h"])
            corners = {"tl-br": (tl, br), "tr-bl": (tr, bl)}
            matched = set()
            for line in lines:
                p1, p2 = line_endpoints(line)
                for diag, (c1, c2) in corners.items():
                    near_a = abs(p1[0] - c1[0]) < self.tolerance and abs(p1[1] - c1[1]) < self.tolerance \
                             and abs(p2[0] - c2[0]) < self.tolerance and abs(p2[1] - c2[1]) < self.tolerance
                    near_b = abs(p1[0] - c2[0]) < self.tolerance and abs(p1[1] - c2[1]) < self.tolerance \
                             and abs(p2[0] - c1[0]) < self.tolerance and abs(p2[1] - c1[1]) < self.tolerance
                    if near_a or near_b:
                        matched.add(diag)
            if len(matched) == 2:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"2 lines form X across {self.rect_type}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No 2 {self.line_type}s span the {self.rect_type} diagonals",
        )


@dataclass
class LayersFlankLayer:
    """Layers of `flanker_type` flank a `pivot_type` instance: at least one
    flanker has center_x < pivot.center_x AND at least one has center_x >
    pivot.center_x. Picks the pivot that satisfies the constraint if any.

    Useful for "windows on either side of door" / "caps top and bottom of body".
    """
    flanker_type: str
    pivot_type: str
    axis: str = "x"               # "x" → flanks horizontally; "y" → vertically
    tolerance: float = 5.0

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        flankers = find_layers_by_type(doc, self.flanker_type)
        pivots = find_layers_by_type(doc, self.pivot_type)
        if len(flankers) < 2 or not pivots:
            return CheckResult(
                passed=False, score=0.0, max_score=1.0,
                message=f"Need ≥2 {self.flanker_type} + ≥1 {self.pivot_type} (got "
                        f"{len(flankers)}+{len(pivots)})",
            )
        for pivot in pivots:
            if self.axis == "x":
                p_center = pivot["x"] + pivot["w"] / 2
                lower = sum(1 for f in flankers if f["x"] + f["w"] / 2 < p_center - self.tolerance)
                upper = sum(1 for f in flankers if f["x"] + f["w"] / 2 > p_center + self.tolerance)
            else:
                p_center = pivot["y"] + pivot["h"] / 2
                lower = sum(1 for f in flankers if f["y"] + f["h"] / 2 < p_center - self.tolerance)
                upper = sum(1 for f in flankers if f["y"] + f["h"] / 2 > p_center + self.tolerance)
            if lower >= 1 and upper >= 1:
                return CheckResult(
                    passed=True, score=1.0, max_score=1.0,
                    message=f"{self.flanker_type} flanks {self.pivot_type} on {self.axis}",
                )
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.pivot_type} is flanked by {self.flanker_type} on both sides ({self.axis})",
        )


@dataclass
class LayerSizeAtLeast:
    """Every layer of layer_type has w ≥ min_w AND h ≥ min_h.
    Catches degenerate 1×1 / 5×5 shapes that satisfy other checks trivially."""
    layer_type: str
    min_w: float = 0.0
    min_h: float = 0.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        if self.layer_type in ("line", "arrow"):
            min_length = max(self.min_w, self.min_h)
            failures = [
                f"{l['id'][:8]}: length {line_length(l):.1f}px below min {min_length}px"
                for l in layers if line_length(l) < min_length
            ]
            passed = not failures
            return CheckResult(
                passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
                message=f"All {self.layer_type} length >= {min_length}px" if passed
                        else "; ".join(failures),
            )
        failures = [
            f"{l['id'][:8]}: {l['w']}×{l['h']} below min {self.min_w}×{self.min_h}"
            for l in layers if l["w"] < self.min_w or l["h"] < self.min_h
        ]
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} ≥ {self.min_w}×{self.min_h}" if passed
                    else "; ".join(failures),
        )


@dataclass
class AllLayerWidthFraction:
    """Every inner_type child of any parent_type layer has width in [min_frac, max_frac]
    × parent's width. Stricter than LayerWidthFraction (which passes on ≥1 child)."""
    inner_type: str
    parent_type: str
    min_frac: float
    max_frac: float

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        parents = find_layers_by_type(doc, self.parent_type)
        if not parents:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.parent_type} layers found")
        children_seen = 0
        failures = []
        for parent in parents:
            if not parent.get("w"):
                continue
            for child in parent.get("children", []):
                if child.get("type") != self.inner_type:
                    continue
                children_seen += 1
                frac = child["w"] / parent["w"]
                if not (self.min_frac <= frac <= self.max_frac):
                    failures.append(f"{child['id'][:8]}: width frac {frac:.2f} ∉ [{self.min_frac}, {self.max_frac}]")
        if children_seen == 0:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.inner_type} children inside any {self.parent_type}")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {children_seen} {self.inner_type} children within [{self.min_frac}, {self.max_frac}] of {self.parent_type}" if passed
                    else "; ".join(failures),
        )


@dataclass
class SmallerLayerInsideLarger:
    """Among layers of layer_type, the largest (by area) is the container; every
    other layer of layer_type must fit inside its bbox (within tolerance overhang).

    Closes the gap in LayerBoundsInside(rectangle, rectangle) where 'body fits
    inside door' would falsely pass when door > body."""
    layer_type: str
    tolerance: float = 4.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥2 {self.layer_type} layers, found {len(layers)}")
        outer = max(layers, key=lambda l: l["w"] * l["h"])
        t = self.tolerance
        failures = []
        for inner in layers:
            if inner is outer:
                continue
            if not (inner["x"] >= outer["x"] - t
                    and inner["y"] >= outer["y"] - t
                    and inner["x"] + inner["w"] <= outer["x"] + outer["w"] + t
                    and inner["y"] + inner["h"] <= outer["y"] + outer["h"] + t):
                failures.append(f"{inner['id'][:8]} not inside largest {self.layer_type}")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All smaller {self.layer_type} fit inside largest" if passed
                    else "; ".join(failures),
        )


@dataclass
class LayerAreaRatioAtLeast:
    """Among layers of layer_type, (largest area) / (second-largest area) >= min_ratio.
    Distinguishes a clear primary instance from a same-type sidekick (e.g., body
    vs. door — both rectangles — where body should dominate by area)."""
    layer_type: str
    min_ratio: float = 2.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥2 {self.layer_type} layers, got {len(layers)}")
        areas = sorted((l["w"] * l["h"] for l in layers), reverse=True)
        if areas[1] <= 0:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"degenerate {self.layer_type} (zero area)")
        ratio = areas[0] / areas[1]
        passed = ratio >= self.min_ratio
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type} area ratio {ratio:.2f} ≥ {self.min_ratio}" if passed
                    else f"{self.layer_type} area ratio {ratio:.2f} < {self.min_ratio} (largest not dominant)",
        )


@dataclass
class CrossTypeAreaRatioAtLeast:
    """(Largest big_type area) / (largest small_type area) >= min_ratio.
    Catches: 'small' element inflated to match a 'big' element (fold == rect, thumb == pill)."""
    big_type: str
    small_type: str
    min_ratio: float = 2.0

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        bigs = find_layers_by_type(doc, self.big_type)
        smalls = find_layers_by_type(doc, self.small_type)
        if not bigs or not smalls:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need both {self.big_type} and {self.small_type}")
        big_area = max(l["w"] * l["h"] for l in bigs)
        small_area = max(l["w"] * l["h"] for l in smalls)
        if small_area <= 0:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"degenerate {self.small_type} (zero area)")
        ratio = big_area / small_area
        passed = ratio >= self.min_ratio
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.big_type}/{self.small_type} area ratio {ratio:.2f} ≥ {self.min_ratio}" if passed
                    else f"{self.big_type}/{self.small_type} area ratio {ratio:.2f} < {self.min_ratio}",
        )


@dataclass
class SmallerLayerCenteredOnLargerEdge:
    """Among layers of layer_type, the smallest (by area) has its `edge` aligned
    with the largest's same edge AND its center on the perpendicular axis aligned
    with the largest's center.

    Captures "door at the bottom-center of body" without needing explicit roles.

    edge ∈ {"top", "bottom", "left", "right"}; the alignment axis is implicit
    (top/bottom → align center_x; left/right → align center_y).
    """
    layer_type: str
    edge: str
    edge_tolerance: float = 10.0
    axis_tolerance: float = 30.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥2 {self.layer_type} layers, got {len(layers)}")
        largest = max(layers, key=lambda l: l["w"] * l["h"])
        smallest = min(layers, key=lambda l: l["w"] * l["h"])
        if largest is smallest:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"{self.layer_type} layers have identical area")
        if self.edge == "top":      lg, sm = largest["y"], smallest["y"]
        elif self.edge == "bottom": lg, sm = largest["y"] + largest["h"], smallest["y"] + smallest["h"]
        elif self.edge == "left":   lg, sm = largest["x"], smallest["x"]
        elif self.edge == "right":  lg, sm = largest["x"] + largest["w"], smallest["x"] + smallest["w"]
        else:
            raise ValueError(f"unknown edge: {self.edge}")
        edge_diff = abs(sm - lg)
        if self.edge in ("top", "bottom"):
            axis_diff = abs((smallest["x"] + smallest["w"] / 2) - (largest["x"] + largest["w"] / 2))
            axis_label = "center_x"
        else:
            axis_diff = abs((smallest["y"] + smallest["h"] / 2) - (largest["y"] + largest["h"] / 2))
            axis_label = "center_y"
        passed = edge_diff <= self.edge_tolerance and axis_diff <= self.axis_tolerance
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=(f"smallest {self.layer_type} {self.edge}-edge {edge_diff:.1f}px from largest, "
                     f"{axis_label} {axis_diff:.1f}px from largest "
                     f"(tol edge={self.edge_tolerance}, axis={self.axis_tolerance})"),
        )


@dataclass
class LayerAboveLargestLayer:
    """At least one top_type layer sits ABOVE the largest bottom_type layer:
       top.bottom ≈ bottom_largest.top (within tolerance) AND top.y < bottom_largest.y
       AND horizontal overlap.

    Stricter than LayerEdgesAligned because (a) only the largest bottom_type counts
    (so a coincidentally-aligned smaller sibling can't satisfy it), and (b) the
    top must actually be above (not overlapping inside)."""
    top_type: str
    bottom_type: str
    tolerance: float = 10.0

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        tops = find_layers_by_type(doc, self.top_type)
        bottoms = find_layers_by_type(doc, self.bottom_type)
        if not tops or not bottoms:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need both {self.top_type} and {self.bottom_type}")
        anchor = max(bottoms, key=lambda l: l["w"] * l["h"])
        anchor_x, anchor_y, anchor_w, _ = _visual_bounds(anchor)
        for top in tops:
            top_x, top_y, top_w, top_h = _visual_bounds(top)
            edge_diff = abs((top_y + top_h) - anchor_y)
            above = top_y < anchor_y
            horiz_overlap = (top_x < anchor_x + anchor_w
                             and top_x + top_w > anchor_x)
            if edge_diff <= self.tolerance and above and horiz_overlap:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.top_type} sits above largest {self.bottom_type}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.top_type} sits above largest {self.bottom_type} "
                    f"(need bottom-edge ≈ top-edge, fully above, horiz overlap)",
        )


@dataclass
class LayersAllShareEdge:
    """All layers of layer_type share the same coordinate on the given edge.

    edge ∈ {"top", "bottom", "left", "right", "center_x", "center_y"}.
    Useful for "5 bars share a bottom baseline" (LayerEdgesAligned only checks
    that ≥1 pair matches, which is too weak for set-wide alignment).
    """
    layer_type: str
    edge: str
    tolerance: float = 5.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥2 {self.layer_type}, got {len(layers)}")
        coords = []
        for l in layers:
            if self.edge == "top":
                coords.append(l["y"])
            elif self.edge == "bottom":
                coords.append(l["y"] + l["h"])
            elif self.edge == "left":
                coords.append(l["x"])
            elif self.edge == "right":
                coords.append(l["x"] + l["w"])
            elif self.edge == "center_x":
                coords.append(l["x"] + l["w"] / 2)
            elif self.edge == "center_y":
                coords.append(l["y"] + l["h"] / 2)
            else:
                raise ValueError(f"unknown edge: {self.edge}")
        spread = max(coords) - min(coords)
        passed = spread <= self.tolerance
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"all {self.layer_type}.{self.edge}: spread {spread:.1f}px (tol {self.tolerance}px)",
        )


@dataclass
class LayerSmallerThanLayer:
    """Every smaller_type layer is strictly smaller than every larger_type layer
    (max_frac × shortest dimension). Catches the "smaller centered circle" /
    "star inside square" deception where the so-called inner is actually the
    same size as or larger than the outer.

    Compares min(w, h) so a squashed inner can't pass via one tiny axis."""
    smaller_type: str
    larger_type: str
    max_frac: float = 0.8

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        smalls = find_layers_by_type(doc, self.smaller_type)
        larges = find_layers_by_type(doc, self.larger_type)
        if not smalls or not larges:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need both {self.smaller_type} and {self.larger_type}")
        anchor = max(larges, key=lambda l: l["w"] * l["h"])
        anchor_short = min(anchor["w"], anchor["h"])
        if anchor_short <= 0:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"degenerate {self.larger_type} (zero dimension)")
        failures = []
        for s in smalls:
            if id(s) == id(anchor):
                continue
            short = min(s["w"], s["h"])
            frac = short / anchor_short
            if frac > self.max_frac:
                failures.append(f"{s['id'][:8]}: short {short:.0f}/{anchor_short:.0f}={frac:.2f} > {self.max_frac}")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.smaller_type} ≤ {self.max_frac} of largest {self.larger_type}" if passed
                    else "; ".join(failures),
        )


@dataclass
class LayerShortDimensionAtMost:
    """Every layer of layer_type has min(w, h) ≤ max_value. Used as an absolute
    cap on giant shapes (e.g., star can't be 5000×5000)."""
    layer_type: str
    max_value: float

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = [
            f"{l['id'][:8]}: short={min(l['w'], l['h']):.0f} > {self.max_value}"
            for l in layers if min(l["w"], l["h"]) > self.max_value
        ]
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} short-dim ≤ {self.max_value}" if passed
                    else "; ".join(failures),
        )


@dataclass
class AllLayersAreCircular:
    """Every layer of layer_type has w ≈ h within tolerance (true circles only).

    Stricter than LayerIsCircular which passes if at least one is round —
    catches the case where one ellipse is a true circle but another is
    visually squashed (e.g. 200×60 oval clapper)."""
    layer_type: str
    tolerance: float = 3.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = [
            f"{l['id'][:8]}: {l['w']}×{l['h']}"
            for l in layers
            if not (l["w"] > 0 and l["h"] > 0 and abs(l["w"] - l["h"]) <= self.tolerance)
        ]
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {len(layers)} {self.layer_type} circular (±{self.tolerance}px)" if passed
                    else f"non-circular {self.layer_type}: " + "; ".join(failures),
        )


@dataclass
class FrameCountAtMost:
    """Document contains at most `maximum` frames at the page-root level (across all pages).

    Catches the design split into multiple top-level frames (e.g. shapes scattered
    across 2+ frames instead of one)."""
    maximum: int

    def run(self, log: dict) -> CheckResult:
        n = 0
        for page in log["outcome"]["document"].get("pages", []):
            for child in page.get("children", []):
                if child.get("type") == "frame":
                    n += 1
        passed = n <= self.maximum
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"top-level frames: {n} ≤ {self.maximum}" if passed
                    else f"top-level frames: {n} > {self.maximum} (design split across frames)",
        )


@dataclass
class LayersHaveDistinctCenters:
    """Among layers of layer_type, every pair has center distance >= min_offset.
    Catches "2 identical-bbox ellipses pretending to be distinct shapes" — when
    LayersOverlap also requires overlap, this enforces partial (not full) overlap.
    """
    layer_type: str
    min_offset: float = 20.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥2 {self.layer_type}, got {len(layers)}")
        for i in range(len(layers)):
            for j in range(i + 1, len(layers)):
                a = layers[i]; b = layers[j]
                acx, acy = a["x"] + a["w"] / 2, a["y"] + a["h"] / 2
                bcx, bcy = b["x"] + b["w"] / 2, b["y"] + b["h"] / 2
                dist = math.hypot(acx - bcx, acy - bcy)
                if dist < self.min_offset:
                    return CheckResult(passed=False, score=0.0, max_score=1.0,
                                       message=f"{self.layer_type} pair {i},{j} centers {dist:.1f}px apart < {self.min_offset}")
        return CheckResult(
            passed=True, score=1.0, max_score=1.0,
            message=f"All {self.layer_type} pairs have center offset ≥ {self.min_offset}",
        )


@dataclass
class LayersHaveDescendingArea:
    """Among layers of layer_type, sorting by area gives a strictly descending
    sequence where each pair (n, n+1) has area_n / area_{n+1} >= min_ratio.

    Catches "concentric circles, but iris ≈ pupil ≈ sclera" — every step in the
    nesting must be a real, visible size jump."""
    layer_type: str
    min_ratio: float = 1.5
    minimum_layers: int = 2

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < self.minimum_layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥{self.minimum_layers} {self.layer_type}, got {len(layers)}")
        areas = sorted((l["w"] * l["h"] for l in layers), reverse=True)
        for i in range(len(areas) - 1):
            if areas[i + 1] <= 0:
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"degenerate {self.layer_type} (zero area)")
            r = areas[i] / areas[i + 1]
            if r < self.min_ratio:
                return CheckResult(passed=False, score=0.0, max_score=1.0,
                                   message=f"{self.layer_type} sizes not descending: pair {i}/{i+1} ratio {r:.2f} < {self.min_ratio}")
        return CheckResult(passed=True, score=1.0, max_score=1.0,
                           message=f"All {len(layers)} {self.layer_type} sizes descend by ≥{self.min_ratio}× each step")


@dataclass
class LayersOrderedByRotation:
    """Among layers of layer_type, the one closest to rotation_first must come
    BEFORE (smaller coord) the one closest to rotation_second along the axis.

    Use case: hourglass triangles — the rotation-180 triangle (pointing down)
    must be positioned ABOVE (smaller y) the rotation-0 triangle (pointing up).
    Catches the "right rotations, wrong vertical order" deception."""
    layer_type: str
    rotation_first: float
    rotation_second: float
    axis: str = "y"        # "x" → first.center_x < second.center_x; "y" → first.center_y < second.center_y
    rotation_tolerance: float = 5.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) < 2:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need ≥2 {self.layer_type}, got {len(layers)}")
        def near(rot, target):
            return abs(((rot - target + 180) % 360) - 180) <= self.rotation_tolerance
        firsts = [l for l in layers if near(l.get("rotation", 0) % 360, self.rotation_first % 360)]
        seconds = [l for l in layers if near(l.get("rotation", 0) % 360, self.rotation_second % 360)]
        if not firsts or not seconds:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need {self.layer_type} at both {self.rotation_first}° and {self.rotation_second}°")
        if self.axis == "y":
            f_coord = min(l["y"] + l["h"] / 2 for l in firsts)
            s_coord = max(l["y"] + l["h"] / 2 for l in seconds)
        else:
            f_coord = min(l["x"] + l["w"] / 2 for l in firsts)
            s_coord = max(l["x"] + l["w"] / 2 for l in seconds)
        passed = f_coord < s_coord
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type} at {self.rotation_first}° before {self.rotation_second}° on {self.axis}" if passed
                    else f"{self.layer_type} at {self.rotation_first}° not before {self.rotation_second}° on {self.axis} (got {f_coord:.1f} ≥ {s_coord:.1f})",
        )


@dataclass
class LayersBracketAllOnAxis:
    """Among layers of bracket_type and inner_type:
       at least one bracket_type sits BEFORE all inner_type bounds, and
       at least one bracket_type sits AFTER all inner_type bounds (along axis).

    Stricter than LayersFlankLayer (which only checks one pivot's center): the
    inner span is taken across the union of all inner_type bboxes.
    Catches "cap inside triangle stack" / "left bracket between bars" deceptions.

    axis="y": bracket center_y < min(inner.top) − tol AND bracket center_y > max(inner.bottom) + tol
    axis="x": same logic on x.
    """
    bracket_type: str
    inner_type: str
    axis: str = "y"
    tolerance: float = 4.0

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        brackets = find_layers_by_type(doc, self.bracket_type)
        inners = find_layers_by_type(doc, self.inner_type)
        if not brackets or not inners or self.bracket_type == self.inner_type:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need distinct {self.bracket_type} and {self.inner_type}")
        if self.axis == "y":
            inner_min = min(i["y"] for i in inners)
            inner_max = max(i["y"] + i["h"] for i in inners)
            before = sum(1 for b in brackets if (b["y"] + b["h"] / 2) <= inner_min + self.tolerance)
            after  = sum(1 for b in brackets if (b["y"] + b["h"] / 2) >= inner_max - self.tolerance)
        else:
            inner_min = min(i["x"] for i in inners)
            inner_max = max(i["x"] + i["w"] for i in inners)
            before = sum(1 for b in brackets if (b["x"] + b["w"] / 2) <= inner_min + self.tolerance)
            after  = sum(1 for b in brackets if (b["x"] + b["w"] / 2) >= inner_max - self.tolerance)
        passed = before >= 1 and after >= 1
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.bracket_type} brackets all {self.inner_type} on {self.axis}" if passed
                    else f"{self.bracket_type} fails to bracket all {self.inner_type} on {self.axis} (before={before}, after={after})",
        )


@dataclass
class LineLengthEquals:
    """At least one line has the requested endpoint-to-endpoint length."""
    layer_type: str = "line"
    length: float = 0.0
    tolerance: float = 5.0

    def run(self, log: dict) -> CheckResult:
        lines = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not lines:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        best = min(((abs(line_length(line) - self.length), line) for line in lines), key=lambda item: item[0])
        diff, line = best
        passed = diff <= self.tolerance
        actual = line_length(line)
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type} length {actual:.1f}px ~= {self.length:.1f}px"
                    if passed else f"Closest {self.layer_type} length {actual:.1f}px differs from {self.length:.1f}px by {diff:.1f}px",
        )


@dataclass
class LineAngleEquals:
    """At least one line has the requested visual angle in degrees."""
    layer_type: str = "line"
    degrees: float = 0.0
    tolerance_deg: float = 5.0

    def run(self, log: dict) -> CheckResult:
        lines = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not lines:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        target = self.degrees % 360

        def angular_diff(line: dict) -> float:
            actual = line_angle_degrees(line) % 360
            return abs(((actual - target + 180) % 360) - 180)

        diff, line = min(((angular_diff(line), line) for line in lines), key=lambda item: item[0])
        actual = line_angle_degrees(line) % 360
        passed = diff <= self.tolerance_deg
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{self.layer_type} angle {actual:.1f}deg ~= {target:.1f}deg"
                    if passed else f"Closest {self.layer_type} angle {actual:.1f}deg differs from {target:.1f}deg by {diff:.1f}deg",
        )


@dataclass
class LinesShareEndpoint:
    """A minimum number of lines share a common visual endpoint."""
    layer_type: str = "line"
    minimum: int = 2
    tolerance: float = 5.0

    def run(self, log: dict) -> CheckResult:
        lines = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(lines) < self.minimum:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Need at least {self.minimum} {self.layer_type} layers")
        endpoints: list[tuple[str, tuple[float, float]]] = []
        for line in lines:
            p1, p2 = line_endpoints(line)
            line_id = line.get("id", "")
            endpoints.extend([(line_id, p1), (line_id, p2)])
        best_count = 0
        best_point = endpoints[0][1]
        for _, point in endpoints:
            shared_line_ids = {
                line_id
                for line_id, other in endpoints
                if math.hypot(point[0] - other[0], point[1] - other[1]) <= self.tolerance
            }
            count = len(shared_line_ids)
            if count > best_count:
                best_count = count
                best_point = point
        passed = best_count >= self.minimum
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"{best_count} {self.layer_type} endpoints share ({best_point[0]:.1f}, {best_point[1]:.1f})"
                    if passed else f"No shared endpoint among {self.layer_type} layers reaches {self.minimum} endpoints",
        )


@dataclass
class LayersOnRing:
    """
    Exactly `n` layers of `layer_type` form a ring:
      1) equal angular spacing around centroid
      2) similar radius from centroid
      3) non-trivial radius (not collapsed near center)
    """
    layer_type: str
    n: int
    angle_tolerance_deg: float = 8.0
    radius_tolerance_px: float = 20.0
    min_radius_px: float = 30.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) != self.n:
            return CheckResult(
                passed=False, score=0.0, max_score=1.0,
                message=f"Need exactly {self.n} {self.layer_type}, found {len(layers)}",
            )

        centers = [(l["x"] + l["w"] / 2, l["y"] + l["h"] / 2) for l in layers]
        cx = sum(p[0] for p in centers) / len(centers)
        cy = sum(p[1] for p in centers) / len(centers)

        radii = [math.hypot(px - cx, py - cy) for px, py in centers]
        min_r = min(radii)
        max_r = max(radii)
        radius_spread = max_r - min_r

        angles = sorted((math.degrees(math.atan2(py - cy, px - cx)) % 360) for px, py in centers)
        gaps = [angles[i + 1] - angles[i] for i in range(len(angles) - 1)]
        gaps.append(360 - angles[-1] + angles[0])
        expected_gap = 360 / self.n
        max_gap_dev = max(abs(g - expected_gap) for g in gaps)

        passed = (
            max_gap_dev <= self.angle_tolerance_deg
            and radius_spread <= self.radius_tolerance_px
            and min_r >= self.min_radius_px
        )
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=(
                f"{self.layer_type} ring: gap dev {max_gap_dev:.1f} deg (tol {self.angle_tolerance_deg} deg), "
                f"radius spread {radius_spread:.1f}px (tol {self.radius_tolerance_px}px), "
                f"min radius {min_r:.1f}px (min {self.min_radius_px}px)"
            ),
        )


@dataclass
class LinesRadialFromSharedEndpoint:
    """
    Exactly `n` line layers form a radial burst from one shared center endpoint.

    For each line we choose the endpoint closest to the inferred shared center,
    then use the opposite endpoint as the ray direction for angular spacing.
    """
    n: int
    center_tolerance_px: float = 12.0
    angle_tolerance_deg: float = 10.0
    min_length_px: float = 10.0
    length_tolerance_px: float = 60.0

    def run(self, log: dict) -> CheckResult:
        lines = find_layers_by_type(log["outcome"]["document"], "line")
        if len(lines) != self.n:
            return CheckResult(
                passed=False, score=0.0, max_score=1.0,
                message=f"Need exactly {self.n} line layers, found {len(lines)}",
            )

        endpoints: list[tuple[float, float]] = []
        line_points: list[tuple[tuple[float, float], tuple[float, float]]] = []
        for l in lines:
            p1 = (l.get("p1", {}).get("x", 0.0) + l["x"], l.get("p1", {}).get("y", 0.0) + l["y"])
            p2 = (l.get("p2", {}).get("x", 0.0) + l["x"], l.get("p2", {}).get("y", 0.0) + l["y"])
            line_points.append((p1, p2))
            endpoints.extend([p1, p2])

        best_center = None
        best_count = -1
        best_sum_dist = float("inf")
        for c in endpoints:
            dists = sorted(math.hypot(c[0] - p[0], c[1] - p[1]) for p in endpoints)
            near = [d for d in dists if d <= self.center_tolerance_px]
            count = len(near)
            sum_dist = sum(near)
            if count > best_count or (count == best_count and sum_dist < best_sum_dist):
                best_center = c
                best_count = count
                best_sum_dist = sum_dist

        assert best_center is not None
        if best_count < self.n:
            return CheckResult(
                passed=False, score=0.0, max_score=1.0,
                message=(
                    f"Shared-center endpoint cluster too weak: only {best_count}/{self.n} "
                    f"endpoints within {self.center_tolerance_px}px"
                ),
            )

        center = best_center
        angles: list[float] = []
        lengths: list[float] = []
        for p1, p2 in line_points:
            d1 = math.hypot(p1[0] - center[0], p1[1] - center[1])
            d2 = math.hypot(p2[0] - center[0], p2[1] - center[1])
            near, far = (p1, p2) if d1 <= d2 else (p2, p1)
            length = math.hypot(far[0] - near[0], far[1] - near[1])
            lengths.append(length)
            angles.append(math.degrees(math.atan2(far[1] - center[1], far[0] - center[0])) % 360)

        min_len = min(lengths)
        max_len = max(lengths)
        if min_len < self.min_length_px:
            return CheckResult(
                passed=False, score=0.0, max_score=1.0,
                message=f"Burst lines too short: min length {min_len:.1f}px (need >={self.min_length_px}px)",
            )

        sorted_angles = sorted(angles)
        gaps = [sorted_angles[i + 1] - sorted_angles[i] for i in range(len(sorted_angles) - 1)]
        gaps.append(360 - sorted_angles[-1] + sorted_angles[0])
        expected_gap = 360 / self.n
        max_gap_dev = max(abs(g - expected_gap) for g in gaps)
        length_spread = max_len - min_len

        passed = max_gap_dev <= self.angle_tolerance_deg and length_spread <= self.length_tolerance_px
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=(
                f"line burst: gap dev {max_gap_dev:.1f} deg (tol {self.angle_tolerance_deg} deg), "
                f"length spread {length_spread:.1f}px (tol {self.length_tolerance_px}px), "
                f"cluster hits {best_count}/{self.n}"
            ),
        )


@dataclass
class VectorsCurvedCountAtLeast:
    """
    At least `minimum` vectors contain curved segments (bezier handles present).
    """
    minimum: int

    def run(self, log: dict) -> CheckResult:
        vectors = find_layers_by_type(log["outcome"]["document"], "vector")
        curved = 0
        for v in vectors:
            network = v.get("network", {})
            segments = network.get("segments", [])
            has_curve = any(seg.get("handleFrom") is not None or seg.get("handleTo") is not None for seg in segments)
            if has_curve:
                curved += 1
        passed = curved >= self.minimum
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"curved vectors: expected >={self.minimum}, got {curved}",
        )


@dataclass
class LayersStrictlyNested:
    """
    Layers of a given type are strictly nested by size:
    sorted by area (largest->smallest), each inner layer must fit inside the
    previous outer layer with a strict size drop.
    """
    layer_type: str
    equals: int
    tolerance_px: float = 2.0
    min_size_drop_px: float = 4.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if len(layers) != self.equals:
            return CheckResult(
                passed=False, score=0.0, max_score=1.0,
                message=f"Need exactly {self.equals} {self.layer_type}, found {len(layers)}",
            )

        ordered = sorted(layers, key=lambda l: l["w"] * l["h"], reverse=True)
        t = self.tolerance_px
        for i in range(len(ordered) - 1):
            outer = ordered[i]
            inner = ordered[i + 1]
            if inner["w"] >= outer["w"] - self.min_size_drop_px or inner["h"] >= outer["h"] - self.min_size_drop_px:
                return CheckResult(
                    passed=False, score=0.0, max_score=1.0,
                    message=(
                        f"Layer {i+1} not strictly smaller than layer {i}: "
                        f"{inner['w']:.1f}x{inner['h']:.1f} vs {outer['w']:.1f}x{outer['h']:.1f}"
                    ),
                )
            if not (
                inner["x"] >= outer["x"] - t
                and inner["y"] >= outer["y"] - t
                and inner["x"] + inner["w"] <= outer["x"] + outer["w"] + t
                and inner["y"] + inner["h"] <= outer["y"] + outer["h"] + t
            ):
                return CheckResult(
                    passed=False, score=0.0, max_score=1.0,
                    message=f"Layer {i+1} is not nested inside layer {i} (tol {t}px)",
                )

        return CheckResult(
            passed=True, score=1.0, max_score=1.0,
            message=f"{self.layer_type} layers are strictly nested ({self.equals} total)",
        )
