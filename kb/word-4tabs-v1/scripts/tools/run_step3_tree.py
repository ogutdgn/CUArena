"""Step 3 — the 3-level knowledge tree (v2, CONSOLIDATED): app -> features -> subfeatures.

Grounded in the measured skeleton (Step 2 + the full-loop contextual crawl). v2 differences
from the v1 run:
  * output through the consolidated kernel writers: one features/<feature>.json per feature
    with ALL its sub-features inline (FeatureFile); app.json; ui.json updated in place;
  * connection vocabulary is the CURRENT one — requires / affects-same / co-location — with
    `requires` carrying closure (04-priority) and contextual discovery producing requires
    edges (element -> the sub-feature that summons its surface);
  * CONTEXTUAL CONTROLS BECOME NODES (the LESSONS fix): every measured control on every
    contextual tab is claimed by a sub-feature below (variation-test folding where children
    are variations of one effect), the container's auto-generated `triggers` references are
    REWRITTEN to the authored node ids (journaled reconciliation, evidence preserved), and
    every contextual node carries a `requires` edge to its summoning sub-feature;
  * fail-loud: any measured contextual element with a triggers/opens marker NOT claimed by
    the spec aborts the run with the unclaimed list (a dead-end face cannot ship silently).

Folding decisions (variation test, playbook 03 par.1) are journaled as decision events.
"""
import json
import sys
from collections import OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

RH = ["ui:main-window", "ui:ribbon-home"]
RI = ["ui:main-window", "ui:ribbon-insert"]


# ============================ HOME + INSERT (ids verified == v1, re-measured this run) =======
# feature id -> (name, tab-path, what_it_does, affects, audience, boundary)
FEATURES = {
    # ---- Home ----
    "feature:clipboard": ("Clipboard", RH,
        "Move and duplicate content and formatting via the clipboard.",
        "document content and the Office clipboard", "everyone", False),
    "feature:font": ("Font", RH,
        "Format the characters of the selected text — typeface, size, weight, color, effects.",
        "the selection's character formatting", "everyone", False),
    "feature:paragraph": ("Paragraph", RH,
        "Format whole paragraphs — lists, indentation, alignment, spacing, shading, borders.",
        "the selected paragraphs' formatting and layout", "everyone", False),
    "feature:styles": ("Styles", RH,
        "Apply named, reusable style sets that bundle character and paragraph formatting.",
        "the paragraph/character style applied to the selection", "most", False),
    "feature:editing": ("Editing", RH,
        "Find, replace and select text within the document.",
        "navigation and selection within the document", "most", False),
    "feature:voice": ("Voice", RH,
        "Dictate text by voice using cloud speech recognition.",
        "document content (inserted by speech)", "niche", True),
    "feature:editor": ("Editor", RH,
        "Check spelling, grammar and writing refinements via the cloud Editor service.",
        "the document text (proofing) and the Editor pane", "most", True),
    "feature:acrobat": ("Adobe Acrobat", RH,
        "Create a PDF from the document via the Adobe Acrobat add-in.",
        "produces a PDF file (external add-in)", "niche", True),
    "feature:add-ins": ("Add-ins", RH,
        "Browse and launch Office Add-ins from the store.",
        "opens the add-in store (external content)", "niche", True),
    # ---- Insert ----
    "feature:pages": ("Pages", RI,
        "Insert page-level structure: preformatted cover pages, blank pages, and page breaks.",
        "the document's page structure and flow", "most", False),
    "feature:tables": ("Tables", RI,
        "Insert tables to organize content in rows and columns; a selected table brings up its "
        "own Table Design and Table Layout contextual tabs.",
        "document content (adds a table object)", "everyone", False),
    "feature:illustrations": ("Illustrations", RI,
        "Insert graphic objects — pictures, shapes, icons, 3D models, SmartArt diagrams, charts "
        "and screenshots; each selected object surfaces its own Format contextual tab(s).",
        "document content (adds graphic objects)", "everyone", False),
    "feature:media": ("Media", RI,
        "Embed online videos into the document from web sources.",
        "document content (adds an embedded video)", "niche", False),
    "feature:links": ("Links", RI,
        "Create navigation targets and jumps: hyperlinks, bookmarks and cross-references.",
        "navigation structure (links, bookmarks, references)", "most", False),
    "feature:comments": ("Comments", RI,
        "Attach review comments to document ranges for collaboration.",
        "the document's comment thread (review layer)", "most", False),
    "feature:header-footer": ("Header & Footer", RI,
        "Repeat content at the top/bottom of every page and number the pages; editing them "
        "activates the Header & Footer contextual tab.",
        "the header/footer stories of every page", "most", False),
    "feature:text": ("Text", RI,
        "Insert text objects and building blocks: text boxes, Quick Parts/fields, WordArt, "
        "drop caps, signature lines, date/time and embedded objects.",
        "document content (adds text objects/fields)", "most", False),
    "feature:symbols": ("Symbols", RI,
        "Insert mathematical equations (with the Equation contextual tab) and special symbols "
        "not on the keyboard.",
        "document content (adds equations/symbols)", "most", False),
    "feature:esignature": ("eSignature", RI,
        "Request electronic signatures on the document via the SharePoint Syntex cloud service.",
        "starts a cloud e-signature request", "niche", True),
}

S = []
def sub(id, feature, name, does, affects, aud, els, opens=None, shortcut=None,
        source="measured", boundary=False):
    S.append(dict(id=id, feature=feature, name=name, does=does, affects=affects, aud=aud,
                  els=els, opens=opens, shortcut=shortcut, source=source, boundary=boundary))

# -------- Home --------
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
    shortcut="Alt+Ctrl+C, Alt+Ctrl+V", source="idmso")
sub("subfeature:office-clipboard", "feature:clipboard", "Office Clipboard",
    "Opens the Office Clipboard pane showing the last 24 copied items for reuse.",
    "opens the Clipboard task pane", "niche", ["el:show-clipboard"],
    opens="ui:show-clipboard-pane")
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
    shortcut="Ctrl+Shift+_")
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
    "Sets the color of the selected text; the dropdown opens a color picker "
    "(theme/standard/more).", "the selection's font color", "everyone",
    ["el:font-color-picker", "el:font-color-picker-dropdown"], opens="ui:font-color-dropdown")
