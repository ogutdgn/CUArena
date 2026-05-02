from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import find_layers_by_type


@dataclass
class TextContent:
    """Any text layer has exactly this content."""
    expected: str

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], "text")
        for l in layers:
            if l.get("content") == self.expected:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"Text content matches: '{self.expected}'")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No text layer with content '{self.expected}'")


@dataclass
class TextContains:
    """Any text layer's content contains this substring."""
    substring: str

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], "text")
        for l in layers:
            if self.substring in l.get("content", ""):
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"Text contains '{self.substring}'")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No text layer containing '{self.substring}'")


@dataclass
class FontSizeEquals:
    """Any text layer has fontSize ≈ expected."""
    size: float
    tolerance: float = 1.0

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], "text")
        for l in layers:
            if abs(l.get("fontSize", 0) - self.size) <= self.tolerance:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"Text fontSize {l['fontSize']} ≈ {self.size}")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No text layer with fontSize {self.size}±{self.tolerance}")


@dataclass
class FontWeightEquals:
    """Any text layer has the given fontWeight."""
    weight: int   # e.g. 400, 700

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], "text")
        for l in layers:
            if l.get("fontWeight") == self.weight:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"Text fontWeight is {self.weight}")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No text layer with fontWeight {self.weight}")


@dataclass
class TextAlignEquals:
    """Any text layer has the given horizontal alignment."""
    align: str   # "left" | "center" | "right" | "justify"

    def run(self, log: dict) -> CheckResult:
        layers = find_layers_by_type(log["outcome"]["document"], "text")
        for l in layers:
            if l.get("hAlign") == self.align:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"Text hAlign is '{self.align}'")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No text layer with hAlign '{self.align}'")
