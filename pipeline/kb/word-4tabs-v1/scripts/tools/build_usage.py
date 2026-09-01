"""Step 4 signal 3 — map the web-usage research (priority/signals/usage_research_raw.json,
one entry per capability NAME with tier + claim + source) onto node ids, producing
priority/signals/usage.json keyed by node id.

Matching: normalized-name match (casefold, strip punctuation and trailing parentheticals)
against sub-feature node names, plus an explicit ALIAS table for capabilities the research
named differently from our node names (mostly contextual controls). Nodes with no research
match simply carry no web signal — the design allows that (signals 1+2 carry them); we report
the unmatched set so coverage is auditable. Every emitted entry keeps its claim + source.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

KB = common.APP_KB
SIG = KB / "priority" / "signals"


def norm(s):
    s = s.lower()
    s = re.sub(r"^[^:]{3,40}:\s*", "", s)          # drop a "Picture Format:" / "Chart Design:" prefix
    s = re.sub(r"\([^)]*\)", "", s)               # drop parentheticals
    s = s.replace("&", "and")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# research capability (normalized) -> node id, where names differ
ALIAS = {
    "select select all select objects": "subfeature:select",
    "clear formatting": "subfeature:clear-formatting",
    "font dialog": "subfeature:font-dialog",
    "paragraph dialog": "subfeature:paragraph-dialog",
    "office clipboard pane": "subfeature:office-clipboard",
    "font typeface choice": "subfeature:font",
    "grow shrink font": "subfeature:font-size-increase",
    "increase decrease indent": "subfeature:indent-increase",
    "align left center right justify": "subfeature:align-left",
    "line and paragraph spacing": "subfeature:line-spacing",
    "quick styles gallery": "subfeature:quick-styles",
    "styles pane": "subfeature:styles-pane",
    "show hide paragraph marks": "subfeature:paragraph-marks",
    "sort paragraphs": "subfeature:sort",
    "sort": "subfeature:sort",
    "insert table": "subfeature:table-insert",
    "insert pictures": "subfeature:insert-pictures",
    "3d models": "subfeature:insert-3d-models",
    "smartart": "subfeature:smart-art-insert",
    "chart": "subfeature:chart-insert",
    "screenshot": "subfeature:screenshot-insert",
    "online videos": "subfeature:online-videos-insert",
    "link hyperlink": "subfeature:insert-link",
    "cross reference": "subfeature:cross-reference-insert",
    "comment": "subfeature:insert-new-comment",
    "page number": "subfeature:page-number-insert",
    "text box": "subfeature:text-box-insert",
    "quick parts": "subfeature:quick-parts-insert",
    "wordart": "subfeature:word-art-insert",
    "drop cap": "subfeature:drop-cap-insert",
    "signature line": "subfeature:signature-line-insert",
    "date and time": "subfeature:date-and-time-insert",
    "object ole": "subfeature:object-insert",
    "equation": "subfeature:equation-insert-gallery",
    "symbol": "subfeature:symbol-insert",
    "cover page": "subfeature:cover-page-insert",
    "blank page": "subfeature:blank-page-insert",
    "page break": "subfeature:page-break-insert",
    "bookmark": "subfeature:bookmark-insert",
    "header": "subfeature:header-insert",
    "footer": "subfeature:footer-insert",
    "icons": "subfeature:icon-insert",
    "shapes": "subfeature:shapes-insert",
    # ---- table editing (Table Design/Layout) ----
    "table styles gallery": "subfeature:table-styles",
    "header row banded rows style options": "subfeature:table-style-options",
    "table shading": "subfeature:table-shading",
    "table borders": "subfeature:table-borders",
    "border painter": "subfeature:table-borders",
    "select table parts": "subfeature:table-select",
    "view gridlines": "subfeature:table-view-gridlines",
    "table properties": "subfeature:table-properties",
    "draw table": "subfeature:table-draw",
    "eraser": "subfeature:table-eraser",
    "delete rows columns table": "subfeature:table-delete",
    "insert rows above below": "subfeature:table-insert-rows",
    "insert columns left right": "subfeature:table-insert-columns",
    "merge cells": "subfeature:table-merge-cells",
    "split cells": "subfeature:table-split-cells",
    "split table": "subfeature:table-split-table",
    "autofit": "subfeature:table-autofit",
    "cell size height width": "subfeature:table-cell-size",
    "text alignment in cells": "subfeature:table-cell-alignment",
    "text direction": "subfeature:table-text-direction",
    "cell margins": "subfeature:table-cell-margins",
    "sort table": "subfeature:sort",
    "repeat header rows": "subfeature:table-repeat-header",
    "convert table to text": "subfeature:table-convert-to-text",
    "formula in table": "subfeature:table-formula",
    "formula": "subfeature:table-formula",
    # ---- object formatting ----
    "remove background": "subfeature:picture-remove-background",
    "corrections brightness sharpen": "subfeature:picture-corrections",
    "corrections": "subfeature:picture-corrections",
    "color recolor": "subfeature:picture-color",
    "artistic effects": "subfeature:picture-artistic-effects",
    "transparency": "subfeature:picture-transparency",
    "compress pictures": "subfeature:picture-compress",
    "change picture": "subfeature:picture-change",
    "reset picture": "subfeature:picture-reset",
    "picture styles gallery": "subfeature:picture-style-gallery",
    "picture styles": "subfeature:picture-style-gallery",
    "picture border": "subfeature:picture-border",
    "picture effects": "subfeature:picture-effects",
    "picture layout": "subfeature:picture-convert-to-smartart",
    "alt text": "subfeature:object-alt-text",
    "wrap text": "subfeature:object-text-wrap",
    "position": "subfeature:object-position",
    "bring forward send backward": "subfeature:object-reorder",
    "crop": "subfeature:picture-crop",
    "picture height width": "subfeature:object-size",
    "edit shape": "subfeature:shape-edit",
    "shape styles": "subfeature:shape-style-gallery",
    "shape fill": "subfeature:shape-fill",
    "shape outline": "subfeature:shape-outline",
    "shape effects": "subfeature:shape-effects",
    "align": "subfeature:object-align",
    "align objects": "subfeature:object-align",
    "group": "subfeature:object-group",
    "group objects": "subfeature:object-group",
    "rotate": "subfeature:object-rotate",
    "rotate objects": "subfeature:object-rotate",
    "selection pane": "subfeature:object-selection-pane",
    "add chart element": "subfeature:chart-add-element",
    "quick layout": "subfeature:chart-quick-layout",
    "change colors": "subfeature:chart-change-colors",
    "chart styles": "subfeature:chart-style",
    "switch row column": "subfeature:chart-switch-row-column",
    "select data": "subfeature:chart-edit-data",
    "edit data": "subfeature:chart-edit-data",
    "refresh data": "subfeature:chart-edit-data",
    "change chart type": "subfeature:chart-change-type",
    "add shape": "subfeature:smartart-add-shape",
    "add bullet": "subfeature:smartart-add-bullet",
    "text pane": "subfeature:smartart-text-pane",
    "promote demote": "subfeature:smartart-promote-demote",
    "change layout": "subfeature:smartart-layout",
    "smartart styles": "subfeature:smartart-style",
    "reset graphic": "subfeature:smartart-reset",
    "professional linear format": "subfeature:equation-conversions",
    "ink equation": "subfeature:equation-ink",
    "equation symbols": "subfeature:equation-symbols",
    "fraction": "subfeature:equation-structures",
    "script": "subfeature:equation-structures",
    "radical": "subfeature:equation-structures",
    "integral": "subfeature:equation-structures",
    "large operator": "subfeature:equation-structures",
    "bracket": "subfeature:equation-structures",
    "function": "subfeature:equation-structures",
    "accent": "subfeature:equation-structures",
    "limit": "subfeature:equation-structures",
    "operator": "subfeature:equation-structures",
    "matrix": "subfeature:equation-structures",
    "text fill outline effects for text in shapes": "subfeature:wordart-text-effects",
    "recolor": "subfeature:graphics-color",
    "convert to shape": "subfeature:graphics-convert-to-shape",
    "graphics styles": "subfeature:graphics-style-gallery",
    "add chart element": "subfeature:chart-add-element",
    "format selection": "subfeature:chart-format-selection",
    "text direction": "subfeature:table-text-direction",
    "different first page": "subfeature:hf-options",
    "different odd even pages": "subfeature:hf-options",
    "document info": "subfeature:hf-document-info",
    "go to header go to footer": "subfeature:hf-navigate",
    "previous next section": "subfeature:hf-navigate",
    "link to previous": "subfeature:hf-link-to-previous",
    "close header and footer": "subfeature:hf-close",
    "picture in header": "subfeature:insert-pictures",
    "quick parts in header": "subfeature:quick-parts-insert",
    # ---- Design + Layout (word-4tabs-v1) ----
    "margins": "subfeature:page-margins",
    "orientation": "subfeature:page-orientation",
    "size": "subfeature:page-size",
    "columns": "subfeature:page-columns",
    "breaks": "subfeature:breaks",
    "line numbers": "subfeature:line-numbers",
    "hyphenation": "subfeature:hyphenation",
    "page setup": "subfeature:page-setup-dialog",
    "indent left": "subfeature:indent-left",
    "indent right": "subfeature:indent-right",
    "spacing before": "subfeature:spacing-before",
    "spacing after": "subfeature:spacing-after",
    "themes": "subfeature:themes",
    "style set": "subfeature:style-set",
    "theme colors": "subfeature:theme-colors",
    "theme fonts": "subfeature:theme-fonts",
    "paragraph spacing": "subfeature:paragraph-spacing-set",
    "theme effects": "subfeature:theme-effects",
    "set as default": "subfeature:set-as-default",
    "watermark": "subfeature:watermark",
    "page color": "subfeature:page-color",
    "page borders": "subfeature:page-borders",
}
# research tiers stand for whole clusters; when several research rows map to one node, keep
# the strongest tier (usage is a ceiling signal).
TIER_RANK = {"very-high": 5, "high": 4, "medium": 3, "low": 2, "rare": 1}


def main():
    raw = json.loads((SIG / "usage_research_raw.json").read_text(encoding="utf-8"))
    ffiles = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((KB / "features").glob("*.json"))]
    subs = [s for ff in ffiles for s in ff["subfeatures"]]
    name_to_id = {norm(s["name"]): s["id"] for s in subs}
    id_set = {s["id"] for s in subs}

    nodes = {}
    unmatched_research = []
    for e in raw["entries"]:
        cap = norm(e["capability"])
        nid = ALIAS.get(cap) or name_to_id.get(cap)
        if not nid or nid not in id_set:
            unmatched_research.append(e["capability"])
            continue
        entry = {"tier": e["tier"], "claim": e["claim"], "source": e["source"]}
        prev = nodes.get(nid)
        if prev is None or TIER_RANK[e["tier"]] > TIER_RANK[prev["tier"]]:
            nodes[nid] = entry

    SIG.mkdir(parents=True, exist_ok=True)
    (SIG / "usage.json").write_text(json.dumps({
        "method": "web-research usage tiers mapped to node ids (normalized-name + alias); "
                  "strongest tier kept when several research rows map to one node; nodes with "
                  "no web evidence carry no entry (signals 1+2 carry them)",
        "nodes": nodes}, indent=2, ensure_ascii=False), encoding="utf-8")

    covered = sorted(nodes)
    uncovered = sorted(id_set - set(nodes))
    print(json.dumps({"research_entries": len(raw["entries"]),
                      "nodes_mapped": len(nodes),
                      "nodes_uncovered": len(uncovered),
                      "unmatched_research_sample": unmatched_research[:15]}, indent=2))
    print("\nUNCOVERED NODES (no web signal — signals 1+2 carry):")
    for u in uncovered:
        print("  ", u)


if __name__ == "__main__":
    main()
