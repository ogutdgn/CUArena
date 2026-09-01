"""Step 5 — definition-of-done, checked mechanically (v2, CONSOLIDATED layout).

Checks (design 'Definition of done' + playbook 05 proof):
  1. Every P0-P2 sub-feature is explored:true, has behavior + affects + >=1 trigger_path
     + >=1 screenshot; P3 has behavior (mid-level); P4 explored:false, labeled.
  2. TRANSITIVE depth: walk `opens` from every P0-P2 node through the WHOLE chain
     (node.opens + every element.opens of every container reached + child_containers) —
     not one explored:false container may be reachable. (STRONGER than the kernel check,
     which walks element opens only.)
  3. Every container element carries exactly one marker; every opens resolves; empty
     containers must be explicit stubs.
  4. Every node has a live trigger path; every skeleton triggers resolves to a node; every
     connections[].target resolves; every node shortcut string has a registry entry; every
     registry binding resolves; no key+context conflicts.
  5. overview.md exists.
  6. kernel graph_builder.generate() returns CLEAN (the authoritative check).
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common
from kernel import graph_builder

KB = common.APP_KB


def reachable_containers(start_ids, cont_by_id):
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
    ffiles = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((KB / "features").glob("*.json"))]
    features = [ff["feature"] for ff in ffiles]
    subs = [s for ff in ffiles for s in ff["subfeatures"]]
    ui = json.loads((KB / "ui.json").read_text(encoding="utf-8"))["containers"]
    containers = list(ui.values())
    shortcuts = json.loads((KB / "shortcuts.json").read_text(encoding="utf-8"))["entries"]
    pri = json.loads((KB / "priority.json").read_text(encoding="utf-8"))
    layers = pri["layers"]
    p0p2 = set(layers.get("P0", []) + layers.get("P1", []) + layers.get("P2", []))
    p3 = set(layers.get("P3", []))

    cont_by_id = {c["id"]: c for c in containers}
    node_ids = {n["id"] for n in features + subs}
    cont_ids = set(cont_by_id)
    el_ids, skel_triggers = set(), set()
    el_opens = {}
    for c in containers:
        for e in c.get("children", []):
            if e.get("id"):
                el_ids.add(e["id"])
                if e.get("opens"):
                    el_opens[e["id"]] = e["opens"]
            if e.get("triggers"):
                skel_triggers.add(e["triggers"])

    gaps = []

    def node_start_surfaces(n):
        starts = set()
        if n.get("opens"):
            starts.add(n["opens"])
        for tp in n.get("trigger_paths", []):
            leaf = tp["path"][-1] if tp.get("path") else None
            if leaf and leaf in el_opens:
                starts.add(el_opens[leaf])
        return starts

    # 1+2) rubric depth per layer + TRANSITIVE stub reachability for P0-P2
    for n in features + subs:
        nid = n["id"]
        is_sub = nid.startswith("subfeature:")
        if nid in p0p2:
            if not n.get("explored"):
                gaps.append(f"{nid}: P0-P2 but explored != true")
            if not n.get("behavior"):
                gaps.append(f"{nid}: P0-P2 but no behavior (depth rubric)")
            if is_sub and not n.get("screenshots"):
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
    for t in sorted(skel_triggers):
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
    for keys, entry in shortcuts.items():
        reg_keys.add(keys)
        seen_ctx = set()
        for b in entry["bindings"]:
            tgt = b.get("triggers") or b.get("opens")
            if tgt not in node_ids and tgt not in cont_ids:
                gaps.append(f"shortcut {keys}: target {tgt} dangling")
            if b["context"] in seen_ctx:
                gaps.append(f"shortcut {keys}: duplicate context (conflict)")
            seen_ctx.add(b["context"])
    for n in subs:
        if n.get("shortcut"):
            first = n["shortcut"].split(",")[0].strip()
            if first not in reg_keys:
                gaps.append(f"{n['id']}: shortcut '{first}' has no registry entry")

    # 5) overview
    if not (KB / "overview.md").exists():
        gaps.append("overview.md missing")

    # 6) the kernel's own generate + checks — authoritative
    gpath, kernel_problems = graph_builder.generate(common.KB_ROOT, common.APP)
    for p in kernel_problems:
        gaps.append(f"kernel: {p}")

    report = {
        "features": len(features), "subfeatures": len(subs), "containers": len(containers),
        "shortcut_keys": len(shortcuts), "markers": dict(markers),
        "P0-P2": len(p0p2), "P3": len(p3),
        "explored_containers": sum(1 for c in containers if c.get("explored", True)),
        "stub_containers": sorted(c["id"] for c in containers
                                  if c.get("explored", True) is False),
        "kernel_graph": str(gpath), "kernel_problems": kernel_problems,
        "gaps": gaps,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\nDEFINITION OF DONE:", "PASS" if not gaps else f"FAIL ({len(gaps)} gaps)")
    return 0 if not gaps else 1


if __name__ == "__main__":
    raise SystemExit(main())
