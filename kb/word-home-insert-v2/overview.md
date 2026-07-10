# Microsoft Word — Home + Insert universe knowledge base

**Version (pinned):** 16.0.20131  |  **Platform:** desktop

A desktop word processor for creating, formatting and editing text documents. Writing and formatting documents — letters, reports, essays, resumes — with rich text styling, paragraph layout, lists, styles, tables, graphics, headers/footers and review tools.

**Who uses it:** Students, office workers, writers, and virtually anyone producing formatted text documents.

**Contents:** 34 features · 172 sub-features · 231 UI containers (37 honest stubs) · 25 shortcut keys · layers: P0=11 P1=32 P2=25 P3=89 P4=49

## Scope

The HOME and INSERT ribbon tabs plus every CONTEXTUAL tab their features summon (Table Design/Layout, Picture/Graphics/Shape Format, Chart Design/Format, SmartArt Design/Format, Equation, Header & Footer). Other always-present tabs are recorded as unexplored names only. The deprecated standalone WordArt tab is out of scope: Insert > WordArt in Word 16 produces a modern text-effect shape whose tab is Shape Format (covered); the legacy tab is reachable only via old COM paths.

## Features

### Adobe Acrobat  `feature:acrobat`  — P4 (scope: none, ratio 0/1)

Create a PDF from the document via the Adobe Acrobat add-in.

*Boundary feature — deliberately not driven (cloud/add-in/store).*

- **Create a PDF** (P4) — Exports the document to a PDF using the Adobe Acrobat add-in.

### Add-ins  `feature:add-ins`  — P4 (scope: none, ratio 0/1)

Browse and launch Office Add-ins from the store.

*Boundary feature — deliberately not driven (cloud/add-in/store).*

- **Add-ins** (P4) — Opens the Office Add-ins store flyout to browse and insert add-ins.

### Clipboard  `feature:clipboard`  — P0 (scope: whole, ratio 4/5)

Move and duplicate content and formatting via the clipboard.

- **Paste** (P0) · `Ctrl+V` · opens `ui:paste-dropdown` — Inserts the clipboard's content at the cursor; the dropdown offers paste-special options (keep formatting, merge, text only, picture).
- **Cut** (P1) · `Ctrl+X` — Removes the selection from the document and places it on the clipboard.
- **Copy** (P0) · `Ctrl+C` — Copies the selection to the clipboard without changing the document.
- **Format Painter** (P2) · `Alt+Ctrl+C, Alt+Ctrl+V` — Copies formatting from the selection to reapply to the next thing you click.
- **Office Clipboard** (P4) · opens `ui:show-clipboard-pane` — Opens the Office Clipboard pane showing the last 24 copied items for reuse.

### Comments  `feature:comments`  — P1 (scope: whole, ratio 1/1)

Attach review comments to document ranges for collaboration.

- **Comment** (P1) · `Ctrl+Alt+M` — Creates a pending draft comment anchored at the selection and opens its card (measured: in-frame 'Post comment' button); the comment joins the review thread when posted.

### Editing  `feature:editing`  — P1 (scope: whole, ratio 2/3)

Find, replace and select text within the document.

- **Find** (P1) · `Ctrl+F` · opens `ui:navigation-pane-find-pane` — Opens the Navigation pane to search the document for text; the dropdown offers Find, Advanced Find and Go To.
- **Replace** (P2) · `Ctrl+H` · opens `ui:replace-dialog` — Opens the Find and Replace dialog to substitute text throughout the document.
- **Select** (P3) · opens `ui:select-menu` — A menu to Select All, select objects, or select text with similar formatting.

### Editor  `feature:editor`  — P4 (scope: none, ratio 0/1)

Check spelling, grammar and writing refinements via the cloud Editor service.

*Boundary feature — deliberately not driven (cloud/add-in/store).*

- **Editor** (P4) — Opens the Editor pane with spelling, grammar and writing-refinement suggestions.

### eSignature  `feature:esignature`  — P4 (scope: none, ratio 0/1)

Request electronic signatures on the document via the SharePoint Syntex cloud service.

*Boundary feature — deliberately not driven (cloud/add-in/store).*

- **eSignature fields** (P4) — Requests electronic signatures on the document through the SharePoint Syntex service.

### Font  `feature:font`  — P0 (scope: gems, ratio 7/16)

Format the characters of the selected text — typeface, size, weight, color, effects.