sub("subfeature:font-dialog", "feature:font", "Font dialog launcher",
    "Opens the Font dialog — the consolidated surface for all character formatting plus "
    "advanced options (spacing, ligatures, defaults).", "opens the Font dialog", "most",
    ["el:font-dialog"], opens="ui:font-dialog", shortcut="Ctrl+D")
sub("subfeature:bullets-gallery", "feature:paragraph", "Bullets",
    "Starts or toggles a bulleted list on the selected paragraphs; the dropdown is the bullet "
    "library.", "the selected paragraphs' list format", "most",
    ["el:bullets-gallery", "el:bullets-gallery-dropdown"], opens="ui:bullets-dropdown")
sub("subfeature:numbering-gallery", "feature:paragraph", "Numbering",
    "Starts or toggles a numbered list on the selected paragraphs; the dropdown is the "
    "numbering library.", "the selected paragraphs' list format", "most",
    ["el:numbering-gallery", "el:numbering-gallery-dropdown"], opens="ui:numbering-dropdown")
sub("subfeature:multilevel-list", "feature:paragraph", "Multilevel List",
    "Applies a multi-level (nested) list scheme to the selected paragraphs.",
    "the selected paragraphs' multi-level list format", "niche",
    ["el:multilevel-list-gallery"], opens="ui:multilevel-list-menu")
sub("subfeature:indent-decrease", "feature:paragraph", "Decrease Indent",
    "Moves the paragraph's left indent one level toward the margin.",
    "the paragraph's left indent", "most", ["el:indent-decrease"])
sub("subfeature:indent-increase", "feature:paragraph", "Increase Indent",
    "Moves the paragraph's left indent one level away from the margin.",
    "the paragraph's left indent", "most", ["el:indent-increase"])
sub("subfeature:sort", "feature:paragraph", "Sort",
    "Opens the Sort dialog to alphabetically/numerically sort the selected paragraphs, list "
    "or table.", "the order of the selected paragraphs", "niche",
    ["el:sort-dialog-classic"], opens="ui:sort-dialog")
sub("subfeature:paragraph-marks", "feature:paragraph", "Show/Hide ¶",
    "Toggles the on-screen display of paragraph marks and other hidden formatting symbols.",
    "the view (formatting marks visibility) — not the document", "most",
    ["el:paragraph-marks"], shortcut="Ctrl+*")
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
    "Fills the background of the selection/paragraph with a color; the dropdown picks the "
    "color.", "the paragraph/selection background shading", "most",
    ["el:shading-color-picker", "el:shading-color-picker-dropdown"],
    opens="ui:shading-color-dropdown", source="idmso")
sub("subfeature:borders-selection-gallery", "feature:paragraph", "Borders",
    "Applies borders to the selection/paragraph; the dropdown lists border options and the "
    "Borders and Shading dialog.", "the paragraph/selection borders", "most",
    ["el:borders-selection-gallery", "el:borders-selection-gallery-dropdown"],
    opens="ui:borders-selection-menu")
sub("subfeature:paragraph-dialog", "feature:paragraph", "Paragraph dialog launcher",
    "Opens the Paragraph dialog — indentation, spacing, alignment and line/page-break options.",
    "opens the Paragraph dialog", "most", ["el:paragraph-dialog"], opens="ui:paragraph-dialog")
sub("subfeature:quick-styles", "feature:styles", "Quick Styles gallery",
    "Applies a named style (Normal, No Spacing, Heading 1/2, Title, Subtitle, Quote…) to the "
    "selection from the in-ribbon gallery; the expand arrow opens the full styles flyout.",
    "the paragraph/character style applied", "most",
    ["el:quick-styles-gallery"], opens="ui:quick-styles-gallery", source="uia")
sub("subfeature:styles-pane", "feature:styles", "Styles pane launcher",
    "Opens the Styles pane — the full style list with apply/new/inspect/manage controls.",
    "opens the Styles task pane", "niche", ["el:styles-pane"], opens="ui:styles-pane",
    shortcut="Alt+Ctrl+Shift+S")
sub("subfeature:find", "feature:editing", "Find",
    "Opens the Navigation pane to search the document for text; the dropdown offers Find, "
    "Advanced Find and Go To.", "opens the Navigation pane / search", "everyone",
    ["el:navigation-pane-find", "el:navigation-pane-find-dropdown"],
    opens="ui:navigation-pane-find-pane", shortcut="Ctrl+F")
sub("subfeature:replace", "feature:editing", "Replace",
    "Opens the Find and Replace dialog to substitute text throughout the document.",
    "document content (via replace)", "most", ["el:replace-dialog"],
    opens="ui:replace-dialog", shortcut="Ctrl+H")
sub("subfeature:select", "feature:editing", "Select",
    "A menu to Select All, select objects, or select text with similar formatting.",
    "the current selection", "niche", ["el:select-menu"], opens="ui:select-menu")
sub("subfeature:dictate", "feature:voice", "Dictate",
    "Converts speech to text via the cloud dictation service.", "document content", "niche",
    ["el:dictate"], source="inference", boundary=True)
sub("subfeature:editor", "feature:editor", "Editor",
    "Opens the Editor pane with spelling, grammar and writing-refinement suggestions.",
    "the document text (proofing) and Editor pane", "most",
    ["el:writing-assistance-check-document"], source="inference", boundary=True)
sub("subfeature:create-pdf", "feature:acrobat", "Create a PDF",
    "Exports the document to a PDF using the Adobe Acrobat add-in.", "produces a PDF file",
    "niche", ["el:create-a-pdf"], source="inference", boundary=True)
sub("subfeature:office-addins", "feature:add-ins", "Add-ins",
    "Opens the Office Add-ins store flyout to browse and insert add-ins.",
    "opens the add-in store", "niche", ["el:office-extensions-show-addin-flyout"],
    source="inference", boundary=True)

# -------- Insert --------
sub("subfeature:cover-page-insert", "feature:pages", "Cover Page",
    "Inserts a preformatted, styled cover page (title/subtitle/date placeholders) at the start "
    "of the document, chosen from a gallery of designs.",
    "document content (adds a formatted first page)", "most",
    ["el:cover-page-insert-gallery"], opens="ui:cover-page-insert-dropdown")
