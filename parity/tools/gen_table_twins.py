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
    "Style apply through the gallery flyout changes the doc. (Painted colors are judged by the VISUAL axis L4 side-by-side.)",
    INSERT_33 + [
        {"do": "activateTab", "tab": "table-design"},
        {"do": "openDropdown", "cmd": "tblStyles"},
        {"do": "clickItem", "match": "Grid Table 4 Accent 1"},
        {"expect": "docChanged"},
    ]))

TWINS.append(twin("tb-shading-cell",
    "Shading swatch #1 (#FFF2CC) paints the caret cell's background ON SCREEN — right cell, right color.",
    INSERT_33 + [
        {"do": "clickCellPainted", "index": 0},
        {"do": "activateTab", "tab": "table-design"},
        {"do": "openDropdown", "cmd": "tblShading"},
        {"do": "clickShadeSwatch", "index": 0},
        {"expect": "paintedCellBg", "index": 0, "anyOf": ["rgb(255,242,204)"]},
    ]))

TWINS.append(twin("tb-borders-all-cell",
    "THE BORDER-COLLAPSE INSTRUMENT: All Borders on the MIDDLE cell must paint ALL FOUR edges on screen — shared bottom/right edges must not be swallowed by the neighbor's thinner border (archive bug 47488c0 class).",
    INSERT_33 + [
        {"do": "clickCellPainted", "index": 4},
        {"do": "activateTab", "tab": "table-design"},
        {"do": "openDropdown", "cmd": "tblBorders"},
        {"do": "clickItem", "match": "All Borders"},
        {"expect": "paintedCellBorder", "index": 4, "edge": "top", "minPx": 1},
        {"expect": "paintedCellBorder", "index": 4, "edge": "left", "minPx": 1},
        {"expect": "paintedCellBorder", "index": 4, "edge": "bottom", "minPx": 1},
        {"expect": "paintedCellBorder", "index": 4, "edge": "right", "minPx": 1},
    ]))

TWINS.append(twin("tb-borders-none-cell",
    "No Border on the middle cell must REMOVE the painted solid line (Word writes per-side nil). The clone's clear-to-{} leaves the style border painted — expected FAIL until fixed.",
    INSERT_33 + [
        {"do": "clickCellPainted", "index": 4},
        {"do": "activateTab", "tab": "table-design"},
        {"do": "openDropdown", "cmd": "tblBorders"},
        {"do": "clickItem", "match": "No Border"},
        {"expect": "paintedCellBorderAbsent", "index": 4, "edge": "top"},
        {"expect": "paintedCellBorderAbsent", "index": 4, "edge": "left"},
    ]))

for tid, cmd in [("tb-insert-above", "tblInsertAbove"), ("tb-insert-below", "tblInsertBelow"),
                 ("tb-insert-left", "tblInsertLeft"), ("tb-insert-right", "tblInsertRight")]:
    TWINS.append(twin(tid,
        f"{cmd} from the ribbon adds a row/column: 9 -> 12 painted cells, caret stays in the table.",
        INSERT_33 + [
            {"do": "clickCellPainted", "index": 0},
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
            {"do": "clickCellPainted", "index": 0},
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
        {"do": "clickCellPainted", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "clickCmd", "cmd": "tblSplitCell"},
        {"expect": "dialogOpen"},
    ]))

TWINS.append(twin("tb-split-table",
    "Split Table with the caret in row 2 paints TWO separate tables.",
    INSERT_33 + [
        {"do": "clickCellPainted", "index": 3},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "clickCmd", "cmd": "tblSplitTable"},
        {"expect": "paintedTableCount", "equals": 2},
    ]))

TWINS.append(twin("tb-autofit-window",
    "AutoFit Window via the dropdown changes the model.",
    INSERT_33 + [
        {"do": "clickCellPainted", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "openDropdown", "cmd": "tblAutoFit"},
        {"do": "clickItem", "match": "AutoFit Window"},
        {"expect": "docChanged"},
    ]))

TWINS.append(twin("tb-rowheight-05in",
    "Row Height 0.5\" preset: the caret row's painted height reaches >=40px (0.5in = 48px at 100% zoom; slack for zoom rounding).",
    INSERT_33 + [
        {"do": "clickCellPainted", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "openDropdown", "cmd": "tblRowHeight"},
        {"do": "clickItem", "match": "0\\.5"},
        {"expect": "paintedCellMinHeight", "index": 0, "minPx": 40},
    ]))

TWINS.append(twin("tb-cellalign-bottomright",
    "Align Bottom (the clone's nearest control to Word's Align Bottom Right): the caret cell paints vertical-align bottom.",
    INSERT_33 + [
        {"do": "clickCellPainted", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "clickCmd", "cmd": "tblVAlignBottom"},
        {"expect": "paintedCellStyleIs", "index": 0, "prop": "vertical-align", "anyOf": ["bottom"]},
    ]))

TWINS.append(twin("tb-textdir",
    "Text Direction first click paints vertical writing in the caret cell (tbRl -> CSS vertical-rl). Word's full 3-state cycle is a ❓ recording item.",
    INSERT_33 + [
        {"do": "clickCellPainted", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "clickCmd", "cmd": "tblTextDir"},
        {"expect": "paintedCellStyleIs", "index": 0, "prop": "writing-mode", "anyOf": ["vertical-rl"]},
    ]))

TWINS.append(twin("tb-align-center",
    "Table Align Center from the (clone-only) Design alignment group changes the model.",
    INSERT_33 + [
        {"do": "clickCellPainted", "index": 0},
        {"do": "activateTab", "tab": "table-design"},
        {"do": "clickCmd", "cmd": "tblAlignCenter"},
        {"expect": "docChanged"},
    ]))

TWINS.append(twin("tb-indent-05in",
    "Table Indent 0.5\" preset changes the model.",
    INSERT_33 + [
        {"do": "clickCellPainted", "index": 0},
        {"do": "activateTab", "tab": "table-design"},
        {"do": "openDropdown", "cmd": "tblIndent"},
        {"do": "clickItem", "match": "0\\.5"},
        {"expect": "docChanged"},
    ]))

TWINS.append(twin("tb-dist-rows",
    "Distribute Rows after a 1\" row height: heights equalize (doc changes).",
    INSERT_33 + [
        {"do": "clickCellPainted", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "openDropdown", "cmd": "tblRowHeight"},
        {"do": "clickItem", "match": "1\\.0"},
        {"do": "clickCmd", "cmd": "tblDistRows"},
        {"expect": "docChanged"},
    ]))

TWINS.append(twin("tb-dist-cols",
    "Distribute Columns after a 2.5\" column width: widths equalize (doc changes).",
    INSERT_33 + [
        {"do": "clickCellPainted", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "openDropdown", "cmd": "tblColWidth"},
        {"do": "clickItem", "match": "2\\.5"},
        {"do": "clickCmd", "cmd": "tblDistCols"},
        {"expect": "docChanged"},
    ]))

TWINS.append(twin("tb-totext-tab",
    "Convert to Text removes the painted table.",
    INSERT_33 + [
        {"do": "clickCellPainted", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "clickCmd", "cmd": "tblToText"},
        {"expect": "paintedCellCount", "equals": 0},
    ]))

TWINS.append(twin("tb-repeatheader",
    "The clone's 'Header Row' button changes the model. (Its SEMANTICS diverge from Word's Repeat Header Rows — the OOXML axis flags that; this twin only proves the click acts.)",
    INSERT_33 + [
        {"do": "clickCellPainted", "index": 0},
        {"do": "activateTab", "tab": "table-layout"},
        {"do": "clickCmd", "cmd": "tblHeaderRow"},
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