- **Font** (P0) · opens `ui:font-dropdown` — Chooses the typeface for the selected text; the box opens a searchable font list.
- **Font Size** (P0) · opens `ui:font-size-dropdown` — Sets the point size of the selected text; the box opens a size list.
- **Grow Font** (P3) · `Ctrl+Shift+>` — Increases the font size of the selection to the next step.
- **Shrink Font** (P3) · `Ctrl+Shift+<` — Decreases the font size of the selection to the previous step.
- **Change Case** (P3) · opens `ui:change-case-menu` — Changes the capitalization of the selected text (Sentence case, lowercase, UPPERCASE, Capitalize Each Word, tOGGLE cASE).
- **Clear All Formatting** (P3) — Removes all character and paragraph formatting from the selection, leaving plain text.
- **Bold** (P0) · `Ctrl+B` — Toggles bold (heavier) weight on the selected text.
- **Italic** (P1) · `Ctrl+I` — Toggles italic (slanted) style on the selected text.
- **Underline** (P1) · `Ctrl+U` · opens `ui:underline-menu` — Toggles an underline on the selected text; the dropdown picks the underline style and color.
- **Strikethrough** (P3) — Draws a line through the middle of the selected text.
- **Subscript** (P3) · `Ctrl+Shift+_` — Places the selected text slightly below the baseline in a smaller size.
- **Superscript** (P3) · `Ctrl+Shift++` — Places the selected text slightly above the baseline in a smaller size.
- **Text Effects and Typography** (P4) · opens `ui:text-effects-dropdown` — Applies visual text effects (outline, shadow, reflection, glow) and OpenType typography.
- **Text Highlight Color** (P1) · opens `ui:text-highlight-color-dropdown` — Applies a highlighter color behind the text; the dropdown picks the color.
- **Font Color** (P1) · opens `ui:font-color-dropdown` — Sets the color of the selected text; the dropdown opens a color picker (theme/standard/more).
- **Font dialog launcher** (P3) · `Ctrl+D` · opens `ui:font-dialog` — Opens the Font dialog — the consolidated surface for all character formatting plus advanced options (spacing, ligatures, defaults).

### Header & Footer  `feature:header-footer`  — P1 (scope: whole, ratio 3/3)

Repeat content at the top/bottom of every page and number the pages; editing them activates the Header & Footer contextual tab.

- **Header** (P1) · opens `ui:header-insert-dropdown` — Opens a gallery of built-in header designs (Blank, Austin, Banded…) plus Edit/Remove Header; applying one enters header editing and activates the Header & Footer contextual tab (measured).
- **Footer** (P1) · opens `ui:footer-insert-dropdown` — Opens a gallery of built-in footer designs plus Edit/Remove Footer; applying one enters footer editing and activates the Header & Footer contextual tab.
- **Page Number** (P1) · opens `ui:header-footer-page-number-insert-menu` — Opens a menu of page-number positions (top, bottom, margins, current position) and formats; numbers live in the header/footer stories.

### Illustrations  `feature:illustrations`  — P0 (scope: gems, ratio 2/7)

Insert graphic objects — pictures, shapes, icons, 3D models, SmartArt diagrams, charts and screenshots; each selected object surfaces its own Format contextual tab(s).

- **Pictures** (P0) · opens `ui:flyout-anchor-insert-pictures-menu` — Inserts a picture from This Device, the Stock Images library, or Online Pictures; a selected picture activates the Picture Format contextual tab (measured). Also reachable inside header/footer editing (Header & Footer tab > Insert group).
- **Shapes** (P2) · opens `ui:shapes-insert-dropdown` — Opens a gallery of ready-made shapes (lines, rectangles, arrows, callouts…) to draw into the document; a selected shape activates the Shape Format contextual tab (measured).
- **Icons** (P4) · opens `ui:icon-insert-from-file-dialog` — Opens the stock icon library dialog to insert symbol graphics (content streams from the Office CDN — network); an inserted icon/SVG graphic activates the Graphics Format contextual tab (measured via a local SVG probe).
- **3D Models** (P4) · opens `ui:insert3-dmodel-default-dialog` — Inserts a rotatable 3D model from the stock library (primary) or from a local file (the dropdown menu offers This Device / Stock 3D Models).
- **SmartArt** (P3) · opens `ui:smart-art-insert-dialog` — Opens the Choose a SmartArt Graphic dialog (lists, processes, cycles, hierarchies…); an inserted SmartArt activates the SmartArt Design + Format contextual tabs (measured).
- **Chart** (P3) · opens `ui:chart-insert-dialog` — Opens the Insert Chart dialog (column, line, pie, bar, area, scatter, map…); an inserted chart activates the Chart Design + Format contextual tabs and links to an embedded Excel datasheet for its data (measured).
- **Screenshot** (P4) · opens `ui:screenshot-insert-dropdown` — Inserts a snapshot of any open window (gallery of live thumbnails) or a Screen Clipping region; the result is a picture (Picture Format applies).

### Links  `feature:links`  — P2 (scope: gems, ratio 1/3)

Create navigation targets and jumps: hyperlinks, bookmarks and cross-references.

- **Link** (P2) · `Ctrl+K` · opens `ui:insert-link-dialog` — Opens the Insert Hyperlink dialog to link the selection to webpages, files, headings or email addresses; the dropdown lists recent items.
- **Bookmark** (P4) · opens `ui:bookmark-insert-dialog` — Opens the Bookmark dialog to name the current place/selection so links and references can jump to it.
- **Cross-reference** (P3) · opens `ui:cross-reference-insert-dialog` — Opens the Cross-reference dialog to insert a live reference to a heading, bookmark, figure or table (updates as the target moves).

### Media  `feature:media`  — P4 (scope: none, ratio 0/1)

Embed online videos into the document from web sources.

- **Online Videos** (P4) · opens `ui:movie-from-clip-organizer-insert-dialog` — Opens a dialog to embed an online video by URL (YouTube etc.); playback happens in-document (network content).

### Pages  `feature:pages`  — P1 (scope: gems, ratio 1/3)

Insert page-level structure: preformatted cover pages, blank pages, and page breaks.

- **Cover Page** (P3) · opens `ui:cover-page-insert-dropdown` — Inserts a preformatted, styled cover page (title/subtitle/date placeholders) at the start of the document, chosen from a gallery of designs.
- **Blank Page** (P3) — Inserts an empty page at the cursor position (measured: two page breaks around a new empty page).
- **Page Break** (P1) · `Ctrl+Return` — Ends the current page at the cursor and continues content on the next page (measured: doc + format delta).

