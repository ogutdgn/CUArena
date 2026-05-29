# Home tab — Word ↔ LibreOffice

> **Status.** Word build: **Microsoft 365** (owner's real Word). Produced by the per-tab
> pipeline: 3 independent extractors → reconciled canonical → mapped to LO `.uno:` →
> verified against the LibreOffice source tree → confirmed against a real-Word screenshot.
> **LO-side confidence: high. Word-side: confirmed for the visible control set (M365).**
> Five mappings carry explicit LO-source corrections (see [LO-source verification](#lo-source-verification)).

This is **Word-clone decision-research**, not LibreOffice documentation. It diffs every Word
Home-tab control against LO's command surface and classifies the **work** each diff implies.
Bucket vocabulary and verdict meanings are in [README.md](README.md#legend).

---

## Outcome

Of 118 catalogued Word Home-tab controls, **22 wire straight through** to an existing LO
`.uno:` command (Free), and the overwhelming majority of the rest are **our-layer UI** —
galleries, dropdowns, dialogs, and group/overflow hosts that re-present commands LO already
has. Only a thin band needs a **behavior shim** (where LO's *result* differs, not just the
chrome). Critically, the controls LO's **engine genuinely cannot do** (Engine gap) number just
**10 — and they are all rich typography** (the Text Effects family + gradient text fill), which
we cut anyway. The rest of the **Cut** pile is cloud/AI/M365 and niche. Just **three** LO-missing
controls are app-state we might *optionally* build (Office Clipboard 24-item pane, Selection
Pane, live Paste-Options gallery).

| Work bucket | Count | What it is |
|---|---:|---|
| **Free** | 22 | wire the existing LO `.uno:` command, no UI work |
| **Our-layer UI** | 51 | build the Word-faithful gallery/dialog/host; dispatch the LO command |
| **Behavior shim** | 10 | intercept/massage in our dispatch layer; LO's result/semantics differ |
| **Engine gap** | 10 | LO engine genuinely can't (all rich typography); cut or accept reduced fidelity |
| **Cut** | 22 | out of scope by product choice (cloud/AI/M365, niche) |
| **Optional our-layer feature** | 3 | LO lacks it but it's app-state we could build |
| **Total** | **118** | |

**Decisive learning:** on Home the engine almost never blocks — **Engine gap = 10 / 118 (~8%),
entirely rich typography that we cut anyway.** Everything else is Free, our-layer UI we already
own, a small behavior-shim band, or cut-by-choice. → strong support for **LO-via-LOK + scoped
parity**.

> **Recurring our-layer theme.** **Live preview** (Quick Styles, Paste Options, text/character
> effects), the **Navigation-pane Find** experience, and the **Quick Styles gallery** are the
> same shape of work repeated across groups: render-on-hover then revert. They all exercise the
> LOK **apply → render → revert** path, so their *cost* is front-end + LOK round-trip latency,
> not engine capability. Worth profiling once, early.

---

## Inventory

One subsection per Word ribbon group. `LO .uno:` is the mapped LibreOffice command (`—` = none).
`work` is the bucket from the table above. Rows touched by the five LO-source corrections are
marked **✓ verified vs LO source** in the note.

### Quick Access / Undo

> Not part of the Home ribbon proper — these live on Word's Quick Access Toolbar. Included
> because the extraction surfaced them; flagged as QAT, not Home.

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Undo | Undo | split-button | `.uno:Undo` | differs | Our-layer UI | Reverses the last action (Ctrl+Z) and steps back through multiple actions; the dropdown lists recent actions to undo several at once. — **LO:** LO has multi-step undo (Ctrl+Z) on the Standard toolbar; no QAT concept. Engine same. |
| Redo / Repeat | RedoOrRepeat | button | `.uno:Redo` | differs | Our-layer UI | Redoes the action just undone, or repeats the last action when nothing has been undone (Ctrl+Y). — **LO:** LO splits into `.uno:Redo` (Ctrl+Y) + `.uno:Repeat`; one Word button → two LO commands. |

### Clipboard

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Clipboard (group) | GroupClipboard | label | — | UI-only | Our-layer UI | Group container holding Paste, Cut, Copy, Format Painter, and the Office Clipboard launcher. — **LO:** Layout label only; no engine action. |
| Paste | PasteMenu | split-button | `.uno:Paste` | differs | Our-layer UI | Top half pastes the most recent clipboard content (Ctrl+V); the arrow opens the Paste Options gallery plus Paste Special and Set Default Paste. — **LO:** LO paste dropdown (`.uno:EditPasteSpecialMenu`) has no live-preview options gallery. |
| Paste (default action) | Paste | button | `.uno:Paste` | same | Free | Default-paste action from clicking the upper half of the split-button; pastes the most recently copied content. — **LO:** Upper-half default paste = Ctrl+V. |
| Paste Options gallery | PasteGallery | gallery | — | LO-missing | Optional our-layer feature | Live-preview gallery of paste-result choices (Keep Source Formatting, Merge, Picture, Keep Text Only) inside the Paste dropdown. — **LO:** No inline live-preview paste-result strip in LO; closest is the modal Paste Special dialog. |
| Paste Special… | PasteSpecialDialog | button | `.uno:PasteSpecial` | differs | Behavior shim | Opens the Paste Special dialog (Ctrl+Alt+V) to paste as a specific format — unformatted text, HTML, RTF, picture, or linked/embedded OLE. — **LO:** Ctrl+Shift+V; LO's **format list and link options differ** from Word's (no "Paste as Hyperlink"). |
| Set Default Paste… | PasteSetDefault | button | — | LO-missing | Cut | Opens Word Options > Advanced (Cut/copy/paste) to configure default paste behavior. — **LO:** Word routes to Options > Advanced; LO has no per-source paste-default surface. |
| Cut | Cut | button | `.uno:Cut` | same | Free | Removes the selection and places it on the clipboard (Ctrl+X). — **LO:** Direct equivalent, Ctrl+X. |
| Copy | Copy | button | `.uno:Copy` | same | Free | Copies the selection to the clipboard, leaving the original in place (Ctrl+C). — **LO:** Direct equivalent, Ctrl+C. |
| Format Painter | FormatPainter | toggle | `.uno:FormatPaintbrush` | differs | Behavior shim | Copies formatting from the selection to the next selection; single-click applies once, double-click stays active until Esc (Ctrl+Shift+C/Ctrl+Shift+V). — **LO:** "Clone Formatting"; sticky on double-click, but **modifier semantics differ** (no Ctrl+Shift+C/V). |
| Clipboard dialog launcher | ShowClipboard | button | — | LO-missing | Optional our-layer feature | Dialog launcher opening the Office Clipboard task pane, which collects up to 24 cut/copied items for individual or bulk pasting. — **LO:** Office Clipboard 24-item collector pane; LO uses the single OS clipboard. |

### Font

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Font (group) | GroupFont | label | — | UI-only | Our-layer UI | Group container for character-level (typeface) formatting controls. — **LO:** Layout label only. |
| Font | Font | combo | `.uno:CharFontName` | same | Free | Editable font/typeface picker with live preview; type to filter installed fonts or pick from the list. — **LO:** Editable font-name combo with live preview. **No font-name focus shortcut in LO** (Ctrl+Shift+F = RepeatSearch). ✓ verified vs LO source. |
| Font Size | FontSize | combo | `.uno:FontHeight` | same | Free | Editable point-size picker; choose from the list or type a custom size. — **LO:** Editable point-size combo. **No default focus shortcut**; Ctrl+Shift+P is Superscript, not size. ✓ verified vs LO source. |
| Increase Font Size | FontSizeIncreaseWord | button | `.uno:Grow` | same | Free | Grows the selected text to the next larger size in the size list. — **LO:** Next size step. Shortcut differs (LO Ctrl+] vs Word Ctrl+>). |
| Decrease Font Size | FontSizeDecreaseWord | button | `.uno:Shrink` | same | Free | Shrinks the selected text to the next smaller size in the size list. — **LO:** Next size step. Shortcut differs (LO Ctrl+[ vs Word Ctrl+<). |
| Change Case | ChangeCaseGallery | gallery | `.uno:ChangeCaseRotateCase` | differs | Our-layer UI | Aa dropdown to recase selected text: Sentence case, lowercase, UPPERCASE, Capitalize Each Word, tOGGLE cASE (Shift+F3 cycles); Small Caps lives in the Font dialog, not here. — **LO:** RotateCase cycles **4** states (Title→Sentence→UPPER→lower); SwTextShell skips Sentence on single-word selections. Five discrete `.uno:ChangeCaseTo*` exist. ✓ verified vs LO source. |
| Clear All Formatting | ClearFormatting | button | `.uno:ResetAttributes` | differs | Behavior shim | Strips all direct character/paragraph formatting from the selection, reverting it to the underlying/default style. — **LO:** LO (Ctrl+M) strips **direct** formatting only, leaving the paragraph style; Word's **scope is wider**. |
| Phonetic Guide | AsianLayoutPhoneticGuide | button | `.uno:RubyDialog` | differs | Our-layer UI | Asian-layout feature that adds phonetic (ruby/furigana) guides above selected characters. — **LO:** Asian Phonetic Guide; dialog layout differs; Asian-language-conditional. |
| Character Border | CharacterBorder | toggle | — | LO-missing | Cut | Asian-layout feature that toggles a border box around the selected characters. — **LO:** Only via Character dialog > Borders; no one-click toggle command. (Conditional — absent in this build.) |
| Bold | Bold | toggle | `.uno:Bold` | same | Free | Toggles bold weight on the selection or for newly typed text (Ctrl+B). — **LO:** Direct equivalent, Ctrl+B. |
| Italic | Italic | toggle | `.uno:Italic` | same | Free | Toggles italic (slanted) style on the selection (Ctrl+I). — **LO:** Direct equivalent, Ctrl+I. |
| Underline | UnderlineGallery | split-button | `.uno:Underline` | differs | Our-layer UI | Main button toggles a single underline (Ctrl+U); the arrow opens a menu of underline styles, underline color, and More Underlines. — **LO:** Ctrl+U toggles single underline; LO has no inline style/color gallery (lives in Character dialog). |
| More Underlines… | UnderlineMoreUnderlinesDialog | button | `.uno:FontDialog` | differs | Our-layer UI | Child of the Underline menu; opens the Font dialog for additional underline styles beyond the gallery presets. — **LO:** Underline style/color set on the Character dialog Effects area. |
| Underline Color | UnderlineColorPicker | gallery | — | LO-missing | Cut | Child of the Underline menu; color picker for the underline line (theme, standard, More Colors). — **LO:** No toolbar underline-color picker; only inside Character dialog. |
| Underline Color > More Colors… | UnderlineColorMoreColorsDialog | button | — | LO-missing | Cut | Child of the Underline color picker; opens the Colors dialog for a custom underline color. — **LO:** No standalone underline-color picker, so no child. |
| Strikethrough | Strikethrough | toggle | `.uno:Strikeout` | same | Free | Toggles a single horizontal line through the middle of the selected text. — **LO:** Single strikethrough toggle (LO command is `Strikeout`). |
| Subscript | Subscript | toggle | `.uno:SubScript` | same | Free | Shrinks the selection and lowers it below the baseline (Ctrl+=). — **LO:** LO shortcut **Ctrl+Shift+B** vs Word Ctrl+=. ✓ verified vs LO source. |
| Superscript | Superscript | toggle | `.uno:SuperScript` | same | Free | Shrinks the selection and raises it above the baseline (Ctrl+Shift+=). — **LO:** LO shortcut **Ctrl+Shift+P** vs Word Ctrl+Shift+=. ✓ verified vs LO source. |
| Text Effects and Typography | TextEffectsGallery | gallery | — | LO-missing | Engine gap | Gallery applying WordArt-style text effects (outline, shadow, reflection, glow) and OpenType typography (number styles, ligatures, stylistic sets) to body text, with live preview. — **LO:** Outline/shadow/reflection/glow + OpenType; no inline-text equivalent (Fontwork is a drawing object). |
| Text Outline | TextOutlineColorPickerAlternate | gallery | — | LO-missing | Engine gap | Text Effects submenu: outline color picker plus weight and dashes galleries for the text outline. — **LO:** Only legacy `.uno:OutlineFont` hollow-glyph toggle; no color/weight/dash. |
| Text Outline > Weight | TextOutlineWeightGallery | gallery | — | LO-missing | Engine gap | Sets the outline line weight for the text-effect outline. — **LO:** No inline text-outline weight control. |
| Text Outline > Dashes | TextOutlineDashesGallery | gallery | — | LO-missing | Engine gap | Sets the outline dash pattern for the text-effect outline. — **LO:** No inline text-outline dash control. |
| Shadow | TextEffectShadowGallery | gallery | `.uno:Shadowed` | differs | Behavior shim | Text Effects submenu applying a shadow preset to text; includes Shadow Options. — **LO:** LO toggles one fixed character shadow; **no presets/offset/blur/color** like Word. |
| Reflection | TextReflectionGallery | gallery | — | LO-missing | Engine gap | Text Effects submenu applying a reflection preset to text; includes Reflection Options. — **LO:** No reflection text effect for inline text. |
| Glow | TextEffectGlowGallery | gallery | — | LO-missing | Engine gap | Text Effects submenu applying a glow preset with a color picker; includes Glow Options. — **LO:** No glow for inline body text. |
| Number Styles | NumberStyleGalleryWord | gallery | — | LO-missing | Engine gap | OpenType typography submenu to pick number style (proportional/tabular, lining/old-style). — **LO:** No OpenType number-style picker. |
| Ligatures | LigatureGalleryWord | gallery | — | LO-missing | Engine gap | OpenType typography submenu to choose ligature settings (Standard, Contextual, Historical, Discretionary). — **LO:** No ligature gallery (only raw font-feature syntax). |
| Stylistic Sets | StylisticSetsMenuWord | gallery | — | LO-missing | Engine gap | OpenType typography submenu to choose a font's stylistic set. — **LO:** No stylistic-set picker UI. |
| Text Highlight Color | TextHighlightColorPicker | split-button | `.uno:CharBackColor` | differs | Our-layer UI | Applies the current/last-used highlight color behind selected text (or turns the pointer into a highlighter); the arrow opens the palette plus No Color and Stop Highlighting. — **LO:** "Character Highlighting Color"; palette/free-form-mode differ. **`.uno:BackColor` is a separate deprecated slot sharing the label — not a live alias.** ✓ verified vs LO source. |
| Stop Highlighting | HighlightingStop | button | — | LO-missing | Cut | Child of the highlight color picker; turns off the free-form highlighter mode. — **LO:** No discrete command; press Esc / re-click in LO. |
| Font Color | FontColorPicker | split-button | `.uno:FontColor` | differs | Our-layer UI | Applies the current/last-used font color; the arrow opens the color picker (Automatic, Theme, Standard, More Colors, Gradient submenu). — **LO:** Applies last-used color; palette structure differs; no text-gradient submenu. |
| Font Color > More Colors… | FontColorMoreColorsDialog | button | — | differs | Our-layer UI | Child of the Font Color picker; opens the Colors dialog for a custom font color. — **LO:** "Custom Color…" in the `.uno:FontColor` dropdown opens the LO color dialog. |
| Font Color > Gradient | TextFillGradientGallery | gallery | — | LO-missing | Engine gap | Child of the Font Color picker; applies a gradient fill to text color, with a More Gradients dialog. — **LO:** No gradient fill for inline character text. |
| Character Shading | CharacterShading | toggle | — | LO-missing | Cut | Asian-layout feature that toggles shading behind selected characters on/off. — **LO:** No dedicated Asian-layout character-shading toggle. (Conditional — absent in this build.) |
| Enclose Characters | AsianLayoutCharactersEnclose | button | — | LO-missing | Cut | Asian-layout feature that wraps selected characters in an enclosing mark (circle, square, etc.). — **LO:** No enclose-characters feature. (Conditional — absent in this build.) |
| Font dialog launcher | FontDialog | button | `.uno:FontDialog` | differs | Our-layer UI | Dialog launcher opening the full Font dialog (Font + Advanced tabs) — character spacing/scaling, Small Caps, default-font settings (Ctrl+D). — **LO:** Opens the Character dialog; tab organization differs; Ctrl+D is Double Underline in LO. |

### Paragraph

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Paragraph (group) | GroupParagraph | label | — | UI-only | Our-layer UI | Group container for list, indent, alignment, spacing, shading, and border controls. — **LO:** Layout label only. |
| Bullets | BulletsGalleryWord | split-button | `.uno:DefaultBullet` | differs | Our-layer UI | Toggles a bulleted list using the last-used bullet; the arrow opens Recently Used Bullets, the Bullet Library, Change List Level, and Define New Bullet. — **LO:** Toggles unordered list; no bullet library/recently-used gallery (uses Bullets & Numbering dialog). |
| Numbering | NumberingGalleryWord | split-button | `.uno:DefaultNumbering` | differs | Our-layer UI | Toggles a numbered list; the arrow opens Recently Used Number Formats, the Numbering Library, Change List Level, Define New Number Format, and Set Numbering Value. — **LO:** Toggles ordered list; no numbering-library gallery. |
| Multilevel List | MultilevelListGallery | gallery | `.uno:OutlineBullet` | differs | Our-layer UI | Applies a multilevel (outline) list format; the gallery includes Current List, List Library, Change List Level, Define New Multilevel List, and Define New List Style. — **LO:** Configured via Bullets & Numbering / Chapter Numbering dialogs; no inline list-library gallery. |
| Change List Level | ListLevelGallery | gallery | `.uno:OutlineRight` | differs | Our-layer UI | Submenu shared across Bullets, Numbering, and Multilevel List to promote/demote the current item to a different level. — **LO:** Promote/demote via `.uno:OutlineRight`/`.uno:OutlineLeft`; no visual level picker. |
| Define New Bullet… | BulletDefineNew | button | `.uno:BulletsAndNumberingDialog` | differs | Our-layer UI | Child of the Bullets dropdown; opens the Define New Bullet dialog (symbol/picture bullet, font, alignment). — **LO:** Custom bullets in the Bullets & Numbering Customize/Image tabs. |
| Define New Number Format… | DefineNewNumberFormat | button | `.uno:BulletsAndNumberingDialog` | differs | Our-layer UI | Child of the Numbering dropdown; opens the Define New Number Format dialog. — **LO:** Number formats in the Customize tab. |
| Set Numbering Value… | ListSetNumberingValue | button | `.uno:NumberingStart` | differs | Our-layer UI | Child of the Numbering dropdown; opens the Set Numbering Value dialog to start, continue, or restart numbering. — **LO:** Split across `.uno:NumberingStart` / `.uno:ContinueNumbering` + dialog; compose into one host. |
| Define New List Style… | ListDefineNewStyle | button | — | LO-missing | Cut (revisit) | Child of the Multilevel List dropdown; opens the Define New List Style dialog. — **LO:** LO has list styles via the Styles window, but no one-click "define new list style" command. |
| Define New Multilevel List… | ListDefineNew | button | `.uno:OutlineBullet` | differs | Our-layer UI | Child of the Multilevel List dropdown; opens the Define New Multilevel List dialog. — **LO:** Per-level setup in the Bullets & Numbering Customize tab. |
| Decrease Indent | IndentDecreaseWord | button | `.uno:DecrementIndent` | same | Free | Moves the selected paragraph(s) one level/tab stop toward the left margin (Ctrl+Shift+M). — **LO:** One-step indent decrease. |
| Increase Indent | IndentIncreaseWord | button | `.uno:IncrementIndent` | same | Free | Moves the selected paragraph(s) one level/tab stop away from the left margin (Ctrl+M). — **LO:** One-step indent increase (Word Ctrl+M = indent; LO Ctrl+M = clear formatting). |
| Left-to-Right Text Direction | TextDirectionLeftToRight | toggle | `.uno:ParaLeftToRight` | same | Free | Sets paragraph reading/text direction to left-to-right (bidi feature). — **LO:** CTL-conditional, mirrors Word. (Conditional — absent in this build.) |
| Right-to-Left Text Direction | TextDirectionRightToLeft | toggle | `.uno:ParaRightToLeft` | same | Free | Sets paragraph reading/text direction to right-to-left (bidi feature). — **LO:** CTL-conditional, mirrors Word. (Conditional — absent in this build.) |
| Asian Layout | AsianLayoutMenu | menu | — | differs | Our-layer UI | Menu of Asian-layout commands: Horizontal in Vertical, Combine Characters, Two Lines in One, Fit Text, and Character Scaling. — **LO:** LO has the pieces scattered (Ruby, Position dialog) but no single bundled menu. (Conditional — absent in this build.) |
| Sort… | SortDialogClassic | button | `.uno:SortDialog` | differs | Our-layer UI | Opens the Sort Text dialog to order selected paragraphs or table rows alphabetically, numerically, or by date, ascending or descending. — **LO:** Sort dialog with up to 3 keys; lacks Word's by-paragraph/date niceties. |
| Show/Hide ¶ (Formatting Marks) | ParagraphMarks | toggle | `.uno:ControlCodes` | same | Free | Toggles on-screen display of nonprinting formatting marks (pilcrows, spaces, tabs, line breaks) without affecting print (Ctrl+Shift+8). — **LO:** Ctrl+F10 in LO vs Word Ctrl+Shift+8; behavior matches. |
| Show East Asian Editing Marks | EastAsianEditingMarks | toggle | — | LO-missing | Cut | Toggles display of East Asian editing marks (grid/control characters). — **LO:** No separate toggle; governed by `.uno:ControlCodes` + formatting-aids options. (Conditional — absent.) |
| Align Left | AlignLeft | toggle | `.uno:LeftPara` | same | Free | Left-aligns the selected paragraph(s) flush to the left margin with a ragged right edge (Ctrl+L). — **LO:** Ctrl+L. |
| Center | AlignCenter | toggle | `.uno:CenterPara` | same | Free | Center-aligns the selected paragraph(s) horizontally between the margins (Ctrl+E). — **LO:** Ctrl+E. |
| Align Right | AlignRight | toggle | `.uno:RightPara` | same | Free | Right-aligns the selected paragraph(s) flush to the right margin with a ragged left edge (Ctrl+R). — **LO:** Ctrl+R. |
| Justify | AlignJustify | toggle | `.uno:JustifyPara` | same | Free | Justifies the selected paragraph(s) flush to both margins by adjusting word spacing (Ctrl+J). — **LO:** Ctrl+J; no density-variant menu. |
| Distributed | ParagraphDistributed | toggle | — | LO-missing | Cut | Distributes text evenly across the full line width (East Asian justification). — **LO:** No paragraph even-distribution alignment. (Conditional — absent in this build.) |
| Align Text (menu) | AlignTextMenu | menu | — | UI-only | Our-layer UI | Consolidated alignment menu used in compact/narrow layouts, re-hosting Left/Center/Right/Justify/Distributed. — **LO:** Compact-layout overflow host re-presenting the four alignment buttons. |
| Line and Paragraph Spacing | LineSpacingGallery | gallery | `.uno:LineSpacing` | differs | Our-layer UI | Dropdown to set line spacing (1.0–3.0) and add/remove space before/after the paragraph; Line Spacing Options opens the Paragraph dialog. — **LO:** Preset line spacings only; paragraph before/after split into `.uno:ParaspaceIncrease/Decrease`. |
| Shading | ShadingColorPicker | split-button | `.uno:BackgroundColor` | differs | Our-layer UI | Applies background shading/fill color to the selected paragraph/text/cell; the arrow opens the shading color palette. — **LO:** Paragraph background palette; LO sharpens char-highlight vs para-background; palette differs. |
| Shading > More Colors… | ShadingColorsMoreColorsDialog | button | — | differs | Our-layer UI | Child of the Shading dropdown; opens the Colors dialog for a custom shading color. — **LO:** "Custom Color…" in the Background Color dropdown. |
| Borders | BordersSelectionGallery | split-button | `.uno:SetBorderStyle` | differs | Our-layer UI | Applies/removes the last-used border; the arrow opens the borders gallery (edge placements) plus Horizontal Line, Draw Table, View Gridlines, and Borders and Shading. — **LO:** `.uno:SetBorderStyle` = the toolbar button/dropdown placement preset; dropdown lacks Word's bundled extras. ✓ verified vs LO source. |
| Horizontal Line | HorizontalLineInsert | button | — | differs | Our-layer UI | Child of the Borders dropdown; inserts a horizontal line below the cursor. — **LO:** LO applies the "Horizontal Line" paragraph style; no dedicated command — wire a button to StyleApply. |
| Draw Table | TableDrawTable | toggle | — | LO-missing | Cut | Child of the Borders dropdown; enters draw-table mode to draw table cells freehand. — **LO:** No freehand draw-table mode; tables via `.uno:InsertTable` only. |
| View Gridlines | TableShowGridlines | toggle | `.uno:TableBoundaries` | differs | Our-layer UI | Child of the Borders dropdown; toggles display of (nonprinting) table gridlines. — **LO:** Table boundaries toggle; lives under the Table menu, not the Borders dropdown. |
| Borders and Shading… | BordersShadingDialogWord | button | `.uno:BorderDialog` | differs | Our-layer UI | Child of the Borders dropdown; opens the full Borders and Shading dialog. — **LO:** `.uno:BorderDialog` = the Borders dialog; Word's unified Borders+Page+Shading is split in LO. ✓ verified vs LO source. |
| Paragraph dialog launcher | ParagraphDialog | button | `.uno:ParagraphDialog` | differs | Our-layer UI | Dialog launcher opening the Paragraph dialog (Indents and Spacing / Line and Page Breaks tabs). — **LO:** Paragraph dialog; tab layout/naming differs (Word "Line and Page Breaks" → LO "Text Flow"). |

### Styles

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Styles (group) | GroupStyles | label | — | UI-only | Our-layer UI | Group container for the Quick Styles gallery and the Styles task-pane launcher. — **LO:** Layout label only. |
| Styles gallery (Quick Styles) | QuickStylesGallery | gallery | `.uno:StyleApply` | differs | Behavior shim | In-ribbon scrollable gallery of named paragraph/character styles with live preview; the More arrow expands the full set and exposes Create a Style, Clear Formatting, and Apply Styles. — **LO:** **Style-set differs** (LO "Default Paragraph Style" vs Word "Normal"; "No Spacing" is Word-only); no in-ribbon hover preview / "More" expander. |
| Create a Style | QuickStylesSaveSelectionAsNew | button | `.uno:StyleNewByExample` | differs | Our-layer UI | Child of the Styles gallery; opens Create New Style from Formatting to save the current formatting as a new named style. — **LO:** "New Style from Selection"; LO prompts for name only, no up-front modify dialog. |
| Clear Formatting (Styles gallery member) | ClearFormatting | button | `.uno:ResetAttributes` | differs | Behavior shim | Child of the Styles gallery; removes direct formatting — the same command as Clear All Formatting in the Font group. — **LO:** Same command as Font-group Clear All Formatting; strips direct formatting only, **narrower scope**. |
| Apply Styles | ApplyStylesPane | toggle | `.uno:StyleApply` | differs | Our-layer UI | Child of the Styles gallery; opens the Apply Styles floating pane to apply a style by typed name (Ctrl+Shift+S). — **LO:** LO uses the Set-Paragraph-Style combo (Ctrl+Shift+S), not a floating pane. |
| Styles pane launcher | StylesPane | button | `.uno:DesignerDialog` | differs | Our-layer UI | Dialog launcher opening/toggling the Styles task pane with all styles, Manage Styles, and the Style Inspector (Alt+Ctrl+Shift+S). — **LO:** F11 Styles window; organized by style-family tabs; no Style Inspector. |

### Editing

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Editing (group) | GroupEditing | label | — | UI-only | Our-layer UI | Group container for Find, Replace, and Select commands. — **LO:** Layout label only. |
| Find | FindDialogWord | split-button | `vnd.sun.star.findbar:FocusToFindbar` | differs | Behavior shim | Opens the Navigation pane search box to locate text/headings/pages (Ctrl+F); the arrow exposes Advanced Find, Go To, and an Insights search. — **LO:** **There is NO `.uno:Search` in LO.** Word's primary Find = the inline FindBar (Ctrl+F); LO has no Navigation-pane find-as-you-type UX. ✓ verified vs LO source. |
| Find (Navigation Pane) | NavigationPaneFind | button | `vnd.sun.star.findbar:FocusToFindbar` | differs | Behavior shim | Child of the Find dropdown; opens the Navigation pane with focus in the search box (Ctrl+F). — **LO:** Inline FindBar (Ctrl+F) is the closest; F5 Navigator browses but does not text-search like Word's pane. ✓ verified vs LO source. |
| Advanced Find… | FindDialog | button | `.uno:SearchDialog` | differs | Our-layer UI | Child of the Find dropdown; opens the Find and Replace dialog on the Find tab with full search options. — **LO:** Find & Replace "Other options" (regex/similarity/attributes); regex dialect differs. ✓ verified vs LO source. |
| Go To… | GoTo | button | `.uno:GotoPage` | differs | Our-layer UI | Child of the Find dropdown; opens Find and Replace on the Go To tab to jump to a page/section/line/bookmark (Ctrl+G). — **LO:** No unified Go To dialog; page jump via `.uno:GotoPage`, rest via Navigator — compose. |
| Search (Insights) | InsightsInDocSearch | button | — | LO-missing | Cut | Child of the Find dropdown; smart-lookup-style search for the selection within/about the document. — **LO:** No Smart-Lookup/Insights web research. |
| Replace | ReplaceDialog | button | `.uno:SearchDialog` | differs | Our-layer UI | Opens Find and Replace on the Replace tab to substitute text/formatting one instance at a time or all at once (Ctrl+H). — **LO:** Ctrl+H opens the unified Find & Replace dialog (Find + Replace fields). ✓ verified vs LO source. |
| Select | SelectMenu | menu | `.uno:EditSelectMenu` | differs | Our-layer UI | Menu with Select All (Ctrl+A), Select Objects, Select All Text With Similar Formatting, and the Selection Pane. — **LO:** Has Select All + selection-mode toggles; lacks Select Objects / Select-Similar / Selection Pane. |
| Select All | SelectAll | button | `.uno:SelectAll` | same | Free | Child of the Select menu; selects the entire document (Ctrl+A). — **LO:** Ctrl+A. |
| Select Objects | ObjectsSelect | toggle | `.uno:SelectObject` | differs | Our-layer UI | Child of the Select menu; toggles object-selection mode for clicking/dragging floating objects. — **LO:** Object-selection cursor mode; behaves differently, surfaced on drawing toolbars. |
| Select All Text With Similar Formatting | SelectTextWithSimilarFormatting | button | — | LO-missing | Cut | Child of the Select menu; selects all text matching the formatting of the current selection. — **LO:** No one-click select-similar (Find & Replace by attributes is the workaround). |
| Selection Pane | SelectionPane | toggle | — | LO-missing | Optional our-layer feature | Child of the Select menu; opens the Selection task pane to list, show/hide, and reorder objects. — **LO:** No object-visibility task pane; Navigator lists but has no per-object show/hide. |
| Find (overflow popup) | FindPopup | menu | — | UI-only | Our-layer UI | Compact/narrow-layout popup that re-hosts the entire Editing group (Find/Replace/Select) when it collapses. — **LO:** Compact-layout overflow host re-presenting the Editing group. |

### Voice

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Voice (group) | GroupVoiceTools | label | — | UI-only | Our-layer UI | Group container for Dictate and Transcribe (Microsoft 365 addition). — **LO:** Layout label only. |
| Dictate | DictationMenu | split-button | — | LO-missing | Cut | Starts/stops speech-to-text dictation at the cursor; the menu sets language, microphone, punctuation, and exposes Transcribe. Requires M365 sign-in and internet. — **LO:** Cloud-backed M365 speech-to-text; no engine equivalent. |
| Dictate (toggle) | Dictate | toggle | — | LO-missing | Cut | Child of the Dictate split-button; toggles the microphone for voice-to-text dictation. — **LO:** No dictation in LO. |
| Dictate (in menu) | DictateInMenu | button | — | LO-missing | Cut | Launches dictation from within the Dictate menu. — **LO:** No dictation in LO. |
| Transcribe | TranscribeWord | button | — | LO-missing | Cut | Child of the Dictate menu; opens the Transcribe pane to record or upload audio and convert it to a text transcript. — **LO:** No audio-to-transcript feature. |

### Editor / AI Assistance (Copilot)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Editor (group) | GroupEditor | label | — | UI-only | Our-layer UI | Group container for the Editor writing-assistance command (Microsoft 365). — **LO:** Layout label only. |
| Editor | WritingAssistanceCheckDocument | button | `.uno:SpellingDialog` | differs | Behavior shim | Opens the Editor (M365 writing assistant) pane showing spelling, grammar, and refinement suggestions with a writing score (F7). — **LO:** Nearest analog is Spelling & Grammar (F7); no AI writing score/refinement. AI portion out of scope. |
| AI Assistance / Copilot (group) | GroupAIAssistance | label | — | UI-only | Our-layer UI | Group container hosting Copilot and the Editor writing-assistance check, shown on Copilot-enabled M365 tenants. — **LO:** Layout label only; no LO analog for its contents. |
| Copilot | Copilot | button | — | LO-missing | Cut | Opens the Copilot pane/chat for AI drafting, summarizing, and rewriting; requires an M365 Copilot license. — **LO:** No built-in AI assistant. (Conditional — absent in this build.) |

### Sensitivity

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Sensitivity (group) | GroupClassifyLabelProtect | label | — | UI-only | Our-layer UI | Group container for the Sensitivity (MIP) label control; shown only when sensitivity labels are configured by tenant policy. — **LO:** Layout label only. (Conditional — absent in this build.) |
| Sensitivity | ClassifyLabelProtect | menu | — | differs | Behavior shim | Opens the Sensitivity menu to apply/change a Microsoft Information Protection (MIP) label on the document. — **LO:** LO has TSCP/BAILS classification, **not Microsoft Information Protection** — backend/protection not interoperable. (Conditional — absent in this build.) |

### Research / Insights (legacy/optional)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Research (group) | GroupResearch | label | — | UI-only | Our-layer UI | Legacy/optional group container hosting the Insights (Smart Lookup) command on Home in some builds. — **LO:** Layout label only. |
| Smart Lookup / Insights | Insights | button | — | LO-missing | Cut | Opens the Smart Lookup (Insights/Researcher) pane with web definitions and references for the selection. — **LO:** No Bing-backed Insights/Researcher pane. (Conditional — absent in this build.) |

### Add-ins (flyout, optional)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Add-ins (group) | GroupOfficeExtensionsAddinFlyout | label | — | UI-only | Our-layer UI | Group container that surfaces installed Office Add-in commands as a flyout on Home in some configurations. — **LO:** Layout label only. |
| Add-ins | OfficeExtensionsShowAddinFlyout | button | — | LO-missing | Cut | Opens a flyout listing installed Office Add-ins / Store add-in commands for insertion. — **LO:** LO has an extension system but no Office Web Add-in (Office.js) flyout. |

### Reuse Files (optional, M365)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Reuse Files | _(none)_ | button | — | LO-missing | Cut | Opens a task pane to search for and insert content from existing documents; M365 feature whose availability varies by channel. — **LO:** No content-search-and-insert pane; closest is Insert > Text from File. (Conditional — absent.) |

### Activate (conditional, unlicensed only)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Activate (group) | GroupActivation | label | — | UI-only | Our-layer UI | Conditional group container shown only when the Office product is unlicensed/unactivated. — **LO:** Layout label only. (Conditional — absent in this build.) |
| Activate | ActivateOffice | button | — | LO-missing | Cut | Starts the Office product-activation flow; appears on Home only when Office is not activated. — **LO:** LO is free/open-source — no product activation; conceptually N/A. (Conditional — absent.) |

---

## LO-source verification

These five mappings were checked against the LibreOffice source tree and **override** the
mapped rows where they conflicted:

- **Find** — there is **no `.uno:Search`** in LibreOffice. Ctrl+F focuses the inline FindBar
  via the protocol URL `vnd.sun.star.findbar:FocusToFindbar`; Ctrl+H = `.uno:SearchDialog`
  (Find & Replace). Word's primary Find maps to the findbar protocol, not `.uno:Search`.
  Evidence: `Accelerators.xcu:130-135,143-148`; `svx/source/dialog/srchdlg.cxx`.
- **Change Case** — `.uno:ChangeCaseRotateCase` cycles **4** states (Title → Sentence →
  UPPERCASE → lowercase), not 3. Evidence: `unotools/source/i18n/caserotate.cxx:16-41` +
  tdf#116315. Nuance: SwTextShell skips Sentence case on single-word selections
  (`sw/source/uibase/shells/textsh.cxx:900-926`), so it *looks* like 3 on one word. The five
  discrete `.uno:ChangeCaseTo*` commands exist.
- **Shortcuts** — Ctrl+Shift+P = `.uno:SuperScript` (`Accelerators.xcu:6876-6881`);
  Subscript = Ctrl+Shift+B. There is **no font-name/size focus shortcut** (Ctrl+Shift+F =
  RepeatSearch in Writer). The earlier "Ctrl+Shift+P focuses font size" / "Ctrl+Shift+F
  focuses font name" claims are struck.
- **BackColor vs CharBackColor** — `.uno:BackColor` (deprecated,
  SID_ATTR_CHAR_COLOR_BACKGROUND) and `.uno:CharBackColor` (current,
  SID_ATTR_CHAR_BACK_COLOR) are **distinct slots that share the same label** — not a live
  alias. Evidence: `sw/sdi/swriter.sdi:382-383`; `svx/sdi/svx.sdi:1572-1573`.
- **Borders** — `.uno:SetBorderStyle` = the toolbar button/dropdown placement preset;
  `.uno:BorderDialog` = the Borders dialog. Both real and distinct. Evidence:
  `GenericCommands.xcu:3861`; `WriterCommands.xcu:1542`.

---

## Conditional controls absent in this build

Confirmed by the owner's real-Word (M365) screenshot — these controls were **not present**,
which confirms they are conditional (and correctly flagged in the inventory):

- Asian Layout, LTR / RTL text direction, Phonetic Guide, Character Border, Character Shading,
  Enclose Characters, Distributed, East-Asian editing marks
- Copilot / AI-Assistance group, Sensitivity, Smart Lookup / Insights, Reuse Files, Activate

They surface only under specific conditions (Asian/CTL language support enabled, an
M365/Copilot license, an unlicensed install, etc.). Their absence in a standard M365 build is
expected and does not change the mapping.

**Visible groups confirmed present** in the screenshot: Clipboard, Font, Paragraph, Styles,
Editing, Voice (Dictate), Editor, Add-ins.

---

## Out of scope

- **Add-in injections.** A third-party **Adobe Acrobat / "Create a PDF"** group appears in the
  owner's Word, injected by an add-in. It is **not canonical Word** and is out of scope (not in
  the inventory).
- **Cloud / AI / M365.** Dictate, Transcribe, Copilot, Editor (the AI score/refinement portion),
  Smart Lookup / Insights, Reuse Files, MIP Sensitivity labeling, Office Web Add-ins. No engine
  equivalent and not part of a local clone's scope.
- **Engine gap — rich typography (the only true engine blockers, 10 controls).** Text Effects
  (outline / shadow presets / reflection / glow), OpenType number styles / ligatures / stylistic
  sets, and text-fill gradient have **no inline-text equivalent in LO's engine**. Cut now, or
  accept reduced fidelity later. This is the band that would matter if we ever reconsidered the engine.
- **Niche (cut by scope).** Character border / shading / enclose, Draw Table, East-Asian editing
  marks, Distributed alignment, product Activation — mostly conditional / rarely used.

---

## QA flags & resolutions

From `result.qa.rowsToVerify`. The Word screenshot and the LO-source pass resolved most; the
remainder are LO-side details that don't change any bucket.

| QA flag | Status | Resolution |
|---|---|---|
| Change Case cycle covers all 5 cases? | **Resolved (LO source)** | RotateCase cycles **4** states; SwTextShell skips Sentence on single-word selections. Five discrete `ToXxx` commands exist. Note corrected. |
| Font / Font Size focus shortcuts (Ctrl+Shift+F / Ctrl+Shift+P)? | **Resolved (LO source)** | **No** font-name/size focus shortcut in LO. Ctrl+Shift+P = Superscript; Ctrl+Shift+F = RepeatSearch. Claims struck. |
| Subscript / Superscript Ctrl+Shift+P double-assignment? | **Resolved (LO source)** | Ctrl+Shift+P = Superscript; Subscript = Ctrl+Shift+B. The contradiction was the bogus font-size shortcut, now removed. |
| `.uno:BackColor` an alias of `.uno:CharBackColor`? | **Resolved (LO source)** | Not an alias — two **distinct slots** sharing one label. Note corrected. |
| Primary Find → `.uno:SearchDialog` vs `.uno:Search`? | **Resolved (LO source)** | `.uno:Search` does not exist. Primary Find → `vnd.sun.star.findbar:FocusToFindbar` (FindBar); Find & Replace → `.uno:SearchDialog`. Both Find rows remapped. |
| Borders split-button — `.uno:SetBorderStyle` vs `.uno:BorderDialog`? | **Resolved (LO source)** | Both real and distinct: `SetBorderStyle` = dropdown preset; `BorderDialog` = the dialog. Borders row → `SetBorderStyle`, Borders and Shading → `BorderDialog`. |
| Asian Layout submenu membership / double-listing? | **Resolved (Word screenshot)** | Asian Layout + its children (Phonetic Guide, Character Border, Character Shading, Enclose Characters) are **conditional and absent** in this M365 build; no live duplicate to reconcile. |
| Paragraph Shading `.uno:BackgroundColor` vs char-highlight `.uno:CharBackColor`? | **Open (LO-side, low risk)** | The two are mapped to distinct commands; a dispatch check in the shipped build would confirm `BackgroundColor` is the paragraph-shading slot and not routed through `ParaBackColor`. Does not change buckets. |
| Multilevel List `.uno:OutlineBullet` collapse (3 Word controls → 1 `.uno`)? | **Open (LO-side, low risk)** | Plausible; verify `OutlineBullet` (not `ChapterNumberingDialog`) is the dispatched id for heading-level lists. Does not change buckets. |
| Editor idMso `WritingAssistanceCheckDocument` vs target build? | **Open (Word-side, low risk)** | idMso is M365-version-sensitive; the LO "nearest analog" (F7 spelling) holds regardless. The AI portion is out of scope. |
