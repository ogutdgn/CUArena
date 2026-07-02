# Locked Scope — RL Environment Feature Set

_Generated from the Step-1 functionality audit (`FEATURE_PARITY_AUDIT.md`) × the Step-2 usage ranking (`FEATURE_USAGE_RANKING.md`). This is the committed scope: the features we measure "% done" against and commit to full Word parity._

## Decision rules

1. **Usage floor:** lock all of **T0–T2** (ubiquitous→medium usage). Certain.
2. **Reward-signal rule (T3):** lock a low-usage (T3) feature only if it produces a verifiable **document change** (a usable RL reward signal). View/window/cloud UI that yields no document mutation is kept but not locked.
3. **Coherence overrides:** **Layout/Arrange** (floating-object foundation) and the **Mailings mail-merge engine** are locked as whole clusters even where individual controls do not write.
4. **Keep ≠ lock:** deferred features stay in the app and keep working; we simply do not commit them to full parity yet.
5. **Done = strict full parity only.** A control counts as done only when faithful to real Word; partial/wrong/stub all count as not-done.

## Headline

- **Locked controls:** 111  (of 214 ranked)
- **Strict % done:** 47/111 = **42.3%**
- **Status mix:** ✅ full 47 · 🟡 partial 62 · ❌ stub 2
- **Road to 100%:** 64 controls (62 partial→full polish, 2 stub→build: Insert/Shapes, Layout/Group)

## Locked features

### Home — 26/41 full

| Feature | Usage | Status | Gap to full parity |
|---|---|---|---|
| **Cut** | T0 | ✅ full |  |
| **Copy** | T0 | ✅ full |  |
| **Font Size** | T0 | ✅ full |  |
| **Bold** | T0 | ✅ full |  |
| **Italic** | T0 | ✅ full |  |
| **Underline** | T0 | ✅ full |  |
| **Bullets** | T0 | ✅ full |  |
| **Align Left** | T0 | ✅ full |  |
| **Center** | T0 | ✅ full |  |
| **Paste** | T0 | 🟡 partial | Paste Special is a simplified dialog (no full RTF/Unformatted/OLE-object format list); merge is HTML-reconciliation heuristic, not Word's st |
| **Font (face)** | T0 | 🟡 partial | No live hover preview on the document; font list is a fixed catalog, not the full installed-font enumeration. |
| **Text Highlight Color** | T1 | ✅ full |  |
| **Font Color** | T1 | ✅ full |  |
| **Numbering** | T1 | ✅ full |  |
| **Align Right** | T1 | ✅ full |  |
| **Justify** | T1 | ✅ full |  |
| **Find** | T1 | ✅ full |  |
| **Replace** | T1 | ✅ full |  |
| **Line and Paragraph Spacing** | T1 | 🟡 partial | Add/Remove Space uses a fixed 12pt; no Exactly/AtLeast/Multiple line-rule shortcuts from the ribbon menu itself. |
| **Styles Gallery** | T1 | 🟡 partial | No live hover preview on the document; gallery is a fixed style list and styles absent from the doc catalog fail with a toast instead of bei |
| **Editor** | T1 | 🟡 partial | Offline engine only: no cloud Editor Score, Similarity, Insights, or M365 Formality/Punctuation refinements; grammar is rule-based not ML. |
| **Increase Font Size** | T2 | ✅ full |  |
| **Decrease Font Size** | T2 | ✅ full |  |
| **Change Case** | T2 | ✅ full |  |
| **Clear All Formatting** | T2 | ✅ full |  |
| **Strikethrough** | T2 | ✅ full |  |
| **Decrease Indent** | T2 | ✅ full |  |
| **Increase Indent** | T2 | ✅ full |  |
| **Shading** | T2 | ✅ full |  |
| **Format Painter** | T2 | 🟡 partial | Relies on fork FormatCommands capture; no cross-document painting and brush UX is a toast rather than a live cursor brush. |
| **Font dialog (launcher)** | T2 | 🟡 partial | No live hover preview on the document; font list is a fixed catalog, not the full installed-font enumeration. |
| **Show/Hide ¶** | T2 | 🟡 partial | Display toggle is faithful but limited to the implemented mark glyphs (e.g. hidden-text, object anchors not represented). |
| **Borders** | T2 | 🟡 partial | Inside-Vertical is a toast no-op, Draw Table is notImplemented, diagonal borders greyed (paragraph context); multi-paragraph selection seeds |
| **Paragraph dialog (launcher)** | T2 | 🟡 partial | Lacks the full Line and Page Breaks tab (widow/orphan, keep-with-next, suppress line numbers) fidelity. |
| **Styles pane (launcher)** | T2 | 🟡 partial | Limited management (no Modify/New Style/Manage Styles dialog, no Options filter, no inline style inspector). |
| **Select** | T2 | 🟡 partial | Similar-formatting selects only one contiguous range (Word multi-selects discontiguous); Selection Pane and Select Objects are limited stand |
| **Subscript** | T3 | ✅ full |  |
| **Superscript** | T3 | ✅ full |  |
| **Text Effects and Typography** | T3 | 🟡 partial | Effects export to w14 effect elements (good) but presets are a curated subset; reflection/glow rendering is CSS-approximate vs Word's exact  |
| **Multilevel List** | T3 | 🟡 partial | Only 5 built-in patterns; no Current-List section, no List-Library thumbnails, and Define New List Style is absent. |
| **Sort** | T3 | 🟡 partial | Sorts only contiguous paragraphs in one parent (no table-column sort); options dialog lacks case-sensitivity / language / separator settings |