### Paragraph  `feature:paragraph`  — P1 (scope: gems, ratio 6/15)

Format whole paragraphs — lists, indentation, alignment, spacing, shading, borders.

- **Bullets** (P1) · opens `ui:bullets-dropdown` — Starts or toggles a bulleted list on the selected paragraphs; the dropdown is the bullet library.
- **Numbering** (P1) · opens `ui:numbering-dropdown` — Starts or toggles a numbered list on the selected paragraphs; the dropdown is the numbering library.
- **Multilevel List** (P3) · opens `ui:multilevel-list-menu` — Applies a multi-level (nested) list scheme to the selected paragraphs.
- **Decrease Indent** (P3) — Moves the paragraph's left indent one level toward the margin.
- **Increase Indent** (P1) — Moves the paragraph's left indent one level away from the margin.
- **Sort** (P4) · opens `ui:sort-dialog` — Opens the Sort dialog to alphabetically/numerically sort the selected paragraphs, list or table.
- **Show/Hide ¶** (P3) · `Ctrl+*` — Toggles the on-screen display of paragraph marks and other hidden formatting symbols.
- **Align Left** (P1) · `Ctrl+L` — Aligns the paragraph text to the left margin.
- **Center** (P3) · `Ctrl+E` — Centers the paragraph text between the margins.
- **Align Right** (P3) · `Ctrl+R` — Aligns the paragraph text to the right margin.
- **Justify** (P3) · `Ctrl+J` — Spaces the paragraph text to align to both left and right margins.
- **Line and Paragraph Spacing** (P1) · opens `ui:line-spacing-menu` — Sets the spacing between lines and before/after paragraphs.
- **Shading** (P3) · opens `ui:shading-color-dropdown` — Fills the background of the selection/paragraph with a color; the dropdown picks the color.
- **Borders** (P3) · opens `ui:borders-selection-menu` — Applies borders to the selection/paragraph; the dropdown lists border options and the Borders and Shading dialog.
- **Paragraph dialog launcher** (P2) · opens `ui:paragraph-dialog` — Opens the Paragraph dialog — indentation, spacing, alignment and line/page-break options.

### Styles  `feature:styles`  — P1 (scope: gems, ratio 1/2)

Apply named, reusable style sets that bundle character and paragraph formatting.

- **Quick Styles gallery** (P1) · opens `ui:styles-gallery` — Applies a named style (Normal, No Spacing, Heading 1/2, Title, Subtitle, Quote…) to the selection from the in-ribbon gallery.
- **Styles pane launcher** (P3) · `Alt+Ctrl+Shift+S` · opens `ui:styles-pane` — Opens the Styles pane — the full style list with apply/new/inspect/manage controls.

### Symbols  `feature:symbols`  — P3 (scope: none, ratio 0/2)

Insert mathematical equations (with the Equation contextual tab) and special symbols not on the keyboard.

- **Equation** (P3) · `Alt+=` · opens `ui:equation-insert-dropdown` — Inserts an empty math zone at the cursor (measured: OMaths 0→1) and activates the Equation contextual tab; the dropdown offers built-in equations (quadratic formula, area of circle…).
- **Symbol** (P3) · opens `ui:symbol-insert-dropdown` — Opens a gallery of recently used symbols plus More Symbols… (the full character map) to insert characters not on the keyboard.

### Tables  `feature:tables`  — P0 (scope: whole, ratio 1/1)

Insert tables to organize content in rows and columns; a selected table brings up its own Table Design and Table Layout contextual tabs.

- **Table** (P0) · opens `ui:table-insert-dropdown` — Opens the table builder: a hover grid to insert an N×M table instantly, plus Insert Table…, Draw Table, Convert Text to Table…, Excel Spreadsheet and Quick Tables. A selected table activates the Table Design + Table Layout contextual tabs (measured).

### Text  `feature:text`  — P3 (scope: none, ratio 0/7)

Insert text objects and building blocks: text boxes, Quick Parts/fields, WordArt, drop caps, signature lines, date/time and embedded objects.

- **Text Box** (P3) · opens `ui:text-box-insert-dropdown` — Inserts a floating text container from a gallery of built-in designs or by drawing one; a selected text box activates the Shape Format contextual tab (measured).
- **Quick Parts** (P4) · opens `ui:quick-parts-insert-dropdown` — Inserts reusable building blocks: AutoText, document properties and fields; also saves the selection to the gallery. Also hosted on the Header & Footer contextual tab.
- **WordArt** (P4) · opens `ui:word-art-insert-dropdown` — Inserts decorative styled text from a gallery; the result is a text object whose selection activates a Format contextual tab (measured: modern WordArt uses Shape Format; legacy WordArt objects surface a dedicated WordArt tab).
- **Drop Cap** (P4) · opens `ui:drop-cap-insert-dropdown` — Turns the paragraph's first letter into a large dropped capital (Dropped / In margin / options dialog); disabled until the document has text (measured).
- **Signature Line** (P4) · opens `ui:signature-line-insert-dialog` — Opens the Signature Setup dialog to insert a signature line naming the required signer (digital signature requires a certificate).
- **Date & Time** (P4) · opens `ui:date-and-time-insert-dialog` — Opens a dialog of date/time formats to insert the current date or time, optionally as an auto-updating field. Also hosted on the Header & Footer contextual tab.
- **Object** (P4) · opens `ui:ole-objectct-insert-dialog` — Embeds an OLE object (or inserts text from another file via the dropdown menu) into the document.

