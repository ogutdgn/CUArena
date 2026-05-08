from __future__ import annotations
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
class VisibleStrokeExists:
    """At least one layer of layer_type has a *rendered* stroke:
       - stroke.visible != False
       - paint.color.a >= min_alpha (default 0.05)
       - stroke.weight >= min_weight (default 0.5)
    Stricter than StrokeExists (which passes on any non-empty strokes array,
    even alpha=0 / weight=0 ones)."""
    layer_type: str
    min_alpha: float = 0.05
    min_weight: float = 0.5

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            for s in l.get("strokes", []):
                if s.get("visible", True) is False:
                    continue
                if s.get("weight", 0) < self.min_weight:
                    continue
                paint = s.get("paint", {}) or {}
                if paint.get("kind") == "solid":
                    a = paint.get("color", {}).get("a", 1.0)
                    if a < self.min_alpha:
                        continue
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} has visible stroke")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No {self.layer_type} with visible stroke")


@dataclass
class AllLayerStrokeVisible:
    """Every layer of layer_type has a *visible* stroke:
       - has at least one stroke with visible != False
       - stroke paint color alpha >= min_alpha
       - stroke weight >= min_weight
    Catches: alpha=0 strokes, visible=False strokes, zero-weight strokes (line types
    that exist structurally but render as nothing)."""
    layer_type: str
    min_alpha: float = 0.1
    min_weight: float = 0.5

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            strokes = l.get("strokes", []) or []
            visible_strokes = []
            for s in strokes:
                if s.get("visible", True) is False:
                    continue
                if s.get("weight", 0) < self.min_weight:
                    continue
                paint = s.get("paint", {}) or {}
                color = paint.get("color", {}) or {}
                if color.get("a", 1.0) < self.min_alpha:
                    continue
                visible_strokes.append(s)
            if not visible_strokes:
                failures.append(f"{l['id'][:8]}: no visible stroke")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} have visible strokes" if passed
                    else "; ".join(failures),
        )


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
class DistinctStrokeColors:
    """At least `minimum` perceptually-distinct stroke colors across the document.
    Parity with DistinctSolidColors, but for stroke paints."""
    minimum: int
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        from verifier.math_utils import find_all_layers
        seen: list = []
        for layer in find_all_layers(log["outcome"]["document"]):
            for stroke in layer.get("strokes", []):
                paint = stroke.get("paint", {})
                if paint.get("kind") != "solid":
                    continue
                c = paint.get("color", {})
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
            message=f"distinct stroke colors: expected ≥{self.minimum}, got {len(seen)}",
        )


@dataclass
class DistinctTypedStrokeColors:
    """At least `minimum` distinct stroke colors among layers of layer_type only.
    Stricter than DistinctStrokeColors which counts all layer types."""
    layer_type: str
    minimum: int
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        seen: list = []
        for l in layers:
            for stroke in l.get("strokes", []):
                paint = stroke.get("paint", {})
                if paint.get("kind") != "solid":
                    continue
                c = paint.get("color", {})
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
            message=f"distinct {self.layer_type} stroke colors: expected ≥{self.minimum}, got {len(seen)}",
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


@dataclass
class AllStrokeExists:
    """Every layer of layer_type has at least one visible non-zero stroke.
    Stricter than StrokeExists which passes on ≥1 layer with a stroke."""
    layer_type: str

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            strokes = l.get("strokes", [])
            ok = False
            for s in strokes:
                if s.get("visible", True) is False: continue
                if s.get("weight", 0) <= 0: continue
                paint = s.get("paint", {})
                color = paint.get("color", {})
                alpha = color.get("a", 1.0) if isinstance(color, dict) else 1.0
                if alpha <= 0: continue
                ok = True
                break
            if not ok:
                failures.append(f"{l['id'][:8]}: no visible non-zero stroke")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} have a stroke" if passed
                    else "; ".join(failures),
        )


@dataclass
class AllStrokeColorEquals:
    """Every layer of layer_type has its first solid stroke ≈ expected_rgb.
    Stricter than StrokeColorEquals (≥1 layer)."""
    layer_type: str
    expected_rgb: dict
    tolerance: float = 0.10

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            s = _first_stroke(l)
            if not s:
                failures.append(f"{l['id'][:8]}: no stroke")
                continue
            paint = s.get("paint", {})
            if paint.get("kind") != "solid":
                failures.append(f"{l['id'][:8]}: stroke not solid")
                continue
            dist = channel_distance(paint.get("color", {}), self.expected_rgb)
            if dist > self.tolerance:
                failures.append(f"{l['id'][:8]}: stroke color off (dist {dist:.2f})")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} stroke colors match" if passed
                    else "; ".join(failures),
        )


@dataclass
class AllStrokeWeightAtMost:
    """Every layer of layer_type has stroke weight ≤ max_weight.
    Catches absurdly thick strokes that overwhelm the design."""
    layer_type: str
    max_weight: float

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            for s in l.get("strokes", []):
                w = s.get("weight", 0)
                if w > self.max_weight:
                    failures.append(f"{l['id'][:8]}: stroke weight {w} > {self.max_weight}")
                    break
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} stroke weights ≤ {self.max_weight}" if passed
                    else "; ".join(failures),
        )


@dataclass
class AllStrokeWeightWithinTolerance:
    """Every layer of layer_type has its first stroke weight ≈ target ± tolerance.
    Stricter than StrokeWeightEquals (≥1 layer)."""
    layer_type: str
    target_weight: float
    tolerance: float = 0.5

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            s = _first_stroke(l)
            if not s:
                failures.append(f"{l['id'][:8]}: no stroke")
                continue
            w = s.get("weight", 0)
            if abs(w - self.target_weight) > self.tolerance:
                failures.append(f"{l['id'][:8]}: weight {w} ≠ {self.target_weight}")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} stroke weights ≈ {self.target_weight}" if passed
                    else "; ".join(failures),
        )


@dataclass
class StrokeRendersVisible:
    """At least one layer of layer_type has a stroke that actually renders:
       - stroke.visible != False
       - stroke.paint.color.a >= min_alpha (default 0.5)
    Catches stroke deceptions where a stroke exists structurally but is
    transparent or hidden (visible=False / alpha=0)."""
    layer_type: str
    min_alpha: float = 0.5

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            s = _first_stroke(l)
            if not s:
                continue
            if s.get("visible", True) is False:
                continue
            paint = s.get("paint", {})
            color = paint.get("color", {})
            alpha = color.get("a", 1.0)
            if alpha >= self.min_alpha:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} stroke renders (alpha {alpha:.2f}, visible)")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} with a renderable stroke (visible + alpha ≥ {self.min_alpha})",
        )
