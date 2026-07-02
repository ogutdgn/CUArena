#!/usr/bin/env python3
"""Micro-twin generator (rubric D6.2) — every UI-REACHABLE Tables OOXML task gets a
live-behavior twin: drive the SAME action through the REAL ribbon UI (clicks, not API
calls), then verify the LIVE PAINT/state. The instrument for the "file is clean but the
screen is wrong" class (the border-collapse lesson). Unreachable actions have no UI to
drive — STRUCTURE/SCORECARD cover their absence, so they get no twin.

Run:  python parity/tools/gen_table_twins.py   (idempotent; writes parity/behavior/cards/twin-tb-*.json)
"""
import json
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.join(os.path.dirname(TOOLS), "behavior", "cards")

# Shared step blocks
INSERT_33 = [
    {"do": "setupText", "text": "Twin base."},
    {"do": "activateTab", "tab": "insert"},
    {"do": "openDropdown", "cmd": "table"},
    {"do": "gridPick", "rows": 3, "cols": 3},
]


def twin(task_id, note, steps):
    return {
        "id": f"twin/{task_id}",
        "kind": "micro-twin",
        "feature": "Table",
        "signedOff": "generated",
        "ooxmlTask": task_id,
        "note": note,
        "steps": steps,
    }


TWINS = []

TWINS.append(twin("table",
    "Grid insert paints a 3x3 and the caret is inside it.",
    INSERT_33 + [
        {"expect": "paintedCellCount", "equals": 9},
        {"expect": "caretInTable"},
    ]))

TWINS.append(twin("tb-style-grid4a1",
    "Style apply through the 030 tile gallery (More grid) changes the doc. (Painted colors are judged by the VISUAL axis L4 side-by-side.)",
    INSERT_33 + [
        {"do": "activateTab", "tab": "table-design"},
        {"do": "clickSelector", "sel": '.ribbon-panel[data-tab="table-design"] .rgallery-more, .ribbon-panel.active .rgallery-more', "waitMs": 400},
        {"do": "clickSelector", "sel": '.flyout .tblstyle-cell[data-style="GridTable4-Accent1"]', "waitMs": 400},
        {"expect": "docChanged"},
    ]))

TWINS.append(twin("tb-shading-cell",
    "Shading swatch #1 (#FFF2CC) paints the caret cell's background ON SCREEN — right cell, right color.",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 0},
        {"do": "activateTab", "tab": "table-design"},
        {"do": "openDropdown", "cmd": "tblShading"},
        {"do": "clickShadeSwatch", "index": 0},
        {"expect": "paintedCellBg", "index": 0, "anyOf": ["rgb(255,242,204)"]},
    ]))

TWINS.append(twin("tb-borders-all-cell",
    "THE BORDER-COLLAPSE INSTRUMENT (collapse-aware, reads the PAINTER not the hidden model host): a THICK RED border on the MIDDLE cell must paint all four VISUAL edges. The painter draws each cell's top+left only, so the middle cell's bottom shows as the below-cell's TOP and its right as the right-cell's LEFT — >=2 red Top edges AND >=2 red Left edges proves the collapse pre-pass (archive 47488c0) propagated the thick edge to neighbors. Drives the real tableSetCellBorders write path with an explicit thick-red spec (thin default black is indistinguishable from the grid).",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 4},
        {"do": "setCellBorders", "spec": {"top": {"val": "single", "color": "FF0000", "size": 24}, "bottom": {"val": "single", "color": "FF0000", "size": 24}, "left": {"val": "single", "color": "FF0000", "size": 24}, "right": {"val": "single", "color": "FF0000", "size": 24}}},
        {"expect": "coloredEdgeCount", "side": "top", "color": "255,\s*0,\s*0", "minPx": 2, "min": 2},
        {"expect": "coloredEdgeCount", "side": "left", "color": "255,\s*0,\s*0", "minPx": 2, "min": 2},
    ]))

TWINS.append(twin("tb-borders-none-cell",
    "No Border must REMOVE the painted line. Apply a thick RED border to the middle cell (>=2 red edges paint), THEN No Border via the real Borders dropdown (per-side nil) — the red edges must all vanish. Reads the PAINTER (collapse-aware). The clone's clear-to-{} left the style border; the 032 nil No-Border fixes it.",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 4},
        {"do": "setCellBorders", "spec": {"top": {"val": "single", "color": "FF0000", "size": 24}, "bottom": {"val": "single", "color": "FF0000", "size": 24}, "left": {"val": "single", "color": "FF0000", "size": 24}, "right": {"val": "single", "color": "FF0000", "size": 24}}},
        {"expect": "coloredEdgeCount", "side": "top", "color": "255,\s*0,\s*0", "minPx": 2, "min": 2},
        {"do": "activateTab", "tab": "table-design"},
        {"do": "openDropdown", "cmd": "tblBorders"},
        {"do": "clickItem", "match": "No Border"},
        {"expect": "coloredEdgeGone", "color": "255,\s*0,\s*0", "minPx": 2},
    ]))