### Voice  `feature:voice`  — P4 (scope: none, ratio 0/1)

Dictate text by voice using cloud speech recognition.

*Boundary feature — deliberately not driven (cloud/add-in/store).*

- **Dictate** (P4) — Converts speech to text via the cloud dictation service.

### Chart Design  `feature:chart-design`  — P2 (scope: gems, ratio 1/7)

Design a selected chart — add chart elements, quick layouts, colors, chart styles, switch row/column, edit the source data and change the chart type.

- **Add Chart Element** (P3) · opens `ui:ribbon-chart-design-add-chart-element-dropdown` — Adds/removes chart elements — axes, titles, data labels, gridlines, legend, trendlines (menu).
- **Change Colors** (P3) · opens `ui:ribbon-chart-design-chart-colors-dropdown` — Applies a color scheme to the chart's data series from a gallery.
- **Change Chart Type** (P3) · opens `ui:ribbon-chart-design-chart-change-type-dialog` — Opens the Change Chart Type dialog to switch the chart to a different type.
- **Edit / Select Data** (P2) · opens `ui:ribbon-chart-design-chart-show-data-grid-dropdown` — Accesses the chart's underlying worksheet data — edit data (opens the linked Excel workbook), select data range, show the data grid, and refresh.
- **Quick Layout** (P3) · opens `ui:ribbon-chart-design-chart-layout-dropdown` — Applies a preset arrangement of the chart's elements from a gallery.
- **Chart Styles gallery** (P3) — Applies an overall visual style to the chart from the gallery.
- **Switch Row/Column** (P3) — Swaps which of the source data's rows and columns map to the chart's axis vs series.

### Chart Format (chart-specific)  `feature:chart-format`  — P3 (scope: none, ratio 0/2)

Format individual chart elements — select and format a specific chart part.

- **Format Selection** (P3) · opens `ui:ribbon-chart-format-chart-format-selection-pane` — Opens the format pane for the selected chart element, and resets it to the style default.
- **Chart Elements selector** (P3) · opens `ui:ribbon-chart-format-chart-element-selector-dropdown` — Selects a specific chart element (series, axis, legend…) to format via the dropdown.

### Equation  `feature:equation-tools`  — P3 (scope: none, ratio 0/4)

Author a mathematical equation in the selected math zone — conversions, symbols and structures (fractions, scripts, radicals, integrals, matrices…).

- **Conversions** (P3) · opens `ui:ribbon-equation-equation-convert-dropdown` — Converts the equation's notation between professional/linear, Unicode, LaTeX and text (Convert menu + Equation Options).
- **Ink Equation** (P4) — Opens a canvas to hand-write a math equation that is recognized into typeset math.
- **Structures** (P3) · opens `ui:ribbon-equation-equation-fraction-dropdown` — Inserts a math structure template into the equation — fraction, script, radical, integral, large operator, bracket, function, accent, limit/log, operator, or matrix (a palette of templates).
- **Equation Symbols** (P3) — Inserts a mathematical symbol (operators, Greek letters, arrows…) from the gallery.

### Graphics Format  `feature:graphics-format`  — P3 (scope: none, ratio 0/7)

Style a selected SVG/icon graphic — recolor, graphics styles, outline, effects, and convert it to an editable shape.

- **Graphics Outline** (P4) · opens `ui:ribbon-graphics-format-graphics-outline-color-dropdown` — Sets the graphic's outline color/weight/dashes (options in the picker).
- **Change Graphic** (P4) · opens `ui:ribbon-graphics-format-graphic-change-dropdown` — Replaces the SVG/icon graphic with another from the library.
- **Graphics Fill (recolor)** (P3) · opens `ui:ribbon-graphics-format-graphics-color-dropdown` — Recolors the graphic's fill from the color picker.
- **Convert to Shape** (P3) — Converts the SVG graphic into an editable Word shape (or group of shapes).
- **Graphics Effects** (P4) · opens `ui:ribbon-graphics-format-graphics-effects-dropdown` — Applies shadow/reflection/glow/3D effects to the graphic (menu).
- **Format Graphic pane** (P4) · opens `ui:ribbon-graphics-format-graphics-format-pane` — Opens the Format Graphic pane — the full fill/line/effects surface.
- **Graphics Styles gallery** (P3) — Applies a preset fill/outline style to the graphic from the gallery.

### Header & Footer Tools  `feature:header-footer-tools`  — P2 (scope: gems, ratio 2/7)

Navigate and configure header/footer editing mode — move between header and footer, set first-page / odd-even options, position, and close the editor.

- **Insert Alignment Tab** (P4) · opens `ui:ribbon-header-footer-insert-alignment-tab-dialog` — Inserts an alignment tab so header/footer content can be left/center/right aligned on one line.
- **Close Header and Footer** (P2) — Exits header/footer editing mode and returns to the document body.
- **Document Info** (P3) · opens `ui:ribbon-header-footer-document-info-dropdown` — Inserts document-property fields (author, file name, path…) into the header/footer.
- **Link to Previous** (P3) — Links this section's header/footer to the previous section's (or breaks the link).
- **Header/Footer Navigation** (P3) — Moves the cursor between the header and footer and between sections' headers/footers (go to header/footer, previous, next).
- **Header/Footer Options** (P2) — Toggles header/footer display options — different first page, different odd & even pages, and showing the document text.
- **Header/Footer Position** (P4) — Sets the distance of the header/footer from the top/bottom page edge.

