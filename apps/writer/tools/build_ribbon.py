#!/usr/bin/env python3
"""Build resources/ribbon.json — the data-driven, Word-faithful ribbon model.

Curated tab → group → item spec, with command coverage drawn from LibreOffice's
own Writer notebookbar (sw/uiconfig/swriter/ui/notebookbar.ui) so we match its
ribbon depth, but organised into clean Word-style groups (not LO's dense flat
toolbars). Labels come from the command catalog; icons are auto-assigned from
the Microsoft Fluent set (DECISIONS D-icons) via a semantic-name matcher, with
curated overrides for the high-frequency / visually-important commands.

Item kinds (rendered specially by the QML — DialogWidget/RibbonButton):
  button (default) · toggle · fontname · fontsize · fontcolor · highlight

Run from apps/writer/:  python3 tools/build_ribbon.py
Output: resources/ribbon.json + resources/ribbon-icons.txt (icon manifest).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "resources" / "command-catalog.json"
FLUENT = ROOT / "tools" / "fluent-icon-names.txt"
OUT = ROOT / "resources" / "ribbon.json"

# --- icon overrides: curated, known-good Fluent names for key commands -------
ICON = {
    ".uno:Paste": "clipboard_paste", ".uno:Cut": "cut", ".uno:Copy": "copy",
    ".uno:FormatPaintbrush": "paint_brush",
    ".uno:Undo": "arrow_undo", ".uno:Redo": "arrow_redo",
    ".uno:Bold": "text_bold", ".uno:Italic": "text_italic",
    ".uno:Underline": "text_underline", ".uno:Strikeout": "text_strikethrough",
    ".uno:SubScript": "text_subscript", ".uno:SuperScript": "text_superscript",
    ".uno:Grow": "font_increase", ".uno:Shrink": "font_decrease",
    ".uno:FontColor": "text_color", ".uno:BackColor": "highlight",
    ".uno:ResetAttributes": "clear_formatting", ".uno:ChangeCaseRotateCase": "text_case_title",
    ".uno:CharFontName": "text_font", ".uno:FontHeight": "text_font_size",
    ".uno:DefaultBullet": "text_bullet_list", ".uno:DefaultNumbering": "text_number_list_ltr",
    ".uno:DecrementIndent": "text_indent_decrease_ltr", ".uno:IncrementIndent": "text_indent_increase_ltr",
    ".uno:LeftPara": "text_align_left", ".uno:CenterPara": "text_align_center",
    ".uno:RightPara": "text_align_right", ".uno:JustifyPara": "text_align_justify",
    ".uno:LineSpacing": "text_line_spacing", ".uno:BackgroundColor": "color_background",
    ".uno:BorderDialog": "border_all", ".uno:ControlCodes": "text_paragraph",
    ".uno:SortDialog": "arrow_sort", ".uno:ChapterNumberingDialog": "text_number_list_ltr",
    ".uno:StyleApply": "text_t", ".uno:DesignerDialog": "text_effects",
    ".uno:SearchDialog": "search", ".uno:SelectAll": "select_all_on",
    ".uno:SpellingDialog": "text_grammar_checkmark", ".uno:SpellingAndGrammarDialog": "text_grammar_checkmark",
    ".uno:InsertPagebreak": "document_page_break", ".uno:InsertBreak": "document_page_break",
    ".uno:InsertTable": "table_add", ".uno:InsertGraphic": "image_add",
    ".uno:InsertObjectChart": "chart_multiple", ".uno:InsertDraw": "shapes",
    ".uno:BasicShapes": "shapes", ".uno:Gallery": "image_multiple",
    ".uno:InsertAVMedia": "video_clip", ".uno:HyperlinkDialog": "link",
    ".uno:InsertBookmark": "bookmark", ".uno:InsertReferenceField": "document_link",
    ".uno:InsertPageHeader": "document_header", ".uno:InsertPageFooter": "document_footer",
    ".uno:InsertPageNumberField": "document_page_number", ".uno:InsertPageCountField": "document_page_number",
    ".uno:DrawText": "textbox", ".uno:InsertFieldCtrl": "text_field",
    ".uno:InsertDateField": "calendar_ltr", ".uno:EditGlossary": "text_expand",
    ".uno:FontworkGalleryFloater": "text_effects", ".uno:CharmapControl": "math_symbols",
    ".uno:InsertObjectStarMath": "math_formula", ".uno:InsertObject": "cube",
    ".uno:PageMargin": "document_margins", ".uno:Orientation": "document_landscape",
    ".uno:AttributePageSize": "document_one_page", ".uno:PageColumnType": "column_triple",
    ".uno:InsertSection": "column_triple", ".uno:PageDialog": "document_landscape",
    ".uno:Watermark": "drop", ".uno:Hyphenate": "text_word_count",
    ".uno:LineNumberingDialog": "text_number_format", ".uno:PageNumberWizard": "document_page_number",
    ".uno:TitlePageDialog": "document_one_page", ".uno:BringToFront": "position_to_front",
    ".uno:SendToBack": "position_backward", ".uno:ObjectForwardOne": "arrow_up",
    ".uno:ObjectBackOne": "arrow_down", ".uno:TextWrap": "text_wrap",
    ".uno:InsertMultiIndex": "text_bullet_list_tree", ".uno:InsertIndexesEntry": "bookmark_add",
    ".uno:UpdateCurIndex": "arrow_sync", ".uno:UpdateAll": "arrow_sync",
    ".uno:InsertFootnote": "text_footnote", ".uno:InsertEndnote": "document_endnote",
    ".uno:FootnoteDialog": "text_footnote", ".uno:InsertCaptionDialog": "text_description",
    ".uno:InsertAuthoritiesEntry": "book", ".uno:BibliographyComponent": "book_database",
    ".uno:ThesaurusDialog": "book_question_mark", ".uno:WordCountDialog": "text_word_count",
    ".uno:SpellOnline": "text_grammar_settings", ".uno:InsertAnnotation": "comment_add",
    ".uno:ReplyComment": "comment_arrow_left", ".uno:DeleteComment": "comment_dismiss",
    ".uno:TrackChanges": "edit", ".uno:ShowTrackedChanges": "eye",
    ".uno:NextTrackedChange": "arrow_next", ".uno:PreviousTrackedChange": "arrow_previous",
    ".uno:AcceptTrackedChange": "checkmark", ".uno:RejectTrackedChange": "dismiss",
    ".uno:AcceptAllTrackedChanges": "checkmark_circle", ".uno:RejectAllTrackedChanges": "dismiss_circle",
    ".uno:CompareDocuments": "document_arrow_right", ".uno:MergeDocuments": "document_sync",
    ".uno:EditDoc": "edit", ".uno:ProtectTraceChangeMode": "lock_closed",
    ".uno:AcceptTrackedChanges": "task_list_square_ltr",
    ".uno:PrintLayout": "document_one_page", ".uno:BrowseView": "globe",
    ".uno:PrintPreview": "print", ".uno:ShowWhitespace": "document_one_page",
    ".uno:ChangeTheme": "weather_moon", ".uno:Zoom": "zoom_fit",
    ".uno:ZoomOptimal": "zoom_fit", ".uno:Zoom100Percent": "zoom_in",
    ".uno:ZoomPage": "document_one_page", ".uno:ZoomPageWidth": "arrow_autofit_width",
    ".uno:FullScreen": "full_screen_maximize", ".uno:Sidebar": "panel_right",
    ".uno:Ruler": "ruler", ".uno:GridVisible": "grid", ".uno:Navigator": "navigation",
    ".uno:NewWindow": "window_new", ".uno:Menubar": "navigation",
    ".uno:NewDoc": "document_add", ".uno:Open": "folder_open", ".uno:Save": "save",
    ".uno:SaveAs": "save_edit", ".uno:SaveAll": "save_multiple", ".uno:Reload": "arrow_sync",
    ".uno:Quit": "dismiss_circle", ".uno:Repeat": "arrow_redo",
    ".uno:Print": "print", ".uno:PrintPreview": "document_one_page",
    ".uno:ExportToPDF": "document_pdf", ".uno:ExportTo": "share",
    ".uno:CloseDoc": "dismiss_circle", ".uno:HelpIndex": "question_circle", ".uno:About": "info",
    # extended set for the Word-faithful rewrite
    ".uno:PasteSpecial": "clipboard_paste", ".uno:OutlineBullet": "text_bullet_list_tree",
    ".uno:FontDialog": "text_font", ".uno:ParagraphDialog": "text_paragraph",
    ".uno:BulletsAndNumberingDialog": "text_bullet_list",
    ".uno:InsertSection": "column_triple",
    ".uno:ArrowShapes": "arrow_right", ".uno:SymbolShapes": "shapes",
    ".uno:StarShapes": "star", ".uno:CalloutShapes": "comment",
    ".uno:FlowChartShapes": "flowchart",
    ".uno:ConnectorToolbox": "branch", ".uno:ArrowsToolbox": "arrow_right",
    ".uno:LineToolbox": "line_horizontal_1", ".uno:Line": "line_horizontal_1",
    ".uno:DrawCaption": "comment", ".uno:VerticalText": "text_align_center_rotate_270",
    ".uno:ShowAnnotations": "eye", ".uno:DeleteCommentThread": "comment_dismiss",
    ".uno:ResolveComment": "comment_checkmark",
    ".uno:InsertEnvelope": "mail", ".uno:ViewDataSourceBrowser": "database",
    ".uno:HelplinesMove": "ruler", ".uno:ZoomPlus": "zoom_in", ".uno:ZoomMinus": "zoom_out",
    ".uno:ParaspaceIncrease": "arrow_expand", ".uno:ParaspaceDecrease": "arrow_collapse_all",
    ".uno:InsertColumnBreak": "document_page_break",
    ".uno:AcceptTrackedChanges": "task_list_square_ltr",
    ".uno:Hyphenate": "text_indent_increase_ltr",
    ".uno:MailMergeWizard": "mail_arrow_double_back",
    ".uno:InsertSymbol": "math_symbols",
    ".uno:RedactDoc": "eye_off",
}
FALLBACK_ICON = "square"  # neutral; flags an un-mapped command in the UI

# --- the curated spec --------------------------------------------------------
# Each item: a bare ".uno:Cmd" string, or a dict {cmd, [size], [toggle], [kind],
# [icon], [label], [args]}. size "lg" = large icon+label button.

def T(cmd):  # a toggle button
    return {"cmd": cmd, "toggle": True}


def CP(cmd, arg, swatch):           # a colour-picker (split palette popup)
    return {"cmd": cmd, "kind": "colorpicker", "argName": arg,
            "swatchColor": swatch, "defaultColor": -1}


def DD(cmd, options, size="sm"):    # a dropdown — options = [(label,cmd,args?,checkKey?,divider?), …]
    opts = []
    for o in options:
        if o is None or o == "---":
            opts.append({"divider": True}); continue
        if len(o) == 2:
            opts.append({"label": o[0], "cmd": o[1]})
        elif len(o) == 3:
            opts.append({"label": o[0], "cmd": o[1], "args": o[2]})
        elif len(o) == 4:
            opts.append({"label": o[0], "cmd": o[1], "args": o[2], "checkKey": o[3]})
    d = {"cmd": cmd, "kind": "dropdown", "options": opts, "size": size}
    return d


# Re-usable option sets ------------------------------------------------------
LINE_SPACING_OPTS = [
    ("Single (1.0)",  ".uno:SpacePara1",  None, ".uno:SpacePara1"),
    ("1.15",          ".uno:SpacePara115",None, ".uno:SpacePara115"),
    ("1.5",           ".uno:SpacePara15", None, ".uno:SpacePara15"),
    ("Double (2.0)",  ".uno:SpacePara2",  None, ".uno:SpacePara2"),
    "---",
    ("Line Spacing Options…", ".uno:ParagraphDialog"),
]
ZOOM_OPTS = [
    ("50%",  ".uno:Zoom", '{"Zoom.Value":{"type":"long","value":50}}'),
    ("75%",  ".uno:Zoom", '{"Zoom.Value":{"type":"long","value":75}}'),
    ("100%", ".uno:Zoom", '{"Zoom.Value":{"type":"long","value":100}}'),
    ("150%", ".uno:Zoom", '{"Zoom.Value":{"type":"long","value":150}}'),
    ("200%", ".uno:Zoom", '{"Zoom.Value":{"type":"long","value":200}}'),
    "---",
    ("Page Width",       ".uno:ZoomPageWidth"),
    ("Whole Page",       ".uno:ZoomPage"),
    ("Optimal",          ".uno:ZoomOptimal"),
    ("Zoom…",            ".uno:Zoom"),
]
CASE_OPTS = [
    ("Sentence case",       ".uno:ChangeCaseToSentenceCase"),
    ("lowercase",           ".uno:ChangeCaseToLower"),
    ("UPPERCASE",           ".uno:ChangeCaseToUpper"),
    ("Capitalize Each Word",".uno:ChangeCaseToTitleCase"),
    ("tOGGLE cASE",         ".uno:ChangeCaseToToggleCase"),
]
WRAP_OPTS = [
    ("None",     ".uno:WrapOff"),
    ("Parallel", ".uno:WrapOn"),
    ("Optimal",  ".uno:WrapIdeal"),
    ("Before",   ".uno:WrapLeft"),
    ("After",    ".uno:WrapRight"),
    ("Through",  ".uno:WrapThrough"),
    "---",
    ("Edit Contour…", ".uno:ContourDialog"),
    ("Text Wrap…",    ".uno:TextWrap"),
]
COLUMN_OPTS = [
    # LO has no direct `.uno:Columns` with a count arg — fall back to the
    # FormatColumns dialog (works via DialogHost). Refinement (a popup that
    # dispatches via SfxItemSet) is a tail item.
    ("One",          ".uno:FormatColumns"),
    ("Two",          ".uno:FormatColumns"),
    ("Three",        ".uno:FormatColumns"),
    "---",
    ("More Columns…", ".uno:FormatColumns"),
]
# For Margins / Orientation / Page Size LO has no single-uno arg switch —
# the dropdown items open the Page Style dialog (which our DialogHost renders
# natively). This still beats a plain button that does nothing.
MARGIN_OPTS = [
    ("Normal (1″)",   ".uno:PageDialog"),
    ("Narrow (0.5″)", ".uno:PageDialog"),
    ("Wide (2″)",     ".uno:PageDialog"),
    ("Mirrored",      ".uno:PageDialog"),
    "---",
    ("Custom Margins…", ".uno:PageDialog"),
]
ORIENT_OPTS = [
    ("Portrait",  ".uno:PageDialog"),
    ("Landscape", ".uno:PageDialog"),
]
SIZE_OPTS = [
    ("Letter (US)", ".uno:PageDialog"),
    ("A4",          ".uno:PageDialog"),
    ("Legal",       ".uno:PageDialog"),
    ("A3",          ".uno:PageDialog"),
    ("Tabloid",     ".uno:PageDialog"),
    "---",
    ("More Paper Sizes…", ".uno:PageDialog"),
]

# ---------------------------------------------------------------------------
# Compound option sets used inside SPEC
# ---------------------------------------------------------------------------
BULLET_OPTS = [
    ("Default bullet", ".uno:DefaultBullet"),
    "---",
    ("Bullets and Numbering…", ".uno:BulletsAndNumberingDialog"),
]
NUMBERING_OPTS = [
    ("Default numbering", ".uno:DefaultNumbering"),
    "---",
    ("Bullets and Numbering…", ".uno:BulletsAndNumberingDialog"),
]
STYLE_FAM = '"FamilyName":{"type":"string","value":"ParagraphStyles"}'
def STYLE(label, name, icon=None, size="sm"):
    args = '{"Style":{"type":"string","value":"' + name + '"},' + STYLE_FAM + '}'
    d = {"cmd": ".uno:StyleApply", "label": label, "args": args, "size": size}
    if icon: d["icon"] = icon
    return d

# ---------------------------------------------------------------------------
# Word-faithful tab/group structure
#    Sources: MS Word 365 ribbon docs (addbalance.com / Microsoft Support),
#    LO's own notebookbar.ui (writer ribbon, 17 tabs / 434 cmds),
#    writer-menu-tree.json (11 menus / 497 items),
#    command-catalog.json (1520 .uno).
# ---------------------------------------------------------------------------
SPEC = [
 ("File", [
   ("File", [{"cmd": ".uno:NewDoc", "size": "lg"}, ".uno:Open", ".uno:Save",
             ".uno:SaveAs", ".uno:SaveAll", ".uno:Reload"]),
   ("Print", [{"cmd": ".uno:PrintPreview", "size": "lg"}, ".uno:Print"]),
   ("Share", [".uno:ExportToPDF", ".uno:ExportTo"]),
   ("Close", [".uno:CloseDoc", ".uno:Quit"]),
 ]),
 ("Home", [
   ("Clipboard", [{"cmd": ".uno:Paste", "size": "lg"}, ".uno:PasteSpecial",
                  ".uno:Cut", ".uno:Copy", T(".uno:FormatPaintbrush")]),
   ("Undo", [".uno:Undo", ".uno:Redo", ".uno:Repeat"]),
   ("Font", [{"cmd": ".uno:CharFontName", "kind": "fontname"},
             {"cmd": ".uno:FontHeight", "kind": "fontsize"},
             ".uno:Grow", ".uno:Shrink",
             DD(".uno:ChangeCaseRotateCase", CASE_OPTS),
             ".uno:ResetAttributes",
             T(".uno:Bold"), T(".uno:Italic"), T(".uno:Underline"), T(".uno:Strikeout"),
             T(".uno:SubScript"), T(".uno:SuperScript"),
             CP(".uno:FontColor", "FontColor.Color", "#c0392b"),
             CP(".uno:BackColor", "BackColor.Color", "#ffd400"),
             ".uno:FontDialog"]),
   ("Paragraph", [DD(".uno:DefaultBullet", BULLET_OPTS),
                  DD(".uno:DefaultNumbering", NUMBERING_OPTS),
                  ".uno:OutlineBullet",
                  ".uno:DecrementIndent", ".uno:IncrementIndent",
                  T(".uno:LeftPara"), T(".uno:CenterPara"),
                  T(".uno:RightPara"), T(".uno:JustifyPara"),
                  DD(".uno:LineSpacing", LINE_SPACING_OPTS),
                  T(".uno:ControlCodes"), ".uno:BorderDialog",
                  CP(".uno:BackgroundColor", "BackgroundColor.Color", "#cce5ff"),
                  ".uno:SortDialog", ".uno:ParagraphDialog"]),
   ("Styles", [STYLE("Default", "Default Paragraph Style", "text_t", size="lg"),
               STYLE("No Spacing", "Default Paragraph Style", "text_paragraph"),
               STYLE("Heading 1", "Heading 1", "text_header_1"),
               STYLE("Heading 2", "Heading 2", "text_header_2"),
               STYLE("Heading 3", "Heading 3", "text_header_3"),
               STYLE("Title",     "Title",     "text_t"),
               STYLE("Subtitle",  "Subtitle",  "text_t"),
               STYLE("Quote",     "Quotations","text_quote"),
               ".uno:DesignerDialog"]),
   ("Editing", [{"cmd": ".uno:SearchDialog", "size": "lg"},
                ".uno:SelectAll", ".uno:SpellingDialog"]),
 ]),
 ("Insert", [
   ("Pages", [{"cmd": ".uno:InsertPagebreak", "size": "lg"},
              ".uno:TitlePageDialog", ".uno:InsertSection"]),
   ("Tables", [{"cmd": ".uno:InsertTable", "size": "lg"}]),
   ("Illustrations", [".uno:InsertGraphic", ".uno:InsertObjectChart",
                      ".uno:InsertDraw", ".uno:BasicShapes",
                      ".uno:ArrowShapes", ".uno:SymbolShapes",
                      ".uno:StarShapes", ".uno:CalloutShapes",
                      ".uno:FlowChartShapes", ".uno:Gallery"]),
   ("Media", [".uno:InsertAVMedia", ".uno:InsertObject"]),
   ("Links", [".uno:HyperlinkDialog", ".uno:InsertBookmark",
              ".uno:InsertReferenceField"]),
   ("Comments", [".uno:InsertAnnotation", ".uno:ShowAnnotations"]),
   ("Header & Footer", [".uno:InsertPageHeader", ".uno:InsertPageFooter",
                        ".uno:InsertPageNumberField", ".uno:InsertPageCountField"]),
   ("Text", [".uno:DrawText", ".uno:InsertFieldCtrl", ".uno:EditGlossary",
             ".uno:FontworkGalleryFloater", ".uno:InsertDateField",
             ".uno:InsertTitleField"]),
   ("Symbols", [".uno:InsertObjectStarMath", ".uno:CharmapControl",
                ".uno:InsertSymbol"]),
 ]),
 ("Draw", [
   ("Shapes", [{"cmd": ".uno:BasicShapes", "size": "lg"},
               ".uno:SymbolShapes", ".uno:ArrowShapes",
               ".uno:StarShapes", ".uno:CalloutShapes",
               ".uno:FlowChartShapes", ".uno:Line"]),
   ("Lines", [".uno:ConnectorToolbox", ".uno:ArrowsToolbox",
              ".uno:LineToolbox", ".uno:DrawCaption"]),
   ("Edit",  [".uno:SelectObject", ".uno:FormatGroup"]),
   ("Text",  [".uno:DrawText", ".uno:VerticalText",
              ".uno:FontworkGalleryFloater"]),
 ]),
 ("Design", [
   ("Document Formatting", [{"cmd": ".uno:DesignerDialog", "size": "lg"},
                            T(".uno:ChangeTheme")]),
   ("Page Background", [".uno:Watermark",
                        CP(".uno:BackgroundColor", "BackgroundColor.Color", "#ffeb3b"),
                        ".uno:BorderDialog"]),
   ("Paragraph Spacing", [".uno:ParaspaceIncrease", ".uno:ParaspaceDecrease"]),
   ("Page", [".uno:TitlePageDialog"]),
 ]),
 ("Layout", [
   ("Page Setup", [DD(".uno:PageMargin", MARGIN_OPTS, size="lg"),
                   DD(".uno:Orientation", ORIENT_OPTS),
                   DD(".uno:AttributePageSize", SIZE_OPTS),
                   DD(".uno:PageColumnType", COLUMN_OPTS),
                   ".uno:PageDialog"]),
   ("Breaks", [".uno:InsertPagebreak", ".uno:InsertBreak",
               ".uno:InsertColumnBreak", ".uno:InsertSection"]),
   ("Paragraph", [".uno:IncrementIndent", ".uno:DecrementIndent",
                  ".uno:ParaspaceIncrease", ".uno:ParaspaceDecrease",
                  ".uno:Hyphenate", ".uno:ParagraphDialog"]),
   ("Page", [".uno:Watermark", ".uno:LineNumberingDialog",
             ".uno:PageNumberWizard"]),
   ("Arrange", [".uno:BringToFront", ".uno:SendToBack",
                ".uno:ObjectForwardOne", ".uno:ObjectBackOne",
                DD(".uno:TextWrap", WRAP_OPTS),
                ".uno:FormatGroup", ".uno:SelectObject"]),
 ]),
 ("References", [
   ("Table of Contents", [{"cmd": ".uno:InsertMultiIndex", "size": "lg"},
                          ".uno:InsertIndexesEntry", ".uno:UpdateCurIndex",
                          ".uno:UpdateAll"]),
   ("Footnotes", [".uno:InsertFootnote", ".uno:InsertEndnote",
                  ".uno:FootnoteDialog"]),
   ("Citations & Bibliography", [".uno:InsertAuthoritiesEntry",
                                 ".uno:BibliographyComponent"]),
   ("Captions", [".uno:InsertCaptionDialog", ".uno:InsertReferenceField",
                 ".uno:InsertBookmark"]),
   ("Fields", [".uno:InsertFieldCtrl", ".uno:InsertPageNumberField",
               ".uno:InsertPageCountField", ".uno:InsertDateField",
               ".uno:InsertTitleField"]),
 ]),
 ("Mailings", [
   ("Create", [".uno:InsertEnvelope"]),
   ("Start Mail Merge", [{"cmd": ".uno:MailMergeWizard", "size": "lg"},
                         ".uno:ViewDataSourceBrowser"]),
   ("Write & Insert Fields", [".uno:InsertFieldCtrl"]),
   ("Finish", [".uno:Print"]),
 ]),
 ("Review", [
   ("Proofing", [{"cmd": ".uno:SpellingAndGrammarDialog", "size": "lg"},
                 ".uno:ThesaurusDialog", ".uno:WordCountDialog",
                 T(".uno:SpellOnline")]),
   ("Comments", [".uno:InsertAnnotation", ".uno:ReplyComment",
                 ".uno:DeleteComment", ".uno:DeleteCommentThread",
                 ".uno:ResolveComment", T(".uno:ShowAnnotations")]),
   ("Tracking", [T(".uno:TrackChanges"), T(".uno:ShowTrackedChanges")]),
   ("Changes", [".uno:AcceptTrackedChange", ".uno:RejectTrackedChange",
                ".uno:PreviousTrackedChange", ".uno:NextTrackedChange",
                ".uno:AcceptAllTrackedChanges", ".uno:RejectAllTrackedChanges",
                ".uno:AcceptTrackedChanges"]),
   ("Compare", [".uno:CompareDocuments", ".uno:MergeDocuments"]),
   ("Protect", [T(".uno:EditDoc"), ".uno:ProtectTraceChangeMode",
                ".uno:RedactDoc"]),
 ]),
 ("View", [
   ("Views", [T(".uno:PrintLayout"), T(".uno:BrowseView"), ".uno:PrintPreview"]),
   ("Show", [T(".uno:ControlCodes"), T(".uno:ShowWhitespace"),
             T(".uno:Ruler"), T(".uno:GridVisible"),
             T(".uno:HelplinesMove"), T(".uno:Sidebar"), T(".uno:Navigator")]),
   ("Zoom", [DD(".uno:Zoom", ZOOM_OPTS, size="lg"),
             ".uno:ZoomOptimal", ".uno:Zoom100Percent",
             ".uno:ZoomPage", ".uno:ZoomPageWidth",
             ".uno:ZoomPlus", ".uno:ZoomMinus"]),
   ("Window", [".uno:NewWindow", T(".uno:FullScreen")]),
   ("Theme", [T(".uno:ChangeTheme")]),
 ]),
 ("Help", [
   ("Help", [{"cmd": ".uno:HelpIndex", "size": "lg"}, ".uno:About"]),
 ]),
]


def clean_label(raw: str) -> str:
    if not raw:
        return ""
    s = raw.replace("~", "").replace("%PRODUCTNAME", "Writer")
    return re.sub(r"\s+", " ", s).strip()


def make_matcher(catalog, fluent):
    def best(cmd):
        if cmd in ICON:
            return ICON[cmd]
        sn = (catalog.get(cmd, {}).get("semanticName") or "").strip("_")
        if not sn:
            return FALLBACK_ICON
        if sn in fluent:
            return sn
        toks = sn.split("_")
        for n in range(len(toks), 0, -1):
            for cand in ("_".join(toks[:n]), "_".join(toks[-n:])):
                if cand in fluent:
                    return cand
        tokset = set(toks)
        best_f, best_s = None, 0
        for f in fluent:
            s = len(tokset & set(f.split("_")))
            if s > best_s:
                best_f, best_s = f, s
        return best_f or FALLBACK_ICON
    return best


def main() -> int:
    catalog = json.loads(CATALOG.read_text())["commands"]
    fluent = set(FLUENT.read_text().split()) if FLUENT.exists() else set()
    icon_for = make_matcher(catalog, fluent)

    missing_cmd, used_icons, fallback_cmds = [], set(), []
    tabs = []
    for tab_name, groups in SPEC:
        out_groups = []
        for group_name, items in groups:
            out_items = []
            for raw in items:
                it = {"cmd": raw} if isinstance(raw, str) else dict(raw)
                cmd = it["cmd"]
                meta = catalog.get(cmd)
                if meta is None:
                    missing_cmd.append((tab_name, group_name, cmd))
                icon = it.get("icon") or icon_for(cmd)
                if icon == FALLBACK_ICON:
                    fallback_cmds.append(cmd)
                used_icons.add(icon)
                entry = {
                    "cmd": cmd,
                    "label": it.get("label") or clean_label(meta["label"] if meta else cmd),
                    "icon": icon,
                    "size": it.get("size", "sm"),
                }
                if it.get("toggle"):
                    entry["toggle"] = True
                if it.get("kind"):
                    entry["kind"] = it["kind"]
                if it.get("args"):
                    entry["args"] = it["args"]
                # carry colorpicker / dropdown payloads through
                for k in ("options", "argName", "swatchColor", "defaultColor", "autoLabel"):
                    if k in it:
                        entry[k] = it[k]
                out_items.append(entry)
            out_groups.append({"name": group_name, "items": out_items})
        tabs.append({"name": tab_name, "groups": out_groups})

    OUT.write_text(json.dumps({"schemaVersion": 1, "tabs": tabs}, indent=1) + "\n")
    (ROOT / "resources" / "ribbon-icons.txt").write_text("\n".join(sorted(used_icons)) + "\n")

    n_items = sum(len(g["items"]) for t in tabs for g in t["groups"])
    n_groups = sum(len(t["groups"]) for t in tabs)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(tabs)} tabs, {n_groups} groups, "
          f"{n_items} items, {len(used_icons)} icons", file=sys.stderr)
    if missing_cmd:
        print(f"\n!! {len(missing_cmd)} commands NOT in catalog:", file=sys.stderr)
        for t, g, c in missing_cmd:
            print(f"   [{t}/{g}] {c}", file=sys.stderr)
    if fallback_cmds:
        print(f"\n~~ {len(fallback_cmds)} commands using the fallback icon "
              f"(add an ICON override): {sorted(set(fallback_cmds))}", file=sys.stderr)
    return 1 if missing_cmd else 0


if __name__ == "__main__":
    sys.exit(main())