for tid, cmd in [("tb-insert-above", "tblInsertAbove"), ("tb-insert-below", "tblInsertBelow"),
                 ("tb-insert-left", "tblInsertLeft"), ("tb-insert-right", "tblInsertRight")]:
    TWINS.append(twin(tid,
        f"{cmd} from the ribbon adds a row/column: 9 -> 12 painted cells, caret stays in the table.",
        INSERT_33 + [
            {"do": "caretIntoCellModel", "index": 0},
            {"do": "activateTab", "tab": "table-layout"},
            {"do": "clickCmd", "cmd": cmd},
            {"expect": "paintedCellCount", "equals": 12},
            {"expect": "caretInTable"},
        ]))

for tid, cmd, count in [("tb-delete-row", "tblDeleteRow", 6), ("tb-delete-col", "tblDeleteColumn", 6),
                        ("tb-delete-table", "tblDeleteTable", 0)]:
    TWINS.append(twin(tid,
        f"{cmd} from the ribbon: painted cells 9 -> {count}.",
        INSERT_33 + [
            {"do": "caretIntoCellModel", "index": 0},
            {"do": "activateTab", "tab": "table-layout"},
            {"do": "clickCmd", "cmd": cmd},
            {"expect": "paintedCellCount", "equals": count},
        ]))

TWINS.append(twin("tb-merge-firstrow2",
    "Merge the first-row pair: 9 -> 8 painted cells. (Cell range via the programmatic fallback until synthetic shift-click drives CellSelection.)",
    INSERT_33 + [
        {"do": "selectCellRange"},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "clickCmd", "cmd": "tblMerge"},
        {"expect": "paintedCellCount", "equals": 8},
    ]))

TWINS.append(twin("tb-split-cell",
    "Split Cells on a PLAIN cell: Word opens the Split Cells dialog (official-inventory ellipsis label). The clone's direct/no-op split MUST fail this — the split-dialog gap live.",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "clickCmd", "cmd": "tblSplitCell"},
        {"expect": "dialogOpen"},
    ]))

TWINS.append(twin("tb-split-table",
    "Split Table with the caret in row 2 paints TWO separate tables.",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 3},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "clickCmd", "cmd": "tblSplitTable"},
        {"expect": "paintedTableCount", "equals": 2},
    ]))

TWINS.append(twin("tb-autofit-window",
    "AutoFit Window via the dropdown changes the model.",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "openDropdown", "cmd": "tblAutoFit"},
        {"do": "clickItem", "match": "AutoFit Window"},
        {"expect": "docChanged"},
    ]))

TWINS.append(twin("tb-rowheight-05in",
    "Row Height 0.5\" preset: the caret row's painted height reaches >=40px (0.5in = 48px at 100% zoom; slack for zoom rounding).",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "openDropdown", "cmd": "tblRowHeight"},
        {"do": "clickItem", "match": "0\\.5"},
        {"expect": "paintedCellMinHeight", "index": 0, "minPx": 40},
    ]))

TWINS.append(twin("tb-cellalign-bottomright",
    "Align Bottom (the clone's nearest control to Word's Align Bottom Right): the caret cell paints vertical-align bottom.",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "clickCmd", "cmd": "tblVAlignBottom"},
        {"expect": "paintedCellStyleIs", "index": 0, "prop": "vertical-align", "anyOf": ["bottom"]},
    ]))

TWINS.append(twin("tb-textdir",
    "Text Direction first click paints vertical writing in the caret cell (tbRl -> CSS vertical-rl). Word's full 3-state cycle is a ❓ recording item.",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "clickCmd", "cmd": "tblTextDir"},
        {"expect": "paintedCellStyleIs", "index": 0, "prop": "writing-mode", "anyOf": ["vertical-rl"]},
    ]))

TWINS.append(twin("tb-align-center",
    "Table Align Center from the (clone-only) Design alignment group changes the model.",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 0},
        {"do": "activateTab", "tab": "table-design"},
        {"do": "clickCmd", "cmd": "tblAlignCenter"},
        {"expect": "docChanged"},
    ]))

