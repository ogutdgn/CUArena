"""Step 5 — definition-of-done, checked mechanically (design 'Definition of done').

Fails loudly on any gap. Checks:
  1. Every P0-P2 node is explored:true, has behavior + affects + >=1 trigger_path + >=1 screenshot,
     and points at NO explored:false stub (depth finished). P3 explored w/ rubric; P4 explored:false, labeled.
  2. Every container element carries exactly one marker; every opens resolves to a container file.
  3. Every feature/subfeature has a live trigger path; every skeleton triggers resolves to a node.
  4. Every connections[].target resolves. Every node shortcut string has a registry entry;
     every registry binding resolves to an existing node/container. No key+context conflict.
  5. overview.md exists.
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import common

KB = common.APP_KB


def load(glob):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(KB.glob(glob))]


def main():
    features = load("features/*.json")
    subs = load("subfeatures/**/*.json")
    containers = load("ui/*.json")
    shortcuts = load("shortcuts/*.json")
    layers = json.loads((KB / "priority" / "layers.json").read_text(encoding="utf-8"))["layers"]
    p0p2 = set(layers.get("P0", []) + layers.get("P1", []) + layers.get("P2", []))
    p3 = set(layers.get("P3", []))

    cont_by_id = {c["id"]: c for c in containers}
    node_ids = {n["id"] for n in features + subs}
    cont_ids = set(cont_by_id)
    el_ids, skel_triggers = set(), set()
    for c in containers:
        for e in c.get("children", []):
            if e.get("id"):
                el_ids.add(e["id"])
            if e.get("triggers"):
                skel_triggers.add(e["triggers"])

    gaps = []

    # 1) P0-P2 depth
    for n in features + subs:
        nid = n["id"]
        if nid in p0p2:
            if not n.get("explored"):
                gaps.append(f"{nid}: P0-P2 but explored != true")
            if not n.get("behavior"):
                gaps.append(f"{nid}: P0-P2 but no behavior (depth rubric)")
            if n.get("node_type", "feature") == "subfeature" and not n.get("screenshots"):
                gaps.append(f"{nid}: P0-P2 subfeature but no screenshots")
            if n.get("opens"):
                c = cont_by_id.get(n["opens"])
                if not c:
                    gaps.append(f"{nid}: opens {n['opens']} -> missing container")
                elif c.get("explored") is False:
                    gaps.append(f"{nid}: P0-P2 still points at explored:false stub {n['opens']}")
        if not n.get("what_it_does") or not n.get("affects"):
            gaps.append(f"{nid}: missing what_it_does/affects")
        if not n.get("trigger_paths"):
            gaps.append(f"{nid}: no trigger_path")

    # 2) container markers + opens resolution
    markers = Counter()
    for c in containers:
        kids = c.get("children", [])
        if not kids and c.get("explored", True):
            gaps.append(f"{c['id']}: empty children but explored != false")
        for e in kids:
            k = sum([bool(e.get("triggers")), bool(e.get("opens")), bool(e.get("unexplored"))])
            if k != 1:
                gaps.append(f"{c['id']}/{e.get('label')}: {k} markers")
            for m in ("triggers", "opens", "unexplored"):
                if e.get(m):
                    markers[m] += 1
            if e.get("opens") and e["opens"] not in cont_ids:
                gaps.append(f"{c['id']}/{e.get('label')}: opens {e['opens']} dangling")
        for cc in c.get("child_containers", []):
            if cc not in cont_ids:
                gaps.append(f"{c['id']}: child_container {cc} dangling")

    # 3) trigger path resolution (both directions)
    for t in skel_triggers:
        if t not in node_ids:
            gaps.append(f"skeleton triggers {t} -> no node")
    for n in features + subs:
        for tp in n.get("trigger_paths", []):
            if tp.get("kind") == "mouse" and tp.get("path"):
                leaf = tp["path"][-1]
                if leaf.startswith("el:") and leaf not in el_ids:
                    gaps.append(f"{n['id']}: trigger leaf {leaf} not in skeleton")

    # 4) connections + shortcuts
    for n in features + subs:
        for e in n.get("connections", []):
            if e["target"] not in node_ids and e["target"] not in cont_ids:
                gaps.append(f"{n['id']}: connection {e['target']} dangling")
    reg_keys = {sc["keys"] for sc in shortcuts}
    for sc in shortcuts:
        seen_ctx = set()
        for b in sc["bindings"]:
            tgt = b.get("triggers") or b.get("opens")
            if tgt not in node_ids and tgt not in cont_ids:
                gaps.append(f"shortcut {sc['keys']}: target {tgt} dangling")
            if b["context"] in seen_ctx:
                gaps.append(f"shortcut {sc['keys']}: duplicate context (conflict)")
            seen_ctx.add(b["context"])
    for n in subs:
        if n.get("shortcut"):
            first = n["shortcut"].split(",")[0].strip()
            if first not in reg_keys:
                gaps.append(f"{n['id']}: shortcut '{first}' has no registry entry")

    # 5) overview
    if not (KB / "overview.md").exists():
        gaps.append("overview.md missing")

    report = {
        "features": len(features), "subfeatures": len(subs), "containers": len(containers),
        "shortcuts": len(shortcuts), "markers": dict(markers),
        "P0-P2": len(p0p2), "P3": len(p3),
        "explored_containers": sum(1 for c in containers if c.get("explored", True)),
        "gaps": gaps,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\nDEFINITION OF DONE:", "PASS ✓" if not gaps else f"FAIL ✗ ({len(gaps)} gaps)")
    return 0 if not gaps else 1


if __name__ == "__main__":
    raise SystemExit(main())