### Arrange objects  `feature:object-arrange`  — P1 (scope: gems, ratio 1/8)

Position and order any selected drawing object — text wrapping, position, z-order, alignment, grouping, rotation, the selection pane, and alt text.

- **Align** (P3) · opens `ui:ribbon-chart-format-object-align-dropdown` — Aligns/distributes the selected object(s) to the page/margin/each other (menu).
- **Alt Text** (P3) · opens `ui:ribbon-chart-format-alt-text-pane-ribbon-pane` — Opens the Alt Text pane to author accessibility descriptions for the object.
- **Group** (P3) — Groups multiple objects into one (or ungroups) so they move together.
- **Position** (P3) · opens `ui:ribbon-chart-format-picture-position-dropdown` — Places the object at a preset position on the page with text wrapping (gallery).
- **Bring Forward / Send Backward** (P3) · opens `ui:ribbon-shape-format-object-bring-forward-dropdown` — Changes the object's z-order relative to other objects and the text (bring forward/to front, send backward/to back — variations of z-order).
- **Rotate** (P3) · opens `ui:ribbon-graphics-format-object-rotate-dropdown` — Rotates or flips the object (right 90°, flip horizontal/vertical, more options).
- **Selection Pane** (P3) · opens `ui:ribbon-chart-format-selection-pane` — Opens the Selection pane listing every object for show/hide/reorder/rename.
- **Wrap Text** (P1) · opens `ui:ribbon-chart-format-text-wrap-dropdown` — Sets how document text wraps around the object (in line, square, tight, behind…).

### Size objects  `feature:object-size`  — P1 (scope: whole, ratio 2/2)

Set the size of any selected drawing object — its height and width, the size/layout dialog, and (for images) cropping.

- **Object Size** (P2) · opens `ui:ribbon-chart-format-layout-options-dialog-size-dialog` — Sets the object's exact height and width (nudge fields) and opens the Layout/Size dialog.
- **Crop** (P1) · opens `ui:ribbon-graphics-format-picture-crop-dropdown` — Crops the image to hide its edges, to a shape, aspect ratio, or fill/fit (menu).

### Picture Format  `feature:picture-format`  — P2 (scope: gems, ratio 1/13)

Adjust and style a selected picture — corrections, color, artistic effects, compression, picture styles, border, effects and layout.

- **Artistic Effects** (P4) · opens `ui:ribbon-picture-format-picture-artistic-effects-dropdown` — Applies a painterly/artistic filter to the picture from a gallery.
- **Picture Border** (P3) · opens `ui:ribbon-picture-format-outline-color-dropdown` — Sets the picture's border color, weight and dash style (options in the picker).
- **Change Picture** (P3) · opens `ui:ribbon-picture-format-picture-change-dropdown` — Replaces the picture with another (from file/stock/online) keeping formatting.
- **Color** (P3) · opens `ui:ribbon-picture-format-picture-color-dropdown` — Recolors the picture — saturation, tone, and recolor presets (gallery + options).
- **Compress Pictures** (P3) · opens `ui:ribbon-picture-format-pictures-compress-dialog` — Opens the Compress Pictures dialog to reduce image resolution/file size.
- **Picture Layout (convert to SmartArt)** (P4) · opens `ui:ribbon-picture-format-pictures-convert-to-smart-art-dropdown` — Converts the picture(s) into a captioned SmartArt layout.
- **Corrections** (P3) · opens `ui:ribbon-picture-format-picture-corrections-dropdown` — Adjusts the picture's sharpness, brightness and contrast (gallery + options).
- **Picture Effects** (P3) · opens `ui:ribbon-picture-format-picture-effects-dropdown` — Applies shadow/reflection/glow/bevel/3D effects to the picture (menu of effect families).
- **Format Picture pane** (P4) · opens `ui:ribbon-picture-format-picture-format-pane` — Opens the Format Picture pane — the full fill/line/effects/picture-adjust surface.
- **Remove Background** (P3) · opens `ui:ribbon-picture-format-picture-background-removal-dropdown` — Enters Background Removal mode to auto-detect and delete the picture's background.
- **Reset Picture** (P3) · opens `ui:ribbon-picture-format-picture-reset-dropdown` — Discards formatting changes (and optionally size) applied to the picture.
- **Picture Styles gallery** (P2) — Applies a framed/shadowed/3D picture style from the gallery.
- **Transparency** (P3) · opens `ui:ribbon-picture-format-picture-transparency-dropdown` — Sets the picture's overall transparency from presets.

### Shape Format (shape-specific)  `feature:shape-format`  — P3 (scope: none, ratio 0/4)

Shape-specific tools for a selected shape/text box — edit the shape geometry and set text direction/alignment inside it.

- **Edit Shape** (P3) · opens `ui:ribbon-shape-format-object-edit-shape-dropdown` — Changes the shape to another or edits its edit-points/geometry (menu).
- **Align Text (in shape)** (P3) · opens `ui:ribbon-shape-format-text-align-dropdown` — Aligns text vertically within the shape/text box (top/middle/bottom).
- **Text Direction (in shape)** (P4) — Rotates the direction of text inside the shape/text box.
- **Create Text Box Link** (P4) — Links text boxes so overflowing text flows from one into the next.

