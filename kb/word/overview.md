# Microsoft Word — Knowledge Base overview

**Version (build):** 16.0.20131 · **Platform:** desktop · **Scope of this KB:** the **Home tab** treated as the whole application.

**What it is.** A desktop word processor for creating, formatting and editing text documents.

**Used for.** Writing and formatting documents — letters, reports, essays, resumes — with rich text styling, paragraph layout, lists, styles and review tools.

**Who uses it.** Students, office workers, writers, and virtually anyone producing formatted text documents.

## At a glance
- **9 features**, **45 sub-features**, **38 UI containers** (20 explored to depth, 18 deliberate stubs), **21 keyboard shortcuts**.
- **Priority layers:** P0=3 · P1=11 · P2=10 · P3=10 · P4=20

## Skeleton (measured trigger surface)
The main window hosts the ribbon tab strip (Home is in scope; other tabs are named but unexplored). The **Home tab** face was mapped by pressing every control and classifying the measured outcome (opens a dialog/dropdown/menu/pane, or triggers a document/format action).

## Feature tree (priority-ranked)
### Clipboard
Move and duplicate content and formatting via the clipboard. _(affects: document content and the Office clipboard; audience: everyone)_

- **[P1]★ Copy** · `Ctrl+C` — Copies the selection to the clipboard without changing the document. _(affects: the Office clipboard)_
- **[P1]★ Paste** · `Ctrl+V` — Inserts the clipboard's content at the cursor; the dropdown offers paste-special options (keep formatting, merge, text only, picture). _(affects: document content)_ · opens `ui:paste-dropdown`
- **[P1]★ Cut** · `Ctrl+X` — Removes the selection from the document and places it on the clipboard. _(affects: document content + clipboard)_
- **[P3] Format Painter** · `Alt+Ctrl+C, Alt+Ctrl+V` — Copies formatting from the selection to reapply to the next thing you click. _(affects: the formatting of the next selection)_
- **[P4] Office Clipboard** — Opens the Office Clipboard pane showing the last 24 copied items for reuse. _(affects: opens the Clipboard task pane)_ · opens `ui:show-clipboard-pane`

