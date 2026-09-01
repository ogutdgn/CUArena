"""Generate kb/word/overview.md — the human-readable KB summary (design 'Stage 5').

A reader who knows Word should recognize the app from it: identity, the priority-ranked feature
tree, the measured skeleton, and the shortcut surface. Rebuilt from the node files each run.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import common

KB = common.APP_KB


def load(glob):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(KB.glob(glob))]


def main():
    app = json.loads((KB / "app.json").read_text(encoding="utf-8"))
    layers = json.loads((KB / "priority" / "layers.json").read_text(encoding="utf-8"))
    ranking = {r["id"]: r for r in json.loads(
        (KB / "priority" / "ranking.json").read_text(encoding="utf-8"))["ranking"]}
    features = {f["id"]: f for f in load("features/*.json")}
    subs = load("subfeatures/**/*.json")
    subs_by_f = {}
    for s in subs:
        subs_by_f.setdefault(s["parent"], []).append(s)
    containers = load("ui/*.json")
    shortcuts = load("shortcuts/*.json")
    explored_ct = sum(1 for c in containers if c.get("explored", True))

    L = []
    A = L.append
    A(f"# {app['name']} — Knowledge Base overview")
    A("")
    A(f"**Version (build):** {app['version']} · **Platform:** {app['platform']} · "
      f"**Scope of this KB:** the **Home tab** treated as the whole application.")
    A("")
    A(f"**What it is.** {app['what_is_it']}")
    A("")
    A(f"**Used for.** {app['used_for']}")
    A("")
    A(f"**Who uses it.** {app['who_uses']}")
    A("")
    A("## At a glance")
    A(f"- **{len(features)} features**, **{len(subs)} sub-features**, "
      f"**{len(containers)} UI containers** ({explored_ct} explored to depth, "
      f"{len(containers)-explored_ct} deliberate stubs), **{len(shortcuts)} keyboard shortcuts**.")
    A(f"- **Priority layers:** " + " · ".join(
        f"{k}={v}" for k, v in layers["counts"].items()))
    A("")
    A("## Skeleton (measured trigger surface)")
    A("The main window hosts the ribbon tab strip (Home is in scope; other tabs are named but "
      "unexplored). The **Home tab** face was mapped by pressing every control and classifying the "
      "measured outcome (opens a dialog/dropdown/menu/pane, or triggers a document/format action).")
    A("")
    A("## Feature tree (priority-ranked)")
    order = ["feature:clipboard", "feature:font", "feature:paragraph", "feature:styles",
             "feature:editing", "feature:voice", "feature:editor", "feature:acrobat",
             "feature:add-ins"]
    for fid in order:
        f = features.get(fid)
        if not f:
            continue
        b = " _(boundary — not pressed; documented from knowledge)_" if f.get("boundary") else ""
        A(f"### {f['name']}{b}")
        A(f"{f['what_it_does']} _(affects: {f['affects']}; audience: {f['audience_breadth']})_")
        A("")
        for s in sorted(subs_by_f.get(fid, []), key=lambda x: -ranking.get(x["id"], {}).get("combined", 0)):
            lay = ranking.get(s["id"], {}).get("layer", "P4")
            sc = f" · `{s['shortcut']}`" if s.get("shortcut") else ""
            op = f" · opens `{s['opens']}`" if s.get("opens") else ""
            star = "★" if lay in ("P0", "P1", "P2") else ""
            A(f"- **[{lay}]{star} {s['name']}**{sc} — {s['what_it_does']} _(affects: {s['affects']})_{op}")
        A("")
    A("## Keyboard shortcuts (registry)")
    for sc in sorted(shortcuts, key=lambda x: x["keys"]):
        for bnd in sc["bindings"]:
            tgt = bnd.get("triggers") or bnd.get("opens")
            A(f"- `{sc['keys']}` — {bnd['effect']} → `{tgt}` _( {bnd['context']} )_")
    A("")
    A("## How priority was decided")
    A("Every node's layer is a recorded weighted sum of three signals — connectivity (degree "
      "over the affects/uses graph), real-world usage (web-researched, evidence-cited, anchored on "
      "Microsoft CEIP telemetry), and audience breadth — cut at recorded boundaries. See "
      "`priority/JUSTIFICATION.md` and `priority/ranking.json`.")
    A("")
    A("_Generated from the node files; the append-only `journal.jsonl` reconstructs the full run._")

    (KB / "overview.md").write_text("\n".join(L), encoding="utf-8")
    print(f"overview.md written: {len(L)} lines, {len(features)} features, {len(subs)} subs, "
          f"{len(shortcuts)} shortcuts")


if __name__ == "__main__":
    main()