### Insert — 5/18 full

| Feature | Usage | Status | Gap to full parity |
|---|---|---|---|
| **Table** | T1 | 🟡 partial | Core table insert/convert is faithful; Excel Spreadsheet is a stub toast and Quick Tables are plain tables with no gallery styling. |
| **Pictures** | T1 | 🟡 partial | This Device works fully; Online Pictures is a stub toast and Stock Images is absent. |
| **Link** | T1 | 🟡 partial | Web/file URL hyperlink works, but no Place-in-Document, E-mail, Create-New-Document, ScreenTip, or Recent Items; the split-button Recent Ite |
| **Header** | T1 | 🟡 partial | Plain-text-only header via a textarea; no built-in gallery designs, no on-page rich editing, no fields/multi-paragraph formatting, no Save t |
| **Footer** | T1 | 🟡 partial | Plain-text-only footer; no gallery, on-page editing, fields, or Save to Gallery. |
| **Page Number** | T1 | 🟡 partial | No design gallery, no Page Margins position, and no Format Page Numbers dialog (number format/start-at); inserts a bare PAGE field only. |
| **Comment** | T2 | ✅ full |  |
| **Symbol** | T2 | ✅ full |  |
| **Page Break** | T2 | 🟡 partial | Inserts an empty new-page paragraph after the block instead of splitting at the caret; content after the caret in the same paragraph stays o |
| **Shapes** | T2 | ❌ stub | Entire Shapes feature is non-functional — picking a shape does nothing but toast. |
| **Bookmark** | T3 | ✅ full |  |
| **Drop Cap** | T3 | ✅ full |  |
| **Date & Time** | T3 | ✅ full |  |
| **Cover Page** | T3 | 🟡 partial | Inserts a generic 3-paragraph SDT block, not the styled gallery design the user picked; no Office.com gallery, no Save to Gallery. |
| **Icons** | T3 | 🟡 partial | Inserts the application's own toolbar icons as images rather than Word's icon gallery; not the curated Office icon set. |
| **Cross-reference** | T3 | 🟡 partial | Only Heading and Bookmark reference types (no Figure/Table/Footnote/Endnote/Equation/Numbered item) and no 'insert as hyperlink' option. |
| **Text Box** | T3 | 🟡 partial | Inserts one generic editable text box; no styled gallery, no real Draw-to-size, no Save to Gallery. |
| **Quick Parts** | T3 | 🟡 partial | Real fields for a fixed handful only; no AutoText gallery, no Building Blocks Organizer, no full Field-codes/options picker, no Save to Gall |

### Design — 0/4 full

| Feature | Usage | Status | Gap to full parity |
|---|---|---|---|
| **Themes** | T3 | 🟡 partial | Rewrites literal fonts/colors on named styles instead of editing the theme part (no theme1.xml color/font/effect scheme); applies no theme e |
| **Paragraph Spacing** | T3 | 🟡 partial | Applies spacing only to docDefaults + Normal, not the full style-set heading/body spacing matrix; presets' exact values depend on clone's WC |
| **Page Color** | T3 | 🟡 partial | Solid color fully works and exports; the 'Fill Effects...' sub-item (gradient/texture/pattern/picture page fills) is not present in the pale |
| **Page Borders** | T3 | 🟡 partial | Real pgBorders write but a stripped dialog: no Setting presets (Box/Shadow/3-D), no per-edge selection, no Art borders, no Apply-to scope; a |

