from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import find_all_layers


def _find_layer_by_name(document: dict, name: str) -> dict | None:
    for layer in find_all_layers(document):
        if layer.get("name") == name:
            return layer
    return None


def _collect_descendant_ids(document: dict, layer_id: str) -> set[str]:
    """Return {layer_id} plus the IDs of all its descendants."""
    ids: set[str] = set()

    def walk(nodes: list[dict], collecting: bool) -> None:
        for node in nodes:
            is_target = node.get("id") == layer_id
            if collecting or is_target:
                ids.add(node["id"])
            children = node.get("children", [])
            if children:
                walk(children, collecting or is_target)

    for page in document.get("pages", []):
        walk(page.get("children", []), False)
    return ids


@dataclass
class LayerSelected:
    """End-state: the named layer (or one of its children) is in the active selection."""
    layer_name: str

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        layer = _find_layer_by_name(doc, self.layer_name)
        if not layer:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Layer '{self.layer_name}' not found in document")
        family_ids = _collect_descendant_ids(doc, layer["id"])
        selected_ids = set(log["outcome"].get("selectedLayerIds", []))
        overlap = family_ids & selected_ids
        passed = bool(overlap)
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"Layer '{self.layer_name}' {'is' if passed else 'is not'} selected",
        )


@dataclass
class ClickedLayer:
    """Event-log: at least one click_select event targeted the named layer or a child of it."""
    layer_name: str

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        layer = _find_layer_by_name(doc, self.layer_name)
        if not layer:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Layer '{self.layer_name}' not found in document")
        family_ids = _collect_descendant_ids(doc, layer["id"])
        for event in log.get("semantic", []):
            if event.get("name") == "click_select" and event.get("targetLayerId") in family_ids:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"Click on '{self.layer_name}' found in event log")
        for event in log.get("semantic", []):
            if event.get("name") == "selection_change":
                after_ids = set(event.get("after", []))
                if family_ids & after_ids:
                    return CheckResult(passed=True, score=1.0, max_score=1.0,
                                       message=f"Selection of '{self.layer_name}' found in event log")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No click/selection event for '{self.layer_name}' in event log")
