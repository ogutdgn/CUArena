"""Step 4 combine (v2): normalize the THREE value signals, weighted-sum, sort SUB-FEATURES
only, cut into P0-P4, derive feature rows, compute closure over `requires` edges.

Arithmetic, not judgment (design 'Priority mechanics'). Everything recorded: weights,
verdict/tier score maps, boundaries, per-node evidence. Connection density is NOT a value
signal anywhere in this file (the v1 mistake). Boundary nodes floored to P4 by policy.
Writes the consolidated priority.json (kernel PriorityFile) + priority/ranking.json for
human auditing.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB
SIG = KB / "priority" / "signals"
PRI = KB / "priority"

WEIGHTS = {"product_purpose": 0.45, "usage": 0.30, "prominence": 0.25}
VERDICT_SCORE = {"indispensable": 1.0, "important": 0.70, "useful": 0.45, "peripheral": 0.18}
USAGE_TIER_SCORE = {"very-high": 1.0, "high": 0.80, "medium": 0.55, "low": 0.30, "rare": 0.12}
USAGE_DEFAULT = 0.25            # no web evidence -> neutral-low; signals 1+2 carry it
BOUNDARIES = {"P0": 0.80, "P1": 0.68, "P2": 0.55, "P3": 0.38}     # else P4


def layer_for(score):
    for lay in ("P0", "P1", "P2", "P3"):
        if score >= BOUNDARIES[lay]:
            return lay
    return "P4"


def main():
    ffiles = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((KB / "features").glob("*.json"))]
    feats = [ff["feature"] for ff in ffiles]
    subs = [s for ff in ffiles for s in ff["subfeatures"]]
    sub_by_id = {s["id"]: s for s in subs}

    prom = json.loads((SIG / "prominence.json").read_text(encoding="utf-8"))["nodes"]
    prod = json.loads((SIG / "product_purpose.json").read_text(encoding="utf-8"))["nodes"]
    usage = json.loads((SIG / "usage.json").read_text(encoding="utf-8"))["nodes"]

    ranking = []
    for s in subs:
        nid = s["id"]
        p_entry = prod.get(nid)
        u_entry = usage.get(nid)
        pr = prom.get(nid, {}).get("score", 0.0)
        pv = VERDICT_SCORE[p_entry["verdict"]] if p_entry else 0.0
        uv = USAGE_TIER_SCORE.get((u_entry or {}).get("tier"), USAGE_DEFAULT)
        combined = round(WEIGHTS["product_purpose"] * pv + WEIGHTS["usage"] * uv
                         + WEIGHTS["prominence"] * pr, 4)
        ranking.append({
            "id": nid, "name": s["name"], "parent": s.get("parent"),
            "boundary": s.get("boundary", False),
            "signals": {
                "product_purpose": pv,
                "product_verdict": (p_entry or {}).get("verdict"),
                "product_reasoning": (p_entry or {}).get("reasoning"),
                "usage": uv, "usage_tier": (u_entry or {}).get("tier", "no-evidence"),
                "usage_claim": (u_entry or {}).get("claim"),
                "usage_source": (u_entry or {}).get("source"),
                "prominence": pr,
            },
            "combined": combined,
        })
    ranking.sort(key=lambda r: -r["combined"])

    layers = {k: [] for k in ("P0", "P1", "P2", "P3", "P4")}
    for r in ranking:
        lay = "P4" if r["boundary"] else layer_for(r["combined"])
        r["layer"] = lay
        if r["boundary"]:
            r["layer_note"] = "boundary — depth excluded by policy; floored to P4"
        layers[lay].append(r["id"])

    # ---- derive features (never scored): layer = best child; ratio -> scope ----
    derived = {}
    for f in feats:
        kids = [r for r in ranking if r["parent"] == f["id"]]
        if not kids:
            derived[f["id"]] = {"layer": "P4", "best_child": None, "ratio": "0/0",
                                "scope": "none"}
            continue
        best = min(kids, key=lambda r: ("P0P1P2P3P4".index(r["layer"]) // 2, -r["combined"]))
        hi = [k for k in kids if k["layer"] in ("P0", "P1", "P2")]
        ratio = f"{len(hi)}/{len(kids)}"
        scope = ("whole" if len(hi) * 2 > len(kids)
                 else ("gems" if hi else "none"))
        derived[f["id"]] = {"layer": best["layer"], "best_child": best["id"],
                            "ratio": ratio, "scope": scope}
        layers[best["layer"]].append(f["id"])

    # ---- closure: P0-P2 + everything reachable via requires edges ----
    p0p2 = {r["id"] for r in ranking if r["layer"] in ("P0", "P1", "P2")}
    requires = {}
    for s in subs:
        for e in s.get("connections", []):
            if e["kind"] == "requires":
                requires.setdefault(s["id"], []).append(e["target"])
    closure, frontier = [], sorted(p0p2)
    in_set = set(p0p2)
    while frontier:
        nid = frontier.pop()
        for req in requires.get(nid, []):
            if req not in in_set and req in sub_by_id:
                in_set.add(req)
                closure.append({"id": req, "pulled_in_by": nid,
                                "reason": next(e["why"] for e in sub_by_id[nid]["connections"]
                                               if e["kind"] == "requires"
                                               and e["target"] == req)})
                frontier.append(req)

    PRI.mkdir(parents=True, exist_ok=True)
    (PRI / "ranking.json").write_text(json.dumps({
        "weights": WEIGHTS, "verdict_score": VERDICT_SCORE,
        "usage_tier_score": USAGE_TIER_SCORE, "usage_default": USAGE_DEFAULT,
        "boundaries": BOUNDARIES,
        "note": "combined = 0.45*product_purpose + 0.30*usage + 0.25*prominence; value = "
                "usage only, connections are logistics (closure), never scored",
        "ranking": ranking}, indent=2, ensure_ascii=False), encoding="utf-8")

    writer = common.get_writer()
    writer.write_priority({
        "layers": layers,
        "ranking": [{"id": r["id"], "score": r["combined"], "layer": r["layer"],
                     "signals": r["signals"]} for r in ranking],
        "derived_features": derived,
        "closure": closure,
        "weights": WEIGHTS,
        "boundaries": BOUNDARIES,
    })
    run_id = common.make_run_id() + "-priority"
    jrnl = common.get_journal(run_id)
    jrnl.append(common.journal_event(actor="stage4", action="rank",
                target="priority.json", outcome="ok",
                data={"counts": {k: len(v) for k, v in layers.items()},
                      "closure_pulled": [c["id"] for c in closure]}))
    print(json.dumps({"counts": {k: len(v) for k, v in layers.items()},
                      "closure": closure}, indent=2))
    print("\nP0:", layers["P0"])
    print("P1:", layers["P1"])
    print("P2:", layers["P2"])
    for r in ranking[:20]:
        print(f"  {r['combined']:.3f} {r['layer']:<3} {r['id']:<52} "
              f"p={r['signals']['product_purpose']:.2f} u={r['signals']['usage']:.2f} "
              f"m={r['signals']['prominence']:.2f}")


if __name__ == "__main__":
    main()
