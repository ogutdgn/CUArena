# Layout tab — Word ↔ LibreOffice

> **Status.** Word build: Microsoft 365 (target). **Word-side: web-sourced + LO-verified —
> screenshot-pending** (not yet confirmed against a live build). LO-side: high. Produced by the
> per-tab pipeline: 3 independent extractors → reconciled canonical → mapped to LO `.uno:` →
> verified against the LibreOffice source tree. The Word/idMso side was set-diffed against the
> official `wordcontrols.xlsx` (M365 Current Channel + 2013/2016/2019) and is essentially complete
> for the classic Layout tab; the LO command facts were checked against the vendored LO tree.
> **No owner screenshot exists for this tab yet**, so conditional/version-sensitive controls below
> are *expected-conditional, unverified against a live build*. The LO-source pass produced **no
> material corrections** — 41 mappings were checked, all CONFIRMED except three minor
> label-precision CORRECTED items (see [LO-source verification](#lo-source-verification)).

This is **Word-clone decision-research**, not LibreOffice documentation. It diffs every Word
Layout-tab control against LO's command surface and classifies the **work** each diff implies.
Bucket vocabulary and verdict meanings are in [README.md](README.md#legend).

---

## Outcome

Of 78 catalogued Word Layout-tab controls, **18 wire straight through** to an existing LO
`.uno:` command (Free), and the largest band — 30 — is **our-layer UI**: galleries, split-button
menus, dialogs, and group/overflow hosts that re-present commands LO already has (Margins, Size,
Orientation, Columns, the z-order/Align/Group/Rotate flat commands, the Page Style and Line
Numbering dialogs). A substantial **behavior-shim** band (25) covers diffs where our dispatch
layer must massage semantics — chiefly Word's **section** model (no LO equivalent), the
**absolute-value indent/spacing spinners** (LO has only stepwise nudge buttons), the **anchor /
layer** model behind Wrap and front-of/behind-text, and the **align-to-page/margin target
toggles**. The decisive number for the engine decision is **Engine gap = 2** — the Layout tab is
almost entirely buildable on LO's existing surface. **Cut = 0**: there are no cloud/AI/online
product-choice controls on this tab. Three controls are app-state we could *optionally* build.

| Work bucket | Count | What it is |
|---|---:|---|
| **Free** | 18 | wire the existing LO `.uno:` command, no UI work |
| **Our-layer UI** | 30 | build the Word-faithful gallery/dialog/host; dispatch the LO command |
| **Behavior shim** | 25 | intercept/massage in our dispatch layer; LO's result/semantics differ |
| **Engine gap** | 2 | LO engine genuinely can't; cut or accept reduced fidelity |
| **Cut** | 0 | out of scope by product choice (none on this tab) |
| **Optional our-layer feature** | 3 | LO lacks it but it's app-state we could build |
| **Total** | **78** | |

**Decisive learning:** on Layout the engine gap is tiny — **Engine gap = 2 / 78 (~3%)** — far
smaller than Home or Insert. The two genuine document-capability gaps are both **section-model
artifacts**: the **Text Wrapping break** (an insertable break character that pushes text below a
floating object — LO's text engine has no such break) and **Restart Each Section line numbering**
(LO has no Word "section" boundary to restart at). Everything else LO covers: it has **full page
setup** (Page Style dialog: margins/orientation/size/columns), **paragraph indent/spacing**, **line
numbering**, **hyphenation**, and **object arrange** (position/wrap/z-order/align/group/rotate for
drawing objects). The recurring work is therefore *re-presentation* (our-layer UI) and
*semantic translation* (behavior shim), not engine surgery. → strongly supports **LO-via-LOK +
scoped parity**, with Word's full "section" model as the one place to accept reduced fidelity.

> **Recurring our-layer theme.** Word's Layout tab is dominated by **preset galleries** (Margins,
> Size, Orientation, Columns, Position, Rotate) and **menus** (Breaks, Line Numbers, Hyphenation,
> Align, Group) that wrap a small set of LO commands or a single LO dialog. Where Word offers a
> quick-pick gallery/menu, LO usually offers one dialog (Page Style, Line Numbering, Hyphenate) or
> a flat set of discrete commands (z-order, align, distribute). The gallery/menu wrapper is the
> repeated shape of our-layer work; the underlying capability is present. The repeated **behavior
> shim** is Word's **section scope** (LO is page-style scoped) and Word's **absolute-value
> spinners** (LO nudges by a fixed step).

---

## Inventory

One subsection per Word ribbon group. `LO .uno:` is the mapped LibreOffice command (`—` = none).
`work` is the bucket from the table above. Rows touched by the LO-source corrections are marked
**✓ verified vs LO source** in the note.

### Page Setup (GroupPageLayoutSetup)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Page Setup group | GroupPageLayoutSetup | group | — | UI-only | Our-layer UI | Ribbon group container holding the page-level setup controls (text direction, margins, orientation, size, columns, breaks, line numbers, hyphenation) plus the Page Setup dialog launcher. — **LO:** Group container, not a command. LO's notebookbar has a "Page Setup" group on its Layout tab but holds a different command set (PageMargin, Orientation, AttributePageSize, PageColumnType, PageDialog) and has no idMso namespace. No dispatchable `.uno`. |
| Text Direction | TextDirectionGalleryWord | gallery | `.uno:TextdirectionTopToBottom` | differs | Behavior shim | Dropdown gallery to set text direction in a text box / shape (horizontal, rotate 90/270, stacked); contains the Text Direction Options child. — **LO:** No text-direction gallery for shapes/text boxes. Closest are the toggles `.uno:TextdirectionLeftToRight` / `.uno:TextdirectionTopToBottom` (LTR vs vertical TTB writing direction), not a multi-option rotate/stacked gallery; no 90/270 rotation or "stacked" text-direction command (object rotation is separate, see Rotate). Partial analog only — dispatch must massage. ✓ verified vs LO source. |
| Text Direction Options | TextDirectionOptionsDialog | button | — | LO-missing | Behavior shim | Child opening the Text Direction dialog for text-box/shape orientation. — **LO:** No separate text-direction options dialog; text direction is toggled directly via the `Textdirection*` commands. The underlying capability exists but there is no 1:1 dialog control. ✓ verified vs LO source. |
| Margins | PageMarginsGallery | gallery | `.uno:PageMargin` | differs | Our-layer UI | Gallery of margin presets (Normal/Narrow/Moderate/Wide/Mirrored/Last Custom) applied to the current section, plus Custom Margins. — **LO:** `.uno:PageMargin` ("Page Margins") is used in LO's Page Setup group but offers only a small preset set, the model is a page **STYLE** not a Word "section", mirrored margins come from the style's page-layout = "Mirrored" (not a preset), and there is no "Last Custom Setting" memory. Gallery is our UI over the LO command. ✓ verified vs LO source. |
| Custom Margins | MarginsCustomMargins | button | `.uno:PageDialog` | differs | Our-layer UI | Opens the Page Setup dialog on the Margins tab. — **LO:** Routes through `.uno:PageDialog` ("~Page Style…") which opens the Page Style dialog; margins live on the "Page" tab (not a dedicated "Margins" tab) and the dialog is page-style-scoped. Gutter is not first-class; only "page layout: mirrored" + inner/outer margins approximate it. Different dialog presentation. ✓ verified vs LO source. |
| Orientation | PageOrientationGallery | gallery | `.uno:Orientation` | same | Free | Two-item dropdown (Portrait/Landscape) for the current section. — **LO:** `.uno:Orientation` ("Orientation") provides the same Portrait/Landscape switch. Difference: it flips the current page **STYLE** rather than a Word section, but the user-facing action matches. ✓ verified vs LO source. |
| Size | PageSizeGallery | gallery | `.uno:AttributePageSize` | differs | Our-layer UI | Gallery of paper sizes (Letter/Legal/A4/A3…) plus More Paper Sizes. — **LO:** `.uno:AttributePageSize` ("Page Size") picks standard paper sizes but is page-style scoped and the preset/paper-source list is LO's. Custom width/height and paper tray go through the Page Style dialog, not a Word "Paper" tab. (`.uno:PageSettingDialog`, "Page Settings - Paper format", also exists, more Calc-style.) Gallery is our UI. ✓ verified vs LO source. |
| More Paper Sizes | PageSizeMorePaperSizesDialog | button | `.uno:PageDialog` | differs | Our-layer UI | Opens the Page Setup dialog (Paper tab). — **LO:** Custom paper size is set on the "Page" tab of the Page Style dialog (`.uno:PageDialog`); no separate "Paper" tab — width/height/orientation/format all sit together. Dialog presentation differs. ✓ verified vs LO source. |
| Columns | TableColumnsGallery | gallery | `.uno:PageColumnType` | differs | Our-layer UI | Gallery of column presets (One/Two/Three/Left/Right) flowing the section into newspaper columns, plus More Columns. — **LO:** `.uno:PageColumnType` ("Page Columns") is the column-count picker for the page style; LO column commands operate on a page style or an inserted text section, not a Word "section". The Word idMso oddity (`TableColumns*`) has no bearing on LO. Gallery is our UI. ✓ verified vs LO source. |
| More Columns | ColumnsDialog | button | `.uno:FormatColumns` | differs | Our-layer UI | Opens the Columns dialog (count, width, spacing, line-between, apply-to). — **LO:** `.uno:FormatColumns` ("Co~lumns…") opens LO's Columns dialog (count/width/spacing/separator). Scope/apply-to differs: LO applies to the page style, the whole document, or a `.uno:InsertSection` text region — no Word section/apply-from-this-point model. (`.uno:PageColumnDialog`, "Page Columns", is the page-style-scoped variant.) ✓ verified vs LO source. |
| Breaks | BreaksGallery | gallery | `.uno:BreaksMenu` | differs | Behavior shim | Gallery of Page Breaks (Page/Column/Text Wrapping) and Section Breaks (Next/Continuous/Even/Odd Page). — **LO:** `.uno:BreaksMenu` ("More Breaks") is the nearest menu but contents differ fundamentally. LO has Page break (`.uno:InsertPagebreak`), Column break (`.uno:InsertColumnBreak`), and a generic Manual Break dialog (`.uno:InsertBreak`); it has **no "section break" concept** — independent formatting is achieved by a page break WITH a page-style change, or via text sections (`.uno:InsertSection`). Dispatch must map section breaks onto page-style switches. ✓ verified vs LO source. |
| Page (break) | _(none)_ | gallery item | `.uno:InsertPagebreak` | same | Free | Inserts a manual page break. — **LO:** `.uno:InsertPagebreak` ("~Page Break", "Insert Page Break", Ctrl+Enter) is a direct match — pushes following text to the next page, same Ctrl+Enter as Word. ✓ verified vs LO source. |
| Column (break) | _(none)_ | gallery item | `.uno:InsertColumnBreak` | same | Free | Pushes columnar text after the break to the next column. — **LO:** `.uno:InsertColumnBreak` ("Insert Column Break") is a direct match inside a multi-column layout. ✓ verified vs LO source. |
| Text Wrapping (break) | _(none)_ | gallery item | — | LO-missing | Engine gap | Text-wrapping break separating text around objects (web layout) — moves text next to an image/table below that object. — **LO:** No equivalent in LO Writer. LO has no "text wrapping break" character; line wrapping around objects is governed entirely by the object's wrap settings, not by an insertable break. Genuine document-capability gap. |
| Next Page (section break) | _(none)_ | gallery item | `.uno:InsertBreak` | differs | Behavior shim | Starts a new section on the next page with independent formatting. — **LO:** No section breaks. Nearest is `.uno:InsertBreak` ("Manual ~Break…") which inserts a page break WITH a "change page style" option (new style = new margins/orientation/columns/headers) — approximates a next-page section break, but is a page-style switch, not a true Word section. Dispatch composes the break + style change. ✓ verified vs LO source. |
| Continuous (section break) | _(none)_ | gallery item | `.uno:InsertSection` | differs | Behavior shim | Starts a new section on the same page without a page break. — **LO:** No continuous section break. Closest is a text section (`.uno:InsertSection`, "Columns" / "Insert a section with columns") carrying its own column layout inline; a different object model (a named text Section) that cannot change margins/orientation mid-page. Dispatch maps to a text section. ✓ verified vs LO source. |
| Even Page (section break) | _(none)_ | gallery item | — | LO-missing | Behavior shim | Starts the next section on the next even page. — **LO:** No even-page section break command, but page styles have left/right/mirrored layout and you can force a left/right page via the page-break-with-style dialog (`.uno:InsertBreak`); approximable in our dispatch layer, just no single command. |
| Odd Page (section break) | _(none)_ | gallery item | — | LO-missing | Behavior shim | Starts the next section on the next odd page. — **LO:** No odd-page section break command; approximated by selecting a right/odd page style on a page break (`.uno:InsertBreak`). Dispatch composes it; no dedicated control. |
| Line Numbers | LineNumbersMenu | menu | `.uno:LineNumberingDialog` | differs | Our-layer UI | Dropdown menu — None / Continuous / Restart Each Page / Restart Each Section / Suppress / Options. — **LO:** `.uno:LineNumberingDialog` ("~Line Numbering…") is a single dialog, NOT a quick-pick menu; the Word presets are checkboxes/fields inside it (enable, "restart every new page", count interval, distance). Our menu drives the one dialog. ✓ verified vs LO source. |
| None (Line Numbers) | LineNumbersOff | toggleButton | `.uno:LineNumberingDialog` | differs | Our-layer UI | Turns line numbering off. — **LO:** The "Show numbering" checkbox (unchecked) inside the Line Numbering dialog, not a discrete toggle command. Our menu surfaces it. ✓ verified vs LO source. |
| Continuous (Line Numbers) | LineNumbersContinuous | toggleButton | `.uno:LineNumberingDialog` | differs | Our-layer UI | Applies continuous line numbering across the document. — **LO:** The default when numbering is enabled and "restart every new page" is off, set inside the Line Numbering dialog. Our menu surfaces it. ✓ verified vs LO source. |
| Restart Each Page | LineNumbersResetPage | toggleButton | `.uno:LineNumberingDialog` | differs | Our-layer UI | Restarts line numbering on each page. — **LO:** The "Restart every new page" checkbox inside the Line Numbering dialog. Our menu surfaces it. ✓ verified vs LO source. |
| Restart Each Section | LineNumbersResetSection | toggleButton | — | LO-missing | Engine gap | Restarts line numbering at each section. — **LO:** No equivalent — LO has no sections, so there is no per-section line-number-restart option anywhere in the Line Numbering dialog. Genuine document-capability gap (no section boundary to restart at). |
| Suppress for Current Paragraph | LineNumbersSuppress | toggleButton | — | differs | Behavior shim | Suppresses line numbering for the current paragraph. — **LO:** No ribbon command; "Include this paragraph in line numbering" is a checkbox on the paragraph properties (Format > paragraph dialog), not a dispatchable `.uno`. Functionally reachable — our layer toggles the paragraph property. |
| Line Numbering Options | LineNumbersOptionsDialog | button | `.uno:LineNumberingDialog` | same | Free | Opens line numbering options. — **LO:** `.uno:LineNumberingDialog` IS the options dialog in LO (start value, count-by interval, distance from text, separator) — in LO it is the whole feature; in Word it is the "Options" leaf of the menu. Best match. ✓ verified vs LO source. |
| Hyphenation | HyphenationMenu | menu | `.uno:Hyphenate` | differs | Our-layer UI | Menu — None / Automatic / Manual / Options. — **LO:** `.uno:Hyphenate` ("~Hyphenation…") is a single command/dialog, not a None/Automatic/Manual menu; in LO Manual hyphenation IS what it runs (interactive pass). Our layer presents the menu over the LO command (with the None/Automatic legs shimmed below). ✓ verified vs LO source. |
| None (Hyphenation) | HyphenationNone | toggleButton | — | differs | Behavior shim | Turns hyphenation off. — **LO:** No discrete command; disabling automatic hyphenation is done by unchecking "Automatically" on the paragraph/page-style Text Flow tab. Our layer toggles the style property. |
| Automatic (Hyphenation) | HyphenationAutomatic | toggleButton | — | differs | Behavior shim | Enables automatic hyphenation. — **LO:** No quick toggle; automatic hyphenation is a paragraph-style/page-style Text Flow property applied per style. `.uno:Hyphenate` is the MANUAL pass, not auto. Our layer toggles the style property. |
| Manual (Hyphenation) | HyphenationManual | button | `.uno:Hyphenate` | same | Free | Runs a manual hyphenation pass prompting per candidate word. — **LO:** `.uno:Hyphenate` ("~Hyphenation…", tooltip "Insert Soft Hyphen…") runs LO's interactive manual pass, prompting per candidate word — a close match. (This same command is LO's whole Hyphenation entry, so it doubles as Word's menu.) ✓ verified vs LO source. |
| Hyphenation Options | HyphenationOptions | button | — | differs | Behavior shim | Opens the Hyphenation options dialog (hyphenate CAPS, zone, consecutive limit). — **LO:** No dedicated hyphenation-options dialog on the ribbon; these settings live on the Text Flow tab of the paragraph/page-style dialog plus Tools > Options > Language Settings. Reachable via styles — our layer routes there. |
| Page Setup (dialog box launcher) | PageSetupDialog | dialogBoxLauncher | `.uno:PageDialog` | differs | Our-layer UI | Opens the full Page Setup dialog (Margins/Paper/Layout tabs) with section start, vertical alignment, apply-to scope. — **LO:** `.uno:PageDialog` ("~Page Style…") opens LO's Page Style dialog — the nearest full page-setup dialog (margins, page size, orientation, columns, header/footer, footnotes, borders). It is a page-STYLE editor with tabs organized differently and lacks Word's "section start", "apply to: this point forward", and on-dialog vertical page-alignment. Different dialog presentation. ✓ verified vs LO source. |

### Paragraph (GroupParagraphLayout)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Paragraph group | GroupParagraphLayout | group | — | UI-only | Our-layer UI | Ribbon group container holding the Indent (Left/Right) and Spacing (Before/After) spinners plus the Paragraph dialog launcher. — **LO:** Ribbon-grouping construct, no command/idMso. LO's notebookbar has a "Paragraph" group on Layout but exposes increase/decrease indent and spacing buttons rather than direct-entry spinners. (Official group label is "Paragraph Indent & Spacing" — see QA flags.) |
| Indent | IndentLabel | labelControl | — | UI-only | Our-layer UI | Static text label for the Indent spinner pair. — **LO:** Pure label, not a command in either app. No LO label control with an id. |
| Indent Left | IndentLeft | spinner | `.uno:IncrementIndent` | differs | Behavior shim | Spin/edit box setting the exact left indent value of the selected paragraph(s). — **LO:** No direct-entry left-indent spinner on the ribbon. LO offers only stepwise buttons `.uno:IncrementIndent` ("Increase" / "Increase Indent") and `.uno:DecrementIndent` ("Decrease") that bump by a fixed step — no typed exact measurement (that requires the Paragraph dialog). Behavior differs: nudge vs absolute value; our layer must intercept and set an exact indent. ✓ verified vs LO source. |
| Indent Right | IndentRight | spinner | — | differs | Behavior shim | Spin/edit box setting the exact right indent of the selected paragraph(s). — **LO:** No right-indent control on the ribbon at all; IncrementIndent/DecrementIndent affect the left/before-text indent only. Right (after-text) indent is set exclusively via the Paragraph dialog's Indents & Spacing tab. Our layer must set it via the paragraph property. |
| Spacing | SpacingLabel | labelControl | — | UI-only | Our-layer UI | Static text label for the Spacing spinner pair. — **LO:** Pure label, no command in either app. |
| Spacing Before | SpacingBefore | spinner | `.uno:ParaspaceIncrease` | differs | Behavior shim | Spin/edit box setting space above the paragraph in points. — **LO:** Only stepwise paragraph-spacing buttons `.uno:ParaspaceIncrease` / `.uno:ParaspaceDecrease` (adjust above-paragraph spacing by a fixed step), not a typed-value spinner and not split into before/after. Exact "space before" requires the Paragraph dialog. Our layer sets the exact value. ✓ verified vs LO source. |
| Spacing After | SpacingAfter | spinner | — | differs | Behavior shim | Spin/edit box setting space below the paragraph in points. — **LO:** No dedicated "space after" control on the ribbon; the Paraspace Increase/Decrease buttons act on above-paragraph spacing only. Exact below-paragraph spacing is set only in the Paragraph dialog. Our layer sets the exact value. |
| Paragraph (dialog box launcher) | ParagraphDialog | dialogBoxLauncher | `.uno:ParagraphDialog` | same | Free | Opens the Paragraph dialog (Indents & Spacing / Line and Page Breaks). — **LO:** `.uno:ParagraphDialog` ("P~aragraph…") opens LO's Paragraph dialog — essentially the same feature: indents (incl. hanging/first-line), spacing above/below, line spacing, alignment, and a Text Flow tab for pagination. Tab names differ slightly ("Text Flow" vs Word's "Line and Page Breaks") but the dialog is the clear equivalent. ✓ verified vs LO source. |

### Arrange (GroupArrange)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Arrange group | GroupArrange | group | — | UI-only | Our-layer UI | Ribbon group container holding object-arrangement controls (Position, Wrap Text, Bring Forward, Send Backward, Selection Pane, Align, Group, Rotate) plus the collapsed Arrange overflow menu. — **LO:** Ribbon-grouping construct. LO's notebookbar has an "Arrange" group on Layout (`.uno:ArrangeMenu` / `ArrangeFrameMenu` exist as menu containers) but no idMso. Container only. |
| Position | PicturePositionGallery | gallery | `.uno:TransformDialog` | differs | Behavior shim | Gallery of 9 "with text wrapping" anchor presets + In Line With Text + More Layout Options. — **LO:** No 9-cell position-preset gallery. Object position is set numerically via `.uno:TransformDialog` ("Position and Si~ze…") or by anchor type (`.uno:AnchorMenu`: to page/paragraph/character/as-character) plus alignment commands. No one-click "top-left / middle-center" preset that sets position and wrapping together. Workflow differs; our layer must translate a preset into position + anchor + wrap. ✓ verified vs LO source. (Official idMso label is "Object Position" — see QA flags.) |
| More Layout Options (Position) | LayoutOptionsDialogPosition | button | `.uno:TransformDialog` | differs | Our-layer UI | Opens the Layout dialog on the Position tab. — **LO:** `.uno:TransformDialog` ("Position and Si~ze…") is LO's nearest exact-position dialog (Position/Size/Rotation/Slant tabs), not Word's three-tab Layout dialog; relative-to-page/margin/paragraph anchoring is split between this dialog and the anchor commands. Dialog presentation differs. ✓ verified vs LO source. |
| Wrap Text | TextWrapGallery | gallery | `.uno:WrapMenu` | differs | Behavior shim | Dropdown of wrap styles (In Line/Square/Tight/Through/Top&Bottom/Behind/In Front) + Edit Wrap Points + Move/Fix toggles. — **LO:** `.uno:WrapMenu` ("~Wrap") is the analog but the vocabulary differs: None (`.uno:WrapOff`), Parallel (`.uno:WrapOn` ≈ Square), Optimal (`.uno:WrapIdeal`), Through (`.uno:WrapThrough`), Before/After (`.uno:WrapLeft`/`WrapRight` — one-sided, no Word equivalent), In Background (`.uno:WrapThroughTransparent` ≈ Behind Text). No distinct "Tight" vs "Square", no "Top and Bottom", no "In Front of Text" (LO uses layer commands). Contour editing = `.uno:WrapContour`, not "Edit Wrap Points". Dispatch must map the wrap vocabulary. ✓ verified vs LO source. |
| Move with Text | MoveObjectWithText | checkBox | `.uno:SetAnchorToPara` | differs | Behavior shim | Anchor the object so it moves with surrounding text. — **LO:** No checkbox of this name. Expressed by ANCHOR type: `.uno:SetAnchorToPara` ("Anchor To Paragraph") / `.uno:SetAnchorAtChar` / `.uno:SetAnchorToChar` make the object move with its text, vs `.uno:SetAnchorToPage` which fixes it. Different model (explicit anchor type, not a move/fix checkbox pair); dispatch maps the checkbox to an anchor type. ✓ verified vs LO source. |
| Fix Position on Page | FixObjectPositionOnPage | checkBox | `.uno:SetAnchorToPage` | differs | Behavior shim | Fix the object on the page so it doesn't move with text. — **LO:** Anchoring to the page via `.uno:SetAnchorToPage` ("Anchor To Page"), optionally with `.uno:ProtectPos` ("Protect Position") to lock it. Not a single "fix position" checkbox; it's the anchor-type + position-protect combination. Dispatch composes it. ✓ verified vs LO source. |
| More Layout Options (Wrapping) | LayoutOptionsDialogWrapping | button | `.uno:TextWrap` | differs | Our-layer UI | Opens the Layout dialog on the Text Wrapping tab. — **LO:** `.uno:TextWrap` ("Text Wrap…") opens LO's Wrap settings (spacing-to-text, contour, first-paragraph, overlap) on the Wrap tab of the object's properties dialog, not a separate three-tab Layout dialog. Same goal, different dialog structure. ✓ verified vs LO source. |
| Set as Default Layout | SetDefaultObjectLayout | button | — | LO-missing | Optional our-layer feature | Set current wrap/layout as default for new objects. — **LO:** No "set current object layout as default for future inserts" command; default wrap/anchor is governed by frame styles / object defaults. App-state we could store and apply on insert. |
| Bring Forward | ObjectBringForwardMenu | splitButton | `.uno:ObjectForwardOne` | differs | Our-layer UI | Split button: primary = forward one level; dropdown = Bring to Front / Bring in Front of Text. — **LO:** "Forward one level" is `.uno:ObjectForwardOne` ("Forward One"), NOT a split button — LO exposes the z-order ops as flat commands. "Bring in Front of Text" maps to a separate layer command. Our layer assembles the split button. ✓ verified vs LO source. (Split-button container idMso suspect — see QA flags.) |
| Bring Forward (primary action) | ObjectBringForward | button | `.uno:ObjectForwardOne` | same | Free | Move the object forward one z-order level. — **LO:** `.uno:ObjectForwardOne` ("Forward One") is a direct behavioral match. ✓ verified vs LO source. |
| Bring to Front | ObjectBringToFront | button | `.uno:BringToFront` | same | Free | Move the object above all other objects. — **LO:** `.uno:BringToFront` ("~Bring to Front", Ctrl+Shift+Plus) is a direct match. ✓ verified vs LO source. |
| Bring in Front of Text | ObjectBringInFrontOfText | button | `.uno:SetObjectToForeground` | differs | Behavior shim | Place the object in front of the document text. — **LO:** `.uno:SetObjectToForeground` ("To Foreground") moves the object into the foreground (text) layer. Differs in model: LO has two discrete layers (foreground vs through-background) toggled by To Foreground/To Background, whereas Word treats "in front of text" as a wrap/z-order style. Closest functional match but conceptually a layer switch. ✓ verified vs LO source. |
| Send Backward | ObjectSendBackwardMenu | splitButton | `.uno:ObjectBackOne` | differs | Our-layer UI | Split button: primary = back one level; dropdown = Send to Back / Send Behind Text. — **LO:** "Back one level" is `.uno:ObjectBackOne` ("Back One"), a flat command, not a split button with a menu; "Send Behind Text" maps to the layer command To Background. Our layer assembles the split button. ✓ verified vs LO source. (Split-button container idMso suspect — see QA flags.) |
| Send Backward (primary action) | ObjectSendBackward | button | `.uno:ObjectBackOne` | same | Free | Move the object back one z-order level. — **LO:** `.uno:ObjectBackOne` ("Back One") is a direct behavioral match. ✓ verified vs LO source. |
| Send to Back | ObjectSendToBack | button | `.uno:SendToBack` | same | Free | Move the object below all other objects. — **LO:** `.uno:SendToBack` ("~Send to Back", Ctrl+Shift+Minus) is a direct match. ✓ verified vs LO source. |
| Send Behind Text | ObjectSendBehindText | button | `.uno:SetObjectToBackground` | differs | Behavior shim | Place the object behind the document text. — **LO:** `.uno:SetObjectToBackground` ("To Background") pushes the object into the background layer so text flows over it. Same layer-switch difference as "in front of text" (LO's two-layer model, not a z-order step). Closest functional match. ✓ verified vs LO source. |
| Selection Pane | SelectionPane | toggleButton | `.uno:Navigator` | differs | Behavior shim | Toggles the Selection task pane listing all objects, with show/hide eye icons, rename, and z-order reorder. — **LO:** No Selection pane. Nearest is the Navigator (`.uno:Navigator`, "Na~vigator") listing drawing objects/frames/images with jump-to and rename, but NOT Word's per-object visibility (eye) toggle or drag-to-reorder. Partial analog only; our layer must add show/hide + reorder. ✓ verified vs LO source. |
| Align | ObjectAlignMenu | menu | `.uno:ObjectAlign` | differs | Our-layer UI | Menu of align/distribute + target toggles (to page/margin/selected) + alignment guides/gridlines + grid settings. — **LO:** `.uno:ObjectAlign` ("Alig~n Objects") is the LO align menu but leaner: left/center/right + top/middle/bottom + distribution, but NO target toggles (alignment is relative to anchor or selection bounds), no "Use Alignment Guides", no in-menu "View Gridlines". Our layer presents the richer menu. ✓ verified vs LO source. |
| Align Left | ObjectsAlignLeftSmart | button | `.uno:ObjectAlignLeft` | same | Free | Align left edges of selected objects. — **LO:** `.uno:ObjectAlignLeft` ("~Left") aligns left edges. Equivalent action (LO aligns to anchor/selection bounds rather than via a target toggle). ✓ verified vs LO source. |
| Align Center | ObjectsAlignCenterHorizontalSmart | button | `.uno:AlignHorizontalCenter` | same | Free | Center selected objects horizontally. — **LO:** `.uno:AlignHorizontalCenter` ("Center Horizontal" in Writer; "Align Center" in Calc) centers horizontally. Equivalent. ✓ verified vs LO source. |
| Align Right | ObjectsAlignRightSmart | button | `.uno:ObjectAlignRight` | same | Free | Align right edges of selected objects. — **LO:** `.uno:ObjectAlignRight` ("~Right") aligns right edges. Equivalent. ✓ verified vs LO source. |
| Align Top | ObjectsAlignTopSmart | button | `.uno:AlignTop` | same | Free | Align top edges of selected objects. — **LO:** `.uno:AlignTop` ("Align Top to Anchor" in Writer; "Align Top" in Calc) aligns top edges. The Writer label reveals the anchor/selection-relative model; action matches. ✓ verified vs LO source. |
| Align Middle | ObjectsAlignMiddleVerticalSmart | button | `.uno:AlignVerticalCenter` | same | Free | Align selected objects to their vertical middle. — **LO:** `.uno:AlignVerticalCenter` ("Align Middle to Anchor") aligns to vertical center. Same anchor/selection caveat; action matches. ✓ verified vs LO source. |
| Align Bottom | ObjectsAlignBottomSmart | button | `.uno:AlignBottom` | same | Free | Align bottom edges of selected objects. — **LO:** `.uno:AlignBottom` ("Align Bottom to Anchor" in Writer; "Align Bottom" in Calc) aligns bottom edges. Anchor/selection-relative; action matches. ✓ verified vs LO source. |
| Distribute Horizontally | AlignDistributeHorizontally | button | `.uno:DistributeHorzCenter` | differs | Our-layer UI | Distribute selected objects evenly along the horizontal axis (single command). — **LO:** No single command; LO splits into `.uno:DistributeHorzLeft` / `DistributeHorzCenter` / `DistributeHorzRight` / `DistributeHorzDistance` ("…Spacing"), plus `.uno:DistributeSelection` ("~Distribution", ≥3 objects). Word's single command maps best to DistributeHorzCenter/Distance; our layer picks the representative. ✓ verified vs LO source. |
| Distribute Vertically | AlignDistributeVertically | button | `.uno:DistributeVertCenter` | differs | Our-layer UI | Distribute selected objects evenly along the vertical axis (single command). — **LO:** LO splits into `.uno:DistributeVertTop` / `DistributeVertCenter` / `DistributeVertBottom` / `DistributeVertDistance` ("…Spacing"). Word's single command maps best to DistributeVertCenter/Distance; `.uno:DistributeSelection` opens the combined dialog. Our layer picks the representative. ✓ verified vs LO source. |
| Align to Page | ObjectsAlignRelativeToContainerSmart | toggleButton | — | LO-missing | Behavior shim | Toggle aligning objects relative to the page. — **LO:** No target toggle; LO alignment is relative to the object's anchor or the selection bounding box. Our dispatch layer can compute page-relative coordinates (page geometry is known) and apply them on the align command — a shim, not an engine gap. (Raw idMso catalog label is "Align to Slide" — see QA flags.) |
| Align to Margin | ObjectsAlignRelativeToMargin | toggleButton | — | LO-missing | Behavior shim | Toggle aligning objects relative to the margin. — **LO:** No align-to-margin target toggle; same reason as Align to Page. Our dispatch layer computes margin-relative coordinates. |
| Align Selected Objects | ObjectsAlignSelectedSmart | toggleButton | — | LO-missing | Behavior shim | Toggle aligning objects relative to each other. — **LO:** No explicit toggle; aligning a multi-selection relative to each other is LO's implicit default, but there is no discrete on/off control. Our layer exposes the toggle over the existing default. |
| Use Alignment Guides | AlignmentGuides | checkBox | — | LO-missing | Optional our-layer feature | Toggle dynamic alignment guides shown while dragging objects. — **LO:** No dynamic "smart guides while dragging" feature in LO Writer (it has snap-to-grid `.uno:GridUse` and manual snap lines, not automatic alignment guides). An interactive editing aid we could build as an overlay. |
| View Gridlines | ViewGridlinesWord | checkBox | `.uno:GridVisible` | differs | Our-layer UI | Toggle display of the drawing gridlines. — **LO:** `.uno:GridVisible` ("Grid", ContextLabel "~Display Grid") toggles the drawing-layer grid in LO. Roughly equivalent, but in Word this lives in the Align menu and refers to table/object layout gridlines; LO's is the drawing snap grid configured via Tools > Options. Related, not identical, and not inside the align menu. ✓ verified vs LO source. |
| Grid Settings | GridSettings | button | `.uno:GridMenu` | differs | Our-layer UI | Opens the Grid and Guides dialog. — **LO:** No single "Grid and Guides" dialog command; grid options live in Tools > Options > Writer > Grid, and on menus there is `.uno:GridMenu` ("Gr~id and Helplines") / `.uno:GridsMenu` ("Gr~ids and Helplines", plural, in WriterCommands) grouping grid toggles. Different location/dialog; our layer routes there. ✓ verified vs LO source. |
| Group | ObjectsGroupMenu | menu | `.uno:GroupMenu` | differs | Our-layer UI | Grouping menu — Group / Ungroup / Regroup. — **LO:** `.uno:GroupMenu` ("~Group Shapes") contains Group / Ungroup / Enter Group / Exit Group — NOT "Regroup" (LO has no Regroup) and adds Enter/Leave Group which Word lacks here. Menu contents differ; our layer presents Word's set. ✓ verified vs LO source. |
| Group (command) | ObjectsGroup | button | `.uno:FormatGroup` | same | Free | Combine selected objects into one group. — **LO:** `.uno:FormatGroup` ("~Group", Ctrl+Shift+G) groups the selected objects into one unit — direct match. (`.uno:Group` is the form-control variant.) ✓ verified vs LO source. |
| Regroup | ObjectsRegroup | button | — | LO-missing | Optional our-layer feature | Re-group objects previously grouped then ungrouped. — **LO:** No Regroup command; LO keeps no memory of a prior grouping to restore. Our layer could track last-group membership and re-group — app-state we could build. ✓ verified vs LO source. |
| Ungroup | ObjectsUngroup | button | `.uno:FormatUngroup` | same | Free | Split a group back into its constituent objects. — **LO:** `.uno:FormatUngroup` ("~Ungroup", Ctrl+Shift+Alt+G) splits a group — direct match. (`.uno:Ungroup` is the form-control variant.) ✓ verified vs LO source. |
| Rotate | ObjectRotateGallery | gallery | `.uno:RotateFlipMenu` | differs | Our-layer UI | Dropdown — Rotate Right 90 / Left 90 / Flip Vertical / Flip Horizontal + More Rotation Options. — **LO:** `.uno:RotateFlipMenu` ("Rot~ate or Flip") / `.uno:RotateMenu` group `.uno:RotateRight` ("Rotate 90° ~Right"), `.uno:RotateLeft` ("Rotate 90° ~Left"), `.uno:FlipVertical` ("Flip Vertically"), `.uno:FlipHorizontal` ("Flip Horizontally") — matching Word's four items. Differs: LO adds Rotate180, RotateReset, and a free-rotate mode (`.uno:ToggleObjectRotateMode`), and it's a menu of discrete commands, not a gallery. Our layer presents the gallery. ✓ verified vs LO source. |
| More Rotation Options | ChartRotationOptionsDialog | button | `.uno:TransformDialog` | differs | Our-layer UI | Opens the Layout dialog (Size tab) for an exact rotation angle. — **LO:** LO sets an exact angle via the Rotation tab of `.uno:TransformDialog` ("Position and Si~ze…") or `.uno:TransformRotationAngle` ("Rotation Angle"), not Word's Layout-dialog Size tab. Same goal, different dialog. ✓ verified vs LO source. |
| Arrange (overflow menu) | ObjectsArrangeMenu | menu | `.uno:ArrangeMenu` | differs | Our-layer UI | Collapsed overflow menu re-hosting the full Arrange command set when the group is narrow. — **LO:** `.uno:ArrangeMenu` ("A~rrange") / `.uno:ArrangeFrameMenu` ("Arrange") exist as genuine arrange menus, but they are NOT a responsive overflow container — they are static menus grouping the z-order/layer commands and do not dynamically re-host Align/Group/Rotate by ribbon width. Conceptually different; our layer handles the collapse. ✓ verified vs LO source. |

---

## LO-source verification

These mappings were checked against the vendored LibreOffice tree at
`apps/libreoffice/libreoffice-codebase/` and **override** the mapped rows where they conflicted.
Every row whose `loUno` is non-null, plus the menu/container labels and the suspect `differs`
behavior claims, were verified directly against `officecfg` `.xcu` command/label files,
`Accelerators.xcu`, `sw/sdi/swriter.sdi`, and one `.cxx` source (`viewling.cxx` for Hyphenate
behavior). **No material correction** was needed — all checks passed CONFIRMED except three minor
label-precision **CORRECTED** items.

**Material corrections:** none.

**Minor label-precision corrections (CORRECTED) — verdicts/buckets unchanged:**

- **TransformDialog (Position / More Layout Options (Position) / More Rotation Options)** — the
  stored label is **"Position and Si~ze…"** (mnemonic tilde before "z"), not "Position and Size…".
  Also `.uno:TransformRotationAngle` Label = "Rotation Angle". Evidence:
  `GenericCommands.xcu:2050` (TransformDialog, label 2052); `:2045` (TransformRotationAngle, label 2047).
- **View Gridlines (`.uno:GridVisible`)** — "Display Grid" is the **ContextLabel** ("~Display
  Grid"), not a TooltipLabel; the node has no TooltipLabel at the inspected lines. Evidence:
  `GenericCommands.xcu:5122` (label 5124, ContextLabel 5126-5127).
- **Grid Settings** — `.uno:GridMenu` ("Gr~id and Helplines", **singular**) lives in
  GenericCommands; `.uno:GridsMenu` ("Gr~ids and Helplines", **plural**) lives in WriterCommands —
  the mapping cited "Grid and Helplines" for both names, but the GridsMenu label is the plural form.
  Snap toggle is `.uno:GridUse` ("Snap to Grid"). Evidence: `GenericCommands.xcu:2712` (GridMenu,
  label 2714); `WriterCommands.xcu:3600` (GridsMenu, label 3602); `GenericCommands.xcu:4120` (GridUse, label 4122).

**Confirmed (CONFIRMED) — command/label/tooltip (and cited shortcut) match the mapping:**

- **Text Direction** — `.uno:TextdirectionTopToBottom` ("Text direction from top to bottom") and `.uno:TextdirectionLeftToRight` ("Text direction from left to right") both exist; no text-direction gallery command found. Evidence: `GenericCommands.xcu:3053/3061`.
- **Margins** — `.uno:PageMargin`, "Page Margins". Evidence: `WriterCommands.xcu:4337-4339`.
- **Custom Margins / Page Setup launcher / More Paper Sizes** — `.uno:PageDialog`, "~Page Style…". Evidence: `WriterCommands.xcu:1571-1573`.
- **Orientation** — `.uno:Orientation`, "Orientation". Evidence: `WriterCommands.xcu:4321-4323`.
- **Size** — `.uno:AttributePageSize`, "Page Size"; `.uno:PageSettingDialog` ("Page Settings - Paper format") also present. Evidence: `WriterCommands.xcu:4329-4331`; `:3750-3752`.
- **Columns / More Columns** — `.uno:PageColumnType` ("Page Columns"), `.uno:PageColumnDialog` ("Page Columns"), `.uno:FormatColumns` ("Co~lumns…"). Evidence: `WriterCommands.xcu:1558/1550/1595`.
- **Breaks** — `.uno:BreaksMenu`, "More Breaks" (defined in GenericCommands). Evidence: `GenericCommands.xcu:7859-7861`.
- **Page (break)** — `.uno:InsertPagebreak`, "~Page Break", tooltip "Insert Page Break", default shortcut Ctrl+Enter (RETURN_MOD1) — matches Word. Evidence: `WriterCommands.xcu:850-855`; `Accelerators.xcu:2780-2783`.
- **Column (break)** — `.uno:InsertColumnBreak`, "Insert Column Break"; slot FN_INSERT_COLUMN_BREAK. Evidence: `WriterCommands.xcu:669-671`; `swriter.sdi:2819`.
- **Next Page (section break)** — `.uno:InsertBreak`, "Manual ~Break…". Evidence: `WriterCommands.xcu:661-663`.
- **Continuous (section break)** — `.uno:InsertSection`, "Columns" / ContextLabel "Section…" / tooltip "Insert a section with columns". Evidence: `WriterCommands.xcu:150-158`.
- **Line Numbers / Line Numbering Options** — `.uno:LineNumberingDialog`, "~Line Numbering…" (a single dialog = the whole feature). Evidence: `WriterCommands.xcu:3071-3073`.
- **Manual (Hyphenation) / Hyphenation menu** — `.uno:Hyphenate`, "~Hyphenation…", tooltip "Insert Soft Hyphen…"; dispatches `SwView::HyphenateDocument()` (interactive pass, guards against concurrent interactive hyph), confirming "manual/interactive, not automatic". Evidence: `WriterCommands.xcu:3160-3165`; `sw/source/uibase/uiview/viewling.cxx:362,364-372`.
- **Paragraph (dialog box launcher)** — `.uno:ParagraphDialog`, "P~aragraph…". Evidence: `GenericCommands.xcu:4608-4610`.
- **Indent Left / Increase Indent** — `.uno:IncrementIndent` ("Increase" / "Increase Indent"), `.uno:DecrementIndent` ("Decrease" / "Decrease Indent"); no direct-entry indent spinner `.uno` found. Evidence: `GenericCommands.xcu:5342/5328`.
- **Spacing Before / Spacing After** — `.uno:ParaspaceIncrease` ("Increase" / "Increase Paragraph Spacing"), `.uno:ParaspaceDecrease` ("Decrease" / "Decrease Paragraph Spacing"). Evidence: `GenericCommands.xcu:160/174`.
- **Wrap Text** — `.uno:WrapMenu` ("~Wrap"), WrapOff ("None"), WrapOn ("~Parallel"), WrapIdeal ("~Optimal"), WrapThrough ("~Through"), WrapLeft ("Before"), WrapRight ("After"), WrapThroughTransparent ("In ~Background"), WrapContour ("Wrap Contour On"). Evidence: `WriterCommands.xcu:3726/1690/1698/2698/1722/2818/2831/2711/2918`.
- **More Layout Options (Wrapping)** — `.uno:TextWrap`, "Text Wrap…". Evidence: `WriterCommands.xcu:3017-3019`.
- **Move with Text / Fix Position on Page** — `.uno:SetAnchorToPara` ("Anchor To Paragraph"), `.uno:SetAnchorToPage` ("Anchor To Page"), `.uno:SetAnchorAtChar` ("Anchor to Character"), `.uno:SetAnchorToChar` ("Anchor as Character"), `.uno:ProtectPos` ("Protect Position"). Evidence: `WriterCommands.xcu:954/946/89/1130`; `GenericCommands.xcu:2688`.
- **Bring Forward (primary)** — `.uno:ObjectForwardOne`, "Forward One". Evidence: `GenericCommands.xcu:4398-4400`.
- **Send Backward (primary)** — `.uno:ObjectBackOne`, "Back One". Evidence: `GenericCommands.xcu:4406-4408`.
- **Bring to Front** — `.uno:BringToFront`, "~Bring to Front", Ctrl+Shift+Plus (ADD_SHIFT_MOD1). Evidence: `GenericCommands.xcu:4493-4495`; `Accelerators.xcu:1704-1707`.
- **Send to Back** — `.uno:SendToBack`, "~Send to Back", Ctrl+Shift+Minus (SUBTRACT_SHIFT_MOD1). Evidence: `GenericCommands.xcu:4501-4503`; `Accelerators.xcu:2028-2031`.
- **Bring in Front of Text** — `.uno:SetObjectToForeground`, "To Foreground". Evidence: `GenericCommands.xcu:4475-4477`.
- **Send Behind Text** — `.uno:SetObjectToBackground`, "To Background". Evidence: `GenericCommands.xcu:4467-4469`.
- **Selection Pane** — `.uno:Navigator`, "Na~vigator" (partial analog, no per-object eye/reorder). Evidence: `GenericCommands.xcu:4830-4832`.
- **Align** — `.uno:ObjectAlign`, "Alig~n Objects". Evidence: `GenericCommands.xcu:7182-7184`.
- **Align Left** — `.uno:ObjectAlignLeft`, "~Left". Evidence: `GenericCommands.xcu:2986-2988`.
- **Align Right** — `.uno:ObjectAlignRight`, "~Right". Evidence: `GenericCommands.xcu:3002-3004`.
- **Align Center** — `.uno:AlignHorizontalCenter`, "Center Horizontal" in Writer (`WriterCommands.xcu:1770-1772`); the same `.uno` reads "Align Center" in Calc (`CalcCommands.xcu:2330`) — the Writer label is the relevant one.
- **Align Top** — `.uno:AlignTop`, "Align Top to Anchor" in Writer (confirms anchor-relative model); "Align Top" in Calc. Evidence: `WriterCommands.xcu:1778-1780`; `CalcCommands.xcu:2346`.
- **Align Middle** — `.uno:AlignVerticalCenter`, "Align Middle to Anchor" (Writer). Evidence: `WriterCommands.xcu:1794-1796`.
- **Align Bottom** — `.uno:AlignBottom`, "Align Bottom to Anchor" in Writer; "Align Bottom" in Calc. Evidence: `WriterCommands.xcu:1786-1788`; `CalcCommands.xcu:2354`.
- **Distribute Horizontally** — all four exist: `.uno:DistributeHorzLeft` ("Distribute Horizontally Left"), `DistributeHorzCenter` ("…Center"), `DistributeHorzDistance` ("…Spacing"), `DistributeHorzRight` ("…Right"); `.uno:DistributeSelection` ("~Distribution"). Evidence: `GenericCommands.xcu:7971/7982/7993/8004/7957`.
- **Distribute Vertically** — all four exist: `.uno:DistributeVertTop` ("Distribute Vertically Top"), `DistributeVertCenter` ("…Center"), `DistributeVertDistance` ("…Spacing"), `DistributeVertBottom` ("…Bottom"). Evidence: `GenericCommands.xcu:8015/8026/8037/8048`.
- **Group (menu)** — `.uno:GroupMenu`, "~Group Shapes" (contains Group/Ungroup/Enter/Exit, no Regroup). Evidence: `GenericCommands.xcu:7394-7396`.
- **Group (command)** — `.uno:FormatGroup`, "~Group", Ctrl+Shift+G (G_SHIFT_MOD1); `.uno:Group` ("~Group…") is the form-control variant. Evidence: `GenericCommands.xcu:5298/3773`; `Accelerators.xcu:1871-1874`.
- **Ungroup** — `.uno:FormatUngroup`, "~Ungroup", Ctrl+Shift+Alt+G (G_SHIFT_MOD1_MOD2); `.uno:Ungroup` ("~Ungroup…") is the form-control variant. Evidence: `GenericCommands.xcu:5306/3789`; `Accelerators.xcu:1877-1880`.
- **Rotate (menu)** — `.uno:RotateFlipMenu` ("Rot~ate or Flip"), `.uno:RotateMenu` ("Rot~ate"), `.uno:ToggleObjectRotateMode` ("~Rotate"); `.uno:RotateLeft` ("Rotate 90° ~Left"), `RotateRight` ("Rotate 90° ~Right"), `Rotate180` ("Rotate 1~80°"), `RotateReset` ("Reset R~otation"); `.uno:FlipHorizontal` ("Flip Horizontally"), `FlipVertical` ("Flip Vertically"). Evidence: `GenericCommands.xcu:7423/7418/2978/5224/5232`; `WriterCommands.xcu:1426/1434/1442/1450`.
- **Arrange (overflow menu)** — `.uno:ArrangeMenu` ("A~rrange", GenericCommands); `.uno:ArrangeFrameMenu` ("Arrange", WriterCommands). Evidence: `GenericCommands.xcu:7402-7404`; `WriterCommands.xcu:3734-3736`.
- **Regroup (LO-missing)** — no `.uno:*Regroup*` or "Regroup" command found anywhere in officecfg; GroupMenu has no regroup child. Evidence: grep for "Regroup" across officecfg returned no command nodes; GroupMenu at `GenericCommands.xcu:7394`.

> **Context-sensitivity finding (important for the clone).** The `Align*` commands carry
> **different labels per module**: in Writer they read "Align Top to Anchor" / "Center Horizontal"
> (anchor-relative, confirming the mapping); the same `.uno` names in Calc read "Align Top" /
> "Align Center". The mapping's labels are the Writer ones, correct for a Word/Writer comparison.

> **Scope caveat from the LO-verify pass.** The `LO-missing` rows with no approximation
> (Set as Default Layout, Use Alignment Guides, Regroup, Align-to-Page/Margin/Selected toggles,
> Restart Each Section, Text Wrapping break) were verified for **absence** by targeted grep (e.g.
> Regroup) but broad "LO has no X feature" claims are treated as plausible rather than exhaustively
> proven; a full enumeration of every `.uno` in officecfg would be needed for a stronger guarantee.
> Supplementary keyboard-shortcut facts (additive, not corrections): InsertPagebreak=Ctrl+Enter,
> FormatGroup=Ctrl+Shift+G, FormatUngroup=Ctrl+Shift+Alt+G, BringToFront=Ctrl+Shift+Plus,
> SendToBack=Ctrl+Shift+Minus.

---

## Conditional / version-sensitive controls

There is **no owner screenshot for the Layout tab yet**, so the following are flagged
**expected-conditional, unverified against a live build** — a screenshot sweep would confirm
whether (and how) they surface. They are not contradicted by the inventory; they simply depend on
selection state or Word version.

- **Text Direction gallery (`TextDirectionGalleryWord`)** — contextual: appears on the Layout tab only when a text box / shape is selected, and its item set (Horizontal / Rotate-90 / Rotate-270 / Stacked) is build-dependent. A real-Word screenshot with a text box selected is needed to confirm presence on Layout (vs the Shape Format tab) and the item list. The LO mapping (`.uno:TextdirectionTopToBottom`) is a weak partial analog.
- **Position gallery (`PicturePositionGallery`)** — the 9-cell "with text wrapping" preset grid + "In Line With Text" is the part with no LO analog; a screenshot is needed to confirm the exact preset set and whether it lives on Layout vs only Picture/Shape Format contextual tabs.
- **Align to Page (`ObjectsAlignRelativeToContainerSmart`)** — the target toggle is sometimes greyed/absent depending on selection; confirm Word surfaces it on the Layout-tab Align menu.
- **Breaks dropdown contents** — version-dependent: classic builds show Page/Column/Text-Wrapping + Next/Continuous/Even/Odd section breaks (what the inventory models); newer simplified builds also show "Remove Page Break" / "Reset All Page Breaks". A screenshot of the exact target Word version is needed to know which content set to clone.
- **idMso version-sensitivity** — several idMsos are M365-Current-Channel values; the split-button container idMsos (`ObjectBringForwardMenu` / `ObjectSendBackwardMenu`) could not be confirmed against Microsoft's official splitButton catalog (see QA flags) and a live-build QAT-hover would settle them.

---

## Out of scope

- **Engine gap — section-model artifacts (the only true engine blockers, 2 controls).** Both are
  downstream of Word's **section** model, which LO genuinely lacks as a document object: (1) the
  **Text Wrapping break** — an insertable break character that pushes text below a floating object;
  LO's text engine has no such break character. (2) **Restart Each Section** line numbering — LO has
  no section boundary to restart numbering at. Cut now, or accept reduced fidelity. (Most other
  "section" uses — next-page / continuous / even / odd section breaks — are *approximable* via page
  breaks + page styles or text sections, so they are behavior shims, not engine gaps.)
- **Cloud / AI / M365 (cut by product choice).** **None on this tab** — the Layout tab is entirely
  local page/paragraph/object formatting with no online/AI controls. Cut = 0.
- **Niche / region-specific (cut by scope).** **None on this tab.**

---

## QA flags & resolutions

From `result.qa`. The Word/idMso side was set-diffed against the official `wordcontrols.xlsx`
(M365 + 2013/2016/2019) and is essentially complete for the classic Layout tab; the LO-source pass
produced no material LO defect. Because there is **no owner screenshot for this tab**, several
structural items remain **screenshot-pending**.

| QA flag | Status | Resolution |
|---|---|---|
| Bring Forward / Send Backward split-button **container** idMsos (`ObjectBringForwardMenu` / `ObjectSendBackwardMenu`)? | **Open (correctness risk, screenshot-pending)** | Microsoft's official-derived splitButton catalog does **not** contain these; the listed containers are `ObjectBringToFrontMenu` / `ObjectSendToBackMenu`. The primary-action buttons (`ObjectBringForward` / `ObjectSendBackward`) ARE confirmed. A real-Word QAT-hover / customUI check is needed; do not trust the container idMsos yet. Buckets unchanged (Our-layer UI either way). |
| Gallery **leaf items** enumerated inconsistently (Position presets, Wrap styles, Columns presets, Rotate leaves)? | **Open (granularity, screenshot-pending)** | Breaks and Line Numbers leaves were broken out as rows, but Position's 9-cell + In-Line presets, the 7 Wrap styles + "Edit Wrap Points", the 5 Columns presets, and the 4 Rotate/Flip leaves are described in prose only. Either enumerate gallery leaves everywhere or collapse everywhere; "completeness" depends on whether leaves are modeled as rows. "Edit Wrap Points" (idMso `EditWrapBoundary` / LO `.uno:WrapContour` edit mode) is arguably a missing row. Does not change buckets. |
| Breaks dropdown missing "Remove Page Break" / "Reset All Page Breaks"? | **Open (version-dependent, screenshot-pending)** | Modern/simplified Word builds show these two items not in the inventory (which models the classic Page/Column/Text-Wrapping + 4 section breaks). Verify against the actual Word build being cloned. |
| Official group/gallery **labels** differ from the on-ribbon contextual labels? | **Resolved (source set-diff) — label-only** | `GroupParagraphLayout` official label is "Paragraph Indent & Spacing" (distinct from Home tab's `GroupParagraph` = "Paragraph"); `PicturePositionGallery` = "Object Position"; `BreaksGallery` = "Insert Page and Section Breaks"; `PageOrientationGallery` = "Page Orientation"; `ObjectsAlignRelativeToContainerSmart` raw catalog label is "Align to Slide" (PowerPoint context, surfaced as "Align to Page" in Word). User-facing labels in the inventory are functionally correct; these are recorded for precision. |
| Odd idMsos confirmed (e.g. `TableColumnsGallery` with the "Table" prefix)? | **Resolved (source)** | Microsoft's actual identifiers — `TableColumnsGallery` (odd "Table" prefix), `ColumnsDialog`, `ChartRotationOptionsDialog`, the `*Smart` align ids — transcribed verbatim and correct. Do **not** "fix". |
| Null-idMso gallery-item rows (break/section-break leaves) correct? | **Resolved (source)** | Built-in gallery leaves legitimately have no idMso; leaving them null matches Microsoft's empty-Name rows. |
| Control types `ObjectAlignMenu` (menu) and `ChartRotationOptionsDialog` (button) — not galleries? | **Resolved (source)** | Positive confirmation: both are absent from the gallery list, matching the inventory's controlType assignments (menu / button). No correction. |
| LO-side mappings vs the supplied LO-source corrections? | **Resolved (LO source)** | All non-null `loUno` mappings, menu/container labels, and suspect `differs` claims were verified directly; all CONFIRMED except three minor label-precision CORRECTED items (TransformDialog mnemonic, GridVisible ContextLabel, GridMenu/GridsMenu singular-vs-plural). No LO mapping conflicts found. |

`completenessConfidence`: **Medium-high.** All non-null idMsos were cross-checked against
Microsoft's official-derived idMso catalog plus the BetterSolutions Layout-tab reference; the
control tree is essentially complete for the classic Layout tab. Held back from high by (1) the
split-button container idMsos (`ObjectBringForwardMenu` / `ObjectSendBackwardMenu`), which could not
be confirmed and are likely mis-named — the one substantive correctness risk; (2) inconsistent
gallery-leaf enumeration (Position/Wrap/Columns/Rotate); and (3) Word version drift (Breaks dropdown
and the Text Direction / Position contextual galleries vary by build, uncertifiable without a
screenshot). LO-side mappings are well-supported by the LO-source corrections, with no contradicting
mapping found.