sub("subfeature:blank-page-insert", "feature:pages", "Blank Page",
    "Inserts an empty page at the cursor position (measured: two page breaks around a new "
    "empty page).", "document content (page flow)", "most", ["el:blank-page-insert"])
sub("subfeature:page-break-insert", "feature:pages", "Page Break",
    "Ends the current page at the cursor and continues content on the next page (measured: "
    "doc + format delta).", "document content (page flow)", "everyone",
    ["el:page-break-insert"], shortcut="Ctrl+Return")
sub("subfeature:table-insert", "feature:tables", "Table",
    "Opens the table builder: a hover grid to insert an N×M table instantly, plus Insert "
    "Table…, Draw Table, Convert Text to Table…, Excel Spreadsheet and Quick Tables. A "
    "selected table activates the Table Design + Table Layout contextual tabs (measured).",
    "document content (adds a table object)", "everyone",
    ["el:table-insert-gallery"], opens="ui:table-insert-dropdown")
sub("subfeature:insert-pictures", "feature:illustrations", "Pictures",
    "Inserts a picture from This Device, the Stock Images library, or Online Pictures; a "
    "selected picture activates the Picture Format contextual tab (measured). Also reachable "
    "inside header/footer editing (Header & Footer tab > Insert group).",
    "document content (adds an image)", "everyone",
    ["el:flyout-anchor-insert-pictures"], opens="ui:flyout-anchor-insert-pictures-menu")
sub("subfeature:shapes-insert", "feature:illustrations", "Shapes",
    "Opens a gallery of ready-made shapes (lines, rectangles, arrows, callouts…) to draw into "
    "the document; a selected shape activates the Shape Format contextual tab (measured).",
    "document content (adds a drawn shape)", "most",
    ["el:shapes-insert-gallery"], opens="ui:shapes-insert-dropdown")
sub("subfeature:icon-insert", "feature:illustrations", "Icons",
    "Opens the stock icon library dialog to insert symbol graphics (content streams from the "
    "Office CDN — network); an inserted icon/SVG graphic activates the Graphics Format "
    "contextual tab (measured via a local SVG probe).",
    "document content (adds an icon graphic)", "niche",
    ["el:icon-insert-from-file"], opens="ui:icon-insert-from-file-dialog")
sub("subfeature:insert-3d-models", "feature:illustrations", "3D Models",
    "Inserts a rotatable 3D model from the stock library (primary) or from a local file (the "
    "dropdown menu offers This Device / Stock 3D Models).",
    "document content (adds a 3D model object)", "niche",
    ["el:insert3-dmodel-default", "el:insert3-dmodel-default-dropdown"],
    opens="ui:insert3-dmodel-default-dialog")
sub("subfeature:smart-art-insert", "feature:illustrations", "SmartArt",
    "Opens the Choose a SmartArt Graphic dialog (lists, processes, cycles, hierarchies…); an "
    "inserted SmartArt activates the SmartArt Design + Format contextual tabs (measured).",
    "document content (adds a SmartArt diagram)", "most",
    ["el:smart-art-insert"], opens="ui:smart-art-insert-dialog")
sub("subfeature:chart-insert", "feature:illustrations", "Chart",
    "Opens the Insert Chart dialog (column, line, pie, bar, area, scatter, map…); an inserted "
    "chart activates the Chart Design + Format contextual tabs and links to an embedded Excel "
    "datasheet for its data (measured).",
    "document content (adds a chart backed by worksheet data)", "most",
    ["el:chart-insert"], opens="ui:chart-insert-dialog")
sub("subfeature:screenshot-insert", "feature:illustrations", "Screenshot",
    "Inserts a snapshot of any open window (gallery of live thumbnails) or a Screen Clipping "
    "region; the result is a picture (Picture Format applies).",
    "document content (adds a screenshot image)", "niche",
    ["el:screenshot-insert-gallery"], opens="ui:screenshot-insert-dropdown")
sub("subfeature:online-videos-insert", "feature:media", "Online Videos",
    "Opens a dialog to embed an online video by URL (YouTube etc.); playback happens "
    "in-document (network content).", "document content (adds an embedded video)", "niche",
    ["el:movie-from-clip-organizer-insert"], opens="ui:movie-from-clip-organizer-insert-dialog")
sub("subfeature:insert-link", "feature:links", "Link",
    "Opens the Insert Hyperlink dialog to link the selection to webpages, files, headings or "
    "email addresses; the dropdown lists recent items.",
    "the selection (wraps it in a hyperlink)", "most",
    ["el:insert-link-gallery", "el:insert-link-gallery-dropdown"],
    opens="ui:insert-link-dialog", shortcut="Ctrl+K")
sub("subfeature:bookmark-insert", "feature:links", "Bookmark",
    "Opens the Bookmark dialog to name the current place/selection so links and references "
    "can jump to it.", "the document's bookmark registry", "niche",
    ["el:bookmark-insert"], opens="ui:bookmark-insert-dialog")
sub("subfeature:cross-reference-insert", "feature:links", "Cross-reference",
    "Opens the Cross-reference dialog to insert a live reference to a heading, bookmark, "
    "figure or table (updates as the target moves).",
    "document content (adds a reference field)", "niche",
    ["el:cross-reference-insert"], opens="ui:cross-reference-insert-dialog")
sub("subfeature:insert-new-comment", "feature:comments", "Comment",
    "Creates a pending draft comment anchored at the selection and opens its card (measured: "
    "in-frame 'Post comment' button); the comment joins the review thread when posted.",
    "the document's comment thread", "most",
    ["el:insert-new-comment"], shortcut="Ctrl+Alt+M")
sub("subfeature:header-insert", "feature:header-footer", "Header",
    "Opens a gallery of built-in header designs (Blank, Austin, Banded…) plus Edit/Remove "
    "Header; applying one enters header editing and activates the Header & Footer contextual "
    "tab (measured).", "the header story of every page", "most",
    ["el:header-insert-gallery"], opens="ui:header-insert-dropdown")
sub("subfeature:footer-insert", "feature:header-footer", "Footer",
    "Opens a gallery of built-in footer designs plus Edit/Remove Footer; applying one enters "
    "footer editing and activates the Header & Footer contextual tab.",
    "the footer story of every page", "most",
    ["el:footer-insert-gallery"], opens="ui:footer-insert-dropdown")
