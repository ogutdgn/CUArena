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
    # R4.7 [kernel-checked]: a CATALOG feature never replicates WHOLE — its children are
    # independent capabilities judged one by one. Only capability-cohesion features may go whole
    # (the majority rule). A catalog with a hot majority still resolves to gems, never whole.
    derived = {}
    for f in feats:
        kids = [r for r in ranking if r["parent"] == f["id"]]
        if not kids:
            derived[f["id"]] = {"layer": "P4", "best_child": None, "ratio": "0/0",
                                "scope": "none", "cohesion": f.get("cohesion")}
            continue
        best = min(kids, key=lambda r: ("P0P1P2P3P4".index(r["layer"]) // 2, -r["combined"]))
        # R4/R5.5: the ratio counts children in the DEPTH-SET layers P0-P3 (the full-depth
        # boundary), NOT P0-P2 — that was v1/v2's boundary and this line was inherited unfixed
        # (measured: all 26 discriminating features matched the P0-P2 formula, none P0-P3).
        hi = [k for k in kids if k["layer"] in ("P0", "P1", "P2", "P3")]
        ratio = f"{len(hi)}/{len(kids)}"
        majority = len(hi) * 2 > len(kids)
        is_catalog = f.get("cohesion") == "catalog"
        if majority and not is_catalog:
            scope = "whole"
        elif hi:
            scope = "gems"
        else:
            scope = "none"
        entry = {"layer": best["layer"], "best_child": best["id"], "ratio": ratio,
                 "scope": scope, "cohesion": f.get("cohesion")}
        if majority and is_catalog:
            entry["scope_note"] = ("R4.7: catalog feature — majority of children rank high but a "
                                   "catalog never goes whole; children judged independently (gems)")
        derived[f["id"]] = entry
        layers[best["layer"]].append(f["id"])

    # ---- closure: the DEPTH SET + everything reachable via `requires` edges ----
    # The depth set the kernel checks is P0-P3 nodes (subs AND derived features) + all children
    # of whole-scope features (R5.5). Closure must follow requires from ALL of them — including
    # FEATURE-level requires (e.g. feature:graphics-format requires its summoner icon-insert) —
    # or a replicated capability ships without the capability that makes it exist.
    whole_features = {fid for fid, dd in derived.items() if dd["scope"] == "whole"}
    node_by_id = {s["id"]: s for s in subs}
    node_by_id.update({f["id"]: f for f in feats})
    depth_set = set()
    for r in ranking:
        if r["layer"] in ("P0", "P1", "P2", "P3") or r.get("parent") in whole_features:
            depth_set.add(r["id"])
    for fid, dd in derived.items():
        if dd["layer"] in ("P0", "P1", "P2", "P3"):
            depth_set.add(fid)
    requires = {}
    for n in subs + feats:
        for e in n.get("connections", []):
            if e["kind"] == "requires":
                requires.setdefault(n["id"], []).append((e["target"], e["why"]))
    closure, frontier = [], sorted(depth_set)
    in_set = set(depth_set)
    while frontier:
        nid = frontier.pop()
        for (req, why) in requires.get(nid, []):
            if req not in in_set and req in node_by_id:
                in_set.add(req)
                closure.append({"id": req, "pulled_in_by": nid, "reason": why})
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
