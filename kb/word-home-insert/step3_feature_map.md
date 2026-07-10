# Word (Home + Insert universe) — Step 3 feature map

The three-level tree measured and authored by this run. **Home tab** features first, then **Insert tab**; boundary features last. Contextual tabs at the end.

## Clipboard (Home)
Move and duplicate content and formatting via the clipboard.
- **Copy** · Ctrl+C — Copies the selection to the clipboard without changing the document.
- **Cut** · Ctrl+X — Removes the selection from the document and places it on the clipboard.
- **Format Painter** · Alt+Ctrl+C, Alt+Ctrl+V — Copies formatting from the selection to reapply to the next thing you click.
- **Office Clipboard** — Opens the Office Clipboard pane showing the last 24 copied items for reuse. · opens ui:show-clipboard-pane
- **Paste** · Ctrl+V — Inserts the clipboard's content at the cursor; the dropdown offers paste-special options (keep formatting, merge, text only, picture). · opens ui:paste-dropdown

## Font (Home)
Format the characters of the selected text — typeface, size, weight, color, effects.
- **Bold** · Ctrl+B — Toggles bold (heavier) weight on the selected text.
- **Change Case** — Changes the capitalization of the selected text (Sentence case, lowercase, UPPERCASE, Capitalize Each Word, tOGGLE cASE). · opens ui:change-case-menu
- **Clear All Formatting** — Removes all character and paragraph formatting from the selection, leaving plain text.
- **Font** — Chooses the typeface for the selected text; the box opens a searchable font list. · opens ui:font-dropdown
- **Font Color** — Sets the color of the selected text; the dropdown opens a color picker (theme/standard/more). · opens ui:font-color-dropdown
- **Font dialog launcher** · Ctrl+D — Opens the Font dialog — the consolidated surface for all character formatting plus advanced options (spacing, ligatures, defaults). · opens ui:font-dialog
- **Font Size** — Sets the point size of the selected text; the box opens a size list. · opens ui:font-size-dropdown
- **Shrink Font** · Ctrl+Shift+< — Decreases the font size of the selection to the previous step.
- **Grow Font** · Ctrl+Shift+> — Increases the font size of the selection to the next step.
- **Italic** · Ctrl+I — Toggles italic (slanted) style on the selected text.
- **Strikethrough** — Draws a line through the middle of the selected text.
- **Subscript** · Ctrl+Shift+_ — Places the selected text slightly below the baseline in a smaller size.
- **Superscript** · Ctrl+Shift++ — Places the selected text slightly above the baseline in a smaller size.
- **Text Effects and Typography** — Applies visual text effects (outline, shadow, reflection, glow) and OpenType typography. · opens ui:text-effects-dropdown
- **Text Highlight Color** — Applies a highlighter color behind the text; the dropdown picks the color. · opens ui:text-highlight-color-dropdown
- **Underline** · Ctrl+U — Toggles an underline on the selected text; the dropdown picks the underline style and color. · opens ui:underline-menu

## Paragraph (Home)
Format whole paragraphs — lists, indentation, alignment, spacing, shading, borders.
- **Center** · Ctrl+E — Centers the paragraph text between the margins.
- **Justify** · Ctrl+J — Spaces the paragraph text to align to both left and right margins.
- **Align Left** · Ctrl+L — Aligns the paragraph text to the left margin.
- **Align Right** · Ctrl+R — Aligns the paragraph text to the right margin.
- **Borders** — Applies borders to the selection/paragraph; the dropdown lists border options and the Borders and Shading dialog. · opens ui:borders-selection-menu
- **Bullets** — Starts or toggles a bulleted list on the selected paragraphs; the dropdown is the bullet library. · opens ui:bullets-dropdown
- **Decrease Indent** — Moves the paragraph's left indent one level toward the margin.
- **Increase Indent** — Moves the paragraph's left indent one level away from the margin.
- **Line and Paragraph Spacing** — Sets the spacing between lines and before/after paragraphs. · opens ui:line-spacing-menu
- **Multilevel List** — Applies a multi-level (nested) list scheme to the selected paragraphs. · opens ui:multilevel-list-menu
- **Numbering** — Starts or toggles a numbered list on the selected paragraphs; the dropdown is the numbering library. · opens ui:numbering-dropdown
- **Paragraph dialog launcher** — Opens the Paragraph dialog — indentation, spacing, alignment and line/page-break options. · opens ui:paragraph-dialog
- **Show/Hide ¶** · Ctrl+* — Toggles the on-screen display of paragraph marks and other hidden formatting symbols.
- **Shading** — Fills the background of the selection/paragraph with a color; the dropdown picks the color. · opens ui:shading-color-dropdown
- **Sort** — Opens the Sort dialog to alphabetically/numerically sort the selected paragraphs, list or table. · opens ui:sort-dialog

