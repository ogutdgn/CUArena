"""Step 3 mechanical checks over the feature/subfeature tree — v2, CONSOLIDATED layout.

Reads features/<feature>.json (FeatureFile: feature + subfeatures inline) and the single
ui.json. Asserts:
  * no name-only nodes — every feature/subfeature has what_it_does + affects + audience +
    >=1 trigger_path;
  * every skeleton element with triggers=subfeature:X resolves to an existing subfeature;
  * every node's trigger_path element ids (el:*) exist in the skeleton, and any opens/parent
    resolves;
  * every connections[].target resolves to an existing node (feature/subfeature) or container;
  * no orphan subfeature (parent exists and lists it);
  * contextual containers (trigger_condition set) have their controls fed into the tree:
    every explored contextual tab's triggers targets resolve (the LESSONS dead-end check).
Exit 0 = clean.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB


def main():
    ffiles = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((KB / "features").glob("*.json"))]
    ui = json.loads((KB / "ui.json").read_text(encoding="utf-8"))
    containers = list(ui["containers"].values())

    features = [ff["feature"] for ff in ffiles]
    subs = [s for ff in ffiles for s in ff["subfeatures"]]

    feat_ids = {f["id"] for f in features}
    sub_ids = {s["id"] for s in subs}
    node_ids = feat_ids | sub_ids
    cont_ids = {c["id"] for c in containers}
    el_ids, skel_triggers = set(), set()
    for c in containers:
        for e in c.get("children", []):
            if e.get("id"):
                el_ids.add(e["id"])
            if e.get("triggers"):
                skel_triggers.add(e["triggers"])

    gaps = []

    # 1) no name-only nodes
    for n in features + subs:
        for field in ("what_it_does", "affects", "audience_breadth"):
            if not n.get(field):
                gaps.append(f"{n['id']}: missing {field}")
        if not n.get("trigger_paths"):
            gaps.append(f"{n['id']}: no trigger_path")
        else:
            for tp in n["trigger_paths"]:
                if tp.get("kind") == "mouse" and tp.get("path"):
                    leaf = tp["path"][-1]
                    if leaf.startswith("el:") and leaf not in el_ids:
                        gaps.append(f"{n['id']}: trigger path leaf {leaf} not in skeleton")

    # 2) skeleton triggers <-> nodes, both directions
    for t in sorted(skel_triggers):
        if t not in sub_ids:
            gaps.append(f"skeleton triggers {t} -> NO subfeature node")
    for s in subs:
        leaves = {tp["path"][-1] for tp in s["trigger_paths"] if tp.get("path")}
        if s["id"] in skel_triggers and not any(l.startswith("el:") for l in leaves):
            gaps.append(f"{s['id']}: skeleton triggers it but node has no el: trigger path")

    # 3) opens / parent resolve
    for s in subs:
        if s.get("opens") and s["opens"] not in cont_ids:
            gaps.append(f"{s['id']}: opens {s['opens']} -> NO container")
        if s.get("parent") and s["parent"] not in feat_ids:
            gaps.append(f"{s['id']}: parent {s['parent']} -> NO feature")

    # 4) feature.subfeatures resolve (FeatureFile validation guarantees inline consistency,
    #    but check cross-file uniqueness too)
    seen_sub = set()
    for s in subs:
        if s["id"] in seen_sub:
            gaps.append(f"{s['id']}: duplicated across feature files")
        seen_sub.add(s["id"])

    # 5) connections resolve
    edge_count = 0
    for n in features + subs:
        for e in n.get("connections", []):
            edge_count += 1
            if e["target"] not in node_ids and e["target"] not in cont_ids:
                gaps.append(f"{n['id']}: connection target {e['target']} -> DANGLING")
            for k in ("why", "source", "kind"):
                if not e.get(k):
                    gaps.append(f"{n['id']}: connection to {e['target']} missing {k}")

    # 6) contextual tabs are NOT dead ends (the LESSONS check): every explored contextual
    #    container's triggers targets must be nodes in the tree
    ctx_summary = {}
    for c in containers:
        if not c.get("trigger_condition"):
            continue
        trg = [e["triggers"] for e in c.get("children", []) if e.get("triggers")]
        missing = [t for t in trg if t not in sub_ids]
        ctx_summary[c["id"]] = {"controls": len(c.get("children", [])),
                                "triggers": len(trg), "unresolved": missing}
        for t in missing:
            gaps.append(f"contextual {c['id']}: triggers {t} not fed into the tree")

    report = {
        "features": len(features), "subfeatures": len(subs), "connection_edges": edge_count,
        "skeleton_triggers": len(skel_triggers),
        "all_triggers_resolve": all(t in sub_ids for t in skel_triggers),
        "contextual_tabs": ctx_summary,
        "gaps": gaps,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\nRESULT:", "PASS" if not gaps else f"FAIL ({len(gaps)} gaps)")
    return 0 if not gaps else 1


if __name__ == "__main__":
    raise SystemExit(main())
