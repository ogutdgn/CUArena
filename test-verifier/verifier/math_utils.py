def find_layers_by_type(document: dict, layer_type: str) -> list[dict]:
    """Recursively collect all layers matching layer_type across all pages."""
    results: list[dict] = []

    def walk(nodes: list[dict]) -> None:
        for node in nodes:
            if node.get("type") == layer_type:
                results.append(node)
            if "children" in node:
                walk(node["children"])

    for page in document.get("pages", []):
        walk(page.get("children", []))

    return results


def find_all_layers(document: dict) -> list[dict]:
    """Recursively collect every layer across all pages."""
    results: list[dict] = []

    def walk(nodes: list[dict]) -> None:
        for node in nodes:
            results.append(node)
            if "children" in node:
                walk(node["children"])

    for page in document.get("pages", []):
        walk(page.get("children", []))

    return results


def layer_center(layer: dict) -> tuple[float, float]:
    return layer["x"] + layer["w"] / 2, layer["y"] + layer["h"] / 2


def layers_aligned(layers: list[dict], axis: str, tolerance: float) -> tuple[bool, float]:
    """
    Check whether layers share approximately the same coordinate on axis.
    axis: "x" | "y" | "center_x" | "center_y"
    Returns (passed, max_diff_px).
    """
    if len(layers) < 2:
        return False, 0.0

    if axis == "x":
        coords = [l["x"] for l in layers]
    elif axis == "y":
        coords = [l["y"] for l in layers]
    elif axis == "center_x":
        coords = [l["x"] + l["w"] / 2 for l in layers]
    elif axis == "center_y":
        coords = [l["y"] + l["h"] / 2 for l in layers]
    else:
        raise ValueError(f"Unknown axis '{axis}'. Use: x, y, center_x, center_y")

    max_diff = max(coords) - min(coords)
    return max_diff <= tolerance, max_diff


def layers_symmetric_x(layers: list[dict], tolerance: float) -> tuple[bool, float]:
    """
    Check that layers are symmetric around their collective horizontal center.
    Returns (passed, max_deviation_px).
    """
    if len(layers) < 2:
        return False, 0.0

    centers = sorted([l["x"] + l["w"] / 2 for l in layers])
    collective_cx = sum(centers) / len(centers)
    max_dev = 0.0

    for cx in centers:
        mirror = 2 * collective_cx - cx
        closest = min(centers, key=lambda x: abs(x - mirror))
        max_dev = max(max_dev, abs(closest - mirror))

    return max_dev <= tolerance, max_dev


def channel_distance(a: dict, b: dict) -> float:
    """Max channel difference between two RGB dicts (0..1 scale)."""
    return max(
        abs(a.get("r", 0) - b.get("r", 0)),
        abs(a.get("g", 0) - b.get("g", 0)),
        abs(a.get("b", 0) - b.get("b", 0)),
    )