### Shape styles  `feature:shape-styles`  — P2 (scope: whole, ratio 3/5)

Style the fill, outline and effects of a selected shape/chart/SmartArt shape from a gallery or individually.

- **Shape Effects** (P3) · opens `ui:ribbon-chart-format-shape-effects-dropdown` — Applies shadow/reflection/glow/bevel/3D effects to the shape (menu of families).
- **Shape Fill** (P2) · opens `ui:ribbon-chart-format-shape-fill-color-dropdown` — Sets the shape's fill — color, gradient, picture, texture (options in the picker).
- **Format Shape pane** (P4) · opens `ui:ribbon-chart-format-object-format-pane` — Opens the Format Shape pane — the full fill/line/effects/text surface.
- **Shape Outline** (P2) · opens `ui:ribbon-chart-format-outline-color-dropdown` — Sets the shape's outline color, weight and dashes (options in the picker).
- **Shape Styles gallery** (P2) — Applies a preset fill+outline+effect style to the shape from the gallery.

### SmartArt Design  `feature:smartart-design`  — P3 (scope: none, ratio 0/10)

Build and restyle a selected SmartArt graphic — add/promote/reorder shapes, change the layout, colors and style.

- **Add Bullet** (P3) — Adds a sub-bullet text item to the selected SmartArt node.
- **Add Shape** (P3) · opens `ui:ribbon-smart-art-design-smart-art-add-shape-dropdown` — Adds a shape/node to the SmartArt graphic (before/after/above/below via the menu).
- **Change Colors** (P3) · opens `ui:ribbon-smart-art-design-smart-art-change-colors-dropdown` — Applies a color scheme to the SmartArt from the gallery.
- **Layouts gallery** (P3) — Changes the SmartArt's overall layout (list, process, cycle, hierarchy…) from the gallery.
- **Organization Layout** (P4) — Changes the hanging/branch layout of an organization-chart SmartArt (menu).
- **Promote / Demote** (P3) — Changes the outline level of the selected SmartArt node (promote/demote), and moves it up/down in order.
- **Reset Graphic** (P4) — Discards all formatting changes back to the default SmartArt appearance.
- **Right to Left** (P4) — Reverses the left-to-right order of the SmartArt layout.
- **SmartArt Styles gallery** (P3) — Applies a visual style (3D, shadow, gradient…) to the SmartArt from the gallery.
- **Text Pane** (P3) — Toggles the text outline pane for editing the SmartArt's text as a bulleted list.

### SmartArt Format (shape-specific)  `feature:smartart-format`  — P4 (scope: none, ratio 0/1)

Shape-level formatting of individual SmartArt shapes — change/resize the shape.

- **Edit SmartArt Shape** (P4) — Changes or resizes an individual shape within the SmartArt (larger/smaller/change/edit in 2-D).

### Table Design  `feature:table-design`  — P2 (scope: gems, ratio 2/4)

Style a selected table — apply a table style, toggle which parts the style emphasizes, and set shading and borders.

- **Table Borders** (P2) · opens `ui:ribbon-table-design-border-styles-dropdown` — Sets the table's borders — border style/pen weight/pen color (options), which edges get a border, the border painter, and the Borders and Shading dialog.
- **Table Shading** (P3) · opens `ui:ribbon-table-design-shading-color-dropdown` — Fills the selected cells' background with a color from the shading picker.
- **Table Style Options** (P3) — Toggles which parts of the table the current table style emphasizes (header row, total row, banded rows, first/last column, banded columns).
- **Table Styles gallery** (P2) — Applies a built-in table style (borders, shading, banding) from the gallery.

### Table Layout  `feature:table-layout`  — P1 (scope: gems, ratio 8/20)

Change a selected table's structure — insert/delete rows and columns, merge and split cells, size and align cells, and sort or convert the contents.

- **AutoFit** (P2) · opens `ui:ribbon-table-layout-table-auto-fit-dropdown` — Auto-fits column widths to contents, to the window, or to a fixed width (menu).
- **Cell Alignment** (P2) — Aligns cell contents to one of the nine positions (top/middle/bottom × left/center/right).
- **Cell Margins** (P3) · opens `ui:ribbon-table-layout-table-options-dialog` — Opens the Cell Options/Table Options dialog to set cell margins and spacing.
- **Cell Size** (P3) · opens `ui:ribbon-table-layout-table-rows-distribute-dialog` — Sets exact row height and column width (nudges + fields) and distributes rows/columns evenly.
- **Convert to Text** (P3) · opens `ui:ribbon-table-layout-convert-table-to-text-dialog` — Opens a dialog to convert the table back to delimited text.
- **Delete** (P1) · opens `ui:ribbon-table-layout-table-delete-rows-and-columns-dropdown` — Deletes cells, rows, columns or the whole table (menu).
- **Draw Table** (P4) — Arms a pen to draw table cell boundaries by hand.
- **Eraser** (P4) — Arms an eraser to remove table cell boundaries (merging cells).
- **Formula** (P4) · opens `ui:ribbon-table-layout-table-formula-dialog` — Opens the Formula dialog to compute a value (SUM, AVERAGE…) in a table cell.
- **Insert Cells** (P4) · opens `ui:ribbon-table-layout-table-insert-cells-dialog` — Opens the Insert Cells dialog to insert cells and shift the rest.
- **Insert Columns** (P1) — Inserts a column to the left or right of the current column.
- **Insert Rows** (P1) — Inserts a row above or below the current row.
- **Merge Cells** (P1) — Merges the selected cells into one.
- **Table Properties** (P2) · opens `ui:ribbon-table-layout-table-properties-dialog` — Opens the Table Properties dialog (size, alignment, text wrapping, row/column/cell options).
- **Repeat Header Rows** (P3) — Repeats the header row(s) at the top of each page the table spans.
- **Select (table parts)** (P3) · opens `ui:ribbon-table-layout-table-select-dropdown` — Selects the cell, row, column or whole table at the cursor.
- **Split Cells** (P2) · opens `ui:ribbon-table-layout-split-cells-dialog` — Opens the Split Cells dialog to divide the selected cell(s) into rows/columns.
- **Split Table** (P3) — Splits the table into two at the current row.
- **Text Direction** (P4) — Rotates the text direction within the selected cells.
- **View Gridlines** (P3) — Toggles the on-screen display of table cell gridlines (non-printing).

