"""Step 5 — harvest the keyboard trigger surface into the shortcut registry.

The registry is the source of truth for keys (design). Every binding carries context (when),
effect (how it acts), exactly one action marker (triggers/opens), and provenance. Built from
the subfeature nodes' shortcut fields. Provenance: most shortcuts came from live UIA
AcceleratorKey/tooltips; three well-known Insert-tab shortcuts absent from UIA (Ctrl+K,
Ctrl+Alt+M, Alt+=) are docs-sourced and carry ["docs"] — weaker evidence by design.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB

CTX_FORMAT = "editing text — applies to the selection or at the cursor"
CTX_PARA = "editing text — applies to the current paragraph(s)"
CTX_DOC = "document has focus"
CONTEXT = {
    "subfeature:bold": CTX_FORMAT, "subfeature:italic": CTX_FORMAT,
    "subfeature:underline-gallery": CTX_FORMAT, "subfeature:subscript": CTX_FORMAT,
    "subfeature:superscript": CTX_FORMAT, "subfeature:font-size-increase": CTX_FORMAT,
    "subfeature:font-size-decrease": CTX_FORMAT, "subfeature:font-dialog": CTX_FORMAT,
    "subfeature:cut": CTX_DOC, "subfeature:copy": CTX_DOC, "subfeature:paste": CTX_DOC,
    "subfeature:format-painter": CTX_DOC,
    "subfeature:align-left": CTX_PARA, "subfeature:align-center": CTX_PARA,
    "subfeature:align-right": CTX_PARA, "subfeature:align-justify": CTX_PARA,
    "subfeature:paragraph-marks": "document has focus (toggles a view setting)",
    "subfeature:find": CTX_DOC, "subfeature:replace": CTX_DOC,
    "subfeature:styles-pane": CTX_DOC,
    "subfeature:page-break-insert": "editing text — inserts at the cursor position",
    "subfeature:insert-link": "text or object selected (the link wraps the selection)",
    "subfeature:insert-new-comment": "text selected or cursor placed (anchors the comment)",
    "subfeature:equation-insert-gallery": "editing text — inserts a math zone at the cursor",
}
DOCS_SOURCED = {"subfeature:insert-link", "subfeature:insert-new-comment",
                "subfeature:equation-insert-gallery"}


def main():
    subs = [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(KB.glob("subfeatures/**/*.json"))]
    el_marker = {}
    for rid in ("ribbon-home", "ribbon-insert"):
        ribbon = json.loads((KB / "ui" / f"{rid}.json").read_text(encoding="utf-8"))
        for e in ribbon["children"]:
            if e.get("id"):
                el_marker[e["id"]] = ("triggers", e["triggers"]) if e.get("triggers") else \
                                     (("opens", e["opens"]) if e.get("opens")
                                      else ("unexplored", None))
    writer = common.get_writer()
    run_id = common.make_run_id() + "-shortcuts"
    jrnl = common.get_journal(run_id)

    entries = {}
    for s in subs:
        sc = s.get("shortcut")
        if not sc:
            continue
        primary = next((tp["path"][-1] for tp in s.get("trigger_paths", [])
                        if tp.get("kind") == "mouse" and tp.get("path")), None)
        kind, target = el_marker.get(primary, ("triggers", s["id"]))
        if kind == "unexplored" or target is None:
            kind, target = "triggers", s["id"]
        combos = [c.strip() for c in sc.split(",")]
        for i, keys in enumerate(combos):
            binding = {
                "context": CONTEXT.get(s["id"], CTX_DOC),
                "effect": s["what_it_does"],
                "source": (["docs"] if s["id"] in DOCS_SOURCED
                           else ["uia-accelerator", "tooltip"]),
                kind: target,
            }
            if s["id"] == "subfeature:format-painter":
                binding["effect"] = ("copy formatting from the selection" if i == 0
                                     else "apply the copied formatting to the selection")
            entries.setdefault(keys, []).append(binding)

    written = []
    for keys, bindings in sorted(entries.items()):
        writer.write_shortcut({"keys": keys, "bindings": bindings})
        written.append(keys)
    jrnl.append(common.journal_event(actor="stage5.shortcuts", action="harvest",
                target="shortcuts/*", outcome="ok", data={"keys": written}))
    print(json.dumps({"shortcut_entries": len(written), "keys": written}, indent=2))


if __name__ == "__main__":
    main()