## Styles (Home)
Apply named, reusable style sets that bundle character and paragraph formatting.
- **Quick Styles gallery** — Applies a named style (Normal, No Spacing, Heading 1/2, Title, Subtitle, Quote…) to the selection from the in-ribbon gallery. · opens ui:styles-gallery
- **Styles pane launcher** · Alt+Ctrl+Shift+S — Opens the Styles pane — the full style list with apply/new/inspect/manage controls. · opens ui:styles-pane

## Editing (Home)
Find, replace and select text within the document.
- **Find** · Ctrl+F — Opens the Navigation pane to search the document for text; the dropdown offers Find, Advanced Find and Go To. · opens ui:navigation-pane-find-pane
- **Replace** · Ctrl+H — Opens the Find and Replace dialog to substitute text throughout the document. · opens ui:replace-dialog
- **Select** — A menu to Select All, select objects, or select text with similar formatting. · opens ui:select-menu

## Pages (Insert)
Insert page-level structure: preformatted cover pages, blank pages, and page breaks.
- **Blank Page** — Inserts an empty page at the cursor position (measured: two page breaks around a new empty page).
- **Cover Page** — Inserts a preformatted, styled cover page (title/subtitle/date placeholders) at the start of the document, chosen from a gallery of designs. · opens ui:cover-page-insert-dropdown
- **Page Break** · Ctrl+Return — Ends the current page at the cursor and continues content on the next page (measured: doc + format delta).

## Tables (Insert)
Insert tables to organize content in rows and columns; a selected table brings up its own Table Design and Table Layout contextual tabs.
- **Table** — Opens the table builder: a hover grid to insert an N×M table instantly, plus Insert Table…, Draw Table, Convert Text to Table…, Excel Spreadsheet and Quick Tables. A selected table activates the Table Design + Table Layout contextual tabs (measured). · opens ui:table-insert-dropdown

## Illustrations (Insert)
Insert graphic objects — pictures, shapes, icons, 3D models, SmartArt diagrams, charts and screenshots; each selected object surfaces its own Format contextual tab(s).
- **Chart** — Opens the Insert Chart dialog (column, line, pie, bar, area, scatter, map…); an inserted chart activates the Chart Design + Format contextual tabs and opens an embedded Excel datasheet for its data (measured). · opens ui:chart-insert-dialog
- **Icons** — Opens the stock icon library dialog to insert symbol graphics (content streams from the Office CDN — network). · opens ui:icon-insert-from-file-dialog
- **3D Models** — Inserts a rotatable 3D model from the stock library (primary) or from a local file (the dropdown menu offers This Device / Stock 3D Models). · opens ui:insert3-dmodel-default-dialog
- **Pictures** — Inserts a picture from This Device, the Stock Images library, or Online Pictures; a selected picture activates the Picture Format contextual tab (measured). · opens ui:flyout-anchor-insert-pictures-menu
- **Screenshot** — Inserts a snapshot of any open window (gallery of live thumbnails) or a Screen Clipping region; the result is a picture (Picture Format applies). · opens ui:screenshot-insert-dropdown
- **Shapes** — Opens a gallery of ready-made shapes (lines, rectangles, arrows, callouts…) to draw into the document; a selected shape activates the Shape Format contextual tab (measured). · opens ui:shapes-insert-dropdown
- **SmartArt** — Opens the Choose a SmartArt Graphic dialog (lists, processes, cycles, hierarchies…); an inserted SmartArt activates the SmartArt Design + Format contextual tabs (measured). · opens ui:smart-art-insert-dialog

## Media (Insert)
Embed online videos into the document from web sources.
- **Online Videos** — Opens a dialog to embed an online video by URL (YouTube etc.); playback happens in-document (network content). · opens ui:movie-from-clip-organizer-insert-dialog

## Links (Insert)
Create navigation targets and jumps: hyperlinks, bookmarks and cross-references.
- **Bookmark** — Opens the Bookmark dialog to name the current place/selection so links and references can jump to it. · opens ui:bookmark-insert-dialog
- **Cross-reference** — Opens the Cross-reference dialog to insert a live reference to a heading, bookmark, figure or table (updates as the target moves). · opens ui:cross-reference-insert-dialog
- **Link** · Ctrl+K — Opens the Insert Hyperlink dialog to link the selection to webpages, files, headings or email addresses; the dropdown lists recent items. · opens ui:insert-link-dialog

## Comments (Insert)
Attach review comments to document ranges for collaboration.
- **Comment** · Ctrl+Alt+M — Creates a pending draft comment anchored at the selection and opens its card (measured: in-frame 'Post comment' button); the comment joins the review thread when posted.

