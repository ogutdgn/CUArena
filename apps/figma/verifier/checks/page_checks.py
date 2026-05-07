from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import find_layers_by_type


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


def _walk(nodes: list[dict]):
    for node in nodes:
        yield node
        if "children" in node:
            yield from _walk(node["children"])
