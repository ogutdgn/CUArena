import math as _math


def polygon_vertices(layer: dict) -> list[tuple[float, float]]:
    """
    Compute actual vertex positions for a polygon layer in parent space.

    Replicates NodeRenderer.tsx PolygonEl vertex formula:
        angle = -π/2 + i * 2π/sides
        x = cx + rx * cos(angle)
        y = cy + ry * sin(angle)

    Then applies scaleX/scaleY mirror flags and clockwise rotation around the
    layer center, then converts to parent space via layer["x"], layer["y"].
    """
    sides = max(3, layer.get("sides", 3))
    w, h = layer["w"], layer["h"]
    cx, cy = w / 2, h / 2
    rotation_rad = _math.radians(layer.get("rotation", 0))

    vertices: list[tuple[float, float]] = []
    for i in range(sides):
        angle = -_math.pi / 2 + (i * 2 * _math.pi) / sides
        lx = cx + (w / 2) * _math.cos(angle)
        ly = cy + (h / 2) * _math.sin(angle)

        # Mirror flags (-1 flips around center axis)
        if layer.get("scaleX", 1) < 0:
            lx = w - lx
        if layer.get("scaleY", 1) < 0:
            ly = h - ly

        # Clockwise rotation in screen-space (Y-down) around center
        if rotation_rad:
            dx, dy = lx - cx, ly - cy
            lx = cx + dx * _math.cos(rotation_rad) - dy * _math.sin(rotation_rad)
            ly = cy + dx * _math.sin(rotation_rad) + dy * _math.cos(rotation_rad)

        vertices.append((layer["x"] + lx, layer["y"] + ly))

    return vertices


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


def transformed_layer_point(layer: dict, point: dict) -> tuple[float, float]:
    """Apply a layer's own scale/rotation/translation to a local point.

    This mirrors the mock renderer's layer transform order for endpoint-based
    shapes: mirror around center, rotate around center, then translate by x/y.
    The result is in the layer's parent coordinate space.
    """
    w = layer.get("w", 0)
    h = layer.get("h", 0)
    cx = w / 2
    cy = h / 2
    x = point.get("x", 0)
    y = point.get("y", 0)

    x = cx + (x - cx) * layer.get("scaleX", 1)
    y = cy + (y - cy) * layer.get("scaleY", 1)

    rotation = layer.get("rotation", 0)
    if rotation:
        rad = _math.radians(rotation)
        dx = x - cx
        dy = y - cy
        x = cx + dx * _math.cos(rad) - dy * _math.sin(rad)
        y = cy + dx * _math.sin(rad) + dy * _math.cos(rad)

    return layer.get("x", 0) + x, layer.get("y", 0) + y


def line_endpoints(layer: dict) -> tuple[tuple[float, float], tuple[float, float]]:
    return transformed_layer_point(layer, layer.get("p1", {})), transformed_layer_point(layer, layer.get("p2", {}))


def line_length(layer: dict) -> float:
    p1, p2 = line_endpoints(layer)
    return _math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def line_angle_degrees(layer: dict) -> float:
    p1, p2 = line_endpoints(layer)
    return _math.degrees(_math.atan2(p2[1] - p1[1], p2[0] - p1[0])) % 360


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

    n=2 special case: with only two layers, the original mirror check is vacuous
    (the collective center IS their midpoint, so any two layers always pass).
    For n=2 we instead require they are actual twins: same Y center AND same
    dimensions, otherwise the symmetry claim is meaningless.
    """
    if len(layers) < 2:
        return False, 0.0

    if len(layers) == 2:
        a, b = layers
        a_cy = a["y"] + a["h"] / 2
        b_cy = b["y"] + b["h"] / 2
        y_diff = abs(a_cy - b_cy)
        size_diff = max(abs(a["w"] - b["w"]), abs(a["h"] - b["h"]))
        worst = max(y_diff, size_diff)
        return worst <= tolerance, worst

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