TWINS.append(twin("tb-indent-05in",
    "Table Indent 0.5\" preset changes the model.",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 0},
        {"do": "activateTab", "tab": "table-design"},
        {"do": "openDropdown", "cmd": "tblIndent"},
        {"do": "clickItem", "match": "0\\.5"},
        {"expect": "docChanged"},
    ]))

TWINS.append(twin("tb-dist-rows",
    "Distribute Rows after a 1\" row height: heights equalize (doc changes).",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "openDropdown", "cmd": "tblRowHeight"},
        {"do": "clickItem", "match": "1\\.0"},
        {"do": "clickCmd", "cmd": "tblDistRows"},
        {"expect": "docChanged"},
    ]))

TWINS.append(twin("tb-dist-cols",
    "Distribute Columns after a 2.5\" column width: widths equalize (doc changes).",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "openDropdown", "cmd": "tblColWidth"},
        {"do": "clickItem", "match": "2\\.5"},
        {"do": "clickCmd", "cmd": "tblDistCols"},
        {"expect": "docChanged"},
    ]))

TWINS.append(twin("tb-totext-tab",
    "Convert to Text removes the painted table.",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "clickCmd", "cmd": "tblToText"},
        {"expect": "paintedCellCount", "equals": 0},
    ]))

TWINS.append(twin("tb-repeatheader",
    "The clone's 'Header Row' button changes the model. (Its SEMANTICS diverge from Word's Repeat Header Rows — the OOXML axis flags that; this twin only proves the click acts.)",
    INSERT_33 + [
        {"do": "caretIntoCellModel", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "clickCmd", "cmd": "tblHeaderRow"},
        {"expect": "docChanged"},
    ]))

# Spec 031: Table Style Options toggle twins. Apply GT4A1 through the 030 tile gallery so the table is
# STYLED, then click the checkbox INPUT (stable [data-cmd] selector) on the Table Design tab and assert
# the doc changed (the tblLook flag flip + cnfStyle re-stamp is a real transaction). (The exported
# stamp/val correctness is the OOXML axis' job — this twin only proves the checkbox click acts on-screen.)
STYLE_VIA_GALLERY = INSERT_33 + [
    {"do": "activateTab", "tab": "table-design"},
    {"do": "clickSelector", "sel": '.ribbon-panel[data-tab="table-design"] .rgallery-more, .ribbon-panel.active .rgallery-more', "waitMs": 400},
    {"do": "clickSelector", "sel": '.flyout .tblstyle-cell[data-style="GridTable4-Accent1"]', "waitMs": 400},
]
for tid, cmd in [
    ("tb-styleopt-headerrow-off", "tblStyleHeaderRow"),
    ("tb-styleopt-totalrow-on", "tblStyleTotalRow"),
    ("tb-styleopt-bandedrows-off", "tblStyleBandedRows"),
    ("tb-styleopt-firstcol-off", "tblStyleFirstCol"),
    ("tb-styleopt-lastcol-on", "tblStyleLastCol"),
    ("tb-styleopt-bandedcols-on", "tblStyleBandedCols"),
]:
    TWINS.append(twin(tid,
        f"Toggle the {cmd} checkbox on a styled (GT4A1) table: the click flips the tblLook flag + re-stamps cnfStyle (doc changes). Stamp/val correctness is judged by the OOXML axis.",
        STYLE_VIA_GALLERY + [
            {"do": "activateTab", "tab": "table-design"},
            {"do": "clickSelector", "sel": 'input[data-cmd="' + cmd + '"]', "waitMs": 300},
            {"expect": "docChanged"},
        ]))

TWINS.append(twin("tb-quicktable-calendar",
    "Quick Tables > Calendar paints the clone's 6x7 preset (42 cells). Word inserts the 'Calendar 1' building block — content fidelity is the OOXML task's job.",
    [
        {"do": "setupText", "text": "Quick table twin."},
        {"do": "activateTab", "tab": "insert"},
        {"do": "openDropdown", "cmd": "table"},
        {"do": "clickItem", "match": "Quick Tables"},
        {"do": "clickItem", "match": "Calendar"},
        {"expect": "paintedCellCount", "equals": 42},
    ]))


def main():
    os.makedirs(CARDS, exist_ok=True)
    for t in TWINS:
        path = os.path.join(CARDS, "twin-" + t["ooxmlTask"] + ".json")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(t, f, indent=2, ensure_ascii=False)
            f.write("\n")
    print(f"generated {len(TWINS)} micro-twin cards into {CARDS}")


if __name__ == "__main__":
    main()
