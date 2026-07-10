"""Contextual-tab knowledge spec (v2) — folds every MEASURED control on every contextual
ribbon tab into feature/sub-feature nodes, so contextual controls become real nodes that
enter the priority ranking (the LESSONS.md dead-end fix).

Design:
  * RULE-BASED, not id-by-id. Each contextual element id is `el:ribbon-<tab>-<suffix>`;
    we strip the tab prefix to a CORE SUFFIX and map that suffix to a sub-feature. This is
    robust to the exact ids the crawl produced and makes shared capabilities (the Arrange /
    Size / Shape-Styles groups repeat identically on every object-format tab) collapse to ONE
    sub-feature reached from MANY tabs (multi-host trigger paths).
  * Variation test (playbook 03 par.1) applied in the fold: border color/weight/pen = OPTIONS
    of `table-borders` (one sub); the 9 cell-align buttons = OPTIONS of `table-cell-alignment`;
    bring-forward/send-backward = the `object-reorder` z-order capability. Controls that do
    DIFFERENT things with different follow-ups stay separate (merge-cells vs split-table).
  * EXISTING nodes hosted on a contextual tab (Header/Footer/Page Number/Date & Time/Quick
    Parts/Pictures on the Header & Footer tab; Sort on Table Layout; Shapes/Text Box on Shape
    Format) are re-used, not re-created — the element becomes an extra trigger path.
  * IDMSO overrides: elements the crawl honestly measured `unexplored` (no fingerprintable
    effect: primary split-button zones whose dropdown is the real surface, mode armers, view
    toggles) but which are known capabilities get a `triggers` marker via idMso knowledge.
  * HONEST unexplored: micro-nudge spinner halves (More/Less height/width) beyond the one that
    carries the capability, and disabled-in-context controls, stay unexplored (journaled).

The module builds CTX_FEATURES / CTX_SUBS / CTX_EXISTING_ELS / CTX_IDMSO_OVERRIDES /
CTX_HONEST_UNEXPLORED at import from the measured ui.json, plus static CTX_CLUSTERS /
CTX_EXTRA / CTX_PRODUCT_VERDICTS. run_step3_tree imports them.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

# ---------------------------------------------------------------------------------------
# FEATURE definitions (contextual). Shared object features are reached from many tabs.
# id -> (name, what_it_does, affects, audience)
FEATURE_META = {
    "feature:table-design": ("Table Design",
        "Style a selected table — apply a table style, toggle which parts the style "
        "emphasizes, and set shading and borders.",
        "the visual style of the selected table", "most"),
    "feature:table-layout": ("Table Layout",
        "Change a selected table's structure — insert/delete rows and columns, merge and "
        "split cells, size and align cells, and sort or convert the contents.",
        "the structure and cell layout of the selected table", "most"),
    "feature:picture-format": ("Picture Format",
        "Adjust and style a selected picture — corrections, color, artistic effects, "
        "compression, picture styles, border, effects and layout.",
        "the appearance of the selected picture", "most"),
    "feature:graphics-format": ("Graphics Format",
        "Style a selected SVG/icon graphic — recolor, graphics styles, outline, effects, and "
        "convert it to an editable shape.",
        "the appearance of the selected graphic", "niche"),
    "feature:shape-format": ("Shape Format (shape-specific)",
        "Shape-specific tools for a selected shape/text box — edit the shape geometry and set "
        "text direction/alignment inside it.",
        "the geometry and in-shape text of the selected shape", "niche"),
    "feature:smartart-design": ("SmartArt Design",
        "Build and restyle a selected SmartArt graphic — add/promote/reorder shapes, change "
        "the layout, colors and style.",
        "the content and style of the selected SmartArt diagram", "niche"),
    "feature:smartart-format": ("SmartArt Format (shape-specific)",
        "Shape-level formatting of individual SmartArt shapes — change/resize the shape.",
        "the individual shapes within the selected SmartArt", "niche"),
    "feature:chart-design": ("Chart Design",
        "Design a selected chart — add chart elements, quick layouts, colors, chart styles, "
        "switch row/column, edit the source data and change the chart type.",
        "the design and data of the selected chart", "niche"),
    "feature:chart-format": ("Chart Format (chart-specific)",
        "Format individual chart elements — select and format a specific chart part.",
        "individual elements of the selected chart", "niche"),
    "feature:equation-tools": ("Equation",
        "Author a mathematical equation in the selected math zone — conversions, symbols and "
        "structures (fractions, scripts, radicals, integrals, matrices…).",
        "the content of the selected equation", "niche"),
    "feature:header-footer-tools": ("Header & Footer Tools",
        "Navigate and configure header/footer editing mode — move between header and footer, "
        "set first-page / odd-even options, position, and close the editor.",
        "the header/footer editing session and its layout options", "most"),
    # ---- shared object features (reached from every object-format tab) ----
    "feature:object-arrange": ("Arrange objects",
        "Position and order any selected drawing object — text wrapping, position, z-order, "
        "alignment, grouping, rotation, the selection pane, and alt text.",
        "the placement, ordering and metadata of the selected object", "most"),
    "feature:object-size": ("Size objects",
        "Set the size of any selected drawing object — its height and width, the size/layout "
        "dialog, and (for images) cropping.",
        "the size of the selected object", "most"),
    "feature:shape-styles": ("Shape styles",
        "Style the fill, outline and effects of a selected shape/chart/SmartArt shape from a "
        "gallery or individually.",
        "the fill/outline/effect styling of the selected drawing object", "most"),
    "feature:wordart-text-styles": ("Text (WordArt) styles",
        "Apply WordArt-style fill, outline and effects to the text inside a selected drawing "
        "object.",
        "the decorative styling of text inside the selected object", "niche"),
}

# ---------------------------------------------------------------------------------------
# SUB-FEATURE definitions. id -> (feature, name, what_it_does, affects, audience)
SUB_META = {
    # ---- Table Design ----
    "subfeature:table-style-options": ("feature:table-design", "Table Style Options",
        "Toggles which parts of the table the current table style emphasizes (header row, "
        "total row, banded rows, first/last column, banded columns).",
        "which table regions the style formats", "most"),
    "subfeature:table-styles": ("feature:table-design", "Table Styles gallery",
        "Applies a built-in table style (borders, shading, banding) from the gallery.",
        "the whole table's style", "most"),
    "subfeature:table-shading": ("feature:table-design", "Table Shading",
        "Fills the selected cells' background with a color from the shading picker.",
        "the selected cells' background fill", "most"),
    "subfeature:table-borders": ("feature:table-design", "Table Borders",
        "Sets the table's borders — border style/pen weight/pen color (options), which edges "
        "get a border, the border painter, and the Borders and Shading dialog.",
        "the selected cells' borders", "most"),
    # ---- Table Layout ----
    "subfeature:table-select": ("feature:table-layout", "Select (table parts)",
        "Selects the cell, row, column or whole table at the cursor.",
        "the current table selection", "niche"),
    "subfeature:table-view-gridlines": ("feature:table-layout", "View Gridlines",
        "Toggles the on-screen display of table cell gridlines (non-printing).",
        "the view (gridline visibility)", "niche"),
    "subfeature:table-properties": ("feature:table-layout", "Table Properties",
        "Opens the Table Properties dialog (size, alignment, text wrapping, row/column/cell "
        "options).", "the table's layout properties", "niche"),
    "subfeature:table-draw": ("feature:table-layout", "Draw Table",
        "Arms a pen to draw table cell boundaries by hand.",
        "the table's cell boundaries (draw mode)", "niche"),
    "subfeature:table-eraser": ("feature:table-layout", "Eraser",
        "Arms an eraser to remove table cell boundaries (merging cells).",
        "the table's cell boundaries (erase mode)", "niche"),
    "subfeature:table-delete": ("feature:table-layout", "Delete",
        "Deletes cells, rows, columns or the whole table (menu).",
        "the table's rows/columns/cells (removal)", "most"),
    "subfeature:table-insert-rows": ("feature:table-layout", "Insert Rows",
        "Inserts a row above or below the current row.",
        "the table's rows (addition)", "most"),
    "subfeature:table-insert-columns": ("feature:table-layout", "Insert Columns",
        "Inserts a column to the left or right of the current column.",
        "the table's columns (addition)", "most"),
    "subfeature:table-insert-cells": ("feature:table-layout", "Insert Cells",
        "Opens the Insert Cells dialog to insert cells and shift the rest.",
        "the table's cells (addition)", "niche"),
    "subfeature:table-merge-cells": ("feature:table-layout", "Merge Cells",
        "Merges the selected cells into one.",
        "the selected cells (merge)", "most"),
    "subfeature:table-split-cells": ("feature:table-layout", "Split Cells",
        "Opens the Split Cells dialog to divide the selected cell(s) into rows/columns.",
        "the selected cells (split)", "most"),
    "subfeature:table-split-table": ("feature:table-layout", "Split Table",
        "Splits the table into two at the current row.",
        "the table (split into two)", "niche"),
    "subfeature:table-autofit": ("feature:table-layout", "AutoFit",
        "Auto-fits column widths to contents, to the window, or to a fixed width (menu).",
        "the table's column widths", "most"),
    "subfeature:table-cell-size": ("feature:table-layout", "Cell Size",
        "Sets exact row height and column width (nudges + fields) and distributes rows/columns "
        "evenly.", "the selected cells' height and width", "most"),
    "subfeature:table-cell-alignment": ("feature:table-layout", "Cell Alignment",
        "Aligns cell contents to one of the nine positions (top/middle/bottom × "
        "left/center/right).", "the alignment of content within the selected cells", "most"),
    "subfeature:table-text-direction": ("feature:table-layout", "Text Direction",
        "Rotates the text direction within the selected cells.",
        "the text orientation within the selected cells", "niche"),
    "subfeature:table-cell-margins": ("feature:table-layout", "Cell Margins",
        "Opens the Cell Options/Table Options dialog to set cell margins and spacing.",
        "the selected cells' internal margins", "niche"),
    "subfeature:table-repeat-header": ("feature:table-layout", "Repeat Header Rows",
        "Repeats the header row(s) at the top of each page the table spans.",
        "the table's page-break header behavior", "niche"),
    "subfeature:table-convert-to-text": ("feature:table-layout", "Convert to Text",
        "Opens a dialog to convert the table back to delimited text.",
        "the table (converted to paragraphs)", "niche"),
    "subfeature:table-formula": ("feature:table-layout", "Formula",
        "Opens the Formula dialog to compute a value (SUM, AVERAGE…) in a table cell.",
        "the selected cell (adds a formula field)", "niche"),
    # ---- Picture Format ----
    "subfeature:picture-remove-background": ("feature:picture-format", "Remove Background",
        "Enters Background Removal mode to auto-detect and delete the picture's background.",
        "the picture's visible area (background removal)", "niche"),
    "subfeature:picture-corrections": ("feature:picture-format", "Corrections",
        "Adjusts the picture's sharpness, brightness and contrast (gallery + options).",
        "the picture's brightness/contrast/sharpness", "most"),
    "subfeature:picture-color": ("feature:picture-format", "Color",
        "Recolors the picture — saturation, tone, and recolor presets (gallery + options).",
        "the picture's color", "most"),
    "subfeature:picture-artistic-effects": ("feature:picture-format", "Artistic Effects",
        "Applies a painterly/artistic filter to the picture from a gallery.",
        "the picture's artistic rendering", "niche"),
    "subfeature:picture-transparency": ("feature:picture-format", "Transparency",
        "Sets the picture's overall transparency from presets.",
        "the picture's transparency", "niche"),
    "subfeature:picture-compress": ("feature:picture-format", "Compress Pictures",
        "Opens the Compress Pictures dialog to reduce image resolution/file size.",
        "the picture's stored resolution/size", "niche"),
    "subfeature:picture-change": ("feature:picture-format", "Change Picture",
        "Replaces the picture with another (from file/stock/online) keeping formatting.",
        "the picture's source image", "niche"),
    "subfeature:picture-reset": ("feature:picture-format", "Reset Picture",
        "Discards formatting changes (and optionally size) applied to the picture.",
        "the picture's formatting (reset)", "niche"),
    "subfeature:picture-style-gallery": ("feature:picture-format", "Picture Styles gallery",
        "Applies a framed/shadowed/3D picture style from the gallery.",
        "the picture's frame/style", "most"),
    "subfeature:picture-border": ("feature:picture-format", "Picture Border",
        "Sets the picture's border color, weight and dash style (options in the picker).",
        "the picture's border", "most"),
    "subfeature:picture-effects": ("feature:picture-format", "Picture Effects",
        "Applies shadow/reflection/glow/bevel/3D effects to the picture (menu of effect "
        "families).", "the picture's visual effects", "niche"),
    "subfeature:picture-convert-to-smartart": ("feature:picture-format",
        "Picture Layout (convert to SmartArt)",
        "Converts the picture(s) into a captioned SmartArt layout.",
        "the picture (converted to a SmartArt layout)", "niche"),
    "subfeature:picture-format-pane": ("feature:picture-format", "Format Picture pane",
        "Opens the Format Picture pane — the full fill/line/effects/picture-adjust surface.",
        "the picture's full formatting (pane)", "niche"),
    # ---- Graphics Format ----
    "subfeature:graphics-change": ("feature:graphics-format", "Change Graphic",
        "Replaces the SVG/icon graphic with another from the library.",
        "the graphic's source", "niche"),
    "subfeature:graphics-convert-to-shape": ("feature:graphics-format", "Convert to Shape",
        "Converts the SVG graphic into an editable Word shape (or group of shapes).",
        "the graphic (converted to editable shapes)", "niche"),
    "subfeature:graphics-style-gallery": ("feature:graphics-format", "Graphics Styles gallery",
        "Applies a preset fill/outline style to the graphic from the gallery.",
        "the graphic's style", "niche"),
    "subfeature:graphics-color": ("feature:graphics-format", "Graphics Fill (recolor)",
        "Recolors the graphic's fill from the color picker.",
        "the graphic's fill color", "niche"),
    "subfeature:graphics-border": ("feature:graphics-format", "Graphics Outline",
        "Sets the graphic's outline color/weight/dashes (options in the picker).",
        "the graphic's outline", "niche"),
    "subfeature:graphics-effects": ("feature:graphics-format", "Graphics Effects",
        "Applies shadow/reflection/glow/3D effects to the graphic (menu).",
        "the graphic's visual effects", "niche"),
    "subfeature:graphics-format-pane": ("feature:graphics-format", "Format Graphic pane",
        "Opens the Format Graphic pane — the full fill/line/effects surface.",
        "the graphic's full formatting (pane)", "niche"),
    # ---- Shape Format (shape-specific) ----
    "subfeature:shape-edit": ("feature:shape-format", "Edit Shape",
        "Changes the shape to another or edits its edit-points/geometry (menu).",
        "the selected shape's geometry", "niche"),
    "subfeature:shape-text-direction": ("feature:shape-format", "Text Direction (in shape)",
        "Rotates the direction of text inside the shape/text box.",
        "the text orientation inside the shape", "niche"),
    "subfeature:shape-text-align": ("feature:shape-format", "Align Text (in shape)",
        "Aligns text vertically within the shape/text box (top/middle/bottom).",
        "the vertical alignment of text inside the shape", "niche"),
    "subfeature:shape-text-link": ("feature:shape-format", "Create Text Box Link",
        "Links text boxes so overflowing text flows from one into the next.",
        "the text-flow link between text boxes", "niche"),
    # ---- SmartArt Design ----
    "subfeature:smartart-add-shape": ("feature:smartart-design", "Add Shape",
        "Adds a shape/node to the SmartArt graphic (before/after/above/below via the menu).",
        "the SmartArt graphic's nodes (addition)", "niche"),
    "subfeature:smartart-add-bullet": ("feature:smartart-design", "Add Bullet",
        "Adds a sub-bullet text item to the selected SmartArt node.",
        "the SmartArt node's sub-items", "niche"),
    "subfeature:smartart-text-pane": ("feature:smartart-design", "Text Pane",
        "Toggles the text outline pane for editing the SmartArt's text as a bulleted list.",
        "opens the SmartArt text pane", "niche"),
    "subfeature:smartart-promote-demote": ("feature:smartart-design", "Promote / Demote",
        "Changes the outline level of the selected SmartArt node (promote/demote), and moves "
        "it up/down in order.", "the selected SmartArt node's level/order", "niche"),
    "subfeature:smartart-reverse": ("feature:smartart-design", "Right to Left",
        "Reverses the left-to-right order of the SmartArt layout.",
        "the SmartArt layout direction", "niche"),
    "subfeature:smartart-org-layout": ("feature:smartart-design", "Organization Layout",
        "Changes the hanging/branch layout of an organization-chart SmartArt (menu).",
        "the org-chart branch layout", "niche"),
    "subfeature:smartart-layout": ("feature:smartart-design", "Layouts gallery",
        "Changes the SmartArt's overall layout (list, process, cycle, hierarchy…) from the "
        "gallery.", "the SmartArt graphic's layout", "niche"),
    "subfeature:smartart-change-colors": ("feature:smartart-design", "Change Colors",
        "Applies a color scheme to the SmartArt from the gallery.",
        "the SmartArt graphic's color scheme", "niche"),
    "subfeature:smartart-style": ("feature:smartart-design", "SmartArt Styles gallery",
        "Applies a visual style (3D, shadow, gradient…) to the SmartArt from the gallery.",
        "the SmartArt graphic's visual style", "niche"),
    "subfeature:smartart-reset": ("feature:smartart-design", "Reset Graphic",
        "Discards all formatting changes back to the default SmartArt appearance.",
        "the SmartArt graphic's formatting (reset)", "niche"),
    "subfeature:smartart-shape-edit": ("feature:smartart-format", "Edit SmartArt Shape",
        "Changes or resizes an individual shape within the SmartArt (larger/smaller/change/"
        "edit in 2-D).", "an individual SmartArt shape's geometry/size", "niche"),
    # ---- Chart Design ----
    "subfeature:chart-add-element": ("feature:chart-design", "Add Chart Element",
        "Adds/removes chart elements — axes, titles, data labels, gridlines, legend, "
        "trendlines (menu).", "which elements the chart displays", "niche"),
    "subfeature:chart-quick-layout": ("feature:chart-design", "Quick Layout",
        "Applies a preset arrangement of the chart's elements from a gallery.",
        "the chart's element layout", "niche"),
    "subfeature:chart-change-colors": ("feature:chart-design", "Change Colors",
        "Applies a color scheme to the chart's data series from a gallery.",
        "the chart's color scheme", "niche"),
    "subfeature:chart-style": ("feature:chart-design", "Chart Styles gallery",
        "Applies an overall visual style to the chart from the gallery.",
        "the chart's visual style", "niche"),
    "subfeature:chart-switch-row-column": ("feature:chart-design", "Switch Row/Column",
        "Swaps which of the source data's rows and columns map to the chart's axis vs series.",
        "the chart's data orientation", "niche"),
    "subfeature:chart-edit-data": ("feature:chart-design", "Edit / Select Data",
        "Accesses the chart's underlying worksheet data — edit data (opens the linked Excel "
        "workbook), select data range, show the data grid, and refresh.",
        "the chart's source data", "niche"),
    "subfeature:chart-change-type": ("feature:chart-design", "Change Chart Type",
        "Opens the Change Chart Type dialog to switch the chart to a different type.",
        "the chart's type", "niche"),
    # ---- Chart Format (chart-element-specific) ----
    "subfeature:chart-select-element": ("feature:chart-format", "Chart Elements selector",
        "Selects a specific chart element (series, axis, legend…) to format via the dropdown.",
        "which chart element is selected", "niche"),
    "subfeature:chart-format-selection": ("feature:chart-format", "Format Selection",
        "Opens the format pane for the selected chart element, and resets it to the style "
        "default.", "the selected chart element's formatting", "niche"),
    # ---- Equation ----
    "subfeature:equation-ink": ("feature:equation-tools", "Ink Equation",
        "Opens a canvas to hand-write a math equation that is recognized into typeset math.",
        "the equation content (ink input)", "niche"),
    "subfeature:equation-conversions": ("feature:equation-tools", "Conversions",
        "Converts the equation's notation between professional/linear, Unicode, LaTeX and text "
        "(Convert menu + Equation Options).",
        "the equation's notation format", "niche"),
    "subfeature:equation-symbols": ("feature:equation-tools", "Equation Symbols",
        "Inserts a mathematical symbol (operators, Greek letters, arrows…) from the gallery.",
        "the equation content (adds a symbol)", "niche"),
    "subfeature:equation-structures": ("feature:equation-tools", "Structures",
        "Inserts a math structure template into the equation — fraction, script, radical, "
        "integral, large operator, bracket, function, accent, limit/log, operator, or matrix "
        "(a palette of templates).", "the equation content (adds a structure)", "niche"),
    # ---- Header & Footer Tools ----
    "subfeature:hf-document-info": ("feature:header-footer-tools", "Document Info",
        "Inserts document-property fields (author, file name, path…) into the header/footer.",
        "the header/footer content (document-info fields)", "niche"),
    "subfeature:hf-navigate": ("feature:header-footer-tools", "Header/Footer Navigation",
        "Moves the cursor between the header and footer and between sections' "
        "headers/footers (go to header/footer, previous, next).",
        "the header/footer editing position", "most"),
    "subfeature:hf-link-to-previous": ("feature:header-footer-tools", "Link to Previous",
        "Links this section's header/footer to the previous section's (or breaks the link).",
        "whether this section reuses the previous header/footer", "niche"),
    "subfeature:hf-options": ("feature:header-footer-tools", "Header/Footer Options",
        "Toggles header/footer display options — different first page, different odd & even "
        "pages, and showing the document text.",
        "the header/footer display options", "most"),
    "subfeature:hf-position": ("feature:header-footer-tools", "Header/Footer Position",
        "Sets the distance of the header/footer from the top/bottom page edge.",
        "the header/footer position on the page", "niche"),
    "subfeature:hf-alignment-tab": ("feature:header-footer-tools", "Insert Alignment Tab",
        "Inserts an alignment tab so header/footer content can be left/center/right aligned "
        "on one line.", "the header/footer content (alignment tab)", "niche"),
    "subfeature:hf-close": ("feature:header-footer-tools", "Close Header and Footer",
        "Exits header/footer editing mode and returns to the document body.",
        "the header/footer editing session (exit)", "most"),
    # ---- shared: object-arrange ----
    "subfeature:object-position": ("feature:object-arrange", "Position",
        "Places the object at a preset position on the page with text wrapping (gallery).",
        "the object's page position", "most"),
    "subfeature:object-text-wrap": ("feature:object-arrange", "Wrap Text",
        "Sets how document text wraps around the object (in line, square, tight, behind…).",
        "how text flows around the object", "most"),
    "subfeature:object-reorder": ("feature:object-arrange", "Bring Forward / Send Backward",
        "Changes the object's z-order relative to other objects and the text (bring "
        "forward/to front, send backward/to back — variations of z-order).",
        "the object's stacking order", "most"),
    "subfeature:object-align": ("feature:object-arrange", "Align",
        "Aligns/distributes the selected object(s) to the page/margin/each other (menu).",
        "the object's alignment", "most"),
    "subfeature:object-group": ("feature:object-arrange", "Group",
        "Groups multiple objects into one (or ungroups) so they move together.",
        "the grouping of the selected objects", "niche"),
    "subfeature:object-rotate": ("feature:object-arrange", "Rotate",
        "Rotates or flips the object (right 90°, flip horizontal/vertical, more options).",
        "the object's rotation", "most"),
    "subfeature:object-selection-pane": ("feature:object-arrange", "Selection Pane",
        "Opens the Selection pane listing every object for show/hide/reorder/rename.",
        "opens the Selection pane", "niche"),
    "subfeature:object-alt-text": ("feature:object-arrange", "Alt Text",
        "Opens the Alt Text pane to author accessibility descriptions for the object.",
        "the object's accessibility alt text", "niche"),
    # ---- shared: object-size ----
    "subfeature:object-size": ("feature:object-size", "Object Size",
        "Sets the object's exact height and width (nudge fields) and opens the Layout/Size "
        "dialog.", "the object's height and width", "most"),
    "subfeature:picture-crop": ("feature:object-size", "Crop",
        "Crops the image to hide its edges, to a shape, aspect ratio, or fill/fit (menu).",
        "the image's visible crop area", "most"),
    # ---- shared: shape-styles ----
    "subfeature:shape-style-gallery": ("feature:shape-styles", "Shape Styles gallery",
        "Applies a preset fill+outline+effect style to the shape from the gallery.",
        "the shape's overall style", "most"),
    "subfeature:shape-fill": ("feature:shape-styles", "Shape Fill",
        "Sets the shape's fill — color, gradient, picture, texture (options in the picker).",
        "the shape's fill", "most"),
    "subfeature:shape-outline": ("feature:shape-styles", "Shape Outline",
        "Sets the shape's outline color, weight and dashes (options in the picker).",
        "the shape's outline", "most"),
    "subfeature:shape-effects": ("feature:shape-styles", "Shape Effects",
        "Applies shadow/reflection/glow/bevel/3D effects to the shape (menu of families).",
        "the shape's visual effects", "niche"),
    "subfeature:shape-format-pane": ("feature:shape-styles", "Format Shape pane",
        "Opens the Format Shape pane — the full fill/line/effects/text surface.",
        "the shape's full formatting (pane)", "niche"),
    # ---- shared: wordart-text-styles ----
    "subfeature:wordart-text-style-gallery": ("feature:wordart-text-styles",
        "WordArt Styles gallery",
        "Applies a preset WordArt style to the text inside the object from the gallery.",
        "the decorative style of text inside the object", "niche"),
    "subfeature:wordart-text-fill": ("feature:wordart-text-styles", "Text Fill",
        "Sets the fill color/gradient of the object's text (options in the picker).",
        "the fill of text inside the object", "niche"),
    "subfeature:wordart-text-outline": ("feature:wordart-text-styles", "Text Outline",
        "Sets the outline of the object's text (options in the picker).",
        "the outline of text inside the object", "niche"),
    "subfeature:wordart-text-effects": ("feature:wordart-text-styles", "Text Effects",
        "Applies shadow/reflection/glow/3D/transform effects to the object's text, incl. the "
        "Format Text Effects dialog.", "the effects on text inside the object", "niche"),
}

# ---------------------------------------------------------------------------------------
# SUFFIX -> subfeature id. The core suffix is the element id with `el:ribbon-<tab>-` stripped.
# One suffix may fold into a shared sub (object-*). Order-independent; exact-match then no-match.
SUFFIX_SUB = {
    # table design
    "table-style-header-row": "subfeature:table-style-options",
    "table-style-total-row": "subfeature:table-style-options",
    "table-style-banded-rows": "subfeature:table-style-options",
    "table-styles-first-column": "subfeature:table-style-options",
    "table-style-last-column": "subfeature:table-style-options",
    "table-style-banded-columns": "subfeature:table-style-options",
    "table-styles-gallery": "subfeature:table-styles",
    "shading-color-picker": "subfeature:table-shading",
    "shading-color-picker-dropdown": "subfeature:table-shading",
    "border-styles-gallery": "subfeature:table-borders",
    "border-styles-gallery-dropdown": "subfeature:table-borders",
    "pen-style": "subfeature:table-borders",
    "pen-weight": "subfeature:table-borders",
    "border-color-picker": "subfeature:table-borders",
    "border-color-picker-dropdown": "subfeature:table-borders",
    "borders-selection-gallery": "subfeature:table-borders",
    "borders-selection-gallery-dropdown": "subfeature:table-borders",
    "table-paint-border": "subfeature:table-borders",
    "borders-shading-dialog": "subfeature:table-borders",
    # table layout
    "table-select-menu": "subfeature:table-select",
    "table-show-gridlines": "subfeature:table-view-gridlines",
    "table-properties-dialog": "subfeature:table-properties",
    "table-draw-table": "subfeature:table-draw",
    "table-eraser": "subfeature:table-eraser",
    "table-delete-rows-and-columns-menu": "subfeature:table-delete",
    "table-rows-insert-above": "subfeature:table-insert-rows",
    "table-rows-insert-below": "subfeature:table-insert-rows",
    "table-columns-insert-left": "subfeature:table-insert-columns",
    "table-columns-insert-right": "subfeature:table-insert-columns",
    "table-insert-cells-dialog": "subfeature:table-insert-cells",
    "merge-cells": "subfeature:table-merge-cells",
    "split-cells": "subfeature:table-split-cells",
    "table-split-table": "subfeature:table-split-table",
    "table-auto-fit-menu": "subfeature:table-autofit",
    "table-rows-distribute": "subfeature:table-cell-size",
    "table-columns-distribute": "subfeature:table-cell-size",
    "table-cell-align-top-left": "subfeature:table-cell-alignment",
    "table-cell-align-top-center": "subfeature:table-cell-alignment",
    "table-cell-align-top-right": "subfeature:table-cell-alignment",
    "table-cell-align-middle-left": "subfeature:table-cell-alignment",
    "table-cell-align-middle-center": "subfeature:table-cell-alignment",
    "table-cell-align-middle-right": "subfeature:table-cell-alignment",
    "table-cell-align-bottom-left": "subfeature:table-cell-alignment",
    "table-cell-align-bottom-center": "subfeature:table-cell-alignment",
    "table-cell-align-bottom-right": "subfeature:table-cell-alignment",
    "text-direction": "subfeature:table-text-direction",
    "table-options-dialog": "subfeature:table-cell-margins",
    "table-repeat-header-rows": "subfeature:table-repeat-header",
    "convert-table-to-text": "subfeature:table-convert-to-text",
    "table-formula-dialog": "subfeature:table-formula",
    # picture format
    "picture-background-removal": "subfeature:picture-remove-background",
    "picture-corrections-menu": "subfeature:picture-corrections",
    "picture-color-menu": "subfeature:picture-color",
    "picture-artistic-effects-gallery": "subfeature:picture-artistic-effects",
    "picture-transparency-gallery": "subfeature:picture-transparency",
    "pictures-compress": "subfeature:picture-compress",
    "picture-change-menu": "subfeature:picture-change",
    "picture-reset": "subfeature:picture-reset",
    "picture-reset-dropdown": "subfeature:picture-reset",
    "picture-styles-gallery": "subfeature:picture-style-gallery",
    "picture-effects-menu": "subfeature:picture-effects",
    "pictures-convert-to-smart-art": "subfeature:picture-convert-to-smartart",
    "picture-format-dialog": "subfeature:picture-format-pane",
    # graphics format
    "graphic-change-menu": "subfeature:graphics-change",
    "svgedit": "subfeature:graphics-convert-to-shape",
    "graphics-styles-gallery": "subfeature:graphics-style-gallery",
    "graphics-color-picker": "subfeature:graphics-color",
    "graphics-color-picker-dropdown": "subfeature:graphics-color",
    "graphics-outline-color-picker": "subfeature:graphics-border",
    "graphics-outline-color-picker-dropdown": "subfeature:graphics-border",
    "graphics-effects-menu": "subfeature:graphics-effects",
    "graphics-format-dialog": "subfeature:graphics-format-pane",
    # shape format (shape-specific)
    "object-edit-shape-menu": "subfeature:shape-edit",
    "text-direction-gallery": "subfeature:shape-text-direction",
    "text-align-gallery": "subfeature:shape-text-align",
    "text-box-link-create": "subfeature:shape-text-link",
    # smartart design
    "smart-art-add-shape": "subfeature:smartart-add-shape",
    "smart-art-add-shape-dropdown": "subfeature:smartart-add-shape",
    "smart-art-add-bullet": "subfeature:smartart-add-bullet",
    "smart-art-text-pane": "subfeature:smartart-text-pane",
    "smart-art-promote": "subfeature:smartart-promote-demote",
    "smart-art-demote": "subfeature:smartart-promote-demote",
    "smart-art-reorder-up": "subfeature:smartart-promote-demote",
    "smart-art-reorder-down": "subfeature:smartart-promote-demote",
    "smart-art-right-to-left": "subfeature:smartart-reverse",
    "smart-art-organization-chart-menu": "subfeature:smartart-org-layout",
    "smart-art-layout-gallery": "subfeature:smartart-layout",
    "smart-art-change-colors-gallery": "subfeature:smartart-change-colors",
    "smart-art-styles-gallery": "subfeature:smartart-style",
    "smart-art-reset-graphic": "subfeature:smartart-reset",
    # smartart format (shape-specific size/2d)
    "smart-art-edit-in2-d": "subfeature:smartart-shape-edit",
    "smart-art-larger-shape": "subfeature:smartart-shape-edit",
    "smart-art-smaller-shape": "subfeature:smartart-shape-edit",
    # shared "change the selected shape" (shape/smartart/chart format Insert-Shapes group)
    "shape-change-shape-gallery": "subfeature:shape-edit",
    # chart format (element-specific)
    "chart-element-selector": "subfeature:chart-select-element",
    "chart-format-selection": "subfeature:chart-format-selection",
    "chart-reset-to-match-style": "subfeature:chart-format-selection",
    # chart design
    "add-chart-element-menu": "subfeature:chart-add-element",
    "chart-layout-gallery": "subfeature:chart-quick-layout",
    "chart-colors-gallery": "subfeature:chart-change-colors",
    "chart-styles-gallery": "subfeature:chart-style",
    "chart-switch-row-column": "subfeature:chart-switch-row-column",
    "chart-edit-data-source": "subfeature:chart-edit-data",
    "chart-show-data-grid": "subfeature:chart-edit-data",
    "chart-show-data-grid-dropdown": "subfeature:chart-edit-data",
    "chart-refresh": "subfeature:chart-edit-data",
    "chart-change-type": "subfeature:chart-change-type",
    # equation
    "ink-equation": "subfeature:equation-ink",
    "equation-unicode-format": "subfeature:equation-conversions",
    "equation-la-tex-format": "subfeature:equation-conversions",
    "equation-normal-text": "subfeature:equation-conversions",
    "equation-convert": "subfeature:equation-conversions",
    "equation-convert-dropdown": "subfeature:equation-conversions",
    "equation-options": "subfeature:equation-conversions",
    "equation-symbols-insert-gallery": "subfeature:equation-symbols",
    "equation-fraction-gallery": "subfeature:equation-structures",
    "equation-script-gallery": "subfeature:equation-structures",
    "equation-radical-gallery": "subfeature:equation-structures",
    "equation-integral-gallery": "subfeature:equation-structures",
    "equation-large-operator-gallery": "subfeature:equation-structures",
    "equation-delimiter-gallery": "subfeature:equation-structures",
    "equation-function-gallery": "subfeature:equation-structures",
    "equation-accent-gallery": "subfeature:equation-structures",
    "equation-limit-gallery": "subfeature:equation-structures",
    "equation-operator-gallery": "subfeature:equation-structures",
    "equation-matrix-gallery": "subfeature:equation-structures",
    # header & footer tools
    "document-info": "subfeature:hf-document-info",
    "go-to-header": "subfeature:hf-navigate",
    "go-to-footer": "subfeature:hf-navigate",
    "header-footer-previous-section": "subfeature:hf-navigate",
    "header-footer-next-section": "subfeature:hf-navigate",
    "header-footer-link-to-previous": "subfeature:hf-link-to-previous",
    "header-footer-different-first-page": "subfeature:hf-options",
    "header-footer-different-odd-even-page": "subfeature:hf-options",
    "header-footer-show-document-text": "subfeature:hf-options",
    "insert-alignment-tab": "subfeature:hf-alignment-tab",
    "header-footer-close": "subfeature:hf-close",
    # shared: object-arrange
    "picture-position-gallery": "subfeature:object-position",
    "text-wrap-gallery": "subfeature:object-text-wrap",
    "object-bring-forward": "subfeature:object-reorder",
    "object-bring-forward-dropdown": "subfeature:object-reorder",
    "object-send-backward": "subfeature:object-reorder",
    "object-send-backward-dropdown": "subfeature:object-reorder",
    "object-align-menu": "subfeature:object-align",
    "objects-group-menu": "subfeature:object-group",
    "object-rotate-gallery": "subfeature:object-rotate",
    "selection-pane": "subfeature:object-selection-pane",
    "alt-text-pane-ribbon": "subfeature:object-alt-text",
    # shared: object-size
    "more": "subfeature:object-size",
    "less": "subfeature:object-size",
    "layout-options-dialog-size": "subfeature:object-size",
    "picture-crop": "subfeature:picture-crop",
    "picture-crop-dropdown": "subfeature:picture-crop",
    # shared: shape-styles
    "shape-styles-gallery": "subfeature:shape-style-gallery",
    "shape-fill-color-picker": "subfeature:shape-fill",
    "shape-fill-color-picker-dropdown": "subfeature:shape-fill",
    "outline-color-picker": "subfeature:shape-outline",
    "outline-color-picker-dropdown": "subfeature:shape-outline",
    "shape-effects-menu": "subfeature:shape-effects",
    "object-format-dialog": "subfeature:shape-format-pane",
    # shared: wordart-text-styles
    "text-styles-gallery": "subfeature:wordart-text-style-gallery",
    "text-fill-color-picker": "subfeature:wordart-text-fill",
    "text-fill-color-picker-dropdown": "subfeature:wordart-text-fill",
    "text-outline-color-picker": "subfeature:wordart-text-outline",
    "text-outline-color-picker-dropdown": "subfeature:wordart-text-outline",
    "text-effects-menu": "subfeature:wordart-text-effects",
    "word-art-format-dialog": "subfeature:wordart-text-effects",
}

# TAB-AWARE overrides for suffixes whose meaning differs by tab (checked before SUFFIX_SUB):
# (tab_cid, suffix) -> subfeature id.
TAB_SUFFIX_SUB = {
    # "More/Less" spinner halves mean different sizes on different tabs
    ("ui:ribbon-table-layout", "more"): "subfeature:table-cell-size",
    ("ui:ribbon-table-layout", "less"): "subfeature:table-cell-size",
    ("ui:ribbon-header-footer", "more"): "subfeature:hf-position",
    ("ui:ribbon-header-footer", "less"): "subfeature:hf-position",
    # on Picture Format the shared "outline-color-picker" slug IS the Picture Border
    ("ui:ribbon-picture-format", "outline-color-picker"): "subfeature:picture-border",
    ("ui:ribbon-picture-format", "outline-color-picker-dropdown"): "subfeature:picture-border",
}

# Existing Home/Insert nodes hosted on a contextual tab: suffix -> existing subfeature id
SUFFIX_EXISTING = {
    "sort-dialog-classic": "subfeature:sort",             # Table Layout Data > Sort
    "shapes-insert-gallery": "subfeature:shapes-insert",  # Shape/Chart Format Insert Shapes
    "text-box-insert": "subfeature:text-box-insert",      # Shape Format Draw Text Box
    "equation-insert-gallery": "subfeature:equation-insert-gallery",   # Equation Tools>Equation
    # Header & Footer tab Insert group re-hosts these Insert-tab capabilities
    "header-insert-gallery": "subfeature:header-insert",
    "footer-insert-gallery": "subfeature:footer-insert",
    "header-footer-page-number-insert": "subfeature:page-number-insert",
    "date-and-time-insert": "subfeature:date-and-time-insert",
    "quick-parts-insert-gallery": "subfeature:quick-parts-insert",
    "picture-insert-from-file": "subfeature:insert-pictures",
    "clip-art-insert-dialog": "subfeature:insert-pictures",   # H&F Insert > Online Pictures
}

# Suffixes whose element the crawl measured `unexplored` but which are known capabilities:
# suffix -> reason (a primary split-button zone whose dropdown is the real surface; a mode
# armer; a view toggle). Applied only when the measured element is unexplored.
IDMSO_OVERRIDE_SUFFIX = {
    "shading-color-picker": "primary zone applies the last-used cell shading (dropdown = picker)",
    "border-styles-gallery": "primary zone applies the last-used border style (dropdown = gallery)",
    "border-color-picker": "primary zone applies the last-used pen color (dropdown = picker)",
    "table-paint-border": "arms the Border Painter mode",
    "table-show-gridlines": "toggles the non-printing gridline view",
    "table-draw-table": "arms the draw-table pen mode",
    "table-eraser": "arms the eraser mode",
    "table-repeat-header-rows": "toggles header-row repetition across pages",
    "picture-reset": "primary zone resets the picture (dropdown = reset incl. size)",
    "picture-styles-gallery": "primary applies the selected picture style tile",
    "smart-art-text-pane": "toggles the SmartArt text outline pane",
    "smart-art-reset-graphic": "resets the SmartArt to default formatting",
    "object-bring-forward": "primary zone brings the object forward one step (dropdown = to front)",
    "object-send-backward": "primary zone sends the object back one step (dropdown = to back)",
    "shapes-insert-gallery": "opens the Insert Shapes gallery (hosted Shapes capability)",
    "shape-fill-color-picker": "primary zone applies the last-used fill (dropdown = picker)",
    "chart-edit-data-source": "opens the chart's linked worksheet (external Excel editor)",
    "chart-show-data-grid": "primary zone shows the data grid (dropdown = Edit Data in Excel)",
    "text-fill-color-picker": "primary zone applies the last-used text fill (dropdown = picker)",
    "text-styles-gallery": "applies the selected WordArt text style tile",
    "graphics-color-picker": "primary zone applies the last-used recolor (dropdown = picker)",
    "graphics-outline-color-picker": "primary zone applies the last-used outline (dropdown = picker)",
    "outline-color-picker": "primary zone applies the last-used outline (dropdown = picker)",
    "chart-reset-to-match-style": "resets the selected chart element to the style default",
}

# ---------------------------------------------------------------------------------------
# Requires: contextual subs require their summoning capability. Beyond the auto summoner edge
# (added in run_step3_tree from CTX_SUBS[].requires), a few cross-capability requires:
SUB_REQUIRES = {
    # every table-layout/design sub requires a table (the summoner) — handled by feature requires
}

# static connections among contextual nodes (affects-same clusters)
CTX_CLUSTERS = [
    (["subfeature:object-position", "subfeature:object-text-wrap", "subfeature:object-align",
      "subfeature:object-rotate", "subfeature:object-reorder"], "affects-same", "shared-target",
     "all reposition/reorder the same selected object on the page"),
    (["subfeature:shape-fill", "subfeature:shape-outline", "subfeature:shape-effects",
      "subfeature:shape-style-gallery"], "affects-same", "shared-target",
     "all style the same shape's fill/outline/effect"),
    (["subfeature:table-insert-rows", "subfeature:table-insert-columns",
      "subfeature:table-delete", "subfeature:table-merge-cells", "subfeature:table-split-cells"],
     "affects-same", "shared-target", "all restructure the same table's cells"),
    (["subfeature:picture-corrections", "subfeature:picture-color",
      "subfeature:picture-artistic-effects", "subfeature:picture-transparency"],
     "affects-same", "shared-target", "all adjust the same picture's rendering"),
]
CTX_EXTRA = [
    # feature-level requires are added from CTX_FEATURES[].requires in run_step3_tree
]

# ---------------------------------------------------------------------------------------
# Which contextual FEATURE requires which universe capability (its summoner):
FEATURE_REQUIRES = {
    "feature:table-design": ["subfeature:table-insert"],
    "feature:table-layout": ["subfeature:table-insert"],
    "feature:picture-format": ["subfeature:insert-pictures"],
    "feature:graphics-format": ["subfeature:icon-insert"],
    "feature:shape-format": ["subfeature:shapes-insert"],
    "feature:smartart-design": ["subfeature:smart-art-insert"],
    "feature:smartart-format": ["subfeature:smart-art-insert"],
    "feature:chart-design": ["subfeature:chart-insert"],
    "feature:chart-format": ["subfeature:chart-insert"],
    "feature:equation-tools": ["subfeature:equation-insert-gallery"],
    "feature:header-footer-tools": ["subfeature:header-insert"],
    # shared object features require at least one object-inserting capability; model the
    # closure via the most representative (pictures — the everyday object)
    "feature:object-arrange": ["subfeature:insert-pictures"],
    "feature:object-size": ["subfeature:insert-pictures"],
    "feature:shape-styles": ["subfeature:shapes-insert"],
    "feature:wordart-text-styles": ["subfeature:shapes-insert"],
}

# product-purpose verdicts for contextual subs: id -> (verdict, Y)
CTX_PRODUCT_VERDICTS = {
    "subfeature:table-style-options": ("useful", "toggles which table regions the style "
        "emphasizes — routine table styling"),
    "subfeature:table-styles": ("important", "applies a whole-table visual style — the "
        "primary way tables are made presentable"),
    "subfeature:table-shading": ("useful", "shades cell backgrounds — common table emphasis"),
    "subfeature:table-borders": ("important", "sets table borders — near-universal in "
        "presented tables"),
    "subfeature:table-select": ("useful", "selects table parts — a precondition convenience"),
    "subfeature:table-view-gridlines": ("useful", "toggles gridline view — an editing aid"),
    "subfeature:table-properties": ("useful", "sets precise table layout properties — "
        "power-table work"),
    "subfeature:table-draw": ("peripheral", "hand-draws cell boundaries — a niche input mode"),
    "subfeature:table-eraser": ("peripheral", "erases cell boundaries — niche"),
    "subfeature:table-delete": ("important", "removes rows/columns/cells — core table editing"),
    "subfeature:table-insert-rows": ("important", "adds rows — core table editing"),
    "subfeature:table-insert-columns": ("important", "adds columns — core table editing"),
    "subfeature:table-insert-cells": ("useful", "inserts cells with shift — less common than "
        "row/column insert"),
    "subfeature:table-merge-cells": ("important", "merges cells — a defining table-layout op"),
    "subfeature:table-split-cells": ("important", "splits cells — a defining table-layout op"),
    "subfeature:table-split-table": ("useful", "splits a table in two — occasional"),
    "subfeature:table-autofit": ("important", "auto-fits column widths — everyday table sizing"),
    "subfeature:table-cell-size": ("useful", "sets exact cell dimensions — precise sizing"),
    "subfeature:table-cell-alignment": ("important", "aligns cell contents — routine in "
        "presented tables"),
    "subfeature:table-text-direction": ("peripheral", "rotates cell text — niche"),
    "subfeature:table-cell-margins": ("useful", "sets cell margins — fine-tuning"),
    "subfeature:table-repeat-header": ("useful", "repeats header rows across pages — long "
        "tables"),
    "subfeature:table-convert-to-text": ("useful", "converts a table to text — occasional"),
    "subfeature:table-formula": ("peripheral", "adds a cell formula — Word tables are rarely "
        "used for calculation"),
    "subfeature:picture-remove-background": ("useful", "auto-removes an image background — a "
        "popular but occasional edit"),
    "subfeature:picture-corrections": ("useful", "adjusts brightness/contrast — common image "
        "tidy-up"),
    "subfeature:picture-color": ("useful", "recolors an image — common image styling"),
    "subfeature:picture-artistic-effects": ("peripheral", "applies painterly filters — "
        "decorative, occasional"),
    "subfeature:picture-transparency": ("useful", "sets image transparency — layout aid"),
    "subfeature:picture-compress": ("useful", "reduces image size — file-size management"),
    "subfeature:picture-change": ("useful", "swaps the image keeping formatting — a handy "
        "edit"),
    "subfeature:picture-reset": ("useful", "reverts image formatting — an undo convenience"),
    "subfeature:picture-style-gallery": ("important", "applies a framed picture style — the "
        "quickest way to make an image look finished"),
    "subfeature:picture-border": ("useful", "sets an image border — common finishing"),
    "subfeature:picture-effects": ("useful", "applies shadow/glow/3D to an image — styling"),
    "subfeature:picture-convert-to-smartart": ("peripheral", "captions images as SmartArt — "
        "niche"),
    "subfeature:picture-format-pane": ("useful", "the full image-formatting pane — power "
        "editing"),
    "subfeature:graphics-change": ("peripheral", "swaps the icon graphic — niche"),
    "subfeature:graphics-convert-to-shape": ("useful", "makes an icon editable — the key "
        "reason to use SVG icons"),
    "subfeature:graphics-style-gallery": ("useful", "styles an icon graphic — routine icon "
        "work"),
    "subfeature:graphics-color": ("useful", "recolors an icon — routine icon work"),
    "subfeature:graphics-border": ("peripheral", "outlines an icon — occasional"),
    "subfeature:graphics-effects": ("peripheral", "adds effects to an icon — occasional"),
    "subfeature:graphics-format-pane": ("peripheral", "the full graphic-formatting pane — "
        "power editing of a niche object"),
    "subfeature:shape-edit": ("useful", "changes/edits a shape's geometry — shape work"),
    "subfeature:shape-text-direction": ("peripheral", "rotates text in a shape — niche"),
    "subfeature:shape-text-align": ("useful", "aligns text in a shape/text box — routine for "
        "text boxes"),
    "subfeature:shape-text-link": ("peripheral", "flows text between text boxes — desktop-"
        "publishing niche"),
    "subfeature:smartart-add-shape": ("useful", "adds nodes to a diagram — core SmartArt "
        "editing"),
    "subfeature:smartart-add-bullet": ("useful", "adds sub-items to a diagram node — SmartArt "
        "editing"),
    "subfeature:smartart-text-pane": ("useful", "edits diagram text as an outline — the "
        "primary SmartArt text entry"),
    "subfeature:smartart-promote-demote": ("useful", "changes a node's level/order — SmartArt "
        "structuring"),
    "subfeature:smartart-reverse": ("peripheral", "reverses layout direction — occasional"),
    "subfeature:smartart-org-layout": ("peripheral", "org-chart branch layout — niche"),
    "subfeature:smartart-layout": ("useful", "changes the diagram layout — core SmartArt "
        "choice"),
    "subfeature:smartart-change-colors": ("useful", "recolors the diagram — routine SmartArt "
        "styling"),
    "subfeature:smartart-style": ("useful", "styles the diagram — routine SmartArt styling"),
    "subfeature:smartart-reset": ("peripheral", "resets diagram formatting — an undo aid"),
    "subfeature:smartart-shape-edit": ("peripheral", "edits an individual SmartArt shape — "
        "fine SmartArt work"),
    "subfeature:chart-add-element": ("useful", "adds/removes chart elements (titles, labels, "
        "legend) — core chart authoring"),
    "subfeature:chart-quick-layout": ("useful", "applies a preset chart layout — quick chart "
        "setup"),
    "subfeature:chart-change-colors": ("useful", "recolors the chart series — routine chart "
        "styling"),
    "subfeature:chart-style": ("useful", "applies a chart style — the quick way to finish a "
        "chart"),
    "subfeature:chart-switch-row-column": ("useful", "swaps the chart's data orientation — "
        "common when the chart reads wrong"),
    "subfeature:chart-edit-data": ("important", "edits the chart's underlying data — a chart "
        "is meaningless without correct data"),
    "subfeature:chart-change-type": ("useful", "changes the chart type — choosing the right "
        "chart"),
    "subfeature:chart-select-element": ("useful", "selects a chart element to format — a "
        "precondition for element formatting"),
    "subfeature:chart-format-selection": ("useful", "formats the selected chart element — "
        "fine chart tuning"),
    "subfeature:equation-ink": ("peripheral", "hand-writes an equation — a niche input mode"),
    "subfeature:equation-conversions": ("useful", "converts equation notation — used by "
        "LaTeX-oriented authors"),
    "subfeature:equation-symbols": ("useful", "inserts math symbols — core to writing "
        "equations"),
    "subfeature:equation-structures": ("useful", "inserts math structure templates "
        "(fractions, integrals…) — core to writing equations"),
    "subfeature:hf-document-info": ("useful", "inserts document-info fields in the "
        "header/footer — common in formal documents"),
    "subfeature:hf-navigate": ("useful", "moves between header and footer — routine while "
        "editing them"),
    "subfeature:hf-link-to-previous": ("useful", "links/unlinks section headers — multi-"
        "section documents"),
    "subfeature:hf-options": ("important", "different-first-page / odd-even options — standard "
        "in formal/book layouts"),
    "subfeature:hf-position": ("useful", "sets header/footer distance from the edge — layout "
        "fine-tuning"),
    "subfeature:hf-alignment-tab": ("peripheral", "inserts an alignment tab — advanced "
        "header/footer layout"),
    "subfeature:hf-close": ("important", "exits header/footer editing — the standard way out "
        "of the mode"),
    "subfeature:object-position": ("useful", "presets an object's page position — common "
        "layout"),
    "subfeature:object-text-wrap": ("important", "sets text wrapping around an object — the "
        "single most-needed object-layout choice"),
    "subfeature:object-reorder": ("useful", "changes object z-order — common with overlapping "
        "objects"),
    "subfeature:object-align": ("useful", "aligns/distributes objects — layout tidiness"),
    "subfeature:object-group": ("useful", "groups objects to move together — multi-object "
        "work"),
    "subfeature:object-rotate": ("useful", "rotates/flips an object — common adjustment"),
    "subfeature:object-selection-pane": ("useful", "lists objects for show/hide/reorder — "
        "multi-object management"),
    "subfeature:object-alt-text": ("useful", "authors accessibility alt text — increasingly "
        "expected"),
    "subfeature:object-size": ("important", "sets an object's exact size — near-universal "
        "after inserting an object"),
    "subfeature:picture-crop": ("important", "crops an image — one of the most-used image "
        "edits"),
    "subfeature:shape-style-gallery": ("important", "applies a shape style — the quick way to "
        "style a shape"),
    "subfeature:shape-fill": ("important", "sets a shape's fill — the most-used shape format"),
    "subfeature:shape-outline": ("important", "sets a shape's outline — everyday shape format"),
    "subfeature:shape-effects": ("useful", "adds effects to a shape — styling"),
    "subfeature:shape-format-pane": ("useful", "the full shape-formatting pane — power "
        "editing"),
    "subfeature:wordart-text-style-gallery": ("useful", "applies a WordArt text style — "
        "decorative text"),
    "subfeature:wordart-text-fill": ("useful", "fills object text — decorative text styling"),
    "subfeature:wordart-text-outline": ("peripheral", "outlines object text — decorative"),
    "subfeature:wordart-text-effects": ("useful", "adds effects to object text — decorative "
        "text styling"),
}


# =======================================================================================
# Build the export lists from the MEASURED contextual containers.
def _core_suffix(cid, eid):
    prefix = "el:" + cid.removeprefix("ui:") + "-"    # el:ribbon-<tab>-
    return eid[len(prefix):] if eid.startswith(prefix) else eid.removeprefix("el:")


def _build():
    ui = json.loads((common.APP_KB / "ui.json").read_text(encoding="utf-8"))["containers"]
    ctx = {cid: c for cid, c in ui.items() if c.get("trigger_condition")}

    sub_hosts = {}       # sub id -> {tab_cid: [el ids]}
    existing = {}        # existing sub id -> [(tab_cid, el id)]
    idmso = {}           # el id -> note
    honest = set()       # el ids intentionally unexplored
    used_features = set()
    unmapped = []

    for cid, c in ctx.items():
        for e in c.get("children", []):
            eid = e.get("id")
            if not eid:
                continue
            suf = _core_suffix(cid, eid)
            disabled = "disabled in this context" in (e.get("state_notes") or "")
            if suf in SUFFIX_EXISTING:
                existing.setdefault(SUFFIX_EXISTING[suf], []).append((cid, eid))
                continue
            sub = TAB_SUFFIX_SUB.get((cid, suf)) or SUFFIX_SUB.get(suf)
            if sub is None:
                # honest micro-nudge / disabled leftovers that carry no distinct capability
                if disabled:
                    honest.add(eid)
                    continue
                unmapped.append(f"{cid} :: {suf} ({eid})")
                continue
            sub_hosts.setdefault(sub, {}).setdefault(cid, []).append(eid)
            used_features.add(SUB_META[sub][0])
            if disabled:
                honest.add(eid)
            elif e.get("unexplored") and suf in IDMSO_OVERRIDE_SUFFIX:
                idmso[eid] = IDMSO_OVERRIDE_SUFFIX[suf]
            elif e.get("unexplored"):
                # unexplored, not a known idMso capability, not disabled -> honest stub
                honest.add(eid)

    ctx_features = []
    for fid in sorted(used_features):
        name, does, affects, aud = FEATURE_META[fid]
        ctx_features.append({"id": fid, "name": name, "does": does, "affects": affects,
                             "aud": aud, "requires": FEATURE_REQUIRES.get(fid, []),
                             "tabs": sorted({t for s, hosts in sub_hosts.items()
                                             if SUB_META[s][0] == fid for t in hosts})})
    ctx_subs = []
    for sub, hosts in sorted(sub_hosts.items()):
        feature, name, does, affects, aud = SUB_META[sub]
        ctx_subs.append({"id": sub, "feature": feature, "name": name, "does": does,
                         "affects": affects, "aud": aud,
                         "hosts": [(cid, els) for cid, els in sorted(hosts.items())],
                         "requires": SUB_REQUIRES.get(sub, [])})
    return ctx_features, ctx_subs, existing, idmso, honest, unmapped


(CTX_FEATURES, CTX_SUBS, CTX_EXISTING_ELS, CTX_IDMSO_OVERRIDES,
 CTX_HONEST_UNEXPLORED, CTX_UNMAPPED) = _build()


if __name__ == "__main__":
    print("features:", len(CTX_FEATURES))
    print("subs:", len(CTX_SUBS))
    print("existing-hosted:", {k: len(v) for k, v in CTX_EXISTING_ELS.items()})
    print("idmso overrides:", len(CTX_IDMSO_OVERRIDES))
    print("honest unexplored:", len(CTX_HONEST_UNEXPLORED))
    if CTX_UNMAPPED:
        print("\nUNMAPPED SUFFIXES (add to SUFFIX_SUB):")
        for u in CTX_UNMAPPED:
            print("  ", u)