sub("subfeature:page-number-insert", "feature:header-footer", "Page Number",
    "Opens a menu of page-number positions (top, bottom, margins, current position) and "
    "formats; numbers live in the header/footer stories.",
    "the header/footer stories (page numbering)", "most",
    ["el:header-footer-page-number-insert"], opens="ui:header-footer-page-number-insert-menu")
sub("subfeature:text-box-insert", "feature:text", "Text Box",
    "Inserts a floating text container from a gallery of built-in designs or by drawing one; "
    "a selected text box activates the Shape Format contextual tab (measured).",
    "document content (adds a floating text container)", "most",
    ["el:text-box-insert-gallery"], opens="ui:text-box-insert-dropdown")
sub("subfeature:quick-parts-insert", "feature:text", "Quick Parts",
    "Inserts reusable building blocks: AutoText, document properties and fields; also saves "
    "the selection to the gallery. Also hosted on the Header & Footer contextual tab.",
    "document content (adds building blocks/fields)", "niche",
    ["el:quick-parts-insert-gallery"], opens="ui:quick-parts-insert-dropdown")
sub("subfeature:word-art-insert", "feature:text", "WordArt",
    "Inserts decorative styled text from a gallery; the result is a text object whose "
    "selection activates a Format contextual tab (measured: modern WordArt uses Shape Format; "
    "legacy WordArt objects surface a dedicated WordArt tab).",
    "document content (adds decorative text)", "niche",
    ["el:word-art-insert-gallery"], opens="ui:word-art-insert-dropdown")
sub("subfeature:drop-cap-insert", "feature:text", "Drop Cap",
    "Turns the paragraph's first letter into a large dropped capital (Dropped / In margin / "
    "options dialog); disabled until the document has text (measured).",
    "the first paragraph character's layout", "niche",
    ["el:drop-cap-insert-gallery"], opens="ui:drop-cap-insert-dropdown")
sub("subfeature:signature-line-insert", "feature:text", "Signature Line",
    "Opens the Signature Setup dialog to insert a signature line naming the required signer "
    "(digital signature requires a certificate).",
    "document content (adds a signature line object)", "niche",
    ["el:signature-line-insert", "el:signature-line-insert-dropdown"],
    opens="ui:signature-line-insert-dialog")
sub("subfeature:date-and-time-insert", "feature:text", "Date & Time",
    "Opens a dialog of date/time formats to insert the current date or time, optionally as an "
    "auto-updating field. Also hosted on the Header & Footer contextual tab.",
    "document content (adds date/time text or field)", "niche",
    ["el:date-and-time-insert"], opens="ui:date-and-time-insert-dialog")
sub("subfeature:object-insert", "feature:text", "Object",
    "Embeds an OLE object (or inserts text from another file via the dropdown menu) into the "
    "document.", "document content (adds an embedded object)", "niche",
    ["el:ole-objectct-insert", "el:ole-objectct-insert-dropdown"],
    opens="ui:ole-objectct-insert-dialog")
sub("subfeature:equation-insert-gallery", "feature:symbols", "Equation",
    "Inserts an empty math zone at the cursor (measured: OMaths 0→1) and activates the "
    "Equation contextual tab; the dropdown offers built-in equations (quadratic formula, area "
    "of circle…).", "document content (adds an equation/math zone)", "niche",
    ["el:equation-insert-gallery", "el:equation-insert-gallery-dropdown"],
    opens="ui:equation-insert-dropdown", shortcut="Alt+=")
sub("subfeature:symbol-insert", "feature:symbols", "Symbol",
    "Opens a gallery of recently used symbols plus More Symbols… (the full character map) to "
    "insert characters not on the keyboard.", "document content (adds a symbol character)",
    "most", ["el:symbol-insert-gallery"], opens="ui:symbol-insert-dropdown")
sub("subfeature:esignature-fields", "feature:esignature", "eSignature fields",
    "Requests electronic signatures on the document through the SharePoint Syntex service.",
    "starts a cloud e-signature request", "niche", ["el:syntex-esign"],
    source="inference", boundary=True)