## Header & Footer (Insert)
Repeat content at the top/bottom of every page and number the pages; editing them activates the Header & Footer contextual tab.
- **Footer** — Opens a gallery of built-in footer designs plus Edit/Remove Footer; applying one enters footer editing and activates the Header & Footer contextual tab. · opens ui:footer-insert-dropdown
- **Header** — Opens a gallery of built-in header designs (Blank, Austin, Banded…) plus Edit/Remove Header; applying one enters header editing and activates the Header & Footer contextual tab (measured). · opens ui:header-insert-dropdown
- **Page Number** — Opens a menu of page-number positions (top, bottom, margins, current position) and formats; numbers live in the header/footer stories. · opens ui:header-footer-page-number-insert-menu

## Text (Insert)
Insert text objects and building blocks: text boxes, Quick Parts/fields, WordArt, drop caps, signature lines, date/time and embedded objects.
- **Date & Time** — Opens a dialog of date/time formats to insert the current date or time, optionally as an auto-updating field. · opens ui:date-and-time-insert-dialog
- **Drop Cap** — Turns the paragraph's first letter into a large dropped capital (Dropped / In margin / options dialog); disabled until the document has text (measured). · opens ui:drop-cap-insert-dropdown
- **Object** — Embeds an OLE object (or inserts text from another file via the dropdown menu) into the document. · opens ui:ole-objectct-insert-dialog
- **Quick Parts** — Inserts reusable building blocks: AutoText, document properties and fields; also saves the selection to the gallery. · opens ui:quick-parts-insert-dropdown
- **Signature Line** — Opens the Signature Setup dialog to insert a signature line naming the required signer (digital signature requires a certificate). · opens ui:signature-line-insert-dialog
- **Text Box** — Inserts a floating text container from a gallery of built-in designs or by drawing one; a selected text box activates the Shape Format contextual tab (measured). · opens ui:text-box-insert-dropdown
- **WordArt** — Inserts decorative styled text from a gallery; the result is a text object whose selection activates a Format contextual tab (measured: modern WordArt uses Shape Format; legacy WordArt objects surface a dedicated WordArt tab). · opens ui:word-art-insert-dropdown

## Symbols (Insert)
Insert mathematical equations (with the Equation contextual tab) and special symbols not on the keyboard.
- **Equation** · Alt+= — Inserts an empty math zone at the cursor (measured: OMaths 0→1) and activates the Equation contextual tab; the dropdown offers built-in equations (quadratic formula, area of circle…). · opens ui:equation-insert-dropdown
- **Symbol** — Opens a gallery of recently used symbols plus More Symbols… (the full character map) to insert characters not on the keyboard. · opens ui:symbol-insert-dropdown

## Voice (Home) *(boundary — documented, never pressed)*
Dictate text by voice using cloud speech recognition.
- **Dictate** — Converts speech to text via the cloud dictation service.

## Editor (Home) *(boundary — documented, never pressed)*
Check spelling, grammar and writing refinements via the cloud Editor service.
- **Editor** — Opens the Editor pane with spelling, grammar and writing-refinement suggestions.

## Adobe Acrobat (Home) *(boundary — documented, never pressed)*
Create a PDF from the document via the Adobe Acrobat add-in.
- **Create a PDF** — Exports the document to a PDF using the Adobe Acrobat add-in.

## Add-ins (Home) *(boundary — documented, never pressed)*
Browse and launch Office Add-ins from the store.
- **Add-ins** — Opens the Office Add-ins store flyout to browse and insert add-ins.

## eSignature (Insert) *(boundary — documented, never pressed)*
Request electronic signatures on the document via the SharePoint Syntex cloud service.
- **eSignature fields** — Requests electronic signatures on the document through the SharePoint Syntex service.

## Contextual tabs (measured with trigger conditions)
- **Chart Design (contextual tab)** — appears when: an embedded chart is selected (9 controls on its face)
- **Format (contextual tab)** — appears when: an embedded chart is selected (29 controls on its face)
- **Equation (contextual tab)** — appears when: the cursor is inside an equation (math zone) (19 controls on its face)
- **Header & Footer (contextual tab)** — appears when: header/footer editing mode is active (cursor in header or footer) (22 controls on its face)
- **Picture Format (contextual tab)** — appears when: an inline picture is selected (28 controls on its face)
- **Shape Format (contextual tab)** — appears when: a drawn shape is selected | a text box is selected (30 controls on its face)
- **SmartArt Design (contextual tab)** — appears when: a SmartArt graphic is selected (13 controls on its face)
- **Format (contextual tab)** — appears when: a SmartArt graphic is selected (28 controls on its face)
- **Table Design (contextual tab)** — appears when: selection is inside a table (15 controls on its face)
- **Table Layout (contextual tab)** — appears when: selection is inside a table (37 controls on its face)
- **WordArt (contextual tab)** — appears when: a WordArt object is selected (33 controls on its face)