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
class CornerRadiusAtLeast:
    """At least one layer of layer_type has cornerRadius ≥ min_value."""
    layer_type: str
    min_value: float

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        for l in layers:
            cr = l.get("cornerRadius", 0)
            if isinstance(cr, (int, float)) and cr >= self.min_value:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} cornerRadius {cr} ≥ {self.min_value}")
            if isinstance(cr, list) and all(v >= self.min_value for v in cr):
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} cornerRadius {cr} ≥ {self.min_value}")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.layer_type} with cornerRadius ≥ {self.min_value}",
        )


@dataclass
class CornerRadiusFractionAtMost:
    """Every layer of layer_type has cornerRadius / min(w, h) ≤ max_frac.
    Catches rectangles with extreme corner-rounding that visually become circles."""
    layer_type: str
    max_frac: float = 0.4

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            cr = l.get("cornerRadius", 0)
            short = min(l["w"], l["h"])
            if short <= 0:
                continue
            cr_max = max(cr) if isinstance(cr, list) else cr
            frac = cr_max / short
            if frac > self.max_frac:
                failures.append(f"{l['id'][:8]}: cornerRadius frac {frac:.2f} > {self.max_frac}")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} cornerRadius ≤ {self.max_frac} of size" if passed
                    else "; ".join(failures),
        )


@dataclass
class LayerVisible:
    """Every layer of layer_type is meaningfully visible:
       - layer.opacity ≥ min_opacity (default 0.5)
       - layer.visible != False
       - first fill (if present): visible != False, color.a ≥ min_alpha, opacity ≥ min_opacity
    Catches transparency tricks where a shape exists structurally but doesn't render."""
    layer_type: str
    min_opacity: float = 0.5
    min_alpha: float = 0.5

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            if l.get("visible", True) is False:
                failures.append(f"{l['id'][:8]}: layer visible=False")
                continue
            if l.get("opacity", 1.0) < self.min_opacity:
                failures.append(f"{l['id'][:8]}: layer opacity {l.get('opacity'):.2f} < {self.min_opacity}")
                continue
            fills = l.get("fills", [])
            if fills:
                f = fills[0]
                if f.get("visible", True) is False:
                    failures.append(f"{l['id'][:8]}: fill visible=False")
                    continue
                a = f.get("color", {}).get("a", 1.0)
                if a < self.min_alpha:
                    failures.append(f"{l['id'][:8]}: fill alpha {a:.2f} < {self.min_alpha}")
                    continue
                if f.get("opacity", 1.0) < self.min_opacity:
                    failures.append(f"{l['id'][:8]}: fill opacity {f.get('opacity'):.2f} < {self.min_opacity}")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} are visible" if passed
                    else "; ".join(failures),
        )


@dataclass
class LayerRendersStrokeOrFill:
    """Every layer of layer_type renders SOMETHING (visible fill OR visible stroke).
    Catches the case where a line/shape has empty fills AND empty strokes —
    structurally present but visually invisible.

    For each layer, requires at least one of:
      - visible solid/image fill (visible=True, opacity ≥ min_opacity, color.a ≥ min_alpha)
      - visible stroke (paint visible, weight > 0)

    Also rejects layer.opacity < min_opacity and layer.visible=False.
    """
    layer_type: str
    min_opacity: float = 0.5
    min_alpha: float = 0.5

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = []
        for l in layers:
            if l.get("visible", True) is False:
                failures.append(f"{l['id'][:8]}: layer hidden")
                continue
            if l.get("opacity", 1.0) < self.min_opacity:
                failures.append(f"{l['id'][:8]}: layer opacity={l.get('opacity'):.2f}")
                continue
            # Check for any visible fill
            has_visible_fill = False
            for f in l.get("fills", []):
                if f.get("visible", True) is False: continue
                if f.get("opacity", 1.0) < self.min_opacity: continue
                if f.get("kind") == "solid":
                    if f.get("color", {}).get("a", 1.0) >= self.min_alpha:
                        has_visible_fill = True; break
                else:
                    has_visible_fill = True; break
            # Check for any visible stroke
            has_visible_stroke = False
            for s in l.get("strokes", []):
                if s.get("visible", True) is False: continue
                if (s.get("weight", 0) or 0) <= 0: continue
                paint = s.get("paint", {})
                if paint.get("kind") == "solid":
                    if paint.get("color", {}).get("a", 1.0) >= self.min_alpha:
                        has_visible_stroke = True; break
                else:
                    has_visible_stroke = True; break
            if not has_visible_fill and not has_visible_stroke:
                failures.append(f"{l['id'][:8]}: no visible fill or stroke")
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} render visibly" if passed
                    else "; ".join(failures),
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


@dataclass
class NoLayerFlipped:
    """No layer of layer_type is flipped horizontally or vertically (scaleX != -1 AND scaleY != -1)."""
    layer_type: str

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        failures = [
            f"{l['id'][:8]}: scaleX={l.get('scaleX')} scaleY={l.get('scaleY')}"
            for l in layers if l.get("scaleX") == -1 or l.get("scaleY") == -1
        ]
        passed = not failures
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"No {self.layer_type} flipped" if passed else "; ".join(failures),
        )


@dataclass
class ConstraintHorizontalEquals:
    """All layers of layer_type have constraints.horizontal == value.

    Values: 'left' | 'right' | 'center' | 'stretch' | 'scale'
    """
    layer_type: str
    value: str

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        wrong = [l for l in layers
                 if (l.get("constraints") or {}).get("horizontal") != self.value]
        passed = not wrong
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} have horizontal constraint '{self.value}'" if passed
                    else f"{len(wrong)}/{len(layers)} {self.layer_type} have wrong horizontal constraint",
        )


@dataclass
class ConstraintVerticalEquals:
    """All layers of layer_type have constraints.vertical == value.

    Values: 'top' | 'bottom' | 'center' | 'stretch' | 'scale' | 'top_bottom'
    """
    layer_type: str
    value: str

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], self.layer_type)
        if not layers:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"No {self.layer_type} layers found")
        wrong = [l for l in layers
                 if (l.get("constraints") or {}).get("vertical") != self.value]
        passed = not wrong
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"All {self.layer_type} have vertical constraint '{self.value}'" if passed
                    else f"{len(wrong)}/{len(layers)} {self.layer_type} have wrong vertical constraint",
        )