# ============================ connections (current vocabulary) ================================
# clusters: all members pairwise affects-same (measured shared state-diff target in step 2)
CLUSTERS = [
    (["subfeature:bold", "subfeature:italic", "subfeature:underline-gallery",
      "subfeature:strikethrough", "subfeature:subscript", "subfeature:superscript"],
     "affects-same", "shared-target", "all mutate the selection's character format"),
    (["subfeature:align-left", "subfeature:align-center", "subfeature:align-right",
      "subfeature:align-justify"], "affects-same", "shared-target",
     "all set paragraph alignment (mutually exclusive)"),
    (["subfeature:bullets-gallery", "subfeature:numbering-gallery",
      "subfeature:multilevel-list"], "affects-same", "shared-target",
     "all apply list formatting to paragraphs"),
    (["subfeature:cut", "subfeature:copy", "subfeature:paste"], "affects-same",
     "shared-target", "operate together through the clipboard"),
    (["subfeature:font-color-picker", "subfeature:text-highlight-color-picker",
      "subfeature:shading-color-picker"], "affects-same", "shared-target",
     "all apply a color (text / highlight / fill) to the selection"),
    (["subfeature:shading-color-picker", "subfeature:borders-selection-gallery"],
     "co-location", "co-location", "paragraph decoration; both live in the Borders and "
     "Shading dialog"),
    (["subfeature:find", "subfeature:replace", "subfeature:select"], "co-location",
     "co-location", "the editing/navigation family"),
    (["subfeature:font", "subfeature:font-size", "subfeature:font-size-increase",
      "subfeature:font-size-decrease"], "affects-same", "shared-target",
     "all set the selection's font or size"),
    (["subfeature:indent-decrease", "subfeature:indent-increase"], "affects-same",
     "shared-target", "both change the paragraph's left indent"),
    (["subfeature:cover-page-insert", "subfeature:blank-page-insert",
      "subfeature:page-break-insert"], "affects-same", "shared-target",
     "all change the document's page structure/flow"),
    (["subfeature:insert-pictures", "subfeature:shapes-insert", "subfeature:icon-insert",
      "subfeature:insert-3d-models", "subfeature:smart-art-insert", "subfeature:chart-insert",
      "subfeature:screenshot-insert"], "affects-same", "shared-target",
     "all insert graphic objects (Shapes/InlineShapes) into the document"),
    (["subfeature:header-insert", "subfeature:footer-insert",
      "subfeature:page-number-insert"], "affects-same", "shared-target",
     "all write into the per-page header/footer stories"),
    (["subfeature:insert-link", "subfeature:bookmark-insert",
      "subfeature:cross-reference-insert"], "co-location", "co-location",
     "the navigation-target family (Links group)"),
    (["subfeature:text-box-insert", "subfeature:word-art-insert"], "affects-same",
     "shared-target", "both create floating text Shapes (both measured to Shape Format "
     "context)"),
    (["subfeature:equation-insert-gallery", "subfeature:symbol-insert"], "co-location",
     "co-location", "the Symbols group family"),
]
# hubs: members co-locate onto a consolidated dialog surface
HUBS = {
    "subfeature:font-dialog": (["subfeature:bold", "subfeature:italic",
        "subfeature:underline-gallery", "subfeature:strikethrough", "subfeature:subscript",
        "subfeature:superscript", "subfeature:font", "subfeature:font-size",
        "subfeature:font-color-picker", "subfeature:text-effects", "subfeature:change-case",
        "subfeature:clear-formatting"],
        "co-location", "co-location", "consolidated in the Font dialog"),
    "subfeature:paragraph-dialog": (["subfeature:align-left", "subfeature:align-center",
        "subfeature:align-right", "subfeature:align-justify", "subfeature:indent-decrease",
        "subfeature:indent-increase", "subfeature:line-spacing",
        "subfeature:shading-color-picker", "subfeature:borders-selection-gallery"],
        "co-location", "co-location", "consolidated in the Paragraph dialog"),
}
# directed extras: (src, target, kind, source, why) — requires points AT the prerequisite
EXTRA = [
    ("subfeature:quick-styles", "subfeature:font-dialog", "affects-same", "observed",
     "a style bundles the character formatting the Font dialog sets"),
    ("subfeature:quick-styles", "subfeature:paragraph-dialog", "affects-same", "observed",
     "a style bundles paragraph formatting"),
    ("subfeature:clear-formatting", "subfeature:font-dialog", "affects-same", "observed",
     "removes the character formatting the Font dialog applies"),
    ("subfeature:clear-formatting", "subfeature:paragraph-dialog", "affects-same", "observed",
     "removes paragraph formatting"),
    ("subfeature:format-painter", "subfeature:font-dialog", "affects-same", "observed",
     "copies character formatting to reapply"),
    ("subfeature:format-painter", "subfeature:paragraph-dialog", "affects-same", "observed",
     "copies paragraph formatting to reapply"),
    ("subfeature:replace", "subfeature:find", "requires", "dependency",
     "Replace is Find plus substitution — the find machinery is its precondition"),
    ("subfeature:multilevel-list", "subfeature:numbering-gallery", "affects-same",
     "shared-target", "multilevel lists build on numbering"),
    ("subfeature:paste", "subfeature:copy", "requires", "dependency",
     "Paste is empty-handed without something cut/copied to the clipboard (measured: "
     "clipboard had to be armed for the paste probe)"),
    ("subfeature:cross-reference-insert", "subfeature:bookmark-insert", "requires",
     "dependency", "cross-references can target bookmarks (B consumes A's artifact; "
     "headings are an alternative target)"),
    ("subfeature:insert-link", "subfeature:bookmark-insert", "requires", "dependency",
     "in-document hyperlinks jump to bookmarks ('Bookmarks work with hyperlinks' — the "
     "control's own ScreenTip); external links work without"),
    ("subfeature:page-number-insert", "subfeature:header-insert", "requires", "dependency",
     "page numbers are written into the header/footer stories"),
    ("subfeature:page-number-insert", "subfeature:footer-insert", "requires", "dependency",
     "page numbers are written into the header/footer stories"),
    ("subfeature:cover-page-insert", "subfeature:quick-parts-insert", "co-location",
     "inference", "cover pages are building blocks from the same gallery system"),
    ("subfeature:date-and-time-insert", "subfeature:quick-parts-insert", "co-location",
     "inference", "an auto-updating date is a field, the machinery Quick Parts exposes"),
    ("subfeature:screenshot-insert", "subfeature:insert-pictures", "affects-same",
     "shared-target", "a screenshot lands as a picture (same object family / Picture Format "
     "context)"),
    ("subfeature:table-insert", "subfeature:sort", "affects-same", "observed",
     "Sort operates on table contents as well as paragraphs"),
    ("subfeature:paste", "subfeature:insert-pictures", "affects-same", "observed",
     "pasted images land as the same picture objects"),
    ("subfeature:text-box-insert", "subfeature:font", "affects-same", "inference",
     "text inside a text box is formatted with the Font tools"),
]
FEATURE_EDGES = [
    ("feature:styles", "feature:font", "affects-same", "observed",
     "styles bundle character formatting"),
    ("feature:styles", "feature:paragraph", "affects-same", "observed",
     "styles bundle paragraph formatting"),
    ("feature:clipboard", "feature:font", "affects-same", "observed",
     "pasted content carries formatting"),
    ("feature:editing", "feature:clipboard", "co-location", "observed",
     "replace edits document content"),
    ("feature:tables", "feature:paragraph", "affects-same", "observed",
     "table cells contain paragraphs formatted by the Paragraph tools"),
    ("feature:illustrations", "feature:clipboard", "affects-same", "observed",
     "graphic objects are moved/duplicated through the clipboard"),
    ("feature:header-footer", "feature:pages", "affects-same", "observed",
     "headers/footers render on every page the page structure creates"),
    ("feature:text", "feature:font", "affects-same", "inference",
     "text objects carry character formatting"),
]

# ============================ CONTEXTUAL spec (filled from measured ui.json) ==================
# The spec is imported from its own module (ctx_spec.py) — it is large, authored against the
# measured containers, and fails loudly when it no longer matches the measurement.
from ctx_spec import CTX_FEATURES, CTX_SUBS, CTX_EXISTING_ELS, CTX_IDMSO_OVERRIDES, \
    CTX_HONEST_UNEXPLORED, CTX_CLUSTERS, CTX_EXTRA, IDMSO_OVERRIDE_SUFFIX
