"""Generate graph.json — the spine — from the fat source files, and run the mechanical
completeness checks. graph.json is DERIVED (like overview.md); never hand-authored, so
structural facts have exactly one home (the fat files) and cannot drift.

The spine holds, per node: id, type, parent, layer, trigger paths, connection edges, and a
pointer to where its content lives. It is what navigation, priority, closure, and completeness
checks run on.
"""
import json
from pathlib import Path
from kernel.models import FeatureFile, UIFile, PriorityFile


def _load(root: Path):
    feats = []
    fdir = root / "features"
    if fdir.exists():
        for f in sorted(fdir.glob("*.json")):
            feats.append((f, FeatureFile.model_validate_json(f.read_text(encoding="utf-8"))))
    ui = UIFile()
    if (root / "ui.json").exists():
        ui = UIFile.model_validate_json((root / "ui.json").read_text(encoding="utf-8"))
    pri = PriorityFile()
    if (root / "priority.json").exists():
        pri = PriorityFile.model_validate_json((root / "priority.json").read_text(encoding="utf-8"))
    return feats, ui, pri


def build_graph(kb_root: Path, app: str) -> dict:
    """Read fat files, emit the spine dict. Does not write — caller decides."""
    root = Path(kb_root) / app
    feats, ui, pri = _load(root)

    layer_of = {}
    for layer, ids in (pri.layers or {}).items():
        for nid in ids:
            layer_of[nid] = layer

    nodes = {}
    edges = []
    for path, ff in feats:
        rel = f"features/{path.name}"
        f = ff.feature
        nodes[f.id] = {"type": "feature", "parent": None, "layer": layer_of.get(f.id),
                       "trigger_paths": [tp.model_dump() for tp in f.trigger_paths],
                       "content": rel}
        for c in f.connections:
            edges.append({"from": f.id, "to": c.target, "kind": c.kind, "why": c.why})
        for s in ff.subfeatures:
            nodes[s.id] = {"type": "subfeature", "parent": f.id, "layer": layer_of.get(s.id),
                           "trigger_paths": [tp.model_dump() for tp in s.trigger_paths],
                           "opens": s.opens, "content": rel}
            for c in s.connections:
                edges.append({"from": s.id, "to": c.target, "kind": c.kind, "why": c.why})

    containers = {cid: {"kind": c.kind, "explored": c.explored,
                        "opens": [ch.opens for ch in c.children if ch.opens],
                        "triggers": [ch.triggers for ch in c.children if ch.triggers],
                        # label summaries by marker class — the element-level checks run on these
                        "unexplored_labels": [ch.label for ch in c.children if ch.unexplored],
                        "endpoint_labels": [ch.label for ch in c.children if ch.triggers]}
                  for cid, c in ui.containers.items()}

    return {"app": app, "nodes": nodes, "edges": edges, "containers": containers,
            "layers": pri.layers, "closure": pri.closure,
            "derived": pri.derived_features}


# Window/scrollbar chrome + dialog-dismiss labels exempt from the unexplored-element depth check
# (playbook R5.4). Lowercase exact match; calibrate as real runs surface new chrome.
_CHROME_LABELS = {
    "minimize", "maximize", "restore", "restore down", "close", "cancel", "ok", "help",
    "line up", "line down", "page up", "page down", "line left", "line right",
    "page left", "page right", "column left", "column right", "position",
    "vertical", "horizontal", "vertical scrollbar", "horizontal scrollbar",
    "ribbon display options",
}


def _is_chrome(label: str) -> bool:
    return (label or "").strip().lower() in _CHROME_LABELS


def _ellipsis_labeled(label: str) -> bool:
    """True for labels that promise a dialog by platform convention (playbook R2.4).
    Requires at least one letter so leader-dot options like '2 .......' don't false-positive."""
    s = (label or "").rstrip()
    return s.endswith(("…", "...")) and any(ch.isalpha() for ch in s)


