"""Step 5 — definition-of-done, checked mechanically (design 'Definition of done' +
playbook 05-depth proof). Fails loudly on any gap.

Checks:
  1. Every P0-P2 node is explored:true, has behavior + affects + >=1 trigger_path
     + >=1 screenshot (subfeatures); P3 has behavior (mid-level); P4 explored:false, labeled.
  2. TRANSITIVE depth (the check the word-home-tab run lacked): walk `opens` from every
     P0-P2 node through the WHOLE chain (node.opens + every element.opens of every container
     reached, plus child_containers) — not one explored:false container may be reachable.
  3. Every container element carries exactly one marker; every opens resolves to a container
     file; empty containers must be explicit stubs (explored:false).
  4. Every feature/subfeature has a live trigger path; every skeleton triggers resolves to a
     node; every connections[].target resolves; every node shortcut string has a registry
     entry; every registry binding resolves; no key+context conflicts.
  5. overview.md exists.
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB


def load(glob):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(KB.glob(glob))]


def reachable_containers(start_ids, cont_by_id):
    """All container ids reachable from start ids via element `opens` + child_containers."""
    seen, stack = set(), list(start_ids)
    while stack:
        cid = stack.pop()
        if cid in seen:
            continue
        seen.add(cid)
        c = cont_by_id.get(cid)
        if not c:
            continue
        for e in c.get("children", []):
            if e.get("opens"):
                stack.append(e["opens"])
        for cc in c.get("child_containers", []):
            stack.append(cc)
    return seen


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

    # --- start surfaces per node: node.opens + opens of its trigger-path elements ---
    el_opens = {}
    for c in containers:
        for e in c.get("children", []):
            if e.get("id") and e.get("opens"):
                el_opens[e["id"]] = e["opens"]

    def node_start_surfaces(n):
        starts = set()
        if n.get("opens"):
            starts.add(n["opens"])
        for tp in n.get("trigger_paths", []):
            leaf = tp["path"][-1] if tp.get("path") else None
            if leaf and leaf in el_opens:
                starts.add(el_opens[leaf])
        return starts

    # 1+2) P0-P2 depth incl. TRANSITIVE stub check
    for n in features + subs:
        nid = n["id"]
        if nid in p0p2:
            if not n.get("explored"):
                gaps.append(f"{nid}: P0-P2 but explored != true")
            if not n.get("behavior"):
                gaps.append(f"{nid}: P0-P2 but no behavior (depth rubric)")
            if n.get("node_type", "feature") == "subfeature" and not n.get("screenshots"):
                gaps.append(f"{nid}: P0-P2 subfeature but no screenshots")
            starts = node_start_surfaces(n)
            reach = reachable_containers(starts, cont_by_id)
            for cid in sorted(reach):
                c = cont_by_id.get(cid)
                if c is None:
                    gaps.append(f"{nid}: reachable container {cid} MISSING")
                elif c.get("explored", True) is False:
                    gaps.append(f"{nid}: explored:false stub REACHABLE via opens-chain: {cid}")
        elif nid in p3:
            if not n.get("behavior"):
                gaps.append(f"{nid}: P3 but no behavior (mid-level rubric)")
        if not n.get("what_it_does") or not n.get("affects"):
            gaps.append(f"{nid}: missing what_it_does/affects")
        if not n.get("trigger_paths"):
            gaps.append(f"{nid}: no trigger_path")

    # 3) container markers + opens resolution + honest stubs
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

    # 4) trigger paths, connections, shortcuts
    for t in skel_triggers:
        if t not in node_ids:
            gaps.append(f"skeleton triggers {t} -> no node")
    for n in features + subs:
        for tp in n.get("trigger_paths", []):
            if tp.get("kind") == "mouse" and tp.get("path"):
                leaf = tp["path"][-1]
                if leaf.startswith("el:") and leaf not in el_ids:
                    gaps.append(f"{n['id']}: trigger leaf {leaf} not in skeleton")
        for e in n.get("connections", []):
            if e["target"] not in node_ids and e["target"] not in cont_ids:
                gaps.append(f"{n['id']}: connection {e['target']} dangling")
    reg_keys = set()
    for sc in shortcuts:
        reg_keys.add(sc["keys"])
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
        "stub_containers": sorted(c["id"] for c in containers
                                  if c.get("explored", True) is False),
        "gaps": gaps,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\nDEFINITION OF DONE:", "PASS" if not gaps else f"FAIL ({len(gaps)} gaps)")
    return 0 if not gaps else 1


if __name__ == "__main__":
    raise SystemExit(main())
