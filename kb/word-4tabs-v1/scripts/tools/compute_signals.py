"""Step 4 signals (v2) — the THREE value signals of 04-priority.md. Value = usage, nothing
else; connections are NOT consulted (the v1 mistake LESSONS.md records).

signal 2: UI PROMINENCE — pure computation from the measured skeleton geometry. The
designer's own usage bet, read from: which surface hosts the control (Home face > Insert
face > contextual tab face), how BIG it is drawn (area of its bounds), and how early it
sits (left-to-right position). Writes priority/signals/prominence.json with the formula.

signal 3: WEB USAGE — loaded from priority/signals/usage.json (written by the research
workflow: claim + source per entry, mapped to node ids). This script only validates it.

signal 1: PRODUCT-PURPOSE — authored verdicts in priority/signals/product_purpose.json
(mandated format per verdict). This script validates coverage: every scored sub-feature
must have a verdict; missing ones are listed loudly.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB
SIG = KB / "priority" / "signals"

# Always-present primary tab faces, weighted by ribbon tab order (the designer's prominence
# bet: leftmost = most-reached). Home > Insert > Design > Layout. Design/Layout are NOT
# contextual — they are always visible, so they outrank the contextual-tab weight.
SURFACE_WEIGHT = {"ui:ribbon-home": 1.00, "ui:ribbon-insert": 0.90,
                  "ui:ribbon-design": 0.82, "ui:ribbon-layout": 0.80}
CTX_SURFACE_WEIGHT = 0.75      # contextual tab face: prominent, but only exists in context
RIBBON_W = 1920.0              # measured frame width (maximized, primary monitor)


def load_nodes():
    ffiles = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((KB / "features").glob("*.json"))]
    feats = [ff["feature"] for ff in ffiles]
    subs = [s for ff in ffiles for s in ff["subfeatures"]]
    return feats, subs


def main():
    SIG.mkdir(parents=True, exist_ok=True)
    feats, subs = load_nodes()
    ui = json.loads((KB / "ui.json").read_text(encoding="utf-8"))["containers"]

    el_geo = {}      # el id -> (surface id, area, x_center)
    for cid, c in ui.items():
        for e in c.get("children", []):
            if e.get("id") and e.get("bounds"):
                l, t, r, b = e["bounds"]
                el_geo.setdefault(e["id"], []).append(
                    (cid, max(0, (r - l)) * max(0, (b - t)), (l + r) / 2))

    # area normalization: big ribbon buttons ~ 60x70=4200 px²; small ~ 20x20=400
    def area_score(a):
        return min(1.0, a / 4200.0) ** 0.5          # sqrt: diminishing returns

    def pos_score(x):
        return 1.0 - max(0.0, min(1.0, x / RIBBON_W)) * 0.5   # left=1.0 .. right=0.5

    prominence = {}
    for s in subs:
        best, evidence = 0.0, None
        for tp in s.get("trigger_paths", []):
            if tp.get("kind") != "mouse" or not tp.get("path"):
                continue
            leaf = tp["path"][-1]
            for (cid, area, xc) in el_geo.get(leaf, []):
                w = SURFACE_WEIGHT.get(cid, CTX_SURFACE_WEIGHT if cid.startswith("ui:ribbon-")
                                       else 0.5)
                score = round(w * (0.55 * area_score(area) + 0.45 * pos_score(xc)), 4)
                if score > best:
                    best = score
                    evidence = {"element": leaf, "surface": cid, "area_px2": area,
                                "x_center": xc, "surface_weight": w}
        prominence[s["id"]] = {"score": best, "evidence": evidence}

    (SIG / "prominence.json").write_text(json.dumps({
        "method": ("prominence = surface_weight * (0.55*sqrt(min(1,area/4200)) + "
                   "0.45*(1 - 0.5*x_center/1920)); surface weights: Home face 1.0, Insert "
                   "face 0.9, contextual tab face 0.75. Max over the node's trigger "
                   "elements. Pure computation from measured bounds — no judgment."),
        "nodes": prominence}, indent=2, ensure_ascii=False), encoding="utf-8")

    # validate coverage. product_purpose MUST cover every scored node (it is authored, not
    # researched). usage MAY be thin — the design lets signals 1+2 carry nodes the web has no
    # data on — so usage gaps are reported as informational coverage, never a failure.
    problems, coverage = [], {}
    scored_ids = [s["id"] for s in subs if not s.get("boundary")]
    for name, hard in (("product_purpose", True), ("usage", False)):
        p = SIG / f"{name}.json"
        if not p.exists():
            problems.append(f"{name}.json missing")
            continue
        nodes = json.loads(p.read_text(encoding="utf-8")).get("nodes", {})
        missing = [i for i in scored_ids if i not in nodes]
        coverage[name] = {"covered": len(scored_ids) - len(missing), "missing": len(missing)}
        if missing and hard:
            problems.append(f"{name}.json missing {len(missing)} nodes: "
                            + ", ".join(missing[:12]) + ("…" if len(missing) > 12 else ""))
    print(json.dumps({"subfeatures": len(subs), "scored": len(scored_ids),
                      "prominence_written": True, "coverage": coverage,
                      "problems": problems}, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