### Layout — 7/16 full

| Feature | Usage | Status | Gap to full parity |
|---|---|---|---|
| **Margins** | T1 | 🟡 partial | Per-edge presets write correctly, but Custom dialog is one uniform value (no separate edges/gutter/apply-to), and Mirrored/Office2003 are no |
| **Orientation** | T2 | ✅ full |  |
| **Size** | T2 | ✅ full |  |
| **Columns** | T2 | ✅ full |  |
| **Indent Left** | T2 | ✅ full |  |
| **Indent Right** | T2 | ✅ full |  |
| **Spacing Before** | T2 | ✅ full |  |
| **Spacing After** | T2 | ✅ full |  |
| **Breaks** | T2 | 🟡 partial | Only one typed section break per document; mid-doc section breaks don't repaginate in-app; Text-Wrapping break is a generic hardBreak. |
| **Position** | T3 | 🟡 partial | All 9 presets only set horizontal alignment (no vertical anchor); requires a selected picture; no More Layout Options dialog. |
| **Wrap Text** | T3 | 🟡 partial | Missing Edit Wrap Points / Move with Text / Fix Position on Page / More Layout Options; requires a selected picture. |
| **Bring Forward** | T3 | 🟡 partial | Re-stacking only effective for absolutely-positioned (Behind/In Front) images; floated-wrap images don't visually re-stack; needs a selected |
| **Send Backward** | T3 | 🟡 partial | Same as Bring Forward — only absolutely-positioned images re-stack; needs a selected floating picture. |
| **Align** | T3 | 🟡 partial | Only horizontal align is real; vertical align + distribute are toast stubs; no page/margin reference toggles, gridlines, or grid settings; s |
| **Rotate** | T3 | 🟡 partial | 90-degree rotate + flips are faithful, but no arbitrary-angle 'More Rotation Options' dialog; needs a selected picture. |
| **Group** | T3 | ❌ stub | No grouping at all — both options are toasts; no w:grpSp written; Regroup missing. |

### References — 0/7 full

| Feature | Usage | Status | Gap to full parity |
|---|---|---|---|
| **Insert Footnote** | T2 | 🟡 partial | Seeds placeholder text 'Footnote' instead of leaving an empty editable note; cursor is not placed in the note body for immediate typing. |
| **Table of Contents** | T3 | 🟡 partial | Real auto-TOC works but headless layout fidelity (clone TOC rendering is approximate); 'Manual Table' does NOT produce Word's editable place |
| **Update Table** | T3 | 🟡 partial | No 'update page numbers only' vs 'entire table' prompt; updates everything indiscriminately; page-number fidelity bounded by clone's approxi |
| **Insert Endnote** | T3 | 🟡 partial | Seeds 'Endnote' placeholder text; no cursor placement into the note body. |
| **Insert Citation** | T3 | 🟡 partial | In-text citation renders headless (field exports but clone display approximate); see 'Add New Placeholder' which is a stub. |
| **Insert Caption** | T3 | 🟡 partial | SEQ number renders empty/headless in the clone (resolves on Word reopen); no numbering-format or 'exclude label from caption' options; no ch |
| **Cross-reference** | T3 | 🟡 partial | Only Heading and Bookmark reference types (no Numbered item / Figure / Table / Footnote targets); display limited to pageNumber/content/abov |

### Mailings — 2/10 full

| Feature | Usage | Status | Gap to full parity |
|---|---|---|---|
| **Insert Merge Field** | T3 | ✅ full |  |
| **Preview Results** | T3 | ✅ full |  |
| **Envelopes** | T3 | 🟡 partial | No envelope size selection, no font/formatting options, no electronic postage; fixed layout; envelope is plain HTML not a real Word envelope |
| **Labels** | T3 | 🟡 partial | Only 3 hardcoded Avery products, no real label dimensions/margins, full-page checkbox ignored, no single-label mode, Print is a stub toast. |
| **Start Mail Merge** | T3 | 🟡 partial | mergeType is stored but barely affects behavior (finish mode is chosen separately); no real main-document setup for Letters/Email/Directory; |
| **Select Recipients** | T3 | 🟡 partial | Outlook contacts unsupported; data source is in-memory only (not persisted to the doc); no Excel/Access/database connectors beyond CSV/TSV t |
| **Edit Recipient List** | T3 | 🟡 partial | No include/exclude checkboxes, no sort, filter, find-duplicates, or validate-addresses; just a raw cell-edit grid. |
| **Address Block** | T3 | 🟡 partial | The dialog's name-format and company/postal options are NOT persisted into the inserted field; composite() always uses a fixed format, so th |
| **Greeting Line** | T3 | 🟡 partial | Chosen greeting word, name format, punctuation and invalid-name fallback are NOT saved into the field; composite() defaults to 'Dear …,' so  |
| **Finish & Merge** | T3 | 🟡 partial | Only Edit Individual Documents truly merges; Print does NOT substitute records (prints the template), and Send E-mail is a stub. Rule fields |

