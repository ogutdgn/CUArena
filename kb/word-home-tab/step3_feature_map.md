# Step 3 — Home-tab feature map (human-readable)

## Clipboard  ·  audience: everyone
Move and duplicate content and formatting via the clipboard.  
*Affects:* document content and the Office clipboard

- **Copy** [Ctrl+C] — Copies the selection to the clipboard without changing the document. _(affects: the Office clipboard; everyone)_
- **Cut** [Ctrl+X] — Removes the selection from the document and places it on the clipboard. _(affects: document content + clipboard; everyone)_
- **Format Painter** [Ctrl+Shift+C] — Copies formatting from the selection to reapply to the next thing you click. _(affects: the formatting of the next selection; most)_
- **Office Clipboard** — Opens the Office Clipboard pane showing the last 24 copied items for reuse. _(affects: opens the Clipboard task pane; niche)_ → opens `ui:show-clipboard-pane`
- **Paste** [Ctrl+V] — Inserts the clipboard's content at the cursor; the dropdown offers paste-special options (keep formatting, merge, text only, picture). _(affects: document content; everyone)_ → opens `ui:paste-dropdown`

## Font  ·  audience: everyone
Format the characters of the selected text — typeface, size, weight, color, effects.  
*Affects:* the selection's character formatting

- **Bold** [Ctrl+B] — Toggles bold (heavier) weight on the selected text. _(affects: the selection's character format (bold); everyone)_
- **Change Case** — Changes the capitalization of the selected text (Sentence case, lowercase, UPPERCASE, Capitalize Each Word, tOGGLE cASE). _(affects: the case of the selected text; most)_ → opens `ui:change-case-menu`
- **Clear All Formatting** — Removes all character and paragraph formatting from the selection, leaving plain text. _(affects: the selection's formatting (reset to default); most)_
- **Font Color** — Sets the color of the selected text; the dropdown opens a color picker (theme/standard/more). _(affects: the selection's font color; everyone)_ → opens `ui:font-color-dropdown`
- **Font dialog launcher** [Ctrl+D] — Opens the Font dialog — the consolidated surface for all character formatting plus advanced options (spacing, ligatures, defaults). _(affects: opens the Font dialog; most)_ → opens `ui:font-dialog`
- **Shrink Font** [Ctrl+Shift+<] — Decreases the font size of the selection to the previous step. _(affects: the selection's font size; most)_
- **Grow Font** [Ctrl+Shift+>] — Increases the font size of the selection to the next step. _(affects: the selection's font size; most)_
- **Font Size** — Sets the point size of the selected text; the box opens a size list. _(affects: the selection's font size; everyone)_ → opens `ui:font-size-dropdown`
- **Font** — Chooses the typeface for the selected text; the box opens a searchable font list. _(affects: the selection's font (typeface); everyone)_ → opens `ui:font-dropdown`
- **Italic** [Ctrl+I] — Toggles italic (slanted) style on the selected text. _(affects: the selection's character format (italic); everyone)_
- **Strikethrough** — Draws a line through the middle of the selected text. _(affects: the selection's character format (strikethrough); most)_
- **Subscript** [Ctrl+Shift+=] — Places the selected text slightly below the baseline in a smaller size. _(affects: the selection's character format (subscript); niche)_
- **Superscript** [Ctrl+Shift++] — Places the selected text slightly above the baseline in a smaller size. _(affects: the selection's character format (superscript); niche)_
- **Text Effects and Typography** — Applies visual text effects (outline, shadow, reflection, glow) and OpenType typography. _(affects: the selection's character appearance; niche)_ → opens `ui:text-effects-dropdown`
- **Text Highlight Color** — Applies a highlighter color behind the text; the dropdown picks the color. _(affects: the selection's highlight color; most)_ → opens `ui:text-highlight-color-dropdown`
- **Underline** [Ctrl+U] — Toggles an underline on the selected text; the dropdown picks the underline style and color. _(affects: the selection's character format (underline); everyone)_ → opens `ui:underline-menu`

## Paragraph  ·  audience: everyone
Format whole paragraphs — lists, indentation, alignment, spacing, shading, borders.  
*Affects:* the selected paragraphs' formatting and layout

- **Center** [Ctrl+E] — Centers the paragraph text between the margins. _(affects: the paragraph's alignment; everyone)_
- **Justify** [Ctrl+J] — Spaces the paragraph text to align to both left and right margins. _(affects: the paragraph's alignment; most)_
- **Align Left** [Ctrl+L] — Aligns the paragraph text to the left margin. _(affects: the paragraph's alignment; everyone)_
- **Align Right** [Ctrl+R] — Aligns the paragraph text to the right margin. _(affects: the paragraph's alignment; everyone)_
- **Borders** — Applies borders to the selection/paragraph; the dropdown lists border options and the Borders and Shading dialog. _(affects: the paragraph/selection borders; most)_ → opens `ui:borders-selection-menu`
- **Bullets** — Starts or toggles a bulleted list on the selected paragraphs; the dropdown is the bullet library. _(affects: the selected paragraphs' list format; most)_ → opens `ui:bullets-dropdown`
- **Decrease Indent** — Moves the paragraph's left indent one level toward the margin. _(affects: the paragraph's left indent; most)_
- **Increase Indent** — Moves the paragraph's left indent one level away from the margin. _(affects: the paragraph's left indent; most)_
- **Line and Paragraph Spacing** — Sets the spacing between lines and before/after paragraphs. _(affects: the paragraph's line and spacing; most)_ → opens `ui:line-spacing-menu`
- **Multilevel List** — Applies a multi-level (nested) list scheme to the selected paragraphs. _(affects: the selected paragraphs' multi-level list format; niche)_ → opens `ui:multilevel-list-menu`
- **Numbering** — Starts or toggles a numbered list on the selected paragraphs; the dropdown is the numbering library. _(affects: the selected paragraphs' list format; most)_ → opens `ui:numbering-dropdown`
- **Paragraph dialog launcher** — Opens the Paragraph dialog — indentation, spacing, alignment and line/page-break options. _(affects: opens the Paragraph dialog; most)_ → opens `ui:paragraph-dialog`
- **Show/Hide ¶** [Ctrl+*] — Toggles the on-screen display of paragraph marks and other hidden formatting symbols. _(affects: the view (formatting marks visibility) — not the document; most)_
- **Shading** — Fills the background of the selection/paragraph with a color; the dropdown picks the color. _(affects: the paragraph/selection background shading; most)_ → opens `ui:shading-color-dropdown`
- **Sort** — Opens the Sort dialog to alphabetically/numerically sort the selected paragraphs, list or table. _(affects: the order of the selected paragraphs; niche)_ → opens `ui:sort-dialog`

## Styles  ·  audience: most
Apply named, reusable style sets that bundle character and paragraph formatting.  
*Affects:* the paragraph/character style applied to the selection

- **Quick Styles gallery** — Applies a named style (Normal, No Spacing, Heading 1/2, Title, Subtitle, Quote…) to the selection from the in-ribbon gallery. _(affects: the paragraph/character style applied; most)_ → opens `ui:styles-gallery`
- **Styles pane launcher** [Alt+Ctrl+Shift+S] — Opens the Styles pane — the full style list with apply/new/inspect/manage controls. _(affects: opens the Styles task pane; niche)_ → opens `ui:styles-pane`

## Editing  ·  audience: most
Find, replace and select text within the document.  
*Affects:* navigation and selection within the document

- **Find** [Ctrl+F] — Opens the Navigation pane to search the document for text; the dropdown offers Find, Advanced Find and Go To. _(affects: opens the Navigation pane / search; everyone)_ → opens `ui:navigation-pane-find-pane`
- **Replace** [Ctrl+H] — Opens the Find and Replace dialog to substitute text throughout the document. _(affects: document content (via replace); most)_ → opens `ui:replace-dialog`
- **Select** — A menu to Select All, select objects, or select text with similar formatting. _(affects: the current selection; niche)_ → opens `ui:select-menu`

## Voice _(boundary — not pressed)_  ·  audience: niche
Dictate text by voice using cloud speech recognition.  
*Affects:* document content (inserted by speech)

- **Dictate** — Converts speech to text via the cloud dictation service. _(affects: document content; niche)_

## Editor _(boundary — not pressed)_  ·  audience: most
Check spelling, grammar and writing refinements via the cloud Editor service.  
*Affects:* the document text (proofing) and the Editor pane

- **Editor** — Opens the Editor pane with spelling, grammar and writing-refinement suggestions. _(affects: the document text (proofing) and Editor pane; most)_

## Adobe Acrobat _(boundary — not pressed)_  ·  audience: niche
Create a PDF from the document via the Adobe Acrobat add-in.  
*Affects:* produces a PDF file (external add-in)

- **Create a PDF** — Exports the document to a PDF using the Adobe Acrobat add-in. _(affects: produces a PDF file; niche)_

## Add-ins _(boundary — not pressed)_  ·  audience: niche
Browse and launch Office Add-ins from the store.  
*Affects:* opens the add-in store (external content)

- **Add-ins** — Opens the Office Add-ins store flyout to browse and insert add-ins. _(affects: opens the add-in store; niche)_

## Contextual surfaces
None within the Home-tab scope: Word's contextual tabs (Table Design/Layout, Picture Format, etc.) appear only after inserting or selecting an object via other tabs, which are out of scope this run. The Home-tab controls are always present, so they expose no context-only surfaces. Transient aids (the on-selection mini-toolbar, post-paste Paste-Options badge) are ephemeral popups, not declared Home-tab surfaces, and are noted here rather than modeled as containers.