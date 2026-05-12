from dataclasses import dataclass
from verifier.types import CheckResult
from verifier.math_utils import find_all_layers


def _find_layer_by_name(document: dict, name: str) -> dict | None:
    for layer in find_all_layers(document):
        if layer.get("name") == name:
            return layer
    return None


@dataclass
class LayerSelected:
    """End-state: the named layer is in the active selection set."""
    layer_name: str

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        layer = _find_layer_by_name(doc, self.layer_name)
        if not layer:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Layer '{self.layer_name}' not found in document")
        selected_ids = log["outcome"].get("selectedLayerIds", [])
        passed = layer["id"] in selected_ids
        return CheckResult(
            passed=passed, score=1.0 if passed else 0.0, max_score=1.0,
            message=f"Layer '{self.layer_name}' {'is' if passed else 'is not'} selected",
        )


@dataclass
class ClickedLayer:
    """Event-log: at least one click event targeted the named layer."""
    layer_name: str

    def run(self, log: dict) -> CheckResult:
        doc = log["outcome"]["document"]
        layer = _find_layer_by_name(doc, self.layer_name)
        if not layer:
            return CheckResult(passed=False, score=0.0, max_score=1.0,
                               message=f"Layer '{self.layer_name}' not found in document")
        layer_id = layer["id"]
        for event in log.get("semantic", []):
            if event.get("name") == "click" and event.get("targetLayerId") == layer_id:
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"Click on '{self.layer_name}' found in event log")
        for event in log.get("semantic", []):
            if event.get("name") == "select_layer" and layer_id in event.get("layerIds", []):
                return CheckResult(passed=True, score=1.0, max_score=1.0,
                                   message=f"Selection of '{self.layer_name}' found in event log")
        return CheckResult(passed=False, score=0.0, max_score=1.0,
                           message=f"No click/selection event for '{self.layer_name}' in event log")
