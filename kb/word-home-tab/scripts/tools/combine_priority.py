"""Step 4 combine: normalize the three signals, weighted-sum, sort, cut into P0-P4.

Arithmetic, not judgment (design §Priority mechanics). Weights and layer boundaries are recorded
in the output so "why is X P0?" is answerable by opening files. Boundary nodes (Home-tab groups
we deliberately never pressed) are floored to P4 — depth is excluded for them by policy, so they
must not claim a depth budget we won't spend.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import common

KB = common.APP_KB
SIG = KB / "priority" / "signals"
PRI = KB / "priority"

WEIGHTS = {"connectivity": 0.30, "usage": 0.40, "audience": 0.30}
USAGE_TIER_SCORE = {"very-high": 1.0, "high": 0.80, "medium": 0.55, "low": 0.30, "rare": 0.15}
USAGE_DEFAULT = 0.25
# score-threshold boundaries (recorded; calibrated against the live distribution)
BOUNDARIES = {"P0": 0.78, "P1": 0.66, "P2": 0.52, "P3": 0.36}   # else P4


def layer_for(score):
    if score >= BOUNDARIES["P0"]:
        return "P0"
    if score >= BOUNDARIES["P1"]:
        return "P1"
    if score >= BOUNDARIES["P2"]:
        return "P2"
    if score >= BOUNDARIES["P3"]:
        return "P3"
    return "P4"


def load_nodes():
    nodes = {}
    for p in sorted(KB.glob("features/*.json")) + sorted(KB.glob("subfeatures/**/*.json")):
        n = json.loads(p.read_text(encoding="utf-8"))
        nodes[n["id"]] = n
    return nodes


def main():
    nodes = load_nodes()
    conn = json.loads((SIG / "connectivity.json").read_text(encoding="utf-8"))["nodes"]
    aud = json.loads((SIG / "audience.json").read_text(encoding="utf-8"))["nodes"]
    usage_doc = json.loads((SIG / "usage.json").read_text(encoding="utf-8"))
    usage = usage_doc.get("node_usage", {})

    ranking = []
    for nid, n in nodes.items():
        c = conn[nid]["score"]
        a = aud[nid]["score"]
        u_entry = usage.get(nid)
        u = USAGE_TIER_SCORE.get(u_entry["tier"], USAGE_DEFAULT) if u_entry else USAGE_DEFAULT
        combined = round(WEIGHTS["connectivity"] * c + WEIGHTS["usage"] * u
                         + WEIGHTS["audience"] * a, 4)
        ranking.append({
            "id": nid, "name": n["name"], "node_type": n.get("node_type", "feature"),
            "boundary": n.get("boundary", False),
            "signals": {"connectivity": c, "usage": u, "audience": a,
                        "usage_tier": (u_entry or {}).get("tier", "default"),
                        "usage_evidence": (u_entry or {}).get("evidence")},
            "combined": combined,
        })
    ranking.sort(key=lambda r: -r["combined"])

    layers = {}
    for r in ranking:
        lay = "P4" if r["boundary"] else layer_for(r["combined"])
        r["layer"] = lay
        if r["boundary"]:
            r["layer_note"] = "boundary — depth excluded by policy; floored to P4"
        layers.setdefault(lay, []).append(r["id"])

    PRI.mkdir(parents=True, exist_ok=True)
    (PRI / "ranking.json").write_text(json.dumps({
        "weights": WEIGHTS, "usage_tier_score": USAGE_TIER_SCORE,
        "usage_default": USAGE_DEFAULT,
        "note": "combined = w.connectivity*conn + w.usage*usage + w.audience*audience",
        "ranking": ranking}, indent=2, ensure_ascii=False), encoding="utf-8")
    (PRI / "layers.json").write_text(json.dumps({
        "boundaries": BOUNDARIES,
        "rule": "score-threshold cut; boundary nodes floored to P4",
        "counts": {k: len(v) for k, v in sorted(layers.items())},
        "layers": {k: layers[k] for k in ["P0", "P1", "P2", "P3", "P4"] if k in layers}},
        indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({"counts": {k: len(v) for k, v in sorted(layers.items())}}, indent=2))
    print("\nP0:", layers.get("P0", []))
    print("P1:", layers.get("P1", []))
    print("P2:", layers.get("P2", []))
    print("\n-- full sorted --")
    for r in ranking:
        print(f"  {r['combined']:.3f} {r['layer']:<3} {r['id']:<42} "
              f"c={r['signals']['connectivity']:.2f} u={r['signals']['usage']:.2f} "
              f"a={r['signals']['audience']:.2f} {r['signals']['usage_tier']}")


if __name__ == "__main__":
    main()
