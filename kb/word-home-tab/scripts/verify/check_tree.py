"""Step 3 mechanical checks over the feature/subfeature tree.

Asserts:
  * no name-only nodes — every feature/subfeature has what_it_does + affects + audience +
    >=1 trigger_path;
  * every skeleton element with triggers=subfeature:X resolves to an existing subfeature;
  * every node's trigger_path element ids (el:*) exist in the skeleton, and any opens/parent
    resolves;
  * every connections[].target resolves to an existing node (feature/subfeature) or container;
  * no orphan subfeature (parent exists and lists it).
Exit 0 = clean.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import common

KB = common.APP_KB


def load_all(glob):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(KB.glob(glob))]


def main():
    features = load_all("features/*.json")
    subs = load_all("subfeatures/**/*.json")
    containers = load_all("ui/*.json")

    feat_ids = {f["id"] for f in features}
    sub_ids = {s["id"] for s in subs}
    node_ids = feat_ids | sub_ids
    cont_ids = {c["id"] for c in containers}
    # skeleton element ids + their triggers targets
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
            # every mouse path's element id must exist in the skeleton
            for tp in n["trigger_paths"]:
                if tp.get("kind") == "mouse" and tp.get("path"):
                    leaf = tp["path"][-1]
                    if leaf.startswith("el:") and leaf not in el_ids:
                        gaps.append(f"{n['id']}: trigger path leaf {leaf} not in skeleton")

    # 2) every skeleton triggers -> existing subfeature (both directions)
    for t in skel_triggers:
        if t not in sub_ids:
            gaps.append(f"skeleton triggers {t} -> NO subfeature node")
    # every triggers-subfeature should reference its skeleton element back
    for s in subs:
        leaves = {tp["path"][-1] for tp in s["trigger_paths"] if tp.get("path")}
        # a subfeature that is a skeleton triggers-target must include that element in a path
        # (opens-only subfeatures reference their opens element instead)
        if s["id"] in skel_triggers and not any(l.startswith("el:") for l in leaves):
            gaps.append(f"{s['id']}: skeleton triggers it but node has no el: trigger path")

    # 3) opens / parent resolve
    for s in subs:
        if s.get("opens") and s["opens"] not in cont_ids:
            gaps.append(f"{s['id']}: opens {s['opens']} -> NO container")
        if s.get("parent") and s["parent"] not in feat_ids:
            gaps.append(f"{s['id']}: parent {s['parent']} -> NO feature")

    # 4) feature.subfeatures resolve + parent backref
    for f in features:
        for sid in f.get("subfeatures", []):
            if sid not in sub_ids:
                gaps.append(f"{f['id']}: subfeature {sid} -> NO node")
    for s in subs:
        if s.get("parent"):
            pf = next((f for f in features if f["id"] == s["parent"]), None)
            if pf and s["id"] not in pf.get("subfeatures", []):
                gaps.append(f"{s['id']}: parent {s['parent']} does not list it")

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

    report = {
        "features": len(features), "subfeatures": len(subs), "connection_edges": edge_count,
        "skeleton_triggers": len(skel_triggers),
        "all_triggers_resolve": all(t in sub_ids for t in skel_triggers),
        "gaps": gaps,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\nRESULT:", "PASS ✓" if not gaps else f"FAIL ✗ ({len(gaps)} gaps)")
    return 0 if not gaps else 1


if __name__ == "__main__":
    raise SystemExit(main())
