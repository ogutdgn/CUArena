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
                       "cohesion": f.cohesion,
                       "trigger_paths": [tp.model_dump() for tp in f.trigger_paths],
                       "content": rel}
        for c in f.connections:
            edges.append({"from": f.id, "to": c.target, "kind": c.kind, "why": c.why})
        for s in ff.subfeatures:
            b = s.behavior_record
            nodes[s.id] = {"type": "subfeature", "parent": f.id, "layer": layer_of.get(s.id),
                           "trigger_paths": [tp.model_dump() for tp in s.trigger_paths],
                           "opens": s.opens, "content": rel,
                           "behavior": ({"evidenced": b.evidenced(), "pending": len(b.pending)}
                                        if b else None)}
            for c in s.connections:
                edges.append({"from": s.id, "to": c.target, "kind": c.kind, "why": c.why})

    containers = {cid: {"kind": c.kind, "explored": c.explored,
                        "opens": [ch.opens for ch in c.children if ch.opens],
                        "triggers": [ch.triggers for ch in c.children if ch.triggers],
                        # label summaries by marker class — the element-level checks run on these
                        "unexplored_labels": [ch.label for ch in c.children if ch.unexplored],
                        "endpoint_labels": [ch.label for ch in c.children if ch.triggers],
                        # R2.8 scroll bookkeeping: does the container show scrollbar traces,
                        # and did the run address them?
                        "scroll_trace": any((ch.label or "").strip().lower() in _SCROLLBAR_LABELS
                                            for ch in c.children),
                        "scrolled_to_end": c.scrolled_to_end,
                        # R2.5 gallery check inputs: per-element (id, label, marker) + id set
                        "element_ids": [ch.id for ch in c.children if ch.id],
                        "elements": [(ch.id, ch.label,
                                      "triggers" if ch.triggers else ("opens" if ch.opens else "unexplored"))
                                     for ch in c.children]}
                  for cid, c in ui.containers.items()}

    return {"app": app, "nodes": nodes, "edges": edges, "containers": containers,
            "layers": pri.layers, "closure": pri.closure,
            "derived": pri.derived_features,
            "weights": pri.weights, "boundaries": pri.boundaries,
            "deviations": pri.deviations}


# Pipeline defaults for priority scoring (playbook 04-priority.md "Pipeline defaults", R4.5).
# Mirror of the playbook table — change only together with it, via a reviewed pipeline commit.
DEFAULT_WEIGHTS = {"product_purpose": 0.45, "usage": 0.30, "prominence": 0.25}
DEFAULT_BOUNDARIES = {"P0": 0.80, "P1": 0.68, "P2": 0.55, "P3": 0.38}


def _differs(actual: dict, default: dict) -> bool:
    if set(actual) != set(default):
        return True
    return any(abs(float(actual[k]) - float(default[k])) > 1e-9 for k in default)


# Scrollbar-part labels — used to detect scroll traces on a container (R2.8). Deliberately
# specific: bare "horizontal"/"vertical" are excluded because they are common CONTENT labels
# (a Text Direction dialog's "Horizontal" radio is not a scrollbar) — a scrollbar always shows
# the line/page steppers plus "position", so those are the reliable signal.
_SCROLLBAR_LABELS = {
    "line up", "line down", "page up", "page down", "line left", "line right",
    "page left", "page right", "position",
    "vertical scrollbar", "horizontal scrollbar",
}

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

    # in-ribbon gallery contract (playbook R2.5): on a TAB surface, a gallery-named element
    # closed as an endpoint with no expand twin is the classification lie that survived two
    # runs. Tab-scope keeps noise out (menu commands named "...Gallery" live inside menus).
    for cid, c in graph["containers"].items():
        if c.get("kind") != "tab":
            continue
        ids = set(c.get("element_ids") or [])
        for eid, label, marker in (c.get("elements") or []):
            name = (eid or label or "").lower()
            if "gallery" not in name or marker != "triggers":
                continue
            if f"{eid}-dropdown" in ids or f"{eid}-expand" in ids:
                continue
            problems.append(f"tab {cid} closes in-ribbon gallery '{eid or label}' as an endpoint with no expand element (R2.5)")

    # scroll completeness (playbook R2.8): gated on the run being rule-aware (any container
    # carries scrolled_to_end). A scroll-traced explored container must have addressed the
    # scroll: True (enumerated to end) or False (honest journaled partial) — unset fails.
    if any(c.get("scrolled_to_end") is not None for c in graph["containers"].values()):
        for cid, c in graph["containers"].items():
            if c["explored"] and c.get("scroll_trace") and c.get("scrolled_to_end") is None:
                problems.append(f"container {cid} shows scrollbar traces but scrolled_to_end is unset (R2.8: scroll not addressed)")

    # catalog-scope contradiction (playbook R4.7 / R3.5): a catalog-cohesion feature must never
    # carry scope:whole — its children are independent capabilities, judged one by one
    for fid, d in (graph.get("derived") or {}).items():
        if isinstance(d, dict) and d.get("scope") == "whole":
            if graph["nodes"].get(fid, {}).get("cohesion") == "catalog":
                problems.append(f"catalog feature {fid} has scope:whole (R4.7: a catalog never replicates whole)")

    # silent-deviation check (playbook R4.5): weights/boundaries must equal the pipeline
    # defaults OR carry a deviations note pointing at the journaled decision
    if layers:
        devs = graph.get("deviations") or {}
        for name, actual, default in (("weights", graph.get("weights") or {}, DEFAULT_WEIGHTS),
                                      ("boundaries", graph.get("boundaries") or {}, DEFAULT_BOUNDARIES)):
            if actual and _differs(actual, default) and not devs.get(name):
                problems.append(f"{name} deviate from pipeline defaults with no deviations note (R4.5: silent deviation)")

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
    # closure invariant (playbook 04 "Closure"): every `requires` target of a depth-set node
    # must itself be in the depth set or pulled in by closure — else the replica ships a
    # capability that cannot work (broken dependency). Targets that are containers are skipped
    # (requires is a node-to-node contract).
    if layers:
        pulled = {c.get("id") for c in (graph.get("closure") or []) if isinstance(c, dict)}
        for e in graph["edges"]:
            if e["kind"] == "requires" and e["from"] in hi and e["to"] in node_ids:
                if e["to"] not in hi and e["to"] not in pulled:
                    problems.append(f"depth-set node {e['from']} requires {e['to']} which is neither in the depth set nor in closure (broken dependency)")

    stubs = {cid for cid, c in graph["containers"].items() if not c["explored"]}
    gapped = {}   # cid -> non-chrome unexplored labels (deduped: reported once per container)
    for cid, c in graph["containers"].items():
        labels = [l for l in c.get("unexplored_labels", []) if not _is_chrome(l)]
        if labels:
            gapped[cid] = labels
    # behavior contract (playbook 06, R6.3): gated on the run having produced ANY behavior
    # record — legacy KBs (pre-Step-6) stay clean. Once one exists, every depth-set
    # sub-feature owes an EVIDENCED record.
    if any(n.get("behavior") for n in graph["nodes"].values()):
        for nid in sorted(hi):
            n = graph["nodes"][nid]
            if n["type"] != "subfeature":
                continue
            b = n.get("behavior")
            if b is None:
                problems.append(f"depth-set node {nid} has no behavior record (R6: semantics unmeasured)")
            elif not b.get("evidenced"):
                problems.append(f"depth-set node {nid} behavior record carries no evidence refs (R6.3)")

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