# Design + Layout tree spec (the new ground this run adds) — see tools/dl_spec.py
from dl_spec import DL_FEATURES, DL_SUBS, DL_EXISTING_ELS, LAYOUT_ARRANGE_HOSTS, \
    DL_CLUSTERS, DL_EXTRA, DL_FEATURE_EDGES

RD = ["ui:main-window", "ui:ribbon-design"]
RL = ["ui:main-window", "ui:ribbon-layout"]

# R3.5 cohesion per feature (playbook-03 tests: capability = facets of ONE capability,
# replicable whole; catalog = independent capabilities sharing a drawer, judged one by one).
# Design/Layout features carry cohesion in dl_spec; these cover Home/Insert + contextual.
COHESION = {
    # ---- Home / Insert ----
    "feature:clipboard": "capability",     # cut/copy/paste/format-painter — all clipboard ops
    "feature:font": "capability",          # all shape the selection's character format
    "feature:paragraph": "capability",     # all format the selected paragraphs
    "feature:styles": "capability",        # apply/manage named styles
    "feature:editing": "catalog",          # find / replace / select — independent utilities
    "feature:voice": "capability",
    "feature:editor": "capability",
    "feature:acrobat": "capability",
    "feature:add-ins": "capability",
    "feature:pages": "catalog",            # cover page / blank page / page break — independent
    "feature:tables": "capability",        # table insertion (its world is Table Design/Layout)
    "feature:illustrations": "catalog",    # the canonical catalog (playbook example)
    "feature:media": "capability",
    "feature:links": "catalog",            # hyperlink / bookmark / cross-reference — independent
    "feature:comments": "capability",
    "feature:header-footer": "capability", # header / footer / page number — all H&F stories
    "feature:text": "catalog",             # text box / quick parts / wordart / drop cap / … indep
    "feature:symbols": "catalog",          # equation vs symbol — different capabilities
    "feature:esignature": "capability",
    # ---- contextual: object-format tabs operate on ONE selected object -> capability ----
    "feature:table-design": "capability", "feature:table-layout": "capability",
    "feature:picture-format": "capability", "feature:graphics-format": "capability",
    "feature:shape-format": "capability", "feature:smartart-design": "capability",
    "feature:smartart-format": "capability", "feature:chart-design": "capability",
    "feature:chart-format": "capability", "feature:equation-tools": "capability",
    "feature:header-footer-tools": "capability", "feature:object-arrange": "capability",
    "feature:object-size": "capability", "feature:shape-styles": "capability",
    "feature:wordart-text-styles": "capability",
}


def build_connections():
    conn = {}

    def add(src, tgt, kind, source, why):
        if src == tgt:
            return
        conn.setdefault(src, [])
        if any(e["target"] == tgt and e["kind"] == kind for e in conn[src]):
            return
        conn[src].append({"target": tgt, "kind": kind, "why": why, "source": source})

    for ids, kind, source, why in CLUSTERS + CTX_CLUSTERS + DL_CLUSTERS:
        for a in ids:
            for b in ids:
                add(a, b, kind, source, why)
    for hub, (members, kind, source, why) in HUBS.items():
        for m in members:
            add(m, hub, kind, source, why)
    for a, b, kind, source, why in EXTRA + CTX_EXTRA + DL_EXTRA:
        add(a, b, kind, source, why)
    # measured contextual requires: every contextual sub/feature requires its summoner
    for s in CTX_SUBS:
        for req in s.get("requires", []):
            add(s["id"], req, "requires", "contextual",
                "measured: this control lives on a contextual tab that exists only after "
                "the required capability's object is inserted/selected (step3 probes)")
    for f in CTX_FEATURES:
        for req in f.get("requires", []):
            add(f["id"], req, "requires", "contextual",
                "measured: the hosting contextual tab appears only in this object's context")
    for a, b, kind, source, why in FEATURE_EDGES + DL_FEATURE_EDGES:
        add(a, b, kind, source, why)
    return conn


def _ellipsis_label(label):
    """True for a label that promises a dialog by platform convention (R2.4) — must never be
    reclassified as a triggers endpoint. Mirrors kernel/graph_builder._ellipsis_labeled."""
    s = (label or "").rstrip()
    return s.endswith(("…", "...")) and any(ch.isalpha() for ch in s)


def trigger_paths(els, shortcut, base):
    tp = [{"path": base + [e], "kind": "mouse"} for e in els]
    if shortcut:
        tp.append({"path": [], "kind": "keyboard", "shortcut": shortcut})
    return tp


