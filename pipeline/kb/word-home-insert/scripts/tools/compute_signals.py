"""Step 4 signals (deterministic): connectivity + audience. No LLM, no research.

connectivity — degree centrality over the UNDIRECTED affects/uses graph (assembly counts an
edge for both endpoints, per the design). Same graph in -> same scores out.
audience    — pure lookup from each node's audience_breadth.
Writes kb/word/priority/signals/connectivity.json and audience.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import common

KB = common.APP_KB
SIG = KB / "priority" / "signals"

AUDIENCE_SCORE = {"everyone": 1.0, "most": 0.65, "niche": 0.30}


def audience_score(v):
    if v in AUDIENCE_SCORE:
        return AUDIENCE_SCORE[v]
    if v.startswith("role-specific:"):
        return 0.40
    return 0.25


def load_nodes():
    nodes = {}
    for p in sorted(KB.glob("features/*.json")):
        n = json.loads(p.read_text(encoding="utf-8"))
        nodes[n["id"]] = n
    for p in sorted(KB.glob("subfeatures/**/*.json")):
        n = json.loads(p.read_text(encoding="utf-8"))
        nodes[n["id"]] = n
    return nodes


def main():
    SIG.mkdir(parents=True, exist_ok=True)
    nodes = load_nodes()

    # undirected neighbor sets from connections (both directions)
    neighbors = {nid: set() for nid in nodes}
    for nid, n in nodes.items():
        for e in n.get("connections", []):
            t = e["target"]
            if t in nodes:                      # ignore edges to containers for centrality
                neighbors[nid].add(t)
                neighbors[t].add(nid)
    degree = {nid: len(s) for nid, s in neighbors.items()}
    maxdeg = max(degree.values()) or 1
    connectivity = {
        nid: {"degree": degree[nid], "score": round(degree[nid] / maxdeg, 4),
              "neighbors": sorted(neighbors[nid])}
        for nid in nodes
    }
    (SIG / "connectivity.json").write_text(json.dumps({
        "method": "undirected degree centrality over affects/uses edges; score = degree / maxdegree",
        "max_degree": maxdeg, "nodes": connectivity}, indent=2, ensure_ascii=False),
        encoding="utf-8")

    audience = {
        nid: {"audience_breadth": n["audience_breadth"],
              "score": audience_score(n["audience_breadth"])}
        for nid, n in nodes.items()
    }
    (SIG / "audience.json").write_text(json.dumps({
        "method": "lookup: everyone=1.0, most=0.65, niche=0.30, role-specific=0.40",
        "nodes": audience}, indent=2, ensure_ascii=False), encoding="utf-8")

    # quick top-degree sanity print
    top = sorted(degree.items(), key=lambda kv: -kv[1])[:12]
    print(json.dumps({"nodes": len(nodes), "max_degree": maxdeg,
                      "top_connectivity": top}, indent=2))


if __name__ == "__main__":
    main()
