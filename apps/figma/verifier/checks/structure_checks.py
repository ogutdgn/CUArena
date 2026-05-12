from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import find_layers_by_type, find_all_layers


@dataclass
class LayerInsideFrame:
    """At least one layer of layer_type is a direct child of a frame."""
    layer_type: str

    def run(self, log: dict) -> CheckResult:
        frames = find_layers_by_type(log["outcome"]["document"], "frame")
        for frame in frames:
            if any(c.get("type") == self.layer_type for c in frame.get("children", [])):
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} found inside a frame")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No {self.layer_type} found as direct child of a frame")


@dataclass
class LayerGroupAllInSameFrame:
    """All layers of layer_type (across the doc) must be direct children of the SAME frame.
    Catches:
      - layers split across multiple frames
      - some layers in a frame, others on the page (no frame)
      - layers buried in groups/components inside a frame (not direct children)
    """
    layer_type: str
    minimum: int = 1

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        all_layers = find_layers_by_type(doc, self.layer_type)
        if len(all_layers) < self.minimum:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Found {len(all_layers)} {self.layer_type} (need ≥{self.minimum})")
        frames = find_layers_by_type(doc, "frame")
        for frame in frames:
            direct_children = [c for c in frame.get("children", []) if c.get("type") == self.layer_type]
            if len(direct_children) == len(all_layers) and len(direct_children) >= self.minimum:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"All {len(all_layers)} {self.layer_type} are direct children of one frame")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"All {len(all_layers)} {self.layer_type} not direct children of a single frame")


@dataclass
class ChildCount:
    """At least one parent_type layer has exactly `equals` children."""
    parent_type: str
    equals: int

    def run(self, log: dict) -> CheckResult:
        parents = find_layers_by_type(log["outcome"]["document"], self.parent_type)
        for p in parents:
            count = len(p.get("children", []))
            if count == self.equals:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.parent_type} has {self.equals} children")
        got = [len(p.get("children", [])) for p in parents]
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"No {self.parent_type} with {self.equals} children (found: {got})",
        )


@dataclass
class ChildCountAtLeast:
    """At least one parent_type layer has at least `minimum` children."""
    parent_type: str
    minimum: int

    def run(self, log: dict) -> CheckResult:
        parents = find_layers_by_type(log["outcome"]["document"], self.parent_type)
        for p in parents:
            if len(p.get("children", [])) >= self.minimum:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.parent_type} has ≥{self.minimum} children")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No {self.parent_type} with ≥{self.minimum} children")


@dataclass
class IsGrouped:
    """At least one layer of layer_type is a direct child of a group."""
    layer_type: str

    def run(self, log: dict) -> CheckResult:
        groups = find_layers_by_type(log["outcome"]["document"], "group")
        for g in groups:
            if any(c.get("type") == self.layer_type for c in g.get("children", [])):
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"{self.layer_type} found inside a group")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No {self.layer_type} found inside a group")


@dataclass
class ZOrderIsFirst:
    """At least one layer of layer_type is at the front (last in its parent's children)."""
    layer_type: str

    def _check_nodes(self, nodes: list[dict]) -> bool:
        if nodes and nodes[-1].get("type") == self.layer_type:
            return True
        for node in nodes:
            if "children" in node and self._check_nodes(node["children"]):
                return True
        return False

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        found = False
        for page in doc.get("pages", []):
            if self._check_nodes(page.get("children", [])):
                found = True
                break
        return CheckResult(
            passed=found, score=1.0 if found else 0.0, max_score=1.0,
            message=f"{self.layer_type} is at front (z-order first)" if found
                    else f"No {self.layer_type} found at front",
        )


@dataclass
class ZOrderIsLast:
    """At least one layer of layer_type is at the back (first in its parent's children)."""
    layer_type: str

    def _check_nodes(self, nodes: list[dict]) -> bool:
        if nodes and nodes[0].get("type") == self.layer_type:
            return True
        for node in nodes:
            if "children" in node and self._check_nodes(node["children"]):
                return True
        return False

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        found = False
        for page in doc.get("pages", []):
            if self._check_nodes(page.get("children", [])):
                found = True
                break
        return CheckResult(
            passed=found, score=1.0 if found else 0.0, max_score=1.0,
            message=f"{self.layer_type} is at back (z-order last)" if found
                    else f"No {self.layer_type} found at back",
        )