### Text (WordArt) styles  `feature:wordart-text-styles`  — P3 (scope: none, ratio 0/4)

Apply WordArt-style fill, outline and effects to the text inside a selected drawing object.

- **Text Effects** (P3) · opens `ui:ribbon-chart-format-text-effects-dropdown` — Applies shadow/reflection/glow/3D/transform effects to the object's text, incl. the Format Text Effects dialog.
- **Text Fill** (P3) · opens `ui:ribbon-chart-format-text-fill-color-dropdown` — Sets the fill color/gradient of the object's text (options in the picker).
- **Text Outline** (P4) · opens `ui:ribbon-chart-format-text-outline-color-dropdown` — Sets the outline of the object's text (options in the picker).
- **WordArt Styles gallery** (P3) — Applies a preset WordArt style to the text inside the object from the gallery.

## Contextual surfaces (measured trigger conditions)

- `ui:ribbon-chart-design` — **Chart Design (contextual tab)**: exists only while an embedded chart is selected (10 controls)
- `ui:ribbon-chart-format` — **Format (contextual tab)**: exists only while an embedded chart is selected (33 controls)
- `ui:ribbon-equation` — **Equation (contextual tab)**: exists only while the cursor is inside an equation (math zone) (20 controls)
- `ui:ribbon-graphics-format` — **Graphics Format (contextual tab)**: exists only while an SVG/icon graphic is selected (25 controls)
- `ui:ribbon-header-footer` — **Header & Footer (contextual tab)**: exists only while header/footer editing mode is active (cursor in header or footer) (22 controls)
- `ui:ribbon-picture-format` — **Picture Format (contextual tab)**: exists only while an inline picture is selected (31 controls)
- `ui:ribbon-shape-format` — **Shape Format (contextual tab)**: exists only while a drawn shape is selected | a text box is selected (34 controls)
- `ui:ribbon-smart-art-design` — **SmartArt Design (contextual tab)**: exists only while a SmartArt graphic is selected (14 controls)
- `ui:ribbon-smart-art-format` — **Format (contextual tab)**: exists only while a SmartArt graphic is selected (32 controls)
- `ui:ribbon-table-design` — **Table Design (contextual tab)**: exists only while selection is inside a table (19 controls)
- `ui:ribbon-table-layout` — **Table Layout (contextual tab)**: exists only while selection is inside a table (37 controls)

## Honest stubs (deliberately not entered — below the depth budget)

- `ui:bookmark-insert-dialog` (dialog) — Bookmark
- `ui:date-and-time-insert-dialog` (dialog) — Date and Time
- `ui:drop-cap-insert-dropdown` (dropdown) — Drop Cap
- `ui:icon-insert-from-file-dialog` (dialog) — Insert Icon
- `ui:insert3-dmodel-default-dialog` (dialog) — Insert 3D Model
- `ui:insert3-dmodel-default-menu` (menu) — 3D Models (dropdown)
- `ui:ole-objectct-insert-dialog` (dialog) — Object
- `ui:ole-objectct-insert-menu` (menu) — Object... (dropdown)
- `ui:quick-parts-insert-dropdown` (dropdown) — Quick Parts
- `ui:ribbon-chart-format-object-format-pane` (pane) — Format Object...
- `ui:ribbon-chart-format-text-outline-color-dropdown` (dropdown) — Text Outline
- `ui:ribbon-graphics-format-graphic-change-dropdown` (dropdown) — Change Graphic
- `ui:ribbon-graphics-format-graphics-color-dropdown` (dropdown) — Graphics Fill
- `ui:ribbon-graphics-format-graphics-effects-dropdown` (dropdown) — Graphics Effects
- `ui:ribbon-graphics-format-graphics-format-pane` (pane) — Format Graphic...
- `ui:ribbon-graphics-format-graphics-outline-color-dropdown` (dropdown) — Graphics Outline
- `ui:ribbon-header-footer-date-and-time-insert-dialog` (dialog) — Date and Time
- `ui:ribbon-header-footer-document-info-dropdown` (dropdown) — Document Info
- `ui:ribbon-header-footer-insert-alignment-tab-dialog` (dialog) — Alignment Tab
- `ui:ribbon-header-footer-quick-parts-insert-dropdown` (dropdown) — Quick Parts
- `ui:ribbon-picture-format-outline-color-dropdown` (dropdown) — Picture Border
- `ui:ribbon-picture-format-picture-artistic-effects-dropdown` (dropdown) — Artistic Effects
- `ui:ribbon-picture-format-picture-format-pane` (pane) — Picture...
- `ui:ribbon-picture-format-pictures-convert-to-smart-art-dropdown` (dropdown) — Picture Layout
- `ui:ribbon-shape-format-object-format-pane` (pane) — Format Object...
- `ui:ribbon-smart-art-format-object-format-pane` (pane) — Format Object...
- `ui:ribbon-smart-art-format-text-outline-color-dropdown` (dropdown) — Text Outline
- `ui:ribbon-table-layout-sort-dialog` (dialog) — Sort
- `ui:ribbon-table-layout-table-formula-dialog` (dialog) — Formula
- `ui:ribbon-table-layout-table-insert-cells-dialog` (dialog) — Insert Cells
- `ui:show-clipboard-pane` (pane) — Office Clipboard...
- `ui:signature-line-insert-dialog` (dialog) — Signature Setup
- `ui:signature-line-insert-menu` (menu) — Signature Line (dropdown)
- `ui:sort-dialog` (dialog) — Sort Text
- `ui:styles-pane` (pane) — Styles
- `ui:text-effects-dropdown` (dropdown) — Text Effects and Typography
- `ui:word-art-insert-dropdown` (dropdown) — WordArt

