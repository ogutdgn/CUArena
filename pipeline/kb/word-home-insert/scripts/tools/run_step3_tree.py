"""Step 3 — the 3-level knowledge tree: app -> features -> subfeatures, + connections.

Grounded in the measured skeleton (Step 2 + the contextual probes): every subfeature maps to
real element id(s) in ui:ribbon-home / ui:ribbon-insert, split-button primary+dropdown fold
into one node, and every contextual edge cites the measured probe. Every node carries the full
identity rubric (what_it_does / how_triggered / what_it_affects / audience) — no name-only
nodes. Home-tab knowledge is adapted from the word-home-tab run (identical element ids, same
build — re-verified against THIS run's measured skeleton by the mechanical checks). Insert-tab
knowledge is authored fresh from this run's measurements; descriptions are grounded in the
controls' own ScreenTips (FullDescription) harvested live.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

RH = ["ui:main-window", "ui:ribbon-home"]
RI = ["ui:main-window", "ui:ribbon-insert"]


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

# ============================== HOME (adapted, ids identical to measured skeleton) ============
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
    "selection from the in-ribbon gallery.", "the paragraph/character style applied", "most",
    ["el:quick-styles-gallery"], opens="ui:styles-gallery", source="uia")
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

# ============================== INSERT (authored fresh from this run's measurements) ==========
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
    "selected picture activates the Picture Format contextual tab (measured).",
    "document content (adds an image)", "everyone",
    ["el:flyout-anchor-insert-pictures"], opens="ui:flyout-anchor-insert-pictures-menu")
sub("subfeature:shapes-insert", "feature:illustrations", "Shapes",
    "Opens a gallery of ready-made shapes (lines, rectangles, arrows, callouts…) to draw into "
    "the document; a selected shape activates the Shape Format contextual tab (measured).",
    "document content (adds a drawn shape)", "most",
    ["el:shapes-insert-gallery"], opens="ui:shapes-insert-dropdown")
sub("subfeature:icon-insert", "feature:illustrations", "Icons",
    "Opens the stock icon library dialog to insert symbol graphics (content streams from the "
    "Office CDN — network).", "document content (adds an icon graphic)", "niche",
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
    "chart activates the Chart Design + Format contextual tabs and opens an embedded Excel "
    "datasheet for its data (measured).",
    "document content (adds a chart backed by worksheet data)", "most",
    ["el:chart-insert"], opens="ui:chart-insert-dialog")
sub("subfeature:screenshot-insert", "feature:illustrations", "Screenshot",
    "Inserts a snapshot of any open window (gallery of live thumbnails) or a Screen Clipping "
    "region; the result is a picture (Picture Format applies).",
    "document content (adds a screenshot image)", "niche",
    ["el:screenshot-insert-gallery"], opens="ui:screenshot-insert-dropdown")
sub("subfeature:online-videos-insert", "feature:media", "Online Videos",
    "Opens a dialog to embed an online video by URL (YouTube etc.); playback happens in-document "
    "(network content).", "document content (adds an embedded video)", "niche",
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
    "the selection to the gallery.", "document content (adds building blocks/fields)", "niche",
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
    "auto-updating field.", "document content (adds date/time text or field)", "niche",
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


# --- connections -------------------------------------------------------------
CLUSTERS = [
    # Home (adopted)
    (["subfeature:bold", "subfeature:italic", "subfeature:underline-gallery",
      "subfeature:strikethrough", "subfeature:subscript", "subfeature:superscript"],
     "affects", "shared-target", "all mutate the selection's character format"),
    (["subfeature:align-left", "subfeature:align-center", "subfeature:align-right",
      "subfeature:align-justify"], "affects", "shared-target",
     "all set paragraph alignment (mutually exclusive)"),
    (["subfeature:bullets-gallery", "subfeature:numbering-gallery",
      "subfeature:multilevel-list"], "affects", "shared-target",
     "all apply list formatting to paragraphs"),
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
    # Insert (authored from this run's measurements)
    (["subfeature:cover-page-insert", "subfeature:blank-page-insert",
      "subfeature:page-break-insert"], "affects", "shared-target",
     "all change the document's page structure/flow"),
    (["subfeature:insert-pictures", "subfeature:shapes-insert", "subfeature:icon-insert",
      "subfeature:insert-3d-models", "subfeature:smart-art-insert", "subfeature:chart-insert",
      "subfeature:screenshot-insert"], "affects", "shared-target",
     "all insert graphic objects (Shapes/InlineShapes) into the document"),
    (["subfeature:header-insert", "subfeature:footer-insert",
      "subfeature:page-number-insert"], "affects", "shared-target",
     "all write into the per-page header/footer stories"),
    (["subfeature:insert-link", "subfeature:bookmark-insert",
      "subfeature:cross-reference-insert"], "uses", "co-location",
     "the navigation-target family (Links group)"),
    (["subfeature:text-box-insert", "subfeature:word-art-insert"], "affects", "shared-target",
     "both create floating text Shapes (both measured to Shape Format context)"),
    (["subfeature:equation-insert-gallery", "subfeature:symbol-insert"], "uses", "co-location",
     "the Symbols group family"),
]
HUBS = {
    "subfeature:font-dialog": (["subfeature:bold", "subfeature:italic",
        "subfeature:underline-gallery", "subfeature:strikethrough", "subfeature:subscript",
        "subfeature:superscript", "subfeature:font", "subfeature:font-size",
        "subfeature:font-color-picker", "subfeature:text-effects", "subfeature:change-case",
        "subfeature:clear-formatting"],
        "uses", "co-location", "consolidated in the Font dialog"),
    "subfeature:paragraph-dialog": (["subfeature:align-left", "subfeature:align-center",
        "subfeature:align-right", "subfeature:align-justify", "subfeature:indent-decrease",
        "subfeature:indent-increase", "subfeature:line-spacing",
        "subfeature:shading-color-picker", "subfeature:borders-selection-gallery"],
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
    # Insert
    ("subfeature:cross-reference-insert", "subfeature:bookmark-insert", "uses", "dependency",
     "cross-references can target bookmarks (B needs A's artifact)"),
    ("subfeature:insert-link", "subfeature:bookmark-insert", "uses", "dependency",
     "hyperlinks can jump to bookmarks ('Bookmarks work with hyperlinks' — the control's own "
     "ScreenTip)"),
    ("subfeature:page-number-insert", "subfeature:header-insert", "uses", "dependency",
     "page numbers are written into the header/footer stories"),
    ("subfeature:page-number-insert", "subfeature:footer-insert", "uses", "dependency",
     "page numbers are written into the header/footer stories"),
    ("subfeature:cover-page-insert", "subfeature:quick-parts-insert", "uses", "inference",
     "cover pages are building blocks from the same gallery system as Quick Parts"),
    ("subfeature:date-and-time-insert", "subfeature:quick-parts-insert", "uses", "inference",
     "an auto-updating date is a field, the machinery Quick Parts exposes"),
    ("subfeature:screenshot-insert", "subfeature:insert-pictures", "affects", "shared-target",
     "a screenshot lands as a picture (same object family / Picture Format context)"),
    ("subfeature:table-insert", "subfeature:sort", "uses", "observed",
     "Sort operates on table contents as well as paragraphs"),
    ("subfeature:table-insert", "subfeature:borders-selection-gallery", "uses", "observed",
     "table borders are edited by the same borders machinery"),
    ("subfeature:paste", "subfeature:insert-pictures", "affects", "observed",
     "pasted images land as the same picture objects"),
    ("subfeature:text-box-insert", "subfeature:font", "uses", "inference",
     "text inside a text box is formatted with the Font tools"),
]
# measured contextual-tab edges: subfeature -> contextual ribbon container
CONTEXTUAL = [
    ("subfeature:table-insert", "ui:ribbon-table-design"),
    ("subfeature:table-insert", "ui:ribbon-table-layout"),
    ("subfeature:insert-pictures", "ui:ribbon-picture-format"),
    ("subfeature:screenshot-insert", "ui:ribbon-picture-format"),
    ("subfeature:shapes-insert", "ui:ribbon-shape-format"),
    ("subfeature:text-box-insert", "ui:ribbon-shape-format"),
    ("subfeature:word-art-insert", "ui:ribbon-shape-format"),
    ("subfeature:word-art-insert", "ui:ribbon-word-art"),
    ("subfeature:smart-art-insert", "ui:ribbon-smart-art-design"),
    ("subfeature:smart-art-insert", "ui:ribbon-smart-art-format"),
    ("subfeature:chart-insert", "ui:ribbon-chart-design"),
    ("subfeature:chart-insert", "ui:ribbon-chart-format"),
    ("subfeature:equation-insert-gallery", "ui:ribbon-equation"),
    ("subfeature:header-insert", "ui:ribbon-header-footer"),
    ("subfeature:footer-insert", "ui:ribbon-header-footer"),
    ("subfeature:page-number-insert", "ui:ribbon-header-footer"),
]
FEATURE_EDGES = [
    ("feature:styles", "feature:font", "uses", "observed", "styles bundle character formatting"),
    ("feature:styles", "feature:paragraph", "uses", "observed",
     "styles bundle paragraph formatting"),
    ("feature:clipboard", "feature:font", "affects", "observed",
     "pasted content carries formatting"),
    ("feature:editing", "feature:clipboard", "uses", "observed",
     "replace edits document content"),
    ("feature:tables", "feature:paragraph", "uses", "observed",
     "table cells contain paragraphs formatted by the Paragraph tools"),
    ("feature:illustrations", "feature:clipboard", "uses", "observed",
     "graphic objects are moved/duplicated through the clipboard"),
    ("feature:header-footer", "feature:pages", "affects", "observed",
     "headers/footers render on every page the page structure creates"),
    ("feature:text", "feature:font", "uses", "inference",
     "text objects carry character formatting"),
]


def build_connections():
    conn = {}

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
    for a, b in CONTEXTUAL:
        add(a, b, "affects", "contextual",
            "measured: inserting/selecting this object makes the contextual tab appear "
            "(run step3-contextual probes)")
    for a, b, kind, source, why in FEATURE_EDGES:
        add(a, b, kind, source, why)
    return conn


def trigger_paths(els, shortcut, base):
    tp = [{"path": base + [e], "kind": "mouse"} for e in els]
    if shortcut:
        tp.append({"path": [], "kind": "keyboard", "shortcut": shortcut})
    return tp


HOME_ELS = None   # filled in main: el -> True for els on Home tab


def main():
    run_id = common.make_run_id() + "-step3-tree"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    conn = build_connections()

    # ground truth: which element ids live on which ribbon (for trigger paths)
    home = json.loads((common.APP_KB / "ui" / "ribbon-home.json").read_text(encoding="utf-8"))
    insert = json.loads((common.APP_KB / "ui" / "ribbon-insert.json").read_text(encoding="utf-8"))
    home_ids = {e["id"] for e in home["children"] if e.get("id")}
    insert_ids = {e["id"] for e in insert["children"] if e.get("id")}

    subs_by_feature = {}
    for s in S:
        subs_by_feature.setdefault(s["feature"], []).append(s["id"])

    version = json.loads((common.APP_KB / "version.json").read_text(encoding="utf-8"))
    for fid, (name, base, does, affects, aud, boundary) in FEATURES.items():
        node = {
            "id": fid, "name": name, "what_it_does": does, "affects": affects,
            "audience_breadth": aud, "location": base[-1],
            "trigger_paths": [{"path": base, "kind": "mouse"}],
            "subfeatures": subs_by_feature.get(fid, []),
            "connections": conn.get(fid, []),
            "boundary": boundary, "source": "inference" if boundary else "measured",
        }
        writer.write_feature(node)

    for s in S:
        # pick the right ribbon path per element (verified against the measured skeleton)
        el0 = s["els"][0]
        base = RH if el0 in home_ids else RI if el0 in insert_ids else None
        assert base, f"{s['id']}: element {el0} not found in either measured ribbon!"
        node = {
            "id": s["id"], "name": s["name"], "parent": s["feature"],
            "what_it_does": s["does"], "affects": s["affects"], "audience_breadth": s["aud"],
            "trigger_paths": trigger_paths(s["els"], s["shortcut"], base),
            "shortcut": s["shortcut"], "opens": s["opens"], "location": base[-1],
            "connections": conn.get(s["id"], []),
            "boundary": s["boundary"], "source": s["source"],
        }
        writer.write_subfeature(node)

    app = {
        "name": "Microsoft Word", "version": version["build"], "platform": "desktop",
        "what_is_it": "A desktop word processor for creating, formatting and editing text "
                      "documents.",
        "used_for": "Writing and formatting documents — letters, reports, essays, resumes — "
                    "with rich text styling, paragraph layout, lists, styles, tables, graphics, "
                    "headers/footers and review tools.",
        "who_uses": "Students, office workers, writers, and virtually anyone producing "
                    "formatted text documents.",
        "layout_regions": ["ui:main-window", "ui:ribbon-home", "ui:ribbon-insert"],
        "feature_inventory": [
            {"id": fid, "name": FEATURES[fid][0],
             "one_liner": FEATURES[fid][2], "trigger_path": FEATURES[fid][1]}
            for fid in FEATURES
        ],
    }
    writer.write_app(app)

    total_edges = sum(len(v) for v in conn.values())
    jrnl.append(common.journal_event(actor="stage3", action="write-tree",
                target="features+subfeatures+app", outcome="ok",
                data={"features": len(FEATURES), "subfeatures": len(S),
                      "connection_edges": total_edges}))
    print(json.dumps({"features": len(FEATURES), "subfeatures": len(S),
                      "connection_edges": total_edges,
                      "subs_per_feature": {k: len(v) for k, v in subs_by_feature.items()}},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