### Font
Format the characters of the selected text — typeface, size, weight, color, effects. _(affects: the selection's character formatting; audience: everyone)_

- **[P0]★ Bold** · `Ctrl+B` — Toggles bold (heavier) weight on the selected text. _(affects: the selection's character format (bold))_
- **[P0]★ Font Size** — Sets the point size of the selected text; the box opens a size list. _(affects: the selection's font size)_ · opens `ui:font-size-dropdown`
- **[P0]★ Font** — Chooses the typeface for the selected text; the box opens a searchable font list. _(affects: the selection's font (typeface))_ · opens `ui:font-dropdown`
- **[P1]★ Italic** · `Ctrl+I` — Toggles italic (slanted) style on the selected text. _(affects: the selection's character format (italic))_
- **[P1]★ Underline** · `Ctrl+U` — Toggles an underline on the selected text; the dropdown picks the underline style and color. _(affects: the selection's character format (underline))_ · opens `ui:underline-menu`
- **[P1]★ Font Color** — Sets the color of the selected text; the dropdown opens a color picker (theme/standard/more). _(affects: the selection's font color)_ · opens `ui:font-color-dropdown`
- **[P2]★ Font dialog launcher** · `Ctrl+D` — Opens the Font dialog — the consolidated surface for all character formatting plus advanced options (spacing, ligatures, defaults). _(affects: opens the Font dialog)_ · opens `ui:font-dialog`
- **[P3] Text Highlight Color** — Applies a highlighter color behind the text; the dropdown picks the color. _(affects: the selection's highlight color)_ · opens `ui:text-highlight-color-dropdown`
- **[P3] Strikethrough** — Draws a line through the middle of the selected text. _(affects: the selection's character format (strikethrough))_
- **[P3] Shrink Font** · `Ctrl+Shift+<` — Decreases the font size of the selection to the previous step. _(affects: the selection's font size)_
- **[P3] Grow Font** · `Ctrl+Shift+>` — Increases the font size of the selection to the next step. _(affects: the selection's font size)_
- **[P4] Clear All Formatting** — Removes all character and paragraph formatting from the selection, leaving plain text. _(affects: the selection's formatting (reset to default))_
- **[P4] Change Case** — Changes the capitalization of the selected text (Sentence case, lowercase, UPPERCASE, Capitalize Each Word, tOGGLE cASE). _(affects: the case of the selected text)_ · opens `ui:change-case-menu`
- **[P4] Subscript** · `Ctrl+Shift+_` — Places the selected text slightly below the baseline in a smaller size. _(affects: the selection's character format (subscript))_
- **[P4] Superscript** · `Ctrl+Shift++` — Places the selected text slightly above the baseline in a smaller size. _(affects: the selection's character format (superscript))_
- **[P4] Text Effects and Typography** — Applies visual text effects (outline, shadow, reflection, glow) and OpenType typography. _(affects: the selection's character appearance)_ · opens `ui:text-effects-dropdown`

### Paragraph
Format whole paragraphs — lists, indentation, alignment, spacing, shading, borders. _(affects: the selected paragraphs' formatting and layout; audience: everyone)_

- **[P1]★ Center** · `Ctrl+E` — Centers the paragraph text between the margins. _(affects: the paragraph's alignment)_
- **[P1]★ Align Left** · `Ctrl+L` — Aligns the paragraph text to the left margin. _(affects: the paragraph's alignment)_
- **[P2]★ Align Right** · `Ctrl+R` — Aligns the paragraph text to the right margin. _(affects: the paragraph's alignment)_
- **[P2]★ Paragraph dialog launcher** — Opens the Paragraph dialog — indentation, spacing, alignment and line/page-break options. _(affects: opens the Paragraph dialog)_ · opens `ui:paragraph-dialog`
- **[P2]★ Bullets** — Starts or toggles a bulleted list on the selected paragraphs; the dropdown is the bullet library. _(affects: the selected paragraphs' list format)_ · opens `ui:bullets-dropdown`
- **[P2]★ Numbering** — Starts or toggles a numbered list on the selected paragraphs; the dropdown is the numbering library. _(affects: the selected paragraphs' list format)_ · opens `ui:numbering-dropdown`
- **[P2]★ Line and Paragraph Spacing** — Sets the spacing between lines and before/after paragraphs. _(affects: the paragraph's line and spacing)_ · opens `ui:line-spacing-menu`
- **[P3] Justify** · `Ctrl+J` — Spaces the paragraph text to align to both left and right margins. _(affects: the paragraph's alignment)_
- **[P3] Decrease Indent** — Moves the paragraph's left indent one level toward the margin. _(affects: the paragraph's left indent)_
- **[P3] Increase Indent** — Moves the paragraph's left indent one level away from the margin. _(affects: the paragraph's left indent)_
- **[P3] Shading** — Fills the background of the selection/paragraph with a color; the dropdown picks the color. _(affects: the paragraph/selection background shading)_ · opens `ui:shading-color-dropdown`
- **[P4] Borders** — Applies borders to the selection/paragraph; the dropdown lists border options and the Borders and Shading dialog. _(affects: the paragraph/selection borders)_ · opens `ui:borders-selection-menu`
- **[P4] Show/Hide ¶** · `Ctrl+*` — Toggles the on-screen display of paragraph marks and other hidden formatting symbols. _(affects: the view (formatting marks visibility) — not the document)_
- **[P4] Multilevel List** — Applies a multi-level (nested) list scheme to the selected paragraphs. _(affects: the selected paragraphs' multi-level list format)_ · opens `ui:multilevel-list-menu`
- **[P4] Sort** — Opens the Sort dialog to alphabetically/numerically sort the selected paragraphs, list or table. _(affects: the order of the selected paragraphs)_ · opens `ui:sort-dialog`

### Styles
Apply named, reusable style sets that bundle character and paragraph formatting. _(affects: the paragraph/character style applied to the selection; audience: most)_

- **[P2]★ Quick Styles gallery** — Applies a named style (Normal, No Spacing, Heading 1/2, Title, Subtitle, Quote…) to the selection from the in-ribbon gallery. _(affects: the paragraph/character style applied)_ · opens `ui:styles-gallery`
- **[P4] Styles pane launcher** · `Alt+Ctrl+Shift+S` — Opens the Styles pane — the full style list with apply/new/inspect/manage controls. _(affects: opens the Styles task pane)_ · opens `ui:styles-pane`

### Editing
Find, replace and select text within the document. _(affects: navigation and selection within the document; audience: most)_

- **[P1]★ Find** · `Ctrl+F` — Opens the Navigation pane to search the document for text; the dropdown offers Find, Advanced Find and Go To. _(affects: opens the Navigation pane / search)_ · opens `ui:navigation-pane-find-pane`
- **[P3] Replace** · `Ctrl+H` — Opens the Find and Replace dialog to substitute text throughout the document. _(affects: document content (via replace))_ · opens `ui:replace-dialog`
- **[P4] Select** — A menu to Select All, select objects, or select text with similar formatting. _(affects: the current selection)_ · opens `ui:select-menu`

### Voice _(boundary — not pressed; documented from knowledge)_
Dictate text by voice using cloud speech recognition. _(affects: document content (inserted by speech); audience: niche)_

- **[P4] Dictate** — Converts speech to text via the cloud dictation service. _(affects: document content)_

### Editor _(boundary — not pressed; documented from knowledge)_
Check spelling, grammar and writing refinements via the cloud Editor service. _(affects: the document text (proofing) and the Editor pane; audience: most)_

- **[P4] Editor** — Opens the Editor pane with spelling, grammar and writing-refinement suggestions. _(affects: the document text (proofing) and Editor pane)_

### Adobe Acrobat _(boundary — not pressed; documented from knowledge)_
Create a PDF from the document via the Adobe Acrobat add-in. _(affects: produces a PDF file (external add-in); audience: niche)_

- **[P4] Create a PDF** — Exports the document to a PDF using the Adobe Acrobat add-in. _(affects: produces a PDF file)_

### Add-ins _(boundary — not pressed; documented from knowledge)_
Browse and launch Office Add-ins from the store. _(affects: opens the add-in store (external content); audience: niche)_

- **[P4] Add-ins** — Opens the Office Add-ins store flyout to browse and insert add-ins. _(affects: opens the add-in store)_

## Keyboard shortcuts (registry)
- `Alt+Ctrl+C` — copy formatting from the selection → `subfeature:format-painter` _( document has focus )_
- `Alt+Ctrl+Shift+S` — Opens the Styles pane — the full style list with apply/new/inspect/manage controls. → `ui:styles-pane` _( document has focus )_
- `Alt+Ctrl+V` — apply the copied formatting to the selection → `subfeature:format-painter` _( document has focus )_
- `Ctrl+*` — Toggles the on-screen display of paragraph marks and other hidden formatting symbols. → `subfeature:paragraph-marks` _( document has focus (toggles a view setting) )_
- `Ctrl+B` — Toggles bold (heavier) weight on the selected text. → `subfeature:bold` _( editing text — applies to the selection or at the cursor )_
- `Ctrl+C` — Copies the selection to the clipboard without changing the document. → `subfeature:copy` _( document has focus )_
- `Ctrl+D` — Opens the Font dialog — the consolidated surface for all character formatting plus advanced options (spacing, ligatures, defaults). → `ui:font-dialog` _( editing text — applies to the selection or at the cursor )_
- `Ctrl+E` — Centers the paragraph text between the margins. → `subfeature:align-center` _( editing text — applies to the current paragraph(s) )_
- `Ctrl+F` — Opens the Navigation pane to search the document for text; the dropdown offers Find, Advanced Find and Go To. → `ui:navigation-pane-find-pane` _( document has focus )_
- `Ctrl+H` — Opens the Find and Replace dialog to substitute text throughout the document. → `ui:replace-dialog` _( document has focus )_
- `Ctrl+I` — Toggles italic (slanted) style on the selected text. → `subfeature:italic` _( editing text — applies to the selection or at the cursor )_
- `Ctrl+J` — Spaces the paragraph text to align to both left and right margins. → `subfeature:align-justify` _( editing text — applies to the current paragraph(s) )_
- `Ctrl+L` — Aligns the paragraph text to the left margin. → `subfeature:align-left` _( editing text — applies to the current paragraph(s) )_
- `Ctrl+R` — Aligns the paragraph text to the right margin. → `subfeature:align-right` _( editing text — applies to the current paragraph(s) )_
- `Ctrl+Shift++` — Places the selected text slightly above the baseline in a smaller size. → `subfeature:superscript` _( editing text — applies to the selection or at the cursor )_
- `Ctrl+Shift+<` — Decreases the font size of the selection to the previous step. → `subfeature:font-size-decrease` _( editing text — applies to the selection or at the cursor )_
- `Ctrl+Shift+>` — Increases the font size of the selection to the next step. → `subfeature:font-size-increase` _( editing text — applies to the selection or at the cursor )_
- `Ctrl+Shift+_` — Places the selected text slightly below the baseline in a smaller size. → `subfeature:subscript` _( editing text — applies to the selection or at the cursor )_
- `Ctrl+U` — Toggles an underline on the selected text; the dropdown picks the underline style and color. → `subfeature:underline-gallery` _( editing text — applies to the selection or at the cursor )_
- `Ctrl+V` — Inserts the clipboard's content at the cursor; the dropdown offers paste-special options (keep formatting, merge, text only, picture). → `subfeature:paste` _( document has focus )_
- `Ctrl+X` — Removes the selection from the document and places it on the clipboard. → `subfeature:cut` _( document has focus )_

## How priority was decided
Every node's layer is a recorded weighted sum of three signals — connectivity (degree over the affects/uses graph), real-world usage (web-researched, evidence-cited, anchored on Microsoft CEIP telemetry), and audience breadth — cut at recorded boundaries. See `priority/JUSTIFICATION.md` and `priority/ranking.json`.

_Generated from the node files; the append-only `journal.jsonl` reconstructs the full run._