## Keyboard surface

- `Alt+=` — Inserts an empty math zone at the cursor (measured: OMaths 0→1) and activates the Equation contextua → `subfeature:equation-insert-gallery` (when: editing text — inserts a math zone at the cursor)
- `Alt+Ctrl+C` — copy formatting from the selection → `subfeature:format-painter` (when: document has focus)
- `Alt+Ctrl+Shift+S` — Opens the Styles pane — the full style list with apply/new/inspect/manage controls. → `ui:styles-pane` (when: document has focus)
- `Alt+Ctrl+V` — apply the copied formatting to the selection → `subfeature:format-painter` (when: document has focus)
- `Ctrl+*` — Toggles the on-screen display of paragraph marks and other hidden formatting symbols. → `subfeature:paragraph-marks` (when: document has focus (toggles a view setting))
- `Ctrl+Alt+M` — Creates a pending draft comment anchored at the selection and opens its card (measured: in-frame 'Po → `subfeature:insert-new-comment` (when: text selected or cursor placed (anchors the comment))
- `Ctrl+B` — Toggles bold (heavier) weight on the selected text. → `subfeature:bold` (when: editing text — applies to the selection or at the cursor)
- `Ctrl+C` — Copies the selection to the clipboard without changing the document. → `subfeature:copy` (when: document has focus)
- `Ctrl+D` — Opens the Font dialog — the consolidated surface for all character formatting plus advanced options  → `ui:font-dialog` (when: editing text — applies to the selection or at the cursor)
- `Ctrl+E` — Centers the paragraph text between the margins. → `subfeature:align-center` (when: editing text — applies to the current paragraph(s))
- `Ctrl+F` — Opens the Navigation pane to search the document for text; the dropdown offers Find, Advanced Find a → `ui:navigation-pane-find-pane` (when: document has focus)
- `Ctrl+H` — Opens the Find and Replace dialog to substitute text throughout the document. → `ui:replace-dialog` (when: document has focus)
- `Ctrl+I` — Toggles italic (slanted) style on the selected text. → `subfeature:italic` (when: editing text — applies to the selection or at the cursor)
- `Ctrl+J` — Spaces the paragraph text to align to both left and right margins. → `subfeature:align-justify` (when: editing text — applies to the current paragraph(s))
- `Ctrl+K` — Opens the Insert Hyperlink dialog to link the selection to webpages, files, headings or email addres → `ui:insert-link-dialog` (when: text or object selected (the link wraps the selection))
- `Ctrl+L` — Aligns the paragraph text to the left margin. → `subfeature:align-left` (when: editing text — applies to the current paragraph(s))
- `Ctrl+R` — Aligns the paragraph text to the right margin. → `subfeature:align-right` (when: editing text — applies to the current paragraph(s))
- `Ctrl+Return` — Ends the current page at the cursor and continues content on the next page (measured: doc + format d → `subfeature:page-break-insert` (when: editing text — inserts at the cursor position)
- `Ctrl+Shift++` — Places the selected text slightly above the baseline in a smaller size. → `subfeature:superscript` (when: editing text — applies to the selection or at the cursor)
- `Ctrl+Shift+<` — Decreases the font size of the selection to the previous step. → `subfeature:font-size-decrease` (when: editing text — applies to the selection or at the cursor)
- `Ctrl+Shift+>` — Increases the font size of the selection to the next step. → `subfeature:font-size-increase` (when: editing text — applies to the selection or at the cursor)
- `Ctrl+Shift+_` — Places the selected text slightly below the baseline in a smaller size. → `subfeature:subscript` (when: editing text — applies to the selection or at the cursor)
- `Ctrl+U` — Toggles an underline on the selected text; the dropdown picks the underline style and color. → `subfeature:underline-gallery` (when: editing text — applies to the selection or at the cursor)
- `Ctrl+V` — Inserts the clipboard's content at the cursor; the dropdown offers paste-special options (keep forma → `subfeature:paste` (when: document has focus)
- `Ctrl+X` — Removes the selection from the document and places it on the clipboard. → `subfeature:cut` (when: document has focus)

*Generated by scripts/tools/generate_overview.py — never hand-edited.*