# Microsoft Word — Knowledge Base overview

**Version (build):** 16.0.20131 · **Platform:** desktop · **Scope of this KB:** the **Home and Insert tabs** (plus the contextual tabs their features trigger) treated as the whole application.

**What it is.** A desktop word processor for creating, formatting and editing text documents.

**Used for.** Writing and formatting documents — letters, reports, essays, resumes — with rich text styling, paragraph layout, lists, styles, tables, graphics, headers/footers and review tools.

**Who uses it.** Students, office workers, writers, and virtually anyone producing formatted text documents.

## At a glance
- **19 features**, **74 sub-features**, **91 UI containers** (69 explored to depth, 22 deliberate stubs), **25 keyboard shortcuts**, **11 contextual ribbon tabs**.
- **Priority layers:** P0=4 · P1=15 · P2=17 · P3=22 · P4=35

## Skeleton (measured trigger surface)
The main window hosts the ribbon tab strip. The **Home** and **Insert** tab faces were mapped by pressing every control and classifying the measured outcome (opens a dialog/dropdown/menu/pane, or triggers a document/format/object action). Other always-present tabs are named but unexplored. **Contextual tabs** exist only in context; each was discovered by inserting its object and is documented with its measured trigger condition:

- **Chart Design (contextual tab)** — exists while: an embedded chart is selected (9 face controls)
- **Format (contextual tab)** — exists while: an embedded chart is selected (29 face controls)
- **Equation (contextual tab)** — exists while: the cursor is inside an equation (math zone) (19 face controls)
- **Header & Footer (contextual tab)** — exists while: header/footer editing mode is active (cursor in header or footer) (22 face controls)
- **Picture Format (contextual tab)** — exists while: an inline picture is selected (28 face controls)
- **Shape Format (contextual tab)** — exists while: a drawn shape is selected | a text box is selected (30 face controls)
- **SmartArt Design (contextual tab)** — exists while: a SmartArt graphic is selected (13 face controls)
- **Format (contextual tab)** — exists while: a SmartArt graphic is selected (28 face controls)
- **Table Design (contextual tab)** — exists while: selection is inside a table (15 face controls)
- **Table Layout (contextual tab)** — exists while: selection is inside a table (37 face controls)
- **WordArt (contextual tab)** — exists while: a WordArt object is selected (33 face controls)

## Feature tree (priority-ranked)
### Clipboard (Home)
Move and duplicate content and formatting via the clipboard. _(affects: document content and the Office clipboard; audience: everyone)_

- **[P1]* Paste** · `Ctrl+V` — Inserts the clipboard's content at the cursor; the dropdown offers paste-special options (keep formatting, merge, text only, picture). _(affects: document content)_ · opens `ui:paste-dropdown`
- **[P1]* Copy** · `Ctrl+C` — Copies the selection to the clipboard without changing the document. _(affects: the Office clipboard)_
- **[P1]* Cut** · `Ctrl+X` — Removes the selection from the document and places it on the clipboard. _(affects: document content + clipboard)_
- **[P3] Format Painter** · `Alt+Ctrl+C, Alt+Ctrl+V` — Copies formatting from the selection to reapply to the next thing you click. _(affects: the formatting of the next selection)_
- **[P4] Office Clipboard** — Opens the Office Clipboard pane showing the last 24 copied items for reuse. _(affects: opens the Clipboard task pane)_ · opens `ui:show-clipboard-pane`

