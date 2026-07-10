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
                        "triggers": [ch.triggers for ch in c.children if ch.triggers]}
                  for cid, c in ui.containers.items()}

    return {"app": app, "nodes": nodes, "edges": edges, "containers": containers,
            "layers": pri.layers, "closure": pri.closure}


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

    # depth invariant: no P0-P2 node reaches an explored:false container by any chain of opens
    hi = {nid for nid, n in graph["nodes"].items() if n.get("layer") in ("P0", "P1", "P2")}
    stubs = {cid for cid, c in graph["containers"].items() if not c["explored"]}
    if stubs:
        for nid in hi:
            start = graph["nodes"][nid].get("opens")
            seen, frontier = set(), ([start] if start else [])
            while frontier:
                cid = frontier.pop()
                if cid in seen or cid not in graph["containers"]:
                    continue
                seen.add(cid)
                if cid in stubs:
                    problems.append(f"P0-P2 node {nid} reaches unexplored stub {cid} (depth incomplete)")
                frontier += graph["containers"][cid]["opens"]
    return problems


def generate(kb_root: Path, app: str) -> tuple[Path, list[str]]:
    """Build graph.json, write it, run checks. Returns (path, problems)."""
    root = Path(kb_root) / app
    graph = build_graph(kb_root, app)
    out = root / "graph.json"
    out.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    return out, check_completeness(graph)
