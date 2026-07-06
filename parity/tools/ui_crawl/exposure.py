"""UIA exposure map: which control types expose which UIA patterns (per DESIGN section 6.3).

Reads one or more enum JSON files (uia.enumerate_tab output) and aggregates a Counter over
(control_type, patterns) plus the section-6.3 flags. The pilot uses this to decide (honestly)
that Office ribbon pattern-availability is too quirky to classify with -> press-and-observe.
"""
import json, collections, pathlib


def _iter_controls(data):
    for g in data.get("groups", []):
        for c in g.get("controls", []):
            yield c


def dump(paths, out):
    by_type = collections.Counter()
    type_counts = collections.Counter()
    flags = {"has_scroll": False, "has_selection_item": False, "has_toggle": False,
             "has_value": False, "splitbuttons": 0, "combos": 0, "galleries": 0}
    for p in paths:
        data = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        for c in _iter_controls(data):
            ct = c.get("control_type", "")
            pats = tuple(sorted(c.get("patterns", [])))
            by_type[(ct, pats)] += 1
            type_counts[ct] += 1
            if "scroll" in pats:
                flags["has_scroll"] = True
            if "selection_item" in pats:
                flags["has_selection_item"] = True
            if "toggle" in pats:
                flags["has_toggle"] = True
            if "value" in pats:
                flags["has_value"] = True
            if ct == "SplitButton":
                flags["splitbuttons"] += 1
            if ct == "ComboBox":
                flags["combos"] += 1
            if c.get("is_gallery"):
                flags["galleries"] += 1
    result = {
        "schema_version": 1,
        "type_counts": dict(type_counts),
        "pattern_by_type": [{"control_type": k[0], "patterns": list(k[1]), "count": v}
                            for k, v in sorted(by_type.items())],
        "flags": flags,
    }
    pathlib.Path(out).write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    return result