def main():
    run_id = common.make_run_id() + "-step3-tree"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()

    ui = writer.load_ui()
    containers = {cid: c.model_dump() for cid, c in ui.containers.items()}
    home_ids = {e["id"] for e in containers["ui:ribbon-home"]["children"] if e.get("id")}
    insert_ids = {e["id"] for e in containers["ui:ribbon-insert"]["children"] if e.get("id")}
    design_ids = {e["id"] for e in containers["ui:ribbon-design"]["children"] if e.get("id")}
    layout_ids = {e["id"] for e in containers["ui:ribbon-layout"]["children"] if e.get("id")}

    # ---------- contextual reconciliation ----------
    # A CTX_SUBS entry hosts on one OR MANY contextual tabs (shared object capabilities like
    # Arrange/Size repeat across every object-format tab). `hosts` = [(tab_cid, [el_ids])].
    def sub_els(s):
        return [el for (_tab, els) in s["hosts"] for el in els]

    # claim map: element id -> (sub id, is_existing_node)
    claim = {}
    for s in CTX_SUBS:
        for el in sub_els(s):
            claim[el] = (s["id"], False)
    for sid, pairs in CTX_EXISTING_ELS.items():
        for (_tab, el) in pairs:
            claim[el] = (sid, True)

    ctx_cids = [cid for cid, c in containers.items() if c.get("trigger_condition")]
    unclaimed, rewrites = [], 0
    el_opens_ctx = {}          # el id -> opened container (for sub.opens resolution)
    el_tooltip = {}
    for cid in ctx_cids:
        c = containers[cid]
        for e in c["children"]:
            eid = e.get("id")
            if not eid:
                continue
            el_tooltip[eid] = e.get("tooltip")
            if e.get("opens"):
                el_opens_ctx.setdefault(eid, e["opens"])
            claimed = claim.get(eid)
            disabled = "disabled in this context" in (e.get("state_notes") or "")
            if claimed is None:
                if disabled or eid in CTX_HONEST_UNEXPLORED:
                    continue        # honest stub at element level, journaled by the crawl
                if e.get("triggers") or e.get("opens"):
                    unclaimed.append(f"{cid} {eid} [{'opens' if e.get('opens') else 'triggers'}]")
                else:
                    unclaimed.append(f"{cid} {eid} [no-effect unclaimed]")
                continue
            target, _ = claimed
            # R2.4 repair (idempotent over re-runs): an ellipsis control previously flipped to a
            # triggers endpoint by an idMso override must be reverted to honest unexplored — a
            # "…" label promises a dialog and a surfaceless press of it is a FAILED press.
            if (e.get("triggers") and e.get("source") == "idmso"
                    and _ellipsis_label(e.get("label"))):
                e["triggers"] = None
                e["unexplored"] = True
                e["source"] = "measured"
                e["state_notes"] = ((e.get("state_notes") or "") + "; R2.4: ellipsis promises a "
                    "dialog and the press revealed no surface -> honest unexplored (failed "
                    "press, not an endpoint)").strip("; ")
                rewrites += 1
                continue
            # rewrite auto-generated triggers to the authored node id
            if e.get("triggers") and e["triggers"] != target:
                e["triggers"] = target
                rewrites += 1
            # idMso-knowledge overrides: known capabilities whose effect was honestly
            # unfingerprintable (mode armers, apply-last-color primaries, view toggles).
            # R2.4 GUARD: an ellipsis-labeled control ("Select Data…") promises a DIALOG — it
            # may never be reclassified as a triggers endpoint. A no-effect press of it is a
            # FAILED press; leave it honestly unexplored (kernel-checked). This caught
            # "Select Data…" on Chart Design being wrongly folded into chart-edit-data.
            if (e.get("unexplored") and eid in CTX_IDMSO_OVERRIDES
                    and not _ellipsis_label(e.get("label"))):
                e.pop("unexplored", None)
                e["unexplored"] = False
                e["triggers"] = target
                e["source"] = "idmso"
                note = CTX_IDMSO_OVERRIDES[eid]
                e["state_notes"] = ((e.get("state_notes") or "") +
                                    f"; feature by idMso knowledge: {note}").strip("; ")
                rewrites += 1
    if unclaimed:
        print("UNCLAIMED CONTEXTUAL ELEMENTS (spec incomplete — fix before shipping):")
        for u in unclaimed:
            print("  ", u)
        raise SystemExit(f"{len(unclaimed)} unclaimed contextual elements")

    # ---------- Layout ARRANGE reconciliation ----------
    # The Layout tab's Arrange group is the SHARED object-arrange machinery (measured with a
    # shape selected in run_step3_layout_arrange). Map those Layout elements to the same
    # object-arrange subs the contextual tabs feed, mirroring the contextual handling: rewrite
    # any auto triggers to the authored sub id, apply the idMso override to unexplored primaries
    # (z-order step whose effect isn't measurable with a single object), and collect the Layout
    # elements as extra hosts (trigger paths) for those subs.
    layout_c = containers["ui:ribbon-layout"]
    layout_by_id = {e["id"]: e for e in layout_c["children"]}
    layout_arrange_hosts = {}      # sub id -> [el ids present on Layout]
    for sub_id, el_ids in LAYOUT_ARRANGE_HOSTS.items():
        for eid in el_ids:
            e = layout_by_id.get(eid)
            if e is None:
                continue
            suffix = eid.removeprefix("el:")
            if e.get("triggers") and e["triggers"] != sub_id:
                e["triggers"] = sub_id
                rewrites += 1
            elif (e.get("unexplored") and suffix in IDMSO_OVERRIDE_SUFFIX
                    and not _ellipsis_label(e.get("label"))):
                e["unexplored"] = False
                e["triggers"] = sub_id
                e["source"] = "idmso"
                e["state_notes"] = ((e.get("state_notes") or "") +
                    f"; feature by idMso knowledge: {IDMSO_OVERRIDE_SUFFIX[suffix]}").strip("; ")
                rewrites += 1
            layout_arrange_hosts.setdefault(sub_id, []).append(eid)
    writer.upsert_container(layout_c)

    # write reconciled containers back
    for cid in ctx_cids:
        writer.upsert_container(containers[cid])
    jrnl.append(common.journal_event(actor="stage3.tree", action="decision",
                target="contextual-reconciliation", outcome="ok",
                data={"reasoning": "auto-generated per-element triggers rewritten to authored "
                      "sub-feature ids (variation-test folding); idMso overrides applied to "
                      "known-capability elements whose effect is not fingerprintable; the Layout "
                      "Arrange group folded into the shared object-arrange subs (extra hosts)",
                      "rewrites": rewrites, "tabs": ctx_cids,
                      "layout_arrange_hosts": layout_arrange_hosts}))

    conn = build_connections()

    # ---------- assemble nodes ----------
    subs_by_feature = {}
    all_sub_defs = []
    for s in S:
        el0 = s["els"][0]
        base = RH if el0 in home_ids else RI if el0 in insert_ids else None
        assert base, f"{s['id']}: element {el0} not found in either measured ribbon!"
        tps = trigger_paths(s["els"], s["shortcut"], base)
        # extra contextual hosting paths for existing nodes (e.g. Header on the H&F tab):
        # CTX_EXISTING_ELS[sub] = [(tab_cid, el_id), ...]
        for (host, eid) in CTX_EXISTING_ELS.get(s["id"], []):
            tps.append({"path": ["ui:main-window", host, eid], "kind": "mouse"})
        # extra Design/Layout hosting paths for existing Home/Insert nodes (e.g. the Layout tab's
        # Paragraph launcher opens the same Paragraph dialog): DL_EXISTING_ELS[sub] = [(cid, el)]
        for (host, eid) in DL_EXISTING_ELS.get(s["id"], []):
            tps.append({"path": ["ui:main-window", host, eid], "kind": "mouse"})
        node = {
            "id": s["id"], "name": s["name"], "parent": s["feature"],
            "what_it_does": s["does"], "affects": s["affects"], "audience_breadth": s["aud"],
            "trigger_paths": tps, "shortcut": s["shortcut"], "opens": s["opens"],
            "location": base[-1], "connections": conn.get(s["id"], []),
            "boundary": s["boundary"], "source": s["source"],
        }
        subs_by_feature.setdefault(s["feature"], []).append(node)
        all_sub_defs.append(node)
    for s in CTX_SUBS:
        hosts = list(s["hosts"])
        # object-arrange subs are ALSO reached from the Layout tab's Arrange group
        if s["id"] in layout_arrange_hosts:
            hosts.append(("ui:ribbon-layout", layout_arrange_hosts[s["id"]]))
        tps = [{"path": ["ui:main-window", tab, e], "kind": "mouse"}
               for (tab, els) in hosts for e in els]
        if s.get("shortcut"):
            tps.append({"path": [], "kind": "keyboard", "shortcut": s["shortcut"]})
        opens = s.get("opens")
        if opens is None:
            for e in sub_els(s):
                if e in el_opens_ctx:
                    opens = el_opens_ctx[e]
                    break
        node = {
            "id": s["id"], "name": s["name"], "parent": s["feature"],
            "what_it_does": s["does"], "affects": s["affects"], "audience_breadth": s["aud"],
            "trigger_paths": tps, "shortcut": s.get("shortcut"), "opens": opens,
            "location": s["hosts"][0][0], "connections": conn.get(s["id"], []),
            "boundary": False, "source": "measured",
        }
        subs_by_feature.setdefault(s["feature"], []).append(node)
        all_sub_defs.append(node)
    # ---------- Design + Layout sub nodes (the new ground) ----------
    for s in DL_SUBS:
        base = s["tab"]      # RD or RL
        tps = trigger_paths(s["els"], s.get("shortcut"), base)
        node = {
            "id": s["id"], "name": s["name"], "parent": s["feature"],
            "what_it_does": s["does"], "affects": s["affects"], "audience_breadth": s["aud"],
            "trigger_paths": tps, "shortcut": s.get("shortcut"), "opens": s.get("opens"),
            "location": base[-1], "connections": conn.get(s["id"], []),
            "boundary": s["boundary"], "source": s["source"],
        }
        subs_by_feature.setdefault(s["feature"], []).append(node)
        all_sub_defs.append(node)

    # ---------- write fat feature files ----------
    n_files = 0
    for fid, (name, base, does, affects, aud, boundary) in FEATURES.items():
        subs = subs_by_feature.get(fid, [])
        ff = {"feature": {
                "id": fid, "name": name, "what_it_does": does, "affects": affects,
                "audience_breadth": aud, "location": base[-1], "cohesion": COHESION.get(fid),
                "trigger_paths": [{"path": base, "kind": "mouse"}],
                "subfeatures": [x["id"] for x in subs],
                "connections": conn.get(fid, []),
                "boundary": boundary, "source": "inference" if boundary else "measured"},
              "subfeatures": subs}
        writer.write_feature_file(ff)
        n_files += 1
    # ---------- Design + Layout features (capability/catalog cohesion recorded) ----------
    for fid, (name, base, does, affects, aud, cohesion) in DL_FEATURES.items():
        subs = subs_by_feature.get(fid, [])
        ff = {"feature": {
                "id": fid, "name": name, "what_it_does": does, "affects": affects,
                "audience_breadth": aud, "location": base[-1], "cohesion": cohesion,
                "trigger_paths": [{"path": base, "kind": "mouse"}],
                "subfeatures": [x["id"] for x in subs],
                "connections": conn.get(fid, []),
                "boundary": False, "source": "measured"},
              "subfeatures": subs}
        writer.write_feature_file(ff)
        n_files += 1
    for f in CTX_FEATURES:
        subs = subs_by_feature.get(f["id"], [])
        hosts = sorted({s["location"] for s in subs}) or f.get("tabs", [])
        ff = {"feature": {
                "id": f["id"], "name": f["name"], "what_it_does": f["does"],
                "affects": f["affects"], "audience_breadth": f["aud"],
                "location": hosts[0] if hosts else None, "cohesion": COHESION.get(f["id"]),
                "trigger_paths": [{"path": ["ui:main-window", h], "kind": "mouse"}
                                  for h in hosts],
                "subfeatures": [x["id"] for x in subs],
                "connections": conn.get(f["id"], []),
                "boundary": False, "source": "measured"},
              "subfeatures": subs}
        writer.write_feature_file(ff)
        n_files += 1

    # ---------- app node ----------
    version = json.loads((common.APP_KB / "version.json").read_text(encoding="utf-8"))
    inventory = [{"id": fid, "name": FEATURES[fid][0], "one_liner": FEATURES[fid][2],
                  "trigger_path": FEATURES[fid][1]} for fid in FEATURES]
    inventory += [{"id": fid, "name": DL_FEATURES[fid][0], "one_liner": DL_FEATURES[fid][2],
                   "trigger_path": DL_FEATURES[fid][1]} for fid in DL_FEATURES]
    inventory += [{"id": f["id"], "name": f["name"], "one_liner": f["does"],
                   "trigger_path": ["ui:main-window", (f.get("tabs") or ["ui:main-window"])[0]]}
                  for f in CTX_FEATURES]
    app = {
        "name": "Microsoft Word", "version": version["build"], "platform": "desktop",
        "what_is_it": "A desktop word processor for creating, formatting and editing text "
                      "documents.",
        "used_for": "Writing and formatting documents — letters, reports, essays, resumes — "
                    "with rich text styling, paragraph layout, lists, styles, tables, graphics, "
                    "page setup, themes, headers/footers and review tools.",
        "who_uses": "Students, office workers, writers, and virtually anyone producing "
                    "formatted text documents.",
        "layout_regions": ["ui:main-window", "ui:ribbon-home", "ui:ribbon-insert",
                           "ui:ribbon-design", "ui:ribbon-layout"] + ctx_cids,
        "feature_inventory": inventory,
    }
    writer.write_app(app)

    total_edges = sum(len(v) for v in conn.values())
    jrnl.append(common.journal_event(actor="stage3.tree", action="write-tree",
                target="features/*.json + app.json", outcome="ok",
                data={"feature_files": n_files, "subfeatures": len(all_sub_defs),
                      "connection_edges": total_edges, "triggers_rewritten": rewrites}))
    print(json.dumps({"feature_files": n_files, "subfeatures": len(all_sub_defs),
                      "connection_edges": total_edges, "triggers_rewritten": rewrites},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
