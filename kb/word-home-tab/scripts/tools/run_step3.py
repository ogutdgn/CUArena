"""Step 3 — the 3-level knowledge tree: app -> features -> subfeatures, + connections.

Grounded in the measured skeleton (Step 2): every subfeature maps to real element id(s) in
ui:ribbon-home and folds split-button primary+dropdown into one node. Every node carries the
full identity rubric (what_it_does / how_triggered / what_it_affects / audience) — no name-only
nodes. Descriptions are domain knowledge CONFIRMED by Step 2's measured behavior; the trigger
paths and opens targets are read straight from the skeleton, not invented.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import common

RH = ["ui:main-window", "ui:ribbon-home"]     # path prefix into the Home tab


# feature id -> (name, group, what_it_does, affects, audience, boundary)
FEATURES = {
    "feature:clipboard": ("Clipboard", "Clipboard",
        "Move and duplicate content and formatting via the clipboard.",
        "document content and the Office clipboard", "everyone", False),
    "feature:font": ("Font", "Font",
        "Format the characters of the selected text — typeface, size, weight, color, effects.",
        "the selection's character formatting", "everyone", False),
    "feature:paragraph": ("Paragraph", "Paragraph",
        "Format whole paragraphs — lists, indentation, alignment, spacing, shading, borders.",
        "the selected paragraphs' formatting and layout", "everyone", False),
    "feature:styles": ("Styles", "Styles",
        "Apply named, reusable style sets that bundle character and paragraph formatting.",
        "the paragraph/character style applied to the selection", "most", False),
    "feature:editing": ("Editing", "Editing",
        "Find, replace and select text within the document.",
        "navigation and selection within the document", "most", False),
    "feature:voice": ("Voice", "Voice",
        "Dictate text by voice using cloud speech recognition.",
        "document content (inserted by speech)", "niche", True),
    "feature:editor": ("Editor", "Editor",
        "Check spelling, grammar and writing refinements via the cloud Editor service.",
        "the document text (proofing) and the Editor pane", "most", True),
    "feature:acrobat": ("Adobe Acrobat", "Adobe Acrobat",
        "Create a PDF from the document via the Adobe Acrobat add-in.",
        "produces a PDF file (external add-in)", "niche", True),
    "feature:add-ins": ("Add-ins", "Add-ins",
        "Browse and launch Office Add-ins from the store.",
        "opens the add-in store (external content)", "niche", True),
}

# subfeature: dict(feature, name, does, affects, aud, shortcut, els=[element ids], opens, source, boundary)
S = []
def sub(id, feature, name, does, affects, aud, els, opens=None, shortcut=None,
        source="measured", boundary=False):
    S.append(dict(id=id, feature=feature, name=name, does=does, affects=affects, aud=aud,
                  els=els, opens=opens, shortcut=shortcut, source=source, boundary=boundary))

# --- Clipboard ---
sub("subfeature:paste", "feature:clipboard", "Paste",
    "Inserts the clipboard's content at the cursor; the dropdown offers paste-special options "
    "(keep formatting, merge, text only, picture).", "document content", "everyone",
    ["el:paste", "el:paste-dropdown"], opens="ui:paste-dropdown", shortcut="Ctrl+V")
sub("subfeature:cut", "feature:clipboard", "Cut",
    "Removes the selection from the document and places it on the clipboard.",
    "document content + clipboard", "everyone", ["el:cut"], shortcut="Ctrl+X")
sub("subfeature:copy", "feature:clipboard", "Copy",
    "Copies the selection to the clipboard without changing the document.",
    "the Office clipboard", "everyone", ["el:copy"], shortcut="Ctrl+C", source="idmso")
sub("subfeature:format-painter", "feature:clipboard", "Format Painter",
    "Copies formatting from the selection to reapply to the next thing you click.",
    "the formatting of the next selection", "most", ["el:format-painter"],
    shortcut="Alt+Ctrl+C, Alt+Ctrl+V", source="idmso")   # measured UIA AcceleratorKey pair
sub("subfeature:office-clipboard", "feature:clipboard", "Office Clipboard",
    "Opens the Office Clipboard pane showing the last 24 copied items for reuse.",
    "opens the Clipboard task pane", "niche", ["el:show-clipboard"], opens="ui:show-clipboard-pane")

# --- Font ---
sub("subfeature:font", "feature:font", "Font",
    "Chooses the typeface for the selected text; the box opens a searchable font list.",
    "the selection's font (typeface)", "everyone", ["el:font"], opens="ui:font-dropdown")
sub("subfeature:font-size", "feature:font", "Font Size",
    "Sets the point size of the selected text; the box opens a size list.",
    "the selection's font size", "everyone", ["el:font-size"], opens="ui:font-size-dropdown")
sub("subfeature:font-size-increase", "feature:font", "Grow Font",
    "Increases the font size of the selection to the next step.",
    "the selection's font size", "most", ["el:font-size-increase"], shortcut="Ctrl+Shift+>")
sub("subfeature:font-size-decrease", "feature:font", "Shrink Font",
    "Decreases the font size of the selection to the previous step.",
    "the selection's font size", "most", ["el:font-size-decrease"], shortcut="Ctrl+Shift+<")
sub("subfeature:change-case", "feature:font", "Change Case",
    "Changes the capitalization of the selected text (Sentence case, lowercase, UPPERCASE, "
    "Capitalize Each Word, tOGGLE cASE).", "the case of the selected text", "most",
    ["el:change-case-gallery"], opens="ui:change-case-menu")
sub("subfeature:clear-formatting", "feature:font", "Clear All Formatting",
    "Removes all character and paragraph formatting from the selection, leaving plain text.",
    "the selection's formatting (reset to default)", "most", ["el:clear-formatting"])
sub("subfeature:bold", "feature:font", "Bold",
    "Toggles bold (heavier) weight on the selected text.",
    "the selection's character format (bold)", "everyone", ["el:bold"], shortcut="Ctrl+B")
sub("subfeature:italic", "feature:font", "Italic",
    "Toggles italic (slanted) style on the selected text.",
    "the selection's character format (italic)", "everyone", ["el:italic"], shortcut="Ctrl+I")
sub("subfeature:underline-gallery", "feature:font", "Underline",
    "Toggles an underline on the selected text; the dropdown picks the underline style and color.",
    "the selection's character format (underline)", "everyone",
    ["el:underline-gallery", "el:underline-gallery-dropdown"], opens="ui:underline-menu",
    shortcut="Ctrl+U")
sub("subfeature:strikethrough", "feature:font", "Strikethrough",
    "Draws a line through the middle of the selected text.",
    "the selection's character format (strikethrough)", "most", ["el:strikethrough"])
sub("subfeature:subscript", "feature:font", "Subscript",
    "Places the selected text slightly below the baseline in a smaller size.",
    "the selection's character format (subscript)", "niche", ["el:subscript"],
    shortcut="Ctrl+Shift+_")   # measured UIA AcceleratorKey (not the docs' Ctrl+=)
sub("subfeature:superscript", "feature:font", "Superscript",
    "Places the selected text slightly above the baseline in a smaller size.",
    "the selection's character format (superscript)", "niche", ["el:superscript"],
    shortcut="Ctrl+Shift++")
sub("subfeature:text-effects", "feature:font", "Text Effects and Typography",
    "Applies visual text effects (outline, shadow, reflection, glow) and OpenType typography.",
    "the selection's character appearance", "niche", ["el:text-effects-gallery"],
    opens="ui:text-effects-dropdown")
sub("subfeature:text-highlight-color-picker", "feature:font", "Text Highlight Color",
    "Applies a highlighter color behind the text; the dropdown picks the color.",
    "the selection's highlight color", "most",
    ["el:text-highlight-color-picker", "el:text-highlight-color-picker-dropdown"],
    opens="ui:text-highlight-color-dropdown")
sub("subfeature:font-color-picker", "feature:font", "Font Color",
    "Sets the color of the selected text; the dropdown opens a color picker (theme/standard/more).",
    "the selection's font color", "everyone",
    ["el:font-color-picker", "el:font-color-picker-dropdown"], opens="ui:font-color-dropdown")
sub("subfeature:font-dialog", "feature:font", "Font dialog launcher",
    "Opens the Font dialog — the consolidated surface for all character formatting plus advanced "
    "options (spacing, ligatures, defaults).", "opens the Font dialog", "most",
    ["el:font-dialog"], opens="ui:font-dialog", shortcut="Ctrl+D")

# --- Paragraph ---
sub("subfeature:bullets-gallery", "feature:paragraph", "Bullets",
    "Starts or toggles a bulleted list on the selected paragraphs; the dropdown is the bullet library.",
    "the selected paragraphs' list format", "most",
    ["el:bullets-gallery", "el:bullets-gallery-dropdown"], opens="ui:bullets-dropdown")
sub("subfeature:numbering-gallery", "feature:paragraph", "Numbering",
    "Starts or toggles a numbered list on the selected paragraphs; the dropdown is the numbering library.",
    "the selected paragraphs' list format", "most",
    ["el:numbering-gallery", "el:numbering-gallery-dropdown"], opens="ui:numbering-dropdown")
sub("subfeature:multilevel-list", "feature:paragraph", "Multilevel List",
    "Applies a multi-level (nested) list scheme to the selected paragraphs.",
    "the selected paragraphs' multi-level list format", "niche", ["el:multilevel-list-gallery"],
    opens="ui:multilevel-list-menu")
sub("subfeature:indent-decrease", "feature:paragraph", "Decrease Indent",
    "Moves the paragraph's left indent one level toward the margin.",
    "the paragraph's left indent", "most", ["el:indent-decrease"])
sub("subfeature:indent-increase", "feature:paragraph", "Increase Indent",
    "Moves the paragraph's left indent one level away from the margin.",
    "the paragraph's left indent", "most", ["el:indent-increase"])
sub("subfeature:sort", "feature:paragraph", "Sort",
    "Opens the Sort dialog to alphabetically/numerically sort the selected paragraphs, list or table.",
    "the order of the selected paragraphs", "niche", ["el:sort-dialog-classic"], opens="ui:sort-dialog")
sub("subfeature:paragraph-marks", "feature:paragraph", "Show/Hide ¶",
    "Toggles the on-screen display of paragraph marks and other hidden formatting symbols.",
    "the view (formatting marks visibility) — not the document", "most", ["el:paragraph-marks"],
    shortcut="Ctrl+*")
sub("subfeature:align-left", "feature:paragraph", "Align Left",
    "Aligns the paragraph text to the left margin.", "the paragraph's alignment", "everyone",
    ["el:align-left"], shortcut="Ctrl+L")
sub("subfeature:align-center", "feature:paragraph", "Center",
    "Centers the paragraph text between the margins.", "the paragraph's alignment", "everyone",
    ["el:align-center"], shortcut="Ctrl+E")
sub("subfeature:align-right", "feature:paragraph", "Align Right",
    "Aligns the paragraph text to the right margin.", "the paragraph's alignment", "everyone",
    ["el:align-right"], shortcut="Ctrl+R")
sub("subfeature:align-justify", "feature:paragraph", "Justify",
    "Spaces the paragraph text to align to both left and right margins.",
    "the paragraph's alignment", "most", ["el:align-justify"], shortcut="Ctrl+J")
sub("subfeature:line-spacing", "feature:paragraph", "Line and Paragraph Spacing",
    "Sets the spacing between lines and before/after paragraphs.",
    "the paragraph's line and spacing", "most", ["el:line-spacing-gallery"],
    opens="ui:line-spacing-menu")
sub("subfeature:shading-color-picker", "feature:paragraph", "Shading",
    "Fills the background of the selection/paragraph with a color; the dropdown picks the color.",
    "the paragraph/selection background shading", "most",
    ["el:shading-color-picker", "el:shading-color-picker-dropdown"], opens="ui:shading-color-dropdown",
    source="idmso")
sub("subfeature:borders-selection-gallery", "feature:paragraph", "Borders",
    "Applies borders to the selection/paragraph; the dropdown lists border options and the "
    "Borders and Shading dialog.", "the paragraph/selection borders", "most",
    ["el:borders-selection-gallery", "el:borders-selection-gallery-dropdown"],
    opens="ui:borders-selection-menu")
sub("subfeature:paragraph-dialog", "feature:paragraph", "Paragraph dialog launcher",
    "Opens the Paragraph dialog — indentation, spacing, alignment and line/page-break options.",
    "opens the Paragraph dialog", "most", ["el:paragraph-dialog"], opens="ui:paragraph-dialog")

# --- Styles ---
sub("subfeature:quick-styles", "feature:styles", "Quick Styles gallery",
    "Applies a named style (Normal, No Spacing, Heading 1/2, Title, Subtitle, Quote…) to the "
    "selection from the in-ribbon gallery.", "the paragraph/character style applied", "most",
    ["el:quick-styles-gallery"], opens="ui:styles-gallery", source="uia")
sub("subfeature:styles-pane", "feature:styles", "Styles pane launcher",
    "Opens the Styles pane — the full style list with apply/new/inspect/manage controls.",
    "opens the Styles task pane", "niche", ["el:styles-pane"], opens="ui:styles-pane",
    shortcut="Alt+Ctrl+Shift+S")

# --- Editing ---
sub("subfeature:find", "feature:editing", "Find",
    "Opens the Navigation pane to search the document for text; the dropdown offers Find, "
    "Advanced Find and Go To.", "opens the Navigation pane / search", "everyone",
    ["el:navigation-pane-find", "el:navigation-pane-find-dropdown"],
    opens="ui:navigation-pane-find-pane", shortcut="Ctrl+F")
sub("subfeature:replace", "feature:editing", "Replace",
    "Opens the Find and Replace dialog to substitute text throughout the document.",
    "document content (via replace)", "most", ["el:replace-dialog"], opens="ui:replace-dialog",
    shortcut="Ctrl+H")
sub("subfeature:select", "feature:editing", "Select",
    "A menu to Select All, select objects, or select text with similar formatting.",
    "the current selection", "niche", ["el:select-menu"], opens="ui:select-menu")

# --- boundary features (rubric from domain knowledge; not pressed) ---
sub("subfeature:dictate", "feature:voice", "Dictate",
    "Converts speech to text via the cloud dictation service.", "document content", "niche",
    ["el:dictate"], source="inference", boundary=True)
sub("subfeature:editor", "feature:editor", "Editor",
    "Opens the Editor pane with spelling, grammar and writing-refinement suggestions.",
    "the document text (proofing) and Editor pane", "most", ["el:writing-assistance-check-document"],
    source="inference", boundary=True)
sub("subfeature:create-pdf", "feature:acrobat", "Create a PDF",
    "Exports the document to a PDF using the Adobe Acrobat add-in.", "produces a PDF file",
    "niche", ["el:create-a-pdf"], source="inference", boundary=True)
sub("subfeature:office-addins", "feature:add-ins", "Add-ins",
    "Opens the Office Add-ins store flyout to browse and insert add-ins.",
    "opens the add-in store", "niche", ["el:office-extensions-show-addin-flyout"],
    source="inference", boundary=True)


# --- connections (affects/uses edges; drive priority) ---
CLUSTERS = [
    (["subfeature:bold", "subfeature:italic", "subfeature:underline-gallery",
      "subfeature:strikethrough", "subfeature:subscript", "subfeature:superscript"],
     "affects", "shared-target", "all mutate the selection's character format"),
    (["subfeature:align-left", "subfeature:align-center", "subfeature:align-right",
      "subfeature:align-justify"], "affects", "shared-target",
     "all set paragraph alignment (mutually exclusive)"),
    (["subfeature:bullets-gallery", "subfeature:numbering-gallery", "subfeature:multilevel-list"],
     "affects", "shared-target", "all apply list formatting to paragraphs"),
    (["subfeature:cut", "subfeature:copy", "subfeature:paste"], "uses", "shared-target",
     "operate together through the clipboard"),
    (["subfeature:font-color-picker", "subfeature:text-highlight-color-picker",
      "subfeature:shading-color-picker"], "affects", "shared-target",
     "all apply a color (text / highlight / fill) to the selection"),
    (["subfeature:shading-color-picker", "subfeature:borders-selection-gallery"], "affects",
     "co-location", "paragraph decoration; both live in the Borders and Shading dialog"),
    (["subfeature:find", "subfeature:replace", "subfeature:select"], "uses", "co-location",
     "the editing/navigation family"),
    (["subfeature:font", "subfeature:font-size", "subfeature:font-size-increase",
      "subfeature:font-size-decrease"], "affects", "shared-target",
     "all set the selection's font or size"),
    (["subfeature:indent-decrease", "subfeature:indent-increase"], "affects", "shared-target",
     "both change the paragraph's left indent"),
]
HUBS = {
    "subfeature:font-dialog": (["subfeature:bold", "subfeature:italic", "subfeature:underline-gallery",
        "subfeature:strikethrough", "subfeature:subscript", "subfeature:superscript",
        "subfeature:font", "subfeature:font-size", "subfeature:font-color-picker",
        "subfeature:text-effects", "subfeature:change-case", "subfeature:clear-formatting"],
        "uses", "co-location", "consolidated in the Font dialog"),
    "subfeature:paragraph-dialog": (["subfeature:align-left", "subfeature:align-center",
        "subfeature:align-right", "subfeature:align-justify", "subfeature:indent-decrease",
        "subfeature:indent-increase", "subfeature:line-spacing", "subfeature:shading-color-picker",
        "subfeature:borders-selection-gallery"],
        "uses", "co-location", "consolidated in the Paragraph dialog"),
}
EXTRA = [
    ("subfeature:quick-styles", "subfeature:font-dialog", "uses", "observed",
     "a style bundles the character formatting the Font dialog sets"),
    ("subfeature:quick-styles", "subfeature:paragraph-dialog", "uses", "observed",
     "a style bundles paragraph formatting"),
    ("subfeature:clear-formatting", "subfeature:font-dialog", "affects", "observed",
     "removes the character formatting the Font dialog applies"),
    ("subfeature:clear-formatting", "subfeature:paragraph-dialog", "affects", "observed",
     "removes paragraph formatting"),
    ("subfeature:format-painter", "subfeature:font-dialog", "uses", "observed",
     "copies character formatting to reapply"),
    ("subfeature:format-painter", "subfeature:paragraph-dialog", "uses", "observed",
     "copies paragraph formatting to reapply"),
    ("subfeature:replace", "subfeature:find", "uses", "dependency",
     "Replace extends Find with substitution"),
    ("subfeature:multilevel-list", "subfeature:numbering-gallery", "uses", "shared-target",
     "multilevel lists build on numbering"),
]
# feature-level edges
FEATURE_EDGES = [
    ("feature:styles", "feature:font", "uses", "observed", "styles bundle character formatting"),
    ("feature:styles", "feature:paragraph", "uses", "observed", "styles bundle paragraph formatting"),
    ("feature:clipboard", "feature:font", "affects", "observed", "pasted content carries formatting"),
    ("feature:editing", "feature:clipboard", "uses", "observed", "replace edits document content"),
]


def build_connections():
    conn = {}   # source id -> list of edges

    def add(src, tgt, kind, source, why):
        if src == tgt:
            return
        conn.setdefault(src, [])
        if any(e["target"] == tgt and e["kind"] == kind for e in conn[src]):
            return
        conn[src].append({"target": tgt, "kind": kind, "why": why, "source": source})

    for ids, kind, source, why in CLUSTERS:
        for a in ids:
            for b in ids:
                add(a, b, kind, source, why)
    for hub, (members, kind, source, why) in HUBS.items():
        for m in members:
            add(m, hub, kind, source, why)
    for a, b, kind, source, why in EXTRA:
        add(a, b, kind, source, why)
    for a, b, kind, source, why in FEATURE_EDGES:
        add(a, b, kind, source, why)
    return conn


def trigger_paths(els, shortcut):
    tp = [{"path": RH + [e], "kind": "mouse"} for e in els]
    if shortcut:
        tp.append({"path": [], "kind": "keyboard", "shortcut": shortcut})
    return tp


def main():
    run_id = common.make_run_id() + "-step3"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    conn = build_connections()

    # subfeatures per feature
    subs_by_feature = {}
    for s in S:
        subs_by_feature.setdefault(s["feature"], []).append(s["id"])

    # write features
    version = json.loads((common.APP_KB / "version.json").read_text(encoding="utf-8"))
    for fid, (name, group, does, affects, aud, boundary) in FEATURES.items():
        node = {
            "id": fid, "name": name, "what_it_does": does, "affects": affects,
            "audience_breadth": aud, "location": "ui:ribbon-home",
            "trigger_paths": [{"path": RH, "kind": "mouse"}],
            "subfeatures": subs_by_feature.get(fid, []),
            "connections": conn.get(fid, []),
            "boundary": boundary, "source": "inference" if boundary else "measured",
        }
        writer.write_feature(node)

    # write subfeatures
    for s in S:
        node = {
            "id": s["id"], "name": s["name"], "parent": s["feature"],
            "what_it_does": s["does"], "affects": s["affects"], "audience_breadth": s["aud"],
            "trigger_paths": trigger_paths(s["els"], s["shortcut"]),
            "shortcut": s["shortcut"], "opens": s["opens"], "location": "ui:ribbon-home",
            "connections": conn.get(s["id"], []),
            "boundary": s["boundary"], "source": s["source"],
        }
        writer.write_subfeature(node)

    # app node
    app = {
        "name": "Microsoft Word", "version": version["build"], "platform": "desktop",
        "what_is_it": "A desktop word processor for creating, formatting and editing text documents.",
        "used_for": "Writing and formatting documents — letters, reports, essays, resumes — with "
                    "rich text styling, paragraph layout, lists, styles and review tools.",
        "who_uses": "Students, office workers, writers, and virtually anyone producing formatted "
                    "text documents.",
        "layout_regions": ["ui:main-window", "ui:ribbon-home"],
        "feature_inventory": [
            {"id": fid, "name": FEATURES[fid][0],
             "one_liner": FEATURES[fid][2], "trigger_path": RH}
            for fid in FEATURES
        ],
    }
    writer.write_app(app)

    total_edges = sum(len(v) for v in conn.values())
    jrnl.append(common.journal_event(actor="stage3", action="write-tree", target="features+subfeatures+app",
                outcome="ok", data={"features": len(FEATURES), "subfeatures": len(S),
                                    "connection_edges": total_edges}))
    print(json.dumps({"features": len(FEATURES), "subfeatures": len(S),
                      "connection_edges": total_edges,
                      "subs_per_feature": {k: len(v) for k, v in subs_by_feature.items()}},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
