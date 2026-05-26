#!/usr/bin/env python3
"""Build resources/ribbon.json — the data-driven, Word-faithful ribbon model.

The ribbon UI (src/ui/qml) is fully data-driven from the JSON this emits, so
iterating on the Word layout never touches QML (CLAUDE.md core value #2). Each
item is validated against resources/command-catalog.json (the real engine
`.uno:` surface) and, when the Fluent name list is present, its icon is
validated against the Microsoft Fluent UI System Icons set (DECISIONS D-icons).

Run from apps/writer/:  python3 tools/build_ribbon.py

Output: resources/ribbon.json  + a validation report on stderr.
Icons referenced here are downloaded/recoloured by tools/fetch_icons.py.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "resources" / "command-catalog.json"
OUT = ROOT / "resources" / "ribbon.json"
FLUENT_NAMES = Path("/tmp/fluent_names_24reg.txt")  # optional dev-time validation

# --- the curated spec -------------------------------------------------------
# item = dict(cmd, icon, [label], [size="lg"|"sm"], [toggle=True], [args=json])
# A group = (group_name, [items]). A tab = (tab_name, [groups]).
# Labels auto-pull from the catalog (mnemonic '~' + %PRODUCTNAME stripped) unless
# overridden. `toggle` items light up from STATE_CHANGED (.uno:Cmd=true).


def I(cmd, icon, label=None, size="sm", toggle=False, args=None):
    d = {"cmd": cmd, "icon": icon, "size": size}
    if label:
        d["label"] = label
    if toggle:
        d["toggle"] = True
    if args:
        d["args"] = args
    return d


SPEC = [
    ("Home", [
        ("Clipboard", [
            I(".uno:Paste", "clipboard_paste", "Paste", size="lg"),
            I(".uno:Cut", "cut", "Cut"),
            I(".uno:Copy", "copy", "Copy"),
            I(".uno:FormatPaintbrush", "paint_brush", "Format Paintbrush", toggle=True),
        ]),
        ("Undo", [
            I(".uno:Undo", "arrow_undo", "Undo"),
            I(".uno:Redo", "arrow_redo", "Redo"),
        ]),
        ("Font", [
            I(".uno:Bold", "text_bold", "Bold", toggle=True),
            I(".uno:Italic", "text_italic", "Italic", toggle=True),
            I(".uno:Underline", "text_underline", "Underline", toggle=True),
            I(".uno:Strikeout", "text_strikethrough", "Strikethrough", toggle=True),
            I(".uno:SubScript", "text_subscript", "Subscript", toggle=True),
            I(".uno:SuperScript", "text_superscript", "Superscript", toggle=True),
            I(".uno:Grow", "font_increase", "Increase Size"),
            I(".uno:Shrink", "font_decrease", "Decrease Size"),
            I(".uno:FontColor", "text_color", "Font Color"),
            I(".uno:BackColor", "highlight", "Highlight Color"),
            I(".uno:ResetAttributes", "clear_formatting", "Clear Formatting"),
        ]),
        ("Paragraph", [
            I(".uno:DefaultBullet", "text_bullet_list", "Bullet List", toggle=True),
            I(".uno:DefaultNumbering", "text_number_list_ltr", "Numbered List", toggle=True),
            I(".uno:DecrementIndent", "text_indent_decrease_ltr", "Decrease Indent"),
            I(".uno:IncrementIndent", "text_indent_increase_ltr", "Increase Indent"),
            I(".uno:LeftPara", "text_align_left", "Align Left", toggle=True),
            I(".uno:CenterPara", "text_align_center", "Center", toggle=True),
            I(".uno:RightPara", "text_align_right", "Align Right", toggle=True),
            I(".uno:JustifyPara", "text_align_justify", "Justify", toggle=True),
            I(".uno:LineSpacing", "text_line_spacing", "Line Spacing"),
        ]),
        ("Styles", [
            I(".uno:StyleApply", "text_t", "Default",
              args='{"Style":{"type":"string","value":"Default Paragraph Style"},"FamilyName":{"type":"string","value":"ParagraphStyles"}}'),
            I(".uno:StyleApply", "text_header_1", "Heading 1",
              args='{"Style":{"type":"string","value":"Heading 1"},"FamilyName":{"type":"string","value":"ParagraphStyles"}}'),
            I(".uno:StyleApply", "text_header_2", "Heading 2",
              args='{"Style":{"type":"string","value":"Heading 2"},"FamilyName":{"type":"string","value":"ParagraphStyles"}}'),
            I(".uno:StyleApply", "text_header_3", "Title",
              args='{"Style":{"type":"string","value":"Title"},"FamilyName":{"type":"string","value":"ParagraphStyles"}}'),
        ]),
        ("Editing", [
            I(".uno:SearchDialog", "search", "Find & Replace", size="lg"),
            I(".uno:SelectAll", "select_all_on", "Select All"),
        ]),
    ]),

    ("Insert", [
        ("Pages", [
            I(".uno:InsertPagebreak", "document_page_break", "Page Break", size="lg"),
        ]),
        ("Tables", [
            I(".uno:InsertTable", "table_add", "Table", size="lg"),
        ]),
        ("Illustrations", [
            I(".uno:InsertGraphic", "image_add", "Picture"),
            I(".uno:InsertObjectChart", "chart_multiple", "Chart"),
            I(".uno:InsertDraw", "shapes", "Shapes"),
        ]),
        ("Links", [
            I(".uno:HyperlinkDialog", "link", "Hyperlink"),
            I(".uno:InsertBookmark", "bookmark", "Bookmark"),
            I(".uno:InsertReferenceField", "document_link", "Cross-reference"),
        ]),
        ("Header & Footer", [
            I(".uno:InsertPageHeader", "document_header", "Header"),
            I(".uno:InsertPageFooter", "document_footer", "Footer"),
            I(".uno:InsertPageNumberField", "document_page_number", "Page Number"),
        ]),
        ("Text", [
            I(".uno:InsertTextFrame", "textbox", "Text Box"),
            I(".uno:InsertFieldCtrl", "text_field", "Field"),
            I(".uno:InsertDateField", "calendar_ltr", "Date"),
        ]),
        ("Symbols", [
            I(".uno:InsertObjectStarMath", "math_formula", "Equation"),
            I(".uno:InsertSymbol", "math_symbols", "Symbol"),
        ]),
    ]),

    ("Layout", [
        ("Page Setup", [
            I(".uno:PageDialog", "document_landscape", "Page Setup", size="lg"),
        ]),
        ("Paragraph", [
            I(".uno:ParaspaceIncrease", "arrow_expand", "Add Space"),
            I(".uno:ParaspaceDecrease", "arrow_collapse_all", "Remove Space"),
            I(".uno:IncrementIndent", "text_indent_increase_ltr", "Indent"),
            I(".uno:DecrementIndent", "text_indent_decrease_ltr", "Outdent"),
        ]),
        ("Page Background", [
            I(".uno:FormatColumns", "column_triple", "Columns"),
            I(".uno:InsertBreak", "document_page_break", "Breaks"),
        ]),
    ]),

    ("References", [
        ("Table of Contents", [
            I(".uno:InsertMultiIndex", "text_bullet_list_tree", "Table of Contents", size="lg"),
        ]),
        ("Footnotes", [
            I(".uno:InsertFootnote", "text_footnote", "Insert Footnote"),
            I(".uno:InsertEndnote", "document_endnote", "Insert Endnote"),
        ]),
        ("Captions", [
            I(".uno:InsertCaptionDialog", "text_description", "Insert Caption"),
            I(".uno:InsertIndexesEntry", "bookmark_add", "Index Entry"),
        ]),
    ]),

    ("Review", [
        ("Proofing", [
            I(".uno:SpellingAndGrammarDialog", "text_grammar_checkmark", "Spelling & Grammar", size="lg"),
            I(".uno:ThesaurusDialog", "book_question_mark", "Thesaurus"),
            I(".uno:WordCountDialog", "text_word_count", "Word Count"),
        ]),
        ("Comments", [
            I(".uno:InsertAnnotation", "comment_add", "New Comment"),
        ]),
        ("Tracking", [
            I(".uno:TrackChanges", "edit", "Record Changes", toggle=True),
            I(".uno:ShowTrackedChanges", "eye", "Show Changes", toggle=True),
        ]),
        ("Changes", [
            I(".uno:AcceptTrackedChange", "checkmark", "Accept"),
            I(".uno:RejectTrackedChange", "dismiss", "Reject"),
        ]),
    ]),

    ("View", [
        ("Views", [
            I(".uno:PrintLayout", "document_one_page", "Print Layout", toggle=True),
            I(".uno:BrowseView", "globe", "Web Layout", toggle=True),
        ]),
        ("Show", [
            I(".uno:ControlCodes", "text_paragraph", "Formatting Marks", toggle=True),
        ]),
        ("Zoom", [
            I(".uno:Zoom", "zoom_fit", "Zoom", size="lg"),
            I(".uno:ZoomPlus", "zoom_in", "Zoom In"),
            I(".uno:ZoomMinus", "zoom_out", "Zoom Out"),
        ]),
    ]),

    ("File", [
        ("File", [
            I(".uno:NewDoc", "document_add", "New", size="lg"),
            I(".uno:Open", "folder_open", "Open"),
            I(".uno:Save", "save", "Save"),
            I(".uno:SaveAs", "save_edit", "Save As"),
        ]),
        ("Print & Share", [
            I(".uno:Print", "print", "Print"),
            I(".uno:ExportToPDF", "document_pdf", "Export PDF"),
            I(".uno:CloseDoc", "dismiss_circle", "Close"),
        ]),
    ]),

    ("Help", [
        ("Help", [
            I(".uno:HelpIndex", "question_circle", "Help", size="lg"),
            I(".uno:About", "info", "About"),
        ]),
    ]),
]


def clean_label(raw: str) -> str:
    if not raw:
        return ""
    s = raw.replace("~", "").replace("%PRODUCTNAME", "Writer")
    return re.sub(r"\s+", " ", s).strip()


def main() -> int:
    catalog = json.loads(CATALOG.read_text())["commands"]
    fluent = set()
    if FLUENT_NAMES.exists():
        fluent = set(FLUENT_NAMES.read_text().split())

    missing_cmd, missing_icon, used_icons = [], [], set()
    tabs = []
    for tab_name, groups in SPEC:
        out_groups = []
        for group_name, items in groups:
            out_items = []
            for it in items:
                cmd = it["cmd"]
                meta = catalog.get(cmd)
                if meta is None:
                    missing_cmd.append((tab_name, group_name, cmd))
                label = it.get("label") or clean_label(meta["label"] if meta else cmd)
                used_icons.add(it["icon"])
                if fluent and it["icon"] not in fluent:
                    missing_icon.append((tab_name, cmd, it["icon"]))
                entry = {"cmd": cmd, "label": label, "icon": it["icon"], "size": it["size"]}
                if it.get("toggle"):
                    entry["toggle"] = True
                if it.get("args"):
                    entry["args"] = it["args"]
                out_items.append(entry)
            out_groups.append({"name": group_name, "items": out_items})
        tabs.append({"name": tab_name, "groups": out_groups})

    model = {"schemaVersion": 1, "tabs": tabs}
    OUT.write_text(json.dumps(model, indent=1) + "\n")

    n_items = sum(len(g["items"]) for t in tabs for g in t["groups"])
    print(f"wrote {OUT.relative_to(ROOT)}: {len(tabs)} tabs, "
          f"{sum(len(t['groups']) for t in tabs)} groups, {n_items} items, "
          f"{len(used_icons)} distinct icons", file=sys.stderr)
    if missing_cmd:
        print(f"\n!! {len(missing_cmd)} commands NOT in catalog:", file=sys.stderr)
        for t, g, c in missing_cmd:
            print(f"   [{t}/{g}] {c}", file=sys.stderr)
    if missing_icon:
        print(f"\n!! {len(missing_icon)} icons NOT in Fluent set:", file=sys.stderr)
        for t, c, ic in missing_icon:
            print(f"   [{t}] {c} -> {ic}", file=sys.stderr)
    # dump the icon list for the fetch step
    (ROOT / "resources" / "ribbon-icons.txt").write_text(
        "\n".join(sorted(used_icons)) + "\n")
    return 1 if (missing_cmd or missing_icon) else 0


if __name__ == "__main__":
    sys.exit(main())