### Font (Home)
Format the characters of the selected text — typeface, size, weight, color, effects. _(affects: the selection's character formatting; audience: everyone)_

- **[P0]* Bold** · `Ctrl+B` — Toggles bold (heavier) weight on the selected text. _(affects: the selection's character format (bold))_
- **[P0]* Font** — Chooses the typeface for the selected text; the box opens a searchable font list. _(affects: the selection's font (typeface))_ · opens `ui:font-dropdown`
- **[P0]* Font Size** — Sets the point size of the selected text; the box opens a size list. _(affects: the selection's font size)_ · opens `ui:font-size-dropdown`
- **[P1]* Italic** · `Ctrl+I` — Toggles italic (slanted) style on the selected text. _(affects: the selection's character format (italic))_
- **[P1]* Underline** · `Ctrl+U` — Toggles an underline on the selected text; the dropdown picks the underline style and color. _(affects: the selection's character format (underline))_ · opens `ui:underline-menu`
- **[P1]* Font Color** — Sets the color of the selected text; the dropdown opens a color picker (theme/standard/more). _(affects: the selection's font color)_ · opens `ui:font-color-dropdown`
- **[P2]* Font dialog launcher** · `Ctrl+D` — Opens the Font dialog — the consolidated surface for all character formatting plus advanced options (spacing, ligatures, defaults). _(affects: opens the Font dialog)_ · opens `ui:font-dialog`
- **[P3] Text Highlight Color** — Applies a highlighter color behind the text; the dropdown picks the color. _(affects: the selection's highlight color)_ · opens `ui:text-highlight-color-dropdown`
- **[P3] Strikethrough** — Draws a line through the middle of the selected text. _(affects: the selection's character format (strikethrough))_
- **[P3] Shrink Font** · `Ctrl+Shift+<` — Decreases the font size of the selection to the previous step. _(affects: the selection's font size)_
- **[P3] Grow Font** · `Ctrl+Shift+>` — Increases the font size of the selection to the next step. _(affects: the selection's font size)_
- **[P4] Clear All Formatting** — Removes all character and paragraph formatting from the selection, leaving plain text. _(affects: the selection's formatting (reset to default))_
- **[P4] Change Case** — Changes the capitalization of the selected text (Sentence case, lowercase, UPPERCASE, Capitalize Each Word, tOGGLE cASE). _(affects: the case of the selected text)_ · opens `ui:change-case-menu`
- **[P4] Subscript** · `Ctrl+Shift+_` — Places the selected text slightly below the baseline in a smaller size. _(affects: the selection's character format (subscript))_
- **[P4] Superscript** · `Ctrl+Shift++` — Places the selected text slightly above the baseline in a smaller size. _(affects: the selection's character format (superscript))_
- **[P4] Text Effects and Typography** — Applies visual text effects (outline, shadow, reflection, glow) and OpenType typography. _(affects: the selection's character appearance)_ · opens `ui:text-effects-dropdown`

### Paragraph (Home)
Format whole paragraphs — lists, indentation, alignment, spacing, shading, borders. _(affects: the selected paragraphs' formatting and layout; audience: everyone)_

- **[P1]* Center** · `Ctrl+E` — Centers the paragraph text between the margins. _(affects: the paragraph's alignment)_
- **[P1]* Align Left** · `Ctrl+L` — Aligns the paragraph text to the left margin. _(affects: the paragraph's alignment)_
- **[P2]* Align Right** · `Ctrl+R` — Aligns the paragraph text to the right margin. _(affects: the paragraph's alignment)_
- **[P2]* Paragraph dialog launcher** — Opens the Paragraph dialog — indentation, spacing, alignment and line/page-break options. _(affects: opens the Paragraph dialog)_ · opens `ui:paragraph-dialog`
- **[P2]* Bullets** — Starts or toggles a bulleted list on the selected paragraphs; the dropdown is the bullet library. _(affects: the selected paragraphs' list format)_ · opens `ui:bullets-dropdown`
- **[P2]* Numbering** — Starts or toggles a numbered list on the selected paragraphs; the dropdown is the numbering library. _(affects: the selected paragraphs' list format)_ · opens `ui:numbering-dropdown`
- **[P2]* Line and Paragraph Spacing** — Sets the spacing between lines and before/after paragraphs. _(affects: the paragraph's line and spacing)_ · opens `ui:line-spacing-menu`
- **[P3] Justify** · `Ctrl+J` — Spaces the paragraph text to align to both left and right margins. _(affects: the paragraph's alignment)_
- **[P3] Decrease Indent** — Moves the paragraph's left indent one level toward the margin. _(affects: the paragraph's left indent)_
- **[P3] Increase Indent** — Moves the paragraph's left indent one level away from the margin. _(affects: the paragraph's left indent)_
- **[P3] Shading** — Fills the background of the selection/paragraph with a color; the dropdown picks the color. _(affects: the paragraph/selection background shading)_ · opens `ui:shading-color-dropdown`
- **[P3] Borders** — Applies borders to the selection/paragraph; the dropdown lists border options and the Borders and Shading dialog. _(affects: the paragraph/selection borders)_ · opens `ui:borders-selection-menu`
- **[P4] Show/Hide ¶** · `Ctrl+*` — Toggles the on-screen display of paragraph marks and other hidden formatting symbols. _(affects: the view (formatting marks visibility) — not the document)_
- **[P4] Multilevel List** — Applies a multi-level (nested) list scheme to the selected paragraphs. _(affects: the selected paragraphs' multi-level list format)_ · opens `ui:multilevel-list-menu`
- **[P4] Sort** — Opens the Sort dialog to alphabetically/numerically sort the selected paragraphs, list or table. _(affects: the order of the selected paragraphs)_ · opens `ui:sort-dialog`

### Styles (Home)
Apply named, reusable style sets that bundle character and paragraph formatting. _(affects: the paragraph/character style applied to the selection; audience: most)_

- **[P2]* Quick Styles gallery** — Applies a named style (Normal, No Spacing, Heading 1/2, Title, Subtitle, Quote…) to the selection from the in-ribbon gallery. _(affects: the paragraph/character style applied)_ · opens `ui:styles-gallery`
- **[P4] Styles pane launcher** · `Alt+Ctrl+Shift+S` — Opens the Styles pane — the full style list with apply/new/inspect/manage controls. _(affects: opens the Styles task pane)_ · opens `ui:styles-pane`

### Editing (Home)
Find, replace and select text within the document. _(affects: navigation and selection within the document; audience: most)_

- **[P1]* Find** · `Ctrl+F` — Opens the Navigation pane to search the document for text; the dropdown offers Find, Advanced Find and Go To. _(affects: opens the Navigation pane / search)_ · opens `ui:navigation-pane-find-pane`
- **[P3] Replace** · `Ctrl+H` — Opens the Find and Replace dialog to substitute text throughout the document. _(affects: document content (via replace))_ · opens `ui:replace-dialog`
- **[P4] Select** — A menu to Select All, select objects, or select text with similar formatting. _(affects: the current selection)_ · opens `ui:select-menu`

### Pages (Insert)
Insert page-level structure: preformatted cover pages, blank pages, and page breaks. _(affects: the document's page structure and flow; audience: most)_

- **[P1]* Page Break** · `Ctrl+Return` — Ends the current page at the cursor and continues content on the next page (measured: doc + format delta). _(affects: document content (page flow))_
- **[P3] Cover Page** — Inserts a preformatted, styled cover page (title/subtitle/date placeholders) at the start of the document, chosen from a gallery of designs. _(affects: document content (adds a formatted first page))_ · opens `ui:cover-page-insert-dropdown`
- **[P4] Blank Page** — Inserts an empty page at the cursor position (measured: two page breaks around a new empty page). _(affects: document content (page flow))_

### Tables (Insert)
Insert tables to organize content in rows and columns; a selected table brings up its own Table Design and Table Layout contextual tabs. _(affects: document content (adds a table object); audience: everyone)_

- **[P1]* Table** — Opens the table builder: a hover grid to insert an N×M table instantly, plus Insert Table…, Draw Table, Convert Text to Table…, Excel Spreadsheet and Quick Tables. A selected table activates the Table Design + Table Layout contextual tabs (measured). _(affects: document content (adds a table object))_ · opens `ui:table-insert-dropdown`

### Illustrations (Insert)
Insert graphic objects — pictures, shapes, icons, 3D models, SmartArt diagrams, charts and screenshots; each selected object surfaces its own Format contextual tab(s). _(affects: document content (adds graphic objects); audience: everyone)_

- **[P0]* Pictures** — Inserts a picture from This Device, the Stock Images library, or Online Pictures; a selected picture activates the Picture Format contextual tab (measured). _(affects: document content (adds an image))_ · opens `ui:flyout-anchor-insert-pictures-menu`
- **[P2]* Shapes** — Opens a gallery of ready-made shapes (lines, rectangles, arrows, callouts…) to draw into the document; a selected shape activates the Shape Format contextual tab (measured). _(affects: document content (adds a drawn shape))_ · opens `ui:shapes-insert-dropdown`
- **[P3] Chart** — Opens the Insert Chart dialog (column, line, pie, bar, area, scatter, map…); an inserted chart activates the Chart Design + Format contextual tabs and opens an embedded Excel datasheet for its data (measured). _(affects: document content (adds a chart backed by worksheet data))_ · opens `ui:chart-insert-dialog`
- **[P3] SmartArt** — Opens the Choose a SmartArt Graphic dialog (lists, processes, cycles, hierarchies…); an inserted SmartArt activates the SmartArt Design + Format contextual tabs (measured). _(affects: document content (adds a SmartArt diagram))_ · opens `ui:smart-art-insert-dialog`
- **[P3] Screenshot** — Inserts a snapshot of any open window (gallery of live thumbnails) or a Screen Clipping region; the result is a picture (Picture Format applies). _(affects: document content (adds a screenshot image))_ · opens `ui:screenshot-insert-dropdown`
- **[P4] Icons** — Opens the stock icon library dialog to insert symbol graphics (content streams from the Office CDN — network). _(affects: document content (adds an icon graphic))_ · opens `ui:icon-insert-from-file-dialog`
- **[P4] 3D Models** — Inserts a rotatable 3D model from the stock library (primary) or from a local file (the dropdown menu offers This Device / Stock 3D Models). _(affects: document content (adds a 3D model object))_ · opens `ui:insert3-dmodel-default-dialog`

### Media (Insert)
Embed online videos into the document from web sources. _(affects: document content (adds an embedded video); audience: niche)_

- **[P4] Online Videos** — Opens a dialog to embed an online video by URL (YouTube etc.); playback happens in-document (network content). _(affects: document content (adds an embedded video))_ · opens `ui:movie-from-clip-organizer-insert-dialog`

### Links (Insert)
Create navigation targets and jumps: hyperlinks, bookmarks and cross-references. _(affects: navigation structure (links, bookmarks, references); audience: most)_

- **[P2]* Link** · `Ctrl+K` — Opens the Insert Hyperlink dialog to link the selection to webpages, files, headings or email addresses; the dropdown lists recent items. _(affects: the selection (wraps it in a hyperlink))_ · opens `ui:insert-link-dialog`
- **[P4] Bookmark** — Opens the Bookmark dialog to name the current place/selection so links and references can jump to it. _(affects: the document's bookmark registry)_ · opens `ui:bookmark-insert-dialog`
- **[P4] Cross-reference** — Opens the Cross-reference dialog to insert a live reference to a heading, bookmark, figure or table (updates as the target moves). _(affects: document content (adds a reference field))_ · opens `ui:cross-reference-insert-dialog`

### Comments (Insert)
Attach review comments to document ranges for collaboration. _(affects: the document's comment thread (review layer); audience: most)_

- **[P3] Comment** · `Ctrl+Alt+M` — Creates a pending draft comment anchored at the selection and opens its card (measured: in-frame 'Post comment' button); the comment joins the review thread when posted. _(affects: the document's comment thread)_

### Header & Footer (Insert)
Repeat content at the top/bottom of every page and number the pages; editing them activates the Header & Footer contextual tab. _(affects: the header/footer stories of every page; audience: most)_

- **[P2]* Footer** — Opens a gallery of built-in footer designs plus Edit/Remove Footer; applying one enters footer editing and activates the Header & Footer contextual tab. _(affects: the footer story of every page)_ · opens `ui:footer-insert-dropdown`
- **[P2]* Header** — Opens a gallery of built-in header designs (Blank, Austin, Banded…) plus Edit/Remove Header; applying one enters header editing and activates the Header & Footer contextual tab (measured). _(affects: the header story of every page)_ · opens `ui:header-insert-dropdown`
- **[P2]* Page Number** — Opens a menu of page-number positions (top, bottom, margins, current position) and formats; numbers live in the header/footer stories. _(affects: the header/footer stories (page numbering))_ · opens `ui:header-footer-page-number-insert-menu`

### Text (Insert)
Insert text objects and building blocks: text boxes, Quick Parts/fields, WordArt, drop caps, signature lines, date/time and embedded objects. _(affects: document content (adds text objects/fields); audience: most)_

- **[P3] Text Box** — Inserts a floating text container from a gallery of built-in designs or by drawing one; a selected text box activates the Shape Format contextual tab (measured). _(affects: document content (adds a floating text container))_ · opens `ui:text-box-insert-dropdown`
- **[P4] Quick Parts** — Inserts reusable building blocks: AutoText, document properties and fields; also saves the selection to the gallery. _(affects: document content (adds building blocks/fields))_ · opens `ui:quick-parts-insert-dropdown`
- **[P4] WordArt** — Inserts decorative styled text from a gallery; the result is a text object whose selection activates a Format contextual tab (measured: modern WordArt uses Shape Format; legacy WordArt objects surface a dedicated WordArt tab). _(affects: document content (adds decorative text))_ · opens `ui:word-art-insert-dropdown`
- **[P4] Object** — Embeds an OLE object (or inserts text from another file via the dropdown menu) into the document. _(affects: document content (adds an embedded object))_ · opens `ui:ole-objectct-insert-dialog`
- **[P4] Date & Time** — Opens a dialog of date/time formats to insert the current date or time, optionally as an auto-updating field. _(affects: document content (adds date/time text or field))_ · opens `ui:date-and-time-insert-dialog`
- **[P4] Drop Cap** — Turns the paragraph's first letter into a large dropped capital (Dropped / In margin / options dialog); disabled until the document has text (measured). _(affects: the first paragraph character's layout)_ · opens `ui:drop-cap-insert-dropdown`
- **[P4] Signature Line** — Opens the Signature Setup dialog to insert a signature line naming the required signer (digital signature requires a certificate). _(affects: document content (adds a signature line object))_ · opens `ui:signature-line-insert-dialog`

### Symbols (Insert)
Insert mathematical equations (with the Equation contextual tab) and special symbols not on the keyboard. _(affects: document content (adds equations/symbols); audience: most)_

- **[P3] Symbol** — Opens a gallery of recently used symbols plus More Symbols… (the full character map) to insert characters not on the keyboard. _(affects: document content (adds a symbol character))_ · opens `ui:symbol-insert-dropdown`
- **[P4] Equation** · `Alt+=` — Inserts an empty math zone at the cursor (measured: OMaths 0→1) and activates the Equation contextual tab; the dropdown offers built-in equations (quadratic formula, area of circle…). _(affects: document content (adds an equation/math zone))_ · opens `ui:equation-insert-dropdown`

### Voice (Home) _(boundary — not pressed; documented from knowledge)_
Dictate text by voice using cloud speech recognition. _(affects: document content (inserted by speech); audience: niche)_

- **[P4] Dictate** — Converts speech to text via the cloud dictation service. _(affects: document content)_

### Editor (Home) _(boundary — not pressed; documented from knowledge)_
Check spelling, grammar and writing refinements via the cloud Editor service. _(affects: the document text (proofing) and the Editor pane; audience: most)_

- **[P4] Editor** — Opens the Editor pane with spelling, grammar and writing-refinement suggestions. _(affects: the document text (proofing) and Editor pane)_

### Adobe Acrobat (Home) _(boundary — not pressed; documented from knowledge)_
Create a PDF from the document via the Adobe Acrobat add-in. _(affects: produces a PDF file (external add-in); audience: niche)_

- **[P4] Create a PDF** — Exports the document to a PDF using the Adobe Acrobat add-in. _(affects: produces a PDF file)_

### Add-ins (Home) _(boundary — not pressed; documented from knowledge)_
Browse and launch Office Add-ins from the store. _(affects: opens the add-in store (external content); audience: niche)_

- **[P4] Add-ins** — Opens the Office Add-ins store flyout to browse and insert add-ins. _(affects: opens the add-in store)_

### eSignature (Insert) _(boundary — not pressed; documented from knowledge)_
Request electronic signatures on the document via the SharePoint Syntex cloud service. _(affects: starts a cloud e-signature request; audience: niche)_

- **[P4] eSignature fields** — Requests electronic signatures on the document through the SharePoint Syntex service. _(affects: starts a cloud e-signature request)_

## Keyboard shortcuts (registry)
- `Alt+=` — Inserts an empty math zone at the cursor (measured: OMaths 0→1) and activates the Equation contextual tab; the dropdown offers built-in equations (quadratic formula, area of circle…). → `subfeature:equation-insert-gallery` _(editing text — inserts a math zone at the cursor; source: docs)_
- `Alt+Ctrl+C` — copy formatting from the selection → `subfeature:format-painter` _(document has focus; source: uia-accelerator,tooltip)_
- `Alt+Ctrl+Shift+S` — Opens the Styles pane — the full style list with apply/new/inspect/manage controls. → `ui:styles-pane` _(document has focus; source: uia-accelerator,tooltip)_
- `Alt+Ctrl+V` — apply the copied formatting to the selection → `subfeature:format-painter` _(document has focus; source: uia-accelerator,tooltip)_
- `Ctrl+*` — Toggles the on-screen display of paragraph marks and other hidden formatting symbols. → `subfeature:paragraph-marks` _(document has focus (toggles a view setting); source: uia-accelerator,tooltip)_
- `Ctrl+Alt+M` — Creates a pending draft comment anchored at the selection and opens its card (measured: in-frame 'Post comment' button); the comment joins the review thread when posted. → `subfeature:insert-new-comment` _(text selected or cursor placed (anchors the comment); source: docs)_
- `Ctrl+B` — Toggles bold (heavier) weight on the selected text. → `subfeature:bold` _(editing text — applies to the selection or at the cursor; source: uia-accelerator,tooltip)_
- `Ctrl+C` — Copies the selection to the clipboard without changing the document. → `subfeature:copy` _(document has focus; source: uia-accelerator,tooltip)_
- `Ctrl+D` — Opens the Font dialog — the consolidated surface for all character formatting plus advanced options (spacing, ligatures, defaults). → `ui:font-dialog` _(editing text — applies to the selection or at the cursor; source: uia-accelerator,tooltip)_
- `Ctrl+E` — Centers the paragraph text between the margins. → `subfeature:align-center` _(editing text — applies to the current paragraph(s); source: uia-accelerator,tooltip)_
- `Ctrl+F` — Opens the Navigation pane to search the document for text; the dropdown offers Find, Advanced Find and Go To. → `ui:navigation-pane-find-pane` _(document has focus; source: uia-accelerator,tooltip)_
- `Ctrl+H` — Opens the Find and Replace dialog to substitute text throughout the document. → `ui:replace-dialog` _(document has focus; source: uia-accelerator,tooltip)_
- `Ctrl+I` — Toggles italic (slanted) style on the selected text. → `subfeature:italic` _(editing text — applies to the selection or at the cursor; source: uia-accelerator,tooltip)_
- `Ctrl+J` — Spaces the paragraph text to align to both left and right margins. → `subfeature:align-justify` _(editing text — applies to the current paragraph(s); source: uia-accelerator,tooltip)_
- `Ctrl+K` — Opens the Insert Hyperlink dialog to link the selection to webpages, files, headings or email addresses; the dropdown lists recent items. → `ui:insert-link-dialog` _(text or object selected (the link wraps the selection); source: docs)_
- `Ctrl+L` — Aligns the paragraph text to the left margin. → `subfeature:align-left` _(editing text — applies to the current paragraph(s); source: uia-accelerator,tooltip)_
- `Ctrl+R` — Aligns the paragraph text to the right margin. → `subfeature:align-right` _(editing text — applies to the current paragraph(s); source: uia-accelerator,tooltip)_
- `Ctrl+Return` — Ends the current page at the cursor and continues content on the next page (measured: doc + format delta). → `subfeature:page-break-insert` _(editing text — inserts at the cursor position; source: uia-accelerator,tooltip)_
- `Ctrl+Shift++` — Places the selected text slightly above the baseline in a smaller size. → `subfeature:superscript` _(editing text — applies to the selection or at the cursor; source: uia-accelerator,tooltip)_
- `Ctrl+Shift+<` — Decreases the font size of the selection to the previous step. → `subfeature:font-size-decrease` _(editing text — applies to the selection or at the cursor; source: uia-accelerator,tooltip)_
- `Ctrl+Shift+>` — Increases the font size of the selection to the next step. → `subfeature:font-size-increase` _(editing text — applies to the selection or at the cursor; source: uia-accelerator,tooltip)_
- `Ctrl+Shift+_` — Places the selected text slightly below the baseline in a smaller size. → `subfeature:subscript` _(editing text — applies to the selection or at the cursor; source: uia-accelerator,tooltip)_
- `Ctrl+U` — Toggles an underline on the selected text; the dropdown picks the underline style and color. → `subfeature:underline-gallery` _(editing text — applies to the selection or at the cursor; source: uia-accelerator,tooltip)_
- `Ctrl+V` — Inserts the clipboard's content at the cursor; the dropdown offers paste-special options (keep formatting, merge, text only, picture). → `subfeature:paste` _(document has focus; source: uia-accelerator,tooltip)_
- `Ctrl+X` — Removes the selection from the document and places it on the clipboard. → `subfeature:cut` _(document has focus; source: uia-accelerator,tooltip)_

## How priority was decided
Every node's layer is a recorded weighted sum of three signals — connectivity (degree over the affects/uses graph), real-world usage (web-researched, evidence-cited), and audience breadth — cut at recorded boundaries. See `priority/JUSTIFICATION.md` and `priority/ranking.json`.

_Generated from the node files; the append-only `journal.jsonl` reconstructs the full run._