@dataclass
class LayerTotalCount:
    """Total layer count across all pages equals `equals`."""
    equals: int

    def run(self, log: dict) -> CheckResult:
        count = len(find_all_layers(log["outcome"]["document"]))
        passed = count == self.equals
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"Total layers: expected {self.equals}, got {count}",
        )


@dataclass
class NoUnexpectedLayerTypes:
    """Every layer must be in the allowed set (optionally allowing frame/group).

    Useful for end-state-only anti-trash checks: exact ShapeCount checks enforce
    expected counts, while this check rejects unrelated extra objects.
    """
    allowed_types: list[str]
    allow_frame: bool = True
    allow_group: bool = False

    def run(self, log: dict) -> CheckResult:
        allowed = set(self.allowed_types)
        if self.allow_frame:
            allowed.add("frame")
        if self.allow_group:
            allowed.add("group")

        layers = find_all_layers(log["outcome"]["document"])
        unexpected = [l.get("type", "?") for l in layers if l.get("type") not in allowed]
        if not unexpected:
            return CheckResult(
                passed=True, score=1.0, max_score=1.0,
                message=f"No unexpected layer types (allowed: {sorted(allowed)})",
            )

        kinds = sorted(set(unexpected))
        return CheckResult(
            passed=False, score=0.0, max_score=1.0,
            message=f"Unexpected layer types: {kinds} (allowed: {sorted(allowed)})",
        )


def _find_layer_by_name(document: dict, name: str) -> dict | None:
    for layer in find_all_layers(document):
        if layer.get("name") == name:
            return layer
    return None


@dataclass
class NoLayerCreated:
    """Pass iff the agent emitted zero create_* events."""

    def run(self, log: dict) -> CheckResult:
        creates = [e for e in log.get("semantic", [])
                   if e.get("name", "").startswith("create_")]
        passed = len(creates) == 0
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"create events: {len(creates)} (expected 0)",
        )


@dataclass
class NoLayerDeleted:
    """Pass iff the agent emitted zero delete events."""

    def run(self, log: dict) -> CheckResult:
        deletes = [e for e in log.get("semantic", [])
                   if e.get("name") == "delete"]
        passed = len(deletes) == 0
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"delete_layer events: {len(deletes)} (expected 0)",
        )


@dataclass
class NoLayerMoved:
    """Pass iff no move_layer events were emitted beyond tolerance pixels."""
    tolerance: float = 2.0

    def run(self, log: dict) -> CheckResult:
        moves = [e for e in log.get("semantic", [])
                 if e.get("name") == "move_layer"]
        if not moves:
            return CheckResult(passed=True, score=1.0, max_score=1.0,
                               message="No move_layer events")
        for e in moves:
            dx = abs(e.get("dx", 0))
            dy = abs(e.get("dy", 0))
            if dx > self.tolerance or dy > self.tolerance:
                return CheckResult(
                    passed=False, score=0.0, max_score=1.0,
                    message=f"Layer moved by ({dx:.1f}, {dy:.1f}) > tolerance {self.tolerance}",
                )
        return CheckResult(passed=True, score=1.0, max_score=1.0,
                           message=f"All moves within tolerance ({self.tolerance}px)")


@dataclass
class NamedLayerDeleted:
    """Pass iff the named layer no longer exists in the end-state document."""
    name: str

    def run(self, log: dict) -> CheckResult:
        layer = _find_layer_by_name(log["outcome"]["document"], self.name)
        passed = layer is None
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"Layer '{self.name}' {'deleted' if passed else 'still exists'}",
        )


@dataclass
class NamedLayerExists:
    """Pass iff the named layer still exists in the end-state document."""
    name: str

    def run(self, log: dict) -> CheckResult:
        layer = _find_layer_by_name(log["outcome"]["document"], self.name)
        passed = layer is not None
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"Layer '{self.name}' {'exists' if passed else 'not found'}",
        )