def check_completeness(graph: dict) -> list[str]:
    """Mechanical checks (design: "Completeness check"). Returns a list of problems; empty = clean.
    Stubs (explored:false) are allowed and NOT reported — they are honest deferrals."""
    problems = []
    node_ids = set(graph["nodes"])
    container_ids = set(graph["containers"])

    # every edge target resolves to a node or container
    for e in graph["edges"]:
        if e["to"] not in node_ids and e["to"] not in container_ids:
            problems.append(f"dangling edge: {e['from']} --{e['kind']}--> {e['to']} (missing)")

    # every opens reference inside a container resolves to a known container
    for cid, c in graph["containers"].items():
        for o in c["opens"]:
            if o not in container_ids:
                problems.append(f"container {cid} opens '{o}' which does not exist")
        for t in c["triggers"]:
            if t not in node_ids:
                problems.append(f"container {cid} triggers '{t}' which is not a known node")

    # every node has at least one trigger path (reachable from the skeleton)
    for nid, n in graph["nodes"].items():
        if n["type"] == "subfeature" and not n["trigger_paths"]:
            problems.append(f"node {nid} has no trigger path (unreachable)")

    # every node is ranked into a layer (playbook R4.3) — an unranked node is a silent gap
    layers = graph.get("layers") or {}
    if layers:
        ranked = {i for ids in layers.values() for i in ids}
        for nid in graph["nodes"]:
            if nid not in ranked:
                problems.append(f"node {nid} is in no priority layer (unranked — silent gap)")

    # ellipsis contract (playbook R2.4): a "…"-labeled element promises a dialog; recording it
    # as an endpoint (triggers) is a classification contradiction, whatever its layer
    for cid, c in graph["containers"].items():
        for label in c.get("endpoint_labels", []):
            if _ellipsis_labeled(label):
                problems.append(f"container {cid} closes ellipsis-labeled \"{label}\" as an endpoint (R2.4: must be opens/unexplored)")

    # depth invariant (playbook R5.4 + R5.5): no DEPTH-SET node reaches an explored:false
    # container or an unexplored element (chrome exempt) by any chain of opens.
    # depth set = P0-P3 nodes + ALL children of scope:whole features (04's majority rule);
    # closure pulls get "enough to work" depth, which is judgment, not mechanically checkable.
    whole = {fid for fid, d in (graph.get("derived") or {}).items()
             if isinstance(d, dict) and d.get("scope") == "whole"}
    hi = {nid for nid, n in graph["nodes"].items()
          if n.get("layer") in ("P0", "P1", "P2", "P3")
          or (n["type"] == "subfeature" and n.get("parent") in whole)}
    stubs = {cid for cid, c in graph["containers"].items() if not c["explored"]}
    gapped = {}   # cid -> non-chrome unexplored labels (deduped: reported once per container)
    for cid, c in graph["containers"].items():
        labels = [l for l in c.get("unexplored_labels", []) if not _is_chrome(l)]
        if labels:
            gapped[cid] = labels
    reported_stub, reported_gap = set(), set()
    if stubs or gapped:
        for nid in sorted(hi):
            start = graph["nodes"][nid].get("opens")
            seen, frontier = set(), ([start] if start else [])
            while frontier:
                cid = frontier.pop()
                if cid in seen or cid not in graph["containers"]:
                    continue
                seen.add(cid)
                if cid in stubs and cid not in reported_stub:
                    reported_stub.add(cid)
                    problems.append(f"depth-set node {nid} reaches unexplored stub {cid} (depth incomplete)")
                if cid in gapped and cid not in reported_gap:
                    reported_gap.add(cid)
                    ex = ", ".join(f'"{l}"' for l in gapped[cid][:3])
                    problems.append(f"depth-set node {nid} reaches container {cid} holding {len(gapped[cid])} unexplored element(s), e.g. {ex} (R5.4)")
                frontier += graph["containers"][cid]["opens"]
    return problems


def generate(kb_root: Path, app: str) -> tuple[Path, list[str]]:
    """Build graph.json, write it, run checks. Returns (path, problems)."""
    root = Path(kb_root) / app
    graph = build_graph(kb_root, app)
    out = root / "graph.json"
    out.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    return out, check_completeness(graph)
