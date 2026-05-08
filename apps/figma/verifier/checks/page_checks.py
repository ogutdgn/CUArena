from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import find_layers_by_type


@dataclass
class DocumentNameEquals:
    """Document/file name matches the expected value."""
    expected: str

    def run(self, log: dict) -> CheckResult:
        actual = log["outcome"]["document"].get("name")
        passed = actual == self.expected
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"document name: expected '{self.expected}', got '{actual}'",
        )


@dataclass
class PageCount:
    """Document has exactly `equals` pages."""
    equals: int

    def run(self, log: dict) -> CheckResult:
        count = len(log["outcome"]["document"].get("pages", []))
        passed = count == self.equals
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"page count: expected {self.equals}, got {count}",
        )


@dataclass
class PageCountAtLeast:
    """Document has at least `minimum` pages."""
    minimum: int

    def run(self, log: dict) -> CheckResult:
        count = len(log["outcome"]["document"].get("pages", []))
        passed = count >= self.minimum
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"page count: expected ≥{self.minimum}, got {count}",
        )


@dataclass
class LayerOnPage:
    """At least one layer of layer_type exists on the page at page_index (0-based)."""
    layer_type: str
    page_index: int

    def run(self, log: dict) -> CheckResult:
        pages = log["outcome"]["document"].get("pages", [])
        if self.page_index >= len(pages):
            return CheckResult(
                passed=False, score=0.0, max_score=1.0,
                message=f"Page index {self.page_index} does not exist (total pages: {len(pages)})",
            )
        page = pages[self.page_index]
        found = any(
            node.get("type") == self.layer_type
            for node in _walk(page.get("children", []))
        )
        return CheckResult(
            passed=found, score=1.0 if found else 0.0, max_score=1.0,
            message=f"{self.layer_type} {'found' if found else 'not found'} on page {self.page_index} ('{page.get('name', '')}')",
        )


@dataclass
class PageBackgroundColorEquals:
    """Page at page_index has backgroundColor matching expected_rgb (within tolerance)."""
    expected_rgb: dict
    page_index: int = 0
    tolerance: float = 0.05

    def run(self, log: dict) -> CheckResult:
        pages = log["outcome"]["document"].get("pages", [])
        if self.page_index >= len(pages):
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Page index {self.page_index} does not exist")
        bg = pages[self.page_index].get("backgroundColor", {})
        if not bg:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Page {self.page_index} has no backgroundColor")
        diff = max(abs(bg.get(k, 0) - self.expected_rgb.get(k, 0)) for k in ("r", "g", "b"))
        passed = diff <= self.tolerance
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"page {self.page_index} backgroundColor diff {diff:.3f} (tol {self.tolerance})",
        )


@dataclass
class PageBackgroundOpacityEquals:
    """Page at page_index has backgroundColor alpha matching opacity."""
    opacity: float
    page_index: int = 0
    tolerance: float = 0.02

    def run(self, log: dict) -> CheckResult:
        pages = log["outcome"]["document"].get("pages", [])
        if self.page_index >= len(pages):
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Page index {self.page_index} does not exist")
        bg = pages[self.page_index].get("backgroundColor", {})
        actual = bg.get("a")
        passed = actual is not None and abs(actual - self.opacity) <= self.tolerance
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"page {self.page_index} background opacity: expected {self.opacity}+-{self.tolerance}, got {actual}",
        )


@dataclass
class PageBackgroundHiddenIs:
    """Page background visibility toggle matches hidden."""
    hidden: bool
    page_index: int = 0

    def run(self, log: dict) -> CheckResult:
        pages = log["outcome"]["document"].get("pages", [])
        if self.page_index >= len(pages):
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Page index {self.page_index} does not exist")
        actual = pages[self.page_index].get("backgroundHidden", False)
        passed = actual == self.hidden
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"page {self.page_index} backgroundHidden: expected {self.hidden}, got {actual}",
        )


@dataclass
class ActivePageIs:
    """The active page at session end matches `page_name`."""
    page_name: str

    def run(self, log: dict) -> CheckResult:
        active_id = log["outcome"].get("activePageId")
        pages = log["outcome"]["document"].get("pages", [])
        active = next((p for p in pages if p["id"] == active_id), None)
        actual_name = active["name"] if active else None
        passed = actual_name == self.page_name
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"active page: expected '{self.page_name}', got '{actual_name}'",
        )


@dataclass
class PrototypeConnectionExists:
    """At least one prototype connection matches the supplied fields."""
    source_layer_id: str | None = None
    destination_frame_id: str | None = None
    trigger: str | None = None
    action: str | None = None
    page_index: int = 0

    def run(self, log: dict) -> CheckResult:
        pages = log["outcome"]["document"].get("pages", [])
        if self.page_index >= len(pages):
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Page index {self.page_index} does not exist")
        connections = pages[self.page_index].get("prototypeConnections", []) or []
        for conn in connections:
            if self.source_layer_id is not None and conn.get("sourceLayerId") != self.source_layer_id:
                continue
            if self.destination_frame_id is not None and conn.get("destinationFrameId") != self.destination_frame_id:
                continue
            if self.trigger is not None and conn.get("trigger") != self.trigger:
                continue
            if self.action is not None and conn.get("action") != self.action:
                continue
            return CheckResult(passed=True, score=1.0, max_score=1.0,
                               message="matching prototype connection found")
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No prototype connection matched on page {self.page_index}",
        )


def _walk(nodes: list[dict]):
    for node in nodes:
        yield node
        if "children" in node:
            yield from _walk(node["children"])