### Review — 5/11 full

| Feature | Usage | Status | Gap to full parity |
|---|---|---|---|
| **Editor** | T1 | 🟡 partial | Local-only proofing engine; cloud refinement categories (Formality/Punctuation/Vocabulary/Similarity) are non-functional disabled rows. |
| **Spelling and Grammar** | T1 | 🟡 partial | No distinct Spelling-only mode; both split items collapse to the local Editor pane. |
| **Word Count** | T2 | ✅ full |  |
| **New Comment** | T2 | ✅ full |  |
| **Delete** | T2 | ✅ full |  |
| **Accept** | T2 | ✅ full |  |
| **Reject** | T2 | ✅ full |  |
| **Display for Review** | T2 | 🟡 partial | Simple Markup shares No-Markup engine state (no true change-bar-only rendering); 4 modes collapse to 3 engine states + a CSS flag. |
| **Track Changes** | T2 | 🟡 partial | 'Just Mine' is identical to 'For Everyone' (no per-author tracking scope); lock is a UI gate, not crypto (matches Word's own note). |
| **Thesaurus** | T3 | 🟡 partial | Synonyms limited to a small built-in dictionary; no definitions/antonyms; 'No synonyms' for any word outside the table. |
| **Compare** | T3 | 🟡 partial | Word-level TEXT diff only (formatting/moves/tables comparison checkboxes disabled); replaces current doc instead of opening a new window; fi |

### View — 2/4 full

| Feature | Usage | Status | Gap to full parity |
|---|---|---|---|
| **Print Layout** | T2 | ✅ full |  |
| **Ruler** | T2 | ✅ full |  |
| **Navigation Pane** | T2 | 🟡 partial | Headings tab only — no Pages (thumbnail) tab, no Results/search tab, no drag-to-reorder headings. |
| **Zoom** | T2 | 🟡 partial | Missing custom percent spinner, Text width, Many-pages grid selector, and the live preview pane. |

## Deferred (kept, not locked) — 103 controls

These remain in the app and keep working; not committed to full parity. By tier: T3 26, T4 77.

- **Design** (6): Colors, Effects, Fonts, Set as Default, Style Set, Watermark
- **Draw** (11): Add Pen, Draw with Trackpad, Drawing, Drawing Canvas, Eraser, Ink Replay, Ink to Math, Ink to Shape, Lasso Select, Pens Gallery, Select Objects
- **Help** (5): Contact Support, Feedback, Help, Show Training, What's New
- **Home** (1): Clipboard (pane launcher)
- **Insert** (12): 3D Models, Blank Page, Chart, Equation, Get Add-ins, My Add-ins, Object, Online Video, Screenshot, Signature Line, SmartArt, WordArt
- **Layout** (3): Hyphenation, Line Numbers, Selection Pane
- **Mailings** (11): Check for Errors, Find Recipient, First Record, Go to Record, Highlight Merge Fields, Last Record, Match Fields, Next Record, Previous Record, Rules, Update Labels
- **References** (16): Add Text, Bibliography, Insert Index, Insert Table of Authorities, Insert Table of Figures, Manage Sources, Mark Citation, Mark Entry, Next Footnote, Researcher, Search, Show Notes, Style, Update Index, Update Table, Update Table
- **Review** (16): Block Authors, Check Accessibility, Filter All Markup, Hide Ink, Language, Next, Next, Previous, Previous, Read Aloud, Restrict Editing, Reviewing Pane, Show Comments, Show Markup, Track Changes Options, Translate
- **View** (22): 100%, Arrange All, Draft, Focus, Gridlines, Immersive Reader, Macros, Multiple Pages, New Window, One Page, Outline, Page Width, Properties, Read Mode, Reset Window Position, Side to Side, Split, Switch Windows, Synchronous Scrolling, Vertical, View Side by Side, Web Layout