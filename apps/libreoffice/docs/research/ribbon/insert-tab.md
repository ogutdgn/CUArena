# Insert tab — Word ↔ LibreOffice

> **Status.** Word build: Microsoft 365 (target). **Word-side: web-sourced + LO-verified —
> screenshot-pending** (not yet confirmed against a live build). LO-side: high. Produced by the
> per-tab pipeline: 3 independent extractors → reconciled canonical → mapped to LO `.uno:` →
> verified against the LibreOffice source tree. The Word/idMso side was set-diffed against the
> official `wordcontrols.xlsx` (M365 Current Channel + 2013/2016/2019) and is ~99% complete; the
> LO command facts were checked against the vendored LO tree. **No owner screenshot exists for
> this tab yet**, so conditional/version-sensitive controls below are *expected-conditional,
> unverified against a live build*. One mapping carries a **material LO-source correction** (Page
> Number → `.uno:PageNumberWizard`); 30 more are confirmed (see
> [LO-source verification](#lo-source-verification)).

This is **Word-clone decision-research**, not LibreOffice documentation. It diffs every Word
Insert-tab control against LO's command surface and classifies the **work** each diff implies.
Bucket vocabulary and verdict meanings are in [README.md](README.md#legend).

---

## Outcome

Of 141 catalogued Word Insert-tab controls, **15 wire straight through** to an existing LO
`.uno:` command (Free), and the largest band — 54 — is **our-layer UI**: galleries, split-button
menus, dialogs, and group/overflow hosts that re-present commands LO already has (Pictures,
Shapes, Header/Footer toggles, Symbol, Equation, Drop Cap, Date & Time, Object, Bookmark,
Cross-reference, the QR/Barcode dialog). Only a thin **behavior-shim** band exists (3). The
decisive number for the engine decision is **Engine gap = 33** — and unlike Home (where the gap
was rich typography) the Insert-tab gap is almost entirely **Word's Building-Blocks / gallery
system plus modern rich-media objects**. The **Cut** pile (32) is cloud/AI/M365 (Loop, web
add-ins, stock/online media) and niche region-specific controls. Four controls are app-state we
could *optionally* build.

| Work bucket | Count | What it is |
|---|---:|---|
| **Free** | 15 | wire the existing LO `.uno:` command, no UI work |
| **Our-layer UI** | 54 | build the Word-faithful gallery/dialog/host; dispatch the LO command |
| **Behavior shim** | 3 | intercept/massage in our dispatch layer; LO's result/semantics differ |
| **Engine gap** | 33 | LO engine genuinely can't; cut or accept reduced fidelity |
| **Cut** | 32 | out of scope by product choice (cloud/AI/M365, store add-ins, niche) |
| **Optional our-layer feature** | 4 | LO lacks it but it's app-state we could build |
| **Total** | **141** | |

**Decisive learning:** on Insert the engine gap is larger than Home — **Engine gap = 33 / 141
(~23%)** — but it is concentrated and predictable: **~25 of the 33 are Word's Building-Blocks /
save-to-gallery system** (cover-page / text-box / equation design galleries, every
Save-Selection-to-Gallery command, page-number-design galleries) which LO has no equivalent for,
and the rest are **modern rich-media objects** (SmartArt, Icons, 3D Models, Screenshot/Screen
Clipping, web Online Pictures, drawing canvas, ink equation, drop-cap-in-margin). LO covers the
*core insert verbs* (page break, table, picture, shapes, header/footer, hyperlink, bookmark,
comment, equation-via-Math, symbol, QR/barcode) — the gap is the **gallery/building-block layer
on top**, not the underlying objects. → still supports **LO-via-LOK + scoped parity**, with
Building Blocks explicitly out of scope.

> **Recurring our-layer theme.** Word's Insert tab is dominated by **building-block galleries**
> (Cover Page, Header, Footer, Text Box, Quick Parts, Quick Tables, Equation, Page-Number
> designs) and **split-button menus** (Pictures, Shapes, Object, Signature Line, Page Number).
> Where LO has the underlying command, the gallery wrapper and "Save Selection to … Gallery"
> footer are the repeated shape of work. The galleries themselves (the design thumbnails + the
> save-to-gallery side) are the Building-Blocks **engine gap**; the command behind each is
> usually present.

---

## Inventory

One subsection per Word ribbon group. `LO .uno:` is the mapped LibreOffice command (`—` = none).
`work` is the bucket from the table above. Rows touched by the LO-source corrections are marked
**✓ verified vs LO source** in the note.

### Pages (GroupInsertPages)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Pages group | GroupInsertPages | group | — | UI-only | Our-layer UI | Ribbon group container holding the page-level insert commands (Cover Page, Blank Page, Page Break). Leftmost group on the Insert tab. — **LO:** Group container, not a command. No `.uno` maps to a group. |
| Cover Page | CoverPageInsertGallery | gallery | `.uno:TitlePageDialog` | differs | Our-layer UI | Drop-down gallery of built-in formatted cover-page designs; selecting one inserts a fully formatted cover page (with title/author/date placeholder fields) at the start of the document. Menu also exposes Remove Current Cover Page, Save Selection to Cover Page Gallery, and (per S2) More Cover Pages from Office.com. — **LO:** Closest is Title Page (`.uno:TitlePageDialog`, "Title Page…"), a dialog that inserts N title pages with their own page style — not a thumbnail gallery of pre-formatted designs, no Office.com designs, no Remove/Save submenu. ✓ verified vs LO source. |
| Built-In cover page designs | _(none)_ | gallery items | — | LO-missing | Engine gap | The individual built-in cover-page design thumbnails inside the gallery. S3 enumerates the legacy set verbatim: Alphabet, Annual, Austere, Conservative, Contrast, Cubicles, Exposure, Mod, Motion, Pinstripes, Puzzle, Sideline, Stacks, Tiles, Transcend. — **LO:** LO has no built-in cover-page design gallery at all; no Building Blocks system. |
| Remove Current Cover Page | CoverPageRemove | button | — | LO-missing | Engine gap | Deletes the cover page currently inserted in the document. Acts immediately. — **LO:** No dedicated remove-cover-page command; tied to the absent Building-Blocks/cover-page feature. |
| Save Selection to Cover Page Gallery | SaveSelectionToCoverPageGallery | button | — | LO-missing | Engine gap | Saves the current selection as a reusable cover-page building block in the gallery. — **LO:** No Building Blocks system — cannot save a selection as a reusable cover page. (Inventory had this idMso nulled; the real Microsoft idMso is `SaveSelectionToCoverPageGallery` — see QA flags.) |
| Blank Page | BlankPageInsert | button | — | LO-missing | Optional our-layer feature | Inserts a blank page at the cursor (mechanically by adding a page break before and after the insertion point). Acts immediately, no dialog. — **LO:** No single command that inserts a whole blank page (break-before + break-after). LO has `.uno:InsertPagebreak` (one break); Word's Blank Page = two breaks, composable in our layer. |
| Page Break | PageBreakInsertWord | button | `.uno:InsertPagebreak` | same | Free | Inserts a hard page break at the cursor so following content starts on the next page (shortcut Ctrl+Enter). Acts immediately, no dialog. — **LO:** Direct equivalent: "Page Break", tooltip "Insert Page Break", same Ctrl+Enter. Behaviour matches. ✓ verified vs LO source. |
| Pages (collapsed menu) | PagesMenuAnchor | menu | — | UI-only | Our-layer UI | Collapsed dropdown anchor shown when the group is rendered narrow; re-exposes Cover Page / Blank Page / Page Break. — **LO:** Ribbon narrow-state collapse anchor; no command. |

### Tables (GroupInsertTables)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Tables group | GroupInsertTables | group | — | UI-only | Our-layer UI | Ribbon group container for the Table command. — **LO:** Group container. |
| Table | TableInsertGallery | gallery | `.uno:InsertTable` | differs | Our-layer UI | Drop-down whose top is an interactive grid (drag up to ~10x8) inserting a table of the highlighted size; below it are Insert Table, Draw Table, Convert Text to Table, Excel Spreadsheet, and Quick Tables. — **LO:** `.uno:InsertTable` is the entry point but opens the Insert Table dialog directly, not an interactive drag-grid with a submenu (Draw Table / Convert Text / Excel Spreadsheet / Quick Tables not bundled). ✓ verified vs LO source. |
| Insert Table… | TableInsertDialogWord | button | `.uno:InsertTable` | same | Free | Opens the Insert Table dialog to specify exact column/row counts and AutoFit behavior. — **LO:** Exactly what `.uno:InsertTable` does: dialog to set columns/rows (+ named table styles, AutoFit-equivalent). ✓ verified vs LO source. |
| Draw Table | TableDrawTable | toggleButton | — | LO-missing | Engine gap | Turns the pointer into a pencil to draw table borders/cells by hand; toggles draw-table mode. — **LO:** Writer has no freehand "draw table with a pencil" mode. No `.uno`. |
| Convert Text to Table… | ConvertTextToTable | button | `.uno:ConvertTextToTable` | same | Free | Converts selected delimited text into a table via a dialog. — **LO:** Table > Convert > Text to Table (`.uno:ConvertTextToTable`); same capability, lives under the Table menu. ✓ verified vs LO source. |
| Excel Spreadsheet | TableExcelSpreadsheetInsert | button | `.uno:InsertObject` | differs | Behavior shim | Inserts/embeds a live Microsoft Excel worksheet object in the document. — **LO:** No "embed an Excel sheet" command; embed a LibreOffice **Calc** OLE object via the OLE Object dialog. Embeds a Calc sheet (not Excel), no one-click button. loUno corrected from `.uno:InsertObjectStarMath` → `.uno:InsertObject`. ✓ verified vs LO source. |
| Quick Tables | QuickTablesInsertGallery | gallery | — | LO-missing | Engine gap | Submenu/gallery of pre-formatted table building blocks (e.g. calendars, tabular lists); also exposes Save Selection to Quick Tables Gallery. — **LO:** No building-block gallery of pre-formatted tables; LO has post-creation AutoFormat styles only. |
| Save Selection to Quick Tables Gallery | SaveSelectionToQuickTablesGallery | button | — | LO-missing | Engine gap | Saves the current selection as a reusable Quick Tables building block. — **LO:** No Building Blocks system. |

### Illustrations (GroupInsertIllustrations)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Illustrations group | GroupInsertIllustrations | group | — | UI-only | Our-layer UI | Ribbon group container for Pictures, Shapes, Icons, 3D Models, SmartArt, Chart, and Screenshot. — **LO:** Group container. |
| Pictures | FlyoutAnchorInsertPictures | gallery / flyout | `.uno:InsertGraphic` | differs | Our-layer UI | Flyout/menu offering picture sources: This Device, Stock Images (M365), Online Pictures (Bing), and (S1) Mobile/Phone. In Word 2007/2010 this was a single Picture button opening the file dialog directly (S3). — **LO:** `.uno:InsertGraphic` ("Image…") opens a file picker directly — a single button, **not** a This Device / Stock / Online / Mobile flyout. ✓ verified vs LO source. |
| Pictures (collapsed menu) | InsertPictureFlyoutAnchor | menu | — | UI-only | Our-layer UI | Alternate/collapsed menu form re-exposing This Device + Online Pictures when the group is narrow. — **LO:** Ribbon narrow-state collapse anchor; no command. |
| Picture from File (This Device) | PictureInsertFromFile | button | `.uno:InsertGraphic` | same | Free | Inserts a picture from a local/network file. — **LO:** Equivalent to `.uno:InsertGraphic`: inserts a picture from a local/network file (LO adds a Link checkbox). |
| Picture from Mobile | InsertMobilePicture | button | — | LO-missing | Cut | Inserts a picture from a linked mobile/phone device. — **LO:** No linked-mobile-device picture source in LO (sign-in/cloud feature). |
| Stock / M365 Pictures (Stock Images) | InsertM365Picture | button | — | LO-missing | Cut | Inserts royalty-free M365 stock pictures, icons, illustrations, cutouts, etc. from Microsoft's library. — **LO:** No Microsoft stock-content library integration; LO's bundled Gallery is local themed media, not M365 royalty-free stock. |
| Online Pictures | ClipArtInsertDialog | button | — | LO-missing | Engine gap | Searches and inserts web/Bing images (and clip art). Replaced the Word 2007/2010 Clip Art control (S3). — **LO:** No Bing/web image search-and-insert; bundled Gallery is local-only. |
| Clip Art (legacy) | ClipArtInsert | button (2007/2010) | `.uno:Gallery` | differs | Our-layer UI | Legacy Word 2007/2010 control that opened the Clip Art task pane; replaced by Online Pictures in later versions. — **LO:** Loosely paralleled by LO's Gallery (`.uno:Gallery`, "Open Clip Art and Media Gallery") — a dockable pane of local themed clip media, drag-based, not a searchable task pane. ✓ verified vs LO source. (Off-ribbon in modern Word — see QA flags.) |
| Shapes | GalleryAllShapesAndCanvas | gallery | `.uno:BasicShapes` | differs | Our-layer UI | Gallery of drawing shapes grouped into categories; after picking a shape the cursor becomes a crosshair to drag it onto the page. Also exposes New Drawing Canvas. — **LO:** LO has no unified Shapes gallery; shapes split across per-category commands (`.uno:BasicShapes`, `.uno:ArrowShapes`, `.uno:StarShapes`, `.uno:CalloutShapes`, `.uno:FlowChartShapes`, `.uno:SymbolShapes`). loUno is the Basic-Shapes representative. ✓ verified vs LO source. |
| Shapes categories | _(none)_ | gallery sections | — | differs | Our-layer UI | Category groupings inside the Shapes gallery. S2/S3 enumerate: Recently Used Shapes, Lines, Rectangles, Basic Shapes, Block Arrows, (S2 adds Equation Shapes), Flowchart, Stars and Banners, Callouts. — **LO:** Word's categories are sections of one gallery; in LO each category **is** a separate top-level command. No "Recently Used" / "Equation Shapes" category. ✓ verified vs LO source. |
| New Drawing Canvas | DrawingCanvasInsert | button | — | LO-missing | Engine gap | Inserts a new drawing canvas (a frame for grouping shapes). Exposed under the Shapes gallery. — **LO:** Writer has no drawing-canvas frame concept; shapes anchor directly. |
| Icons | IconInsertFromFile | button | — | LO-missing | Engine gap | Opens the Microsoft stock-content/icon picker to browse or search categorized scalable SVG icons; selected icons insert as editable graphics. Added in Word 2016/365. — **LO:** No scalable-SVG stock-icon picker / searchable icon library (you can insert a raw SVG via `.uno:InsertGraphic`, but no library). |
| 3D Models | Insert3DModelDropdown | splitButton | — | LO-missing | Engine gap | Split button: default action inserts a 3D model; dropdown offers From a File (This Device) and Online/Stock sources, with commercial vs consumer variants. Inserted models can be rotated/tilted in 3D. Added in Word 2016/365. — **LO:** Writer cannot insert/manipulate glTF/3D-model objects. |
| 3D Models (default button / fallback) | Insert3DModelFallback | button | — | LO-missing | Engine gap | Fallback single-button form of 3D Models used when the split button is not rendered. — **LO:** Same — no 3D-model support in Writer. |
| 3D Models default action | Insert3DModelDefault | button | — | LO-missing | Engine gap | Primary/default action invoked by clicking the main body of the 3D Models split button. — **LO:** No 3D-model support. |
| This Device (3D Model from File) | Insert3DModelFromFile | button | — | LO-missing | Engine gap | Inserts a 3D model from a local file (commercial SKU). — **LO:** No 3D-model-from-file insert. |
| This Device (3D Model from File, consumer) | Insert3DModelFromFileConsumer | button | — | LO-missing | Engine gap | Consumer-SKU variant of inserting a 3D model from a local file. — **LO:** No 3D-model support; no SKU variants. |
| Stock 3D Models (Online) | Insert3DModelFromOnline | button | — | LO-missing | Cut | Inserts a 3D model from Microsoft's online stock library (commercial SKU). — **LO:** No online 3D-model library (cloud service). |
| Stock 3D Models (Online, consumer) | Insert3DModelFromOnlineConsumer | button | — | LO-missing | Cut | Consumer-SKU variant of inserting a 3D model from the online stock library. — **LO:** No online 3D-model library; no SKU variants. |
| SmartArt | SmartArtInsert | button | — | LO-missing | Engine gap | Opens the Choose a SmartArt Graphic dialog (List, Process, Cycle, Hierarchy, Relationship, Matrix, Pyramid, Picture); choosing a layout inserts an editable diagram with a text-entry pane. — **LO:** No SmartArt/diagram-builder; can render imported OOXML SmartArt as static shapes but offers no editable diagram layouts. |
| Chart | ChartInsert | button | `.uno:InsertObjectChart` | differs | Our-layer UI | Opens the Insert Chart dialog to pick a chart type (column, line, pie, bar, etc.); inserting a chart opens an embedded Excel-style datasheet for editing the source data. — **LO:** `.uno:InsertObjectChart` inserts an embedded LO Chart object with its own chart-edit mode + Chart Type dialog; no Excel-style datasheet, different type picker and data editor. ✓ verified vs LO source. |
| Screenshot | ScreenshotInsertGallery | gallery | — | LO-missing | Engine gap | Drop-down showing thumbnails of currently open (non-minimized) windows; clicking one inserts that window's screenshot. Also exposes Screen Clipping. — **LO:** No built-in screenshot/available-windows capture in Writer. |
| Available Windows / Available Screenshots | _(none)_ | gallery items | — | LO-missing | Engine gap | Thumbnails of currently open windows inside the Screenshot gallery; clicking one inserts a screenshot of that window. — **LO:** No screenshot feature, so no window-thumbnail items. |
| Screen Clipping | ScreenClipping | button | — | LO-missing | Engine gap | Dims the screen and lets you drag a rectangle to capture and insert any region. — **LO:** No screen-clipping capture mode in LO. |

### Media (GroupMedia)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Media group | GroupMedia | group | — | UI-only | Our-layer UI | Ribbon group container for Online Video. A region/SKU-conditional group reflecting modern builds; in some layouts Online Video also appears under Illustrations. — **LO:** Group container. |
| Online Video | MovieFromClipOrganizerInsert | button | `.uno:InsertAVMedia` | differs | Behavior shim | Opens the Insert Video dialog where you paste a video URL (e.g. YouTube) or embed code; Word inserts a thumbnail/poster that streams inline when clicked (requires internet). Grayed out in Compatibility Mode. — **LO:** `.uno:InsertAVMedia` (Label "Media") inserts a media **file** (or downloads a URL), **not** a streaming-poster embed from a YouTube URL/embed-code. No inline web-video player object. ✓ verified vs LO source. |

### Reuse Files

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Reuse Files | ReuseFilesForLink | button | `.uno:InsertDoc` | differs | Our-layer UI | Opens the Reuse Files search task pane to find recent/cloud documents and insert content (text, tables, images) from another file. A Microsoft 365 / cloud-only feature that may be absent in some builds. — **LO:** Insert > Text from File (`.uno:InsertDoc`, "Content from Document…"): inserts the entire contents of another document at the cursor. Local-file only — no cloud/recent task pane, no search, no selective extraction. ✓ verified vs LO source. |

### Links (GroupInsertLinks)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Links group | GroupInsertLinks | group | — | UI-only | Our-layer UI | Ribbon group container for Link, Bookmark, and Cross-reference. — **LO:** Group container. |
| Link | InsertLinkGallery | gallery / split-button | `.uno:HyperlinkDialog` | differs | Our-layer UI | Modern Link control: a gallery/menu offering Insert Link (opens the Insert Hyperlink dialog, Ctrl+K), Recent Items, and Reuse Files. In older versions this was a single Hyperlink button. — **LO:** LO has only the classic single Hyperlink command; no modern Link gallery/menu with Recent Items or Reuse Files. |
| Recent Items | _(none)_ | menu items | — | LO-missing | Optional our-layer feature | Quick list of recently used link targets for one-click insertion. — **LO:** No recent-link-targets quick list; app-state we could maintain. |
| Search for Files | _(none)_ | menu command | — | LO-missing | Optional our-layer feature | Searches for a file to link to. — **LO:** No "search for a file to link to" submenu; LO's Hyperlink dialog has a Document tab with manual browse instead. |
| Insert Link… | HyperlinkInsert | button | `.uno:HyperlinkDialog` | same | Free | Opens the full Insert Hyperlink dialog to configure the link target and display text. — **LO:** `.uno:HyperlinkDialog` ("Hyperlink…", "Insert Hyperlink", Ctrl+K): full dialog to configure target + display text. ✓ verified vs LO source. |
| Link / Hyperlink (classic) | HyperlinkInsert | button | `.uno:HyperlinkDialog` | same | Free | Classic Insert Hyperlink button (Ctrl+K) linking selected text/object to a web page, file, email, place in document, or new document. — **LO:** Direct match: Internet/Mail/Document/New-Document tabs ≈ Word's web/email/place-in-doc/new-doc targets. Ctrl+K in both. ✓ verified vs LO source. |
| Reuse Files (for link) | ReuseFilesForLink | button | `.uno:InsertDoc` | differs | Our-layer UI | Reuse Files command surfaced under the Link gallery. — **LO:** Same surface as the Reuse Files group; LO's nearest is `.uno:InsertDoc` (Text from File), which inserts content rather than offering a cloud link picker. |
| Bookmark | BookmarkInsert | button | `.uno:InsertBookmark` | same | Free | Opens the Bookmark dialog to name and create an invisible anchor at the cursor/selection that hyperlinks and cross-references can jump to. — **LO:** Direct equivalent: "Bookmark…", "Insert Bookmark" — dialog to name/create an anchor. ✓ verified vs LO source. |
| Cross-reference | CrossReferenceInsert | button | `.uno:InsertReferenceField` | differs | Our-layer UI | Opens the Cross-reference dialog to insert a field referencing another item (heading, figure/table caption, numbered item, bookmark, footnote); updates automatically as numbering/pages change. — **LO:** `.uno:InsertReferenceField` opens the Fields dialog's Cross-references tab (headings, numbered items, bookmarks, captions, foot/endnotes). LO references its own caption sequences rather than Word caption labels; format options differ. ✓ verified vs LO source. |

### Comments (GroupInsertComments)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Comments group | GroupInsertComments | group | — | UI-only | Our-layer UI | Ribbon group container for the Comment command. — **LO:** Group container. |
| Comment | InsertNewComment | button | `.uno:InsertAnnotation` | same | Free | Inserts a new comment anchored to the current selection and opens the comment card/pane in the margin for typing a remark. Acts immediately (no modal dialog). — **LO:** Direct equivalent: "Comment", "Insert Comment", Ctrl+Alt+C — anchors a comment to the selection (LO shows margin notes vs Word's docked pane, same action). ✓ verified vs LO source. |

### Header & Footer (GroupHeaderFooter)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Header & Footer group | GroupHeaderFooter | group | — | UI-only | Our-layer UI | Ribbon group container for Header, Footer, and Page Number. — **LO:** Group container. |
| Header | HeaderInsertGallery | gallery | `.uno:InsertPageHeader` | differs | Our-layer UI | Gallery of built-in header building blocks; selecting one enters header edit mode and inserts the design. Also exposes Edit Header, Remove Header, Save Selection to Header Gallery (and per S2, More Headers from Office.com). — **LO:** `.uno:InsertPageHeader` is a **per-page-style toggle** that turns the header region on/off and moves the cursor in — no design-gallery, no Save-to-gallery, no Office.com designs. ✓ verified vs LO source. |
| Edit Header | HeaderFooterEditHeader | button | `.uno:InsertPageHeader` | differs | Our-layer UI | Moves the cursor into the header area for editing. — **LO:** No distinct "edit header" command; clicking into the header area (or the toggle) is how you edit. ✓ verified vs LO source. |
| Remove Header | HeaderFooterRemoveHeaderWord | button | `.uno:InsertPageHeader` | differs | Our-layer UI | Deletes the current header. Acts immediately. — **LO:** Removal is the OFF state of the same toggle (`On=false` prompts to delete content). ✓ verified vs LO source. |
| Save Selection to Header Gallery | SaveSelectionToHeaderGallery | button | — | LO-missing | Engine gap | Saves the current selection as a reusable header building block. — **LO:** No Building Blocks system — cannot save a header design to a gallery. |
| Footer | FooterInsertGallery | gallery | `.uno:InsertPageFooter` | differs | Our-layer UI | Gallery of built-in footer building blocks; selecting one enters footer edit mode and inserts the design. Also exposes Edit Footer, Remove Footer, Save Selection to Footer Gallery. — **LO:** Per-page-style toggle that enables the footer region; no footer building-block gallery, no Save-to-gallery. Same model as Header. ✓ verified vs LO source. |
| Edit Footer | HeaderFooterEditFooter | button | `.uno:InsertPageFooter` | differs | Our-layer UI | Moves the cursor into the footer area for editing. — **LO:** No separate edit-footer command; the toggle + clicking the footer area is how editing happens. ✓ verified vs LO source. |
| Remove Footer | HeaderFooterRemoveFooterWord | button | `.uno:InsertPageFooter` | differs | Our-layer UI | Deletes the current footer. Acts immediately. — **LO:** Removal is the OFF state of the toggle; no dedicated remove command. ✓ verified vs LO source. |
| Save Selection to Footer Gallery | SaveSelectionToFooterGallery | button | — | LO-missing | Engine gap | Saves the current selection as a reusable footer building block. — **LO:** No Building Blocks system. |
| Header & Footer (collapsed menu) | HeaderAndFooterMenuAnchor | menu | — | UI-only | Our-layer UI | Collapsed dropdown anchor re-exposing the Header and Footer galleries when the group is narrow. — **LO:** Ribbon narrow-state collapse anchor; no command. |
| Page Number | HeaderFooterPageNumberInsert | menu | `.uno:PageNumberWizard` | differs | Our-layer UI | Menu with placement submenus (Top of Page, Bottom of Page, Page Margins, Current Position), each a gallery of numbering designs; plus Format Page Numbers and Remove Page Numbers. — **LO:** **Corrected:** LO ships a Page Number Wizard (`.uno:PageNumberWizard`, "Page Number…", FN_PGNUMBER_WIZARD) whose dialog offers Position (top/bottom), Alignment, mirror-on-even-pages, include-page-total, number format, fit-into-margins and a live preview, **auto-placing** the field into the header/footer. Still not a thumbnail design gallery, but the earlier "no placement menu / no auto-placement" claim is wrong. ✓ verified vs LO source. |
| Top of Page (page number gallery) | PageNumbersInHeaderInsertGallery | gallery | `.uno:PageNumberWizard` | differs | Our-layer UI | Gallery of page-number designs placed in the header. — **LO:** **Corrected:** the top-of-page placement intent is covered by `.uno:PageNumberWizard` (Position=top, auto-placed into the header); only the design-thumbnail gallery is absent. ✓ verified vs LO source. |
| Save Selection (Top of Page page number) | SaveSelectionToPageNumberTop | button | — | LO-missing | Engine gap | Saves the selection as a reusable top-of-page page-number building block. — **LO:** No Building Blocks system. |
| Bottom of Page (page number gallery) | PageNambersInFooterInsertGallery | gallery | `.uno:PageNumberWizard` | differs | Our-layer UI | Gallery of page-number designs placed in the footer. — **LO:** **Corrected:** bottom-of-page placement covered by `.uno:PageNumberWizard` (Position=bottom, auto-placed into the footer); design gallery absent. ✓ verified vs LO source. |
| Save Selection (Bottom of Page page number) | SaveSelectionToPageNumberBottom | button | — | LO-missing | Engine gap | Saves the selection as a reusable bottom-of-page page-number building block. — **LO:** No Building Blocks system. |
| Page Margins (page number gallery) | PageNambersInMarginsInsertGallery | gallery | — | LO-missing | Engine gap (revisit) | Gallery of page-number designs placed in the page margins. — **LO:** The wizard covers top/bottom but **not margin-placement** page numbers; LO cannot place page numbers in the side margin. |
| Save Selection (Page Margins page number) | SaveSelectionToPageNumberMargin | button | — | LO-missing | Engine gap | Saves the selection as a reusable page-margins page-number building block. — **LO:** No Building Blocks system. |
| Current Position (page number field gallery) | PageNumberFieldInsertGallery | gallery | `.uno:InsertPageNumberField` | differs | Our-layer UI | Inserts a page-number field at the current cursor position. — **LO:** The bare "insert a page-number field at the cursor" intent = `.uno:InsertPageNumberField` ("Page Number Field"); LO inserts a single plain field with no design-thumbnail gallery. ✓ verified vs LO source. |
| Save Selection to Page Number Gallery | SaveSelectionToPageNumberGallery | button | — | LO-missing | Engine gap | Saves the selection as a reusable page-number building block. — **LO:** No Building Blocks system. |
| Format Page Numbers… | PageNumberFormat | button | — | differs | Our-layer UI | Opens the Page Number Format dialog to set number style, chapter inclusion, and starting value. — **LO:** No dedicated command; number style/start value live in the Page Style dialog (Page tab + paragraph offset), not a Page-Number submenu. Capability exists, reached via page-style settings. |
| Remove Page Numbers | PageNumbersRemove | button | — | LO-missing | Optional our-layer feature | Removes page numbers from the document. — **LO:** No one-click remove-all-page-numbers command; delete the field(s) manually. App-state we could build. |

### Text (GroupInsertText)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Text group | GroupInsertText | group | — | UI-only | Our-layer UI | Ribbon group container for Text Box, Quick Parts, WordArt, Drop Cap, Signature Line, Date & Time, Object, and East-Asian greeting commands. — **LO:** Group container. |
| Greeting (Japanese) menu | JapaneseGreetingsInsertMenu | menu | — | LO-missing | Cut | Japanese greeting insert menu present in East Asian builds. — **LO:** East-Asian-only Word feature; no LO equivalent. (Conditional — East-Asian build.) |
| Insert Greeting (Japanese) | MailMergeJapaneseGreetingInsert | button | — | LO-missing | Cut | Inserts a Japanese greeting phrase. — **LO:** No Japanese-greeting command in LO. (Conditional.) |
| Insert Opening Sentence (Japanese) | MailMergeJapaneseGreetingJapaneseOpeningSentenceInsert | button | — | LO-missing | Cut | Inserts a Japanese opening sentence. — **LO:** No Japanese-greeting command. (Conditional.) |
| Insert Closing Sentence (Japanese) | MailMergeJapaneseGreetingClosingSentenceInsert | button | — | LO-missing | Cut | Inserts a Japanese closing sentence. — **LO:** No Japanese-greeting command. (Conditional.) |
| Text Box | TextBoxInsertGallery | gallery | `.uno:DrawText` | differs | Our-layer UI | Gallery of pre-formatted text-box building blocks (sidebars, pull quotes); selecting one inserts a positioned, editable text box. Also exposes Draw Text Box, Draw Vertical Text Box, Save Selection to Text Box Gallery (and per S2, More Text Boxes from Office.com). — **LO:** `.uno:DrawText` ("Text Box", "Insert Text Box") drops into draw-a-text-box mode; no gallery of pre-formatted sidebars/pull-quotes, no Save-to-gallery. ✓ verified vs LO source. |
| Built-In text box designs | _(none)_ | gallery items | — | LO-missing | Engine gap | The pre-formatted text-box / pull-quote / sidebar design thumbnails inside the gallery. — **LO:** No pre-formatted text-box design gallery in LO. |
| Draw Text Box | TextBoxInsert | button | `.uno:DrawText` | same | Free | Lets you drag to draw a custom blank text box. — **LO:** Direct match: drag to draw a blank text box. ✓ verified vs LO source. |
| Draw Vertical Text Box | TextBoxInsertVerticalWord | button | `.uno:VerticalText` | differs | Our-layer UI | Draws a text box with vertical text orientation. — **LO:** `.uno:VerticalText` exists but is gated by Asian/CJK vertical-text support and lives on the drawing toolbar, not as a sibling of the Insert Text Box command. (Conditional — CJK.) ✓ verified vs LO source. |
| Save Selection to Text Box Gallery | SaveSelectionToTextBoxGallery | button | — | LO-missing | Engine gap | Saves the selected text box as a reusable building block. — **LO:** No Building Blocks system. |
| Quick Parts | QuickPartsInsertGallery | gallery | `.uno:EditGlossary` | differs | Our-layer UI | Menu/gallery for reusable content; exposes AutoText, Document Property, Field, Building Blocks Organizer, and Save Selection to Quick Part Gallery. — **LO:** No unified Quick Parts menu; LO's reusable-content feature is AutoText (`.uno:EditGlossary`). No Document Property / Building Blocks Organizer / Save-to-Quick-Part bundle. |
| AutoText | AutoTextGallery | gallery | `.uno:EditGlossary` | differs | Our-layer UI | Stores and inserts reusable AutoText snippets. — **LO:** `.uno:EditGlossary` ("AutoText…", Ctrl+F3 to define / F3 to expand via `.uno:ExpandGlossary`) — dialog-driven glossary, not a thumbnail gallery. ✓ verified vs LO source. |
| Save Selection to AutoText Gallery | SaveSelectionToAutoTextGallery | button | `.uno:EditGlossary` | differs | Our-layer UI | Saves the selection as a reusable AutoText building block. — **LO:** Saving an AutoText entry is done inside the `.uno:EditGlossary` dialog (or Ctrl+F3); no standalone save-selection command. ✓ verified vs LO source. |
| Document Property | PropertyInsert | gallery / submenu | `.uno:InsertFieldCtrl` | differs | Our-layer UI (revisit) | Inserts a document property field (Author, Title, Company, etc.). — **LO:** No dedicated Document Property gallery; properties inserted as fields via the Fields dialog (`.uno:InsertFieldCtrl`, DocInformation tab). They are display fields, not Word content controls. *(LO-verify: command-level mapping reasonable; the "DocInformation tab" routing is UNCERTAIN from `.xcu`/`.sdi` alone.)* |
| Field… | FieldInsert | button | `.uno:InsertFieldCtrl` | differs | Behavior shim | Opens the Field dialog to insert a Word field code for dynamic content. — **LO:** `.uno:InsertFieldCtrl` opens LO's Fields dialog and inserts **LO field types**, not Word field codes — codes are not interchangeable. Different field model → dispatch-layer translation needed. ✓ verified vs LO source. |
| Building Blocks Organizer… | BuildingBlocksOrganizer | button | — | LO-missing | Engine gap | Browses, edits, and inserts all defined building blocks. — **LO:** No Building Blocks system, hence no organizer (the AutoText dialog manages AutoText only). |
| Save Selection to Quick Part Gallery | SaveSelectionToQuickPartGallery | button | — | LO-missing | Engine gap | Saves the selection as a reusable Quick Part building block. — **LO:** No Quick Parts/Building Blocks gallery to save into (AutoText aside). |
| WordArt | WordArtInsertGallery | gallery | `.uno:FontworkGalleryFloater` | differs | Our-layer UI | Gallery of WordArt text styles; choosing one inserts a stylized, editable decorative text object ('Your text here') formattable with text effects. — **LO:** `.uno:FontworkGalleryFloater` ("Insert Fontwork") opens the Fontwork gallery of stylized-text presets — LO's genuine WordArt analog. Style/effect library differs and editing uses the Fontwork toolbar. ✓ verified vs LO source. |
| WordArt (Classic) | WordArtInsertGalleryClassic | gallery | `.uno:FontworkGalleryFloater` | differs | Our-layer UI | Classic WordArt style gallery variant (legacy style set). — **LO:** LO has only the one Fontwork gallery; no separate classic vs modern WordArt style sets. ✓ verified vs LO source. |
| Drop Cap | DropCapInsertGallery | gallery / menu | `.uno:FormatDropcap` | differs | Our-layer UI | Menu/gallery with None, Dropped, and In-margin options applying a large initial capital to the current paragraph; also exposes Drop Cap Options. Requires character(s) selected (S3). — **LO:** LO has drop caps as a paragraph-format dialog (`.uno:FormatDropcap`, Format > Paragraph > Drop Caps tab), not an Insert-tab None/Dropped/In-margin menu. No "In Margin" placement. ✓ verified vs LO source. |
| Drop Cap: None | _(none)_ | menu command | `.uno:FormatDropcap` | differs | Our-layer UI | Removes drop-cap formatting. Acts immediately. — **LO:** No discrete "None"; clear the setting in the dialog. ✓ verified vs LO source. |
| Drop Cap: Dropped | _(none)_ | menu command | `.uno:FormatDropcap` | differs | Our-layer UI | Drops the capital inside the text margin. Acts immediately. — **LO:** No one-click "Dropped" preset; configured via the dialog (in-text dropped is the only mode LO supports). ✓ verified vs LO source. |
| Drop Cap: In Margin | _(none)_ | menu command | — | LO-missing | Engine gap | Places the dropped capital out in the page margin. Acts immediately. — **LO:** LO drop caps cannot be placed in the page margin — only in-text. ✓ verified vs LO source. |
| Drop Cap Options… | DropCapOptionsDialog | button | `.uno:FormatDropcap` | same | Free | Configures font, lines to drop, and distance from text. — **LO:** This is exactly what LO offers: the Drop Caps options dialog (whole word, char count, lines, space to text). ✓ verified vs LO source. |
| Signature Line | SignatureLineInsertMenu | splitButton | `.uno:InsertSignatureLine` | differs | Our-layer UI | Split button: default action inserts a Microsoft Office signature line (specifying who must sign); dropdown also offers Add Signature Services. — **LO:** `.uno:InsertSignatureLine` ("Signature Line…") is a single command, not a split button; no "Add Signature Services" dropdown. ✓ verified vs LO source. |
| Microsoft Office Signature Line… | SignatureLineInsert | button | `.uno:InsertSignatureLine` | same | Free | Opens the Signature Setup dialog (signer name, title, email, instructions, allow comments, show sign date), then inserts a signature line object that can later be digitally signed. — **LO:** Direct equivalent: Signature Line setup dialog (signer name/title/email/instructions/date) then inserts a signable graphic. (LO also has `.uno:EditSignatureLine`.) ✓ verified vs LO source. |
| Add Signature Services | SignatureServicesAdd | button | — | LO-missing | Cut | Opens info about / adds third-party signature services. — **LO:** No third-party signature-services marketplace hook in LO. |
| Date & Time | DateAndTimeInsert | button | `.uno:InsertDateField` | differs | Our-layer UI | Opens the Date and Time dialog to choose a date/time format and language, optionally inserting it as an auto-updating field. — **LO:** Word opens one Date and Time dialog; LO splits into `.uno:InsertDateField` ("Date (fixed)") + `.uno:InsertTimeField` ("Time (fixed)") (+ variable variants), each inserting a field directly with no combined format dialog. Compose into one host. ✓ verified vs LO source. |
| Object | OleObjectInsertMenu | splitButton | `.uno:InsertObject` | differs | Our-layer UI | Split button: default action opens the Object dialog to embed/link an OLE object (Excel worksheet, PDF, equation, etc.); dropdown adds Text from File. — **LO:** `.uno:InsertObject` ("Insert OLE Object") is a single command, not a split button with a "Text from File" dropdown. ✓ verified vs LO source. |
| Object… | OleObjectctInsert | button | `.uno:InsertObject` | same | Free | Inserts an embedded or linked OLE object (new or from file). — **LO:** Direct equivalent: dialog to embed/link an OLE object (Calc sheet, Math, Chart, "Further objects"/from file). Object-type list differs (LO components vs Windows OLE servers). ✓ verified vs LO source. |
| Text from File… | TextFromFileInsert | button | `.uno:InsertDoc` | same | Free | Inserts the text/contents of another file into the document. — **LO:** `.uno:InsertDoc` ("Content from Document…") inserts the full contents of another document at the cursor (LO lacks Word's optional bookmark-range insert). |

### Symbols (GroupInsertSymbols)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Symbols group | GroupInsertSymbols | group | — | UI-only | Our-layer UI | Ribbon group container for Equation and Symbol (and, in East Asian builds, Number). — **LO:** Group container. |
| Equation | InsertBuildingBlocksEquationsGallery | gallery / split-button | `.uno:InsertObjectStarMath` | differs | Our-layer UI | Built-in equations gallery; default action inserts a new equation placeholder and surfaces the Equation Tools / Design tab. Also exposes Insert New Equation, Ink Equation, and Save Selection to Equation Gallery. — **LO:** `.uno:InsertObjectStarMath` ("Formula Object…") embeds a LibreOffice Math OLE object and opens the markup-based Math editor — no built-in equations gallery, no Ink Equation, no Save-to-gallery. Same end product, very different editor. ✓ verified vs LO source. |
| Built-In equations | _(none)_ | gallery items | — | LO-missing | Engine gap | The built-in equation thumbnails. S3 enumerates verbatim: Area of Circle, Binomial Theorem, Expansion of a Sum, Fourier Series, Pythagorean Theorem, Quadratic Formula. — **LO:** No built-in equation gallery (no Quadratic/Pythagorean presets); you type Math markup. |
| Insert New Equation | EquationInsertNew | button | `.uno:InsertObjectStarMath` | same | Free | Inserts an empty equation placeholder to type a new equation. — **LO:** Equivalent action: inserts a fresh empty Math formula object (different editor — Math markup). ✓ verified vs LO source. |
| Ink Equation | InkEquation | button | — | LO-missing | Engine gap | Lets you handwrite math which Word converts to a typeset equation. — **LO:** No handwriting-to-equation recognition in LO Math/Writer. |
| Save Selection to Equation Gallery | SaveSelectionToEquationGallery | button | — | LO-missing | Engine gap | Saves the selected equation as a reusable building block. — **LO:** No Building Blocks/equation gallery to save into. |
| Symbol | SymbolInsertGallery | gallery | `.uno:CharmapControl` | differs | Our-layer UI | Drop-down showing recently used / common symbols for one-click insertion; also exposes More Symbols. — **LO:** `.uno:CharmapControl` ("Symbol" / "Special Character…") opens a special-character picker; LO organizes by font/Unicode block and (classic UI) has no recently-used ribbon flyout. ✓ verified vs LO source. |
| Common symbols | _(none)_ | gallery items | — | differs | Our-layer UI | Recently-used / common symbol glyphs. S3 enumerates verbatim: Euro, Pound, Yen, Copyright, Registered, Trademark, Plus-Minus, Not Equal To, Less-Than or Equal To, Greater-Than or Equal To, Division, Multiplication, Infinity, Micro, Alpha, Beta, Pi, Ohm, Summation, Smiley Face. — **LO:** LO's dialog has Recently Used + Favorite rows (loosely Word's common-symbols grid) but no static curated Euro/Pound/Pi… preset list. ✓ verified vs LO source. |
| More Symbols… (Symbol dialog) | SymbolsDialog | button | `.uno:InsertSymbol` | same | Free | Opens the full Symbol dialog (Symbols and Special Characters tabs) to browse any font's glyphs, special characters, character codes, and assign shortcut keys. — **LO:** `.uno:InsertSymbol` / `.uno:CharmapControl` opens the full Special Character dialog (browse by Unicode block, search by name, favorites). No assign-shortcut-from-here (set in Tools > Customize). ✓ verified vs LO source. |
| Number | InsertNumberAlternate | button | — | LO-missing | Cut | Inserts a number; present in East Asian builds of the Symbols group. — **LO:** East-Asian-build-only Word command; no LO insert-number equivalent. (Conditional — East-Asian build.) |

### Collaborate (GroupCollaborate)

> Modern M365 Microsoft Loop group. **Expected-conditional / version-sensitive** — Loop is M365-only and unverified against a live build.

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Collaborate group | GroupCollaborate | group | — | LO-missing | Cut | Ribbon group container for Loop Components. A modern M365 addition not present in older Office 201x builds. — **LO:** LO has no Microsoft Loop integration at all. (Conditional — M365 Loop.) |
| Loop Components | LoopComponents | menu | — | LO-missing | Cut | Menu of insertable Microsoft Loop components (live, co-editable embedded blocks). — **LO:** No live co-editable Loop components. (Conditional.) |
| Bulleted List (Loop) | LoopBulletedList | button | — | LO-missing | Cut | Inserts a Loop bulleted-list component. — **LO:** No Loop support. (Conditional.) |
| Checklist (Loop) | LoopChecklist | button | — | LO-missing | Cut | Inserts a Loop checklist component. — **LO:** No Loop support. (Conditional.) |
| Numbered List (Loop) | LoopNumberedList | button | — | LO-missing | Cut | Inserts a Loop numbered-list component. — **LO:** No Loop support. (Conditional.) |
| Paragraph (Loop) | LoopParagraph | button | — | LO-missing | Cut | Inserts a Loop paragraph component. — **LO:** No Loop support. (Conditional.) |
| Table (Loop) | LoopTable | button | — | LO-missing | Cut | Inserts a Loop table component. — **LO:** No Loop support. (Conditional.) |
| Task List (Loop) | LoopTaskList | button | — | LO-missing | Cut | Inserts a Loop task-list component. — **LO:** No Loop support. (Conditional.) |
| Q&A (Loop) | LoopQA | button | — | LO-missing | Cut | Inserts a Loop Q&A component. — **LO:** No Loop support. (Conditional.) |

### Add-ins (GroupOfficeExtension)

> Modern M365 Office Add-ins (web add-in / Office.js) group. **Expected-conditional / version-sensitive** — depends on M365 / store availability and unverified against a live build.

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Add-ins group | GroupOfficeExtension | group | — | LO-missing | Cut | Ribbon group container for Get Add-ins / My Add-ins and featured add-in slots. A modern M365 addition; in narrow/some builds the two add-in commands collapse into a single Add-ins button. — **LO:** LO has OXT extensions (`.uno:AdditionsDialog`), a different model — no Insert-tab Office-Add-ins group. (Conditional.) ✓ verified vs LO source. |
| Get Add-ins / Store | OfficeExtensionsAppStore | button | — | LO-missing | Cut | Opens the Office Add-ins store to browse, search, and install add-ins. Renamed from 'Store' to 'Get Add-ins' in Word 2019 (S3). — **LO:** No Office Add-ins store; LO's Extension Manager is a different OXT ecosystem. (Conditional.) |
| My Add-ins | OfficeExtensionsGallery2 | gallery / split-button | — | LO-missing | Cut | Lists/launches installed/admin-deployed add-ins; dropdown shows recently used and a See All option, plus Manage Other Add-ins and experimentation. Selecting one loads its task pane or command. — **LO:** No installed-web-add-ins launcher. (Conditional.) |
| See All / Office Add-ins dialog | OfficeExtensionsDialog | button | — | LO-missing | Cut | Opens the full Office Add-ins dialog listing all available add-ins. — **LO:** No Office Add-ins dialog in LO. (Conditional.) |
| Manage Other Add-ins | OfficeExtensionsManageOtherAddins | button | — | LO-missing | Cut | Opens management for COM/other add-in types. — **LO:** No COM/other-add-in management surfaced here. (Conditional.) |
| Add-in Experimentation | ExtensibilityExperimentation | button | — | LO-missing | Cut | Toggles/manages add-in experimentation features. — **LO:** No add-in experimentation feature. (Conditional.) |
| Featured Add-in 1 | OfficeExtensionsFeaturedApp1 | button | — | LO-missing | Cut | Promoted/featured add-in slot in the Add-ins group. — **LO:** No promoted-add-in slots. (Conditional.) |
| Featured Add-in 2 | OfficeExtensionsFeaturedApp2 | button | — | LO-missing | Cut | Promoted/featured add-in slot in the Add-ins group. — **LO:** No promoted-add-in slots. (Conditional.) |
| Featured Add-in 3 | OfficeExtensionsFeaturedApp3 | button | — | LO-missing | Cut | Promoted/featured add-in slot in the Add-ins group. — **LO:** No promoted-add-in slots. (Conditional.) |
| Featured Add-in 4 | OfficeExtensionsFeaturedApp4 | button | — | LO-missing | Cut | Promoted/featured add-in slot in the Add-ins group. — **LO:** No promoted-add-in slots. (Conditional.) |
| Featured Add-in 5 | OfficeExtensionsFeaturedApp5 | button | — | LO-missing | Cut | Promoted/featured add-in slot in the Add-ins group. — **LO:** No promoted-add-in slots. (Conditional.) |
| Featured Add-in 6 | OfficeExtensionsFeaturedApp6 | button | — | LO-missing | Cut | Promoted/featured add-in slot in the Add-ins group. — **LO:** No promoted-add-in slots. (Conditional.) |
| Add-ins (collapsed menu) | AddInsMenuAnchor | menu | — | UI-only | Our-layer UI | Collapsed dropdown anchor re-exposing the store, My Add-ins, and featured apps when the group is narrow. — **LO:** Ribbon narrow-state collapse anchor; no command (and the add-ins feature itself is LO-missing). |

### Barcode (GroupInsertBarcode)

> China/region-specific Word group. **Expected-conditional / version-sensitive** — region-locked and unverified against a live build.

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Barcode group | GroupInsertBarcode | group | — | UI-only | Our-layer UI | Ribbon group container for Barcode and Document Label. A China/region-specific group. — **LO:** Region-specific group container; LO's barcode capability is a single command, not a group. (Conditional — region.) |
| Barcode | BarcodeInsert | button | `.uno:InsertQrCode` | differs | Our-layer UI | Inserts a barcode. — **LO:** LO does barcode insertion: `.uno:InsertQrCode` ("QR and Barcode…") opens a dialog to generate a QR/1D/2D barcode — not region-specific, available everywhere. (`.uno:EditQrCode` edits one; its label reads "Edit Barcode…".) ✓ verified vs LO source. |
| Document Label / Label | LabelInsert | button | — | LO-missing | Cut | Inserts a document label. — **LO:** No "document label" insert matching this China-specific command (File > New > Labels is a different mail-label feature). (Conditional — region.) |

---

## LO-source verification

These mappings were checked against the vendored LibreOffice tree at
`apps/libreoffice/libreoffice-codebase/` and **override** the mapped rows where they conflicted.
One is a **material correction** (Page Number); the rest **confirm** the mapped command, label,
tooltip, slot, and (where cited) shortcut. The single **UNCERTAIN** item (Document Property) is
noted but not treated as authoritative.

**Material correction (CORRECTED):**

- **Page Number group** — the mapping repeatedly asserted LO has "no page-number placement
  menu/gallery" and "no auto-placement into header/footer," mapping Page Number only to the
  bare-field command. In fact LO Writer ships a **Page Number Wizard**: `.uno:PageNumberWizard`
  ("Page Number…", tooltip "Insert page number", FN_PGNUMBER_WIZARD). Its dialog (SwPageNumberDlg)
  offers Position (top/bottom), Alignment (left/center/right), mirror-on-even-pages,
  include-page-total, number format, fit-into-existing-margins and a **live preview**, and
  **auto-inserts** the page number into the header/footer. The Top-of-Page / Bottom-of-Page /
  Position intent is therefore covered (verdicts softened LO-missing → differs); only the
  thumbnail design gallery and margin-placement remain absent, and the Save-Selection children
  stay LO-missing. Evidence: `GenericCommands.xcu:1216-1222`; `swriter.sdi:3623` (FN_PGNUMBER_WIZARD);
  `sw/source/ui/misc/pagenumberdlg.cxx:31-65`; `WriterCommands.xcu:1227-1235` (InsertPageNumberField).

**Confirmed (CONFIRMED) — command/label/tooltip (and cited shortcut) match the mapping:**

- **Page Break** — `.uno:InsertPagebreak`, "~Page Break", "Insert Page Break", RETURN_MOD1 (Ctrl+Enter). Evidence: `WriterCommands.xcu:850-856`; `Accelerators.xcu:2780-2784`; `swriter.sdi:3516`.
- **Cover Page / Title Page** — `.uno:TitlePageDialog`, "Title Page…" (FN_FORMAT_TITLEPAGE_DLG). (Prose "unstyled page" is imprecise — the dialog can apply a title-page page style — but loUno/verdict stand.) Evidence: `WriterCommands.xcu:1579-1586`; `swriter.sdi:5090`.
- **Table / Insert Table…** — `.uno:InsertTable`, "Table" / "Insert ~Table…"; slot takes Columns/Rows/AutoFormat. Evidence: `WriterCommands.xcu:869-878`; `swriter.sdi:3766-3767`.
- **Convert Text to Table…** — `.uno:ConvertTextToTable`, "~Text to Table…" (FN_CONVERT_TEXT_TO_TABLE), confirmed directly. Evidence: `WriterCommands.xcu:1855-1857`; `swriter.sdi:7694`.
- **Excel Spreadsheet** — correction to `.uno:InsertObject` ("Insert OLE Object", SID_INSERT_OBJECT) is right; the originally-listed `.uno:InsertObjectStarMath` is the Math embed, not a spreadsheet. Evidence: `GenericCommands.xcu:3695-3704`; `svx.sdi:5067`; `WriterCommands.xcu:1111-1116`.
- **Pictures / Picture from File** — `.uno:InsertGraphic`, "~Image…", PopupLabel "Insert Image…" (SID_INSERT_GRAPHIC). Evidence: `GenericCommands.xcu:4226-4232`; `svx.sdi:4946`.
- **Clip Art (legacy) / Gallery** — `.uno:Gallery`, "Gallery", tooltip "Open Clip Art and Media Gallery" (SID_GALLERY). Evidence: `GenericCommands.xcu:5970-5978`; `svx.sdi:3746`.
- **Shapes** — all six per-category commands exist as separate top-level nodes with per-shape children (e.g. `.uno:BasicShapes.rectangle`); no unified all-shapes gallery. Evidence: `GenericCommands.xcu:132/146/188/202/216/230` (+ per-shape children at :244+).
- **Chart** — `.uno:InsertObjectChart`, "~Chart…", tooltip "Insert Chart" (SID_INSERT_DIAGRAM). Evidence: `GenericCommands.xcu:3069-3075`; `svx.sdi:5086`.
- **Online Video / Media** — `.uno:InsertAVMedia`, Label "Media" / ContextLabel "Audio or ~Video…", tooltip "Insert Audio or Video" (SID_INSERT_AVMEDIA). (Mapping quoted the tooltip form as the name.) Evidence: `GenericCommands.xcu:7475-7483`; `sfx.sdi:5598`.
- **Reuse Files / Text from File** — `.uno:InsertDoc`, "Content from Document…". Evidence: `GenericCommands.xcu:3218-3221`.
- **Hyperlink (Link / Insert Link)** — `.uno:HyperlinkDialog`, "~Hyperlink…", "Insert Hyperlink", K_MOD1 (Ctrl+K) (SID_HYPERLINK_DIALOG). Evidence: `GenericCommands.xcu:4517-4523`; `Accelerators.xcu:93-97`; `sfx.sdi:2002`.
- **Bookmark** — `.uno:InsertBookmark`, "Bookmar~k…", "Insert Bookmark" (FN_INSERT_BOOKMARK). Evidence: `WriterCommands.xcu:595-601`; `swriter.sdi:2631`.
- **Cross-reference** — `.uno:InsertReferenceField`, "Cross-~reference…", tooltip "Insert Cross-reference" (FN_INSERT_REF_FIELD). Evidence: `WriterCommands.xcu:712-717`; `swriter.sdi:3658`.
- **Comment** — `.uno:InsertAnnotation`, "Comme~nt", "Insert Comment", C_MOD1_MOD2 (Ctrl+Alt+C) (FN_POSTIT). Evidence: `GenericCommands.xcu:2948-2956`; `Accelerators.xcu:66-69`; `swriter.sdi:2576`.
- **Header** — `.uno:InsertPageHeader`, "He~ader"; slot has PageStyle + On params, confirming the per-page-style toggle (On=false removes). Evidence: `WriterCommands.xcu:110-116`; `swriter.sdi:3587-3588`.
- **Footer** — `.uno:InsertPageFooter`, "Foote~r" (FN_INSERT_PAGEFOOTER); same toggle/per-page-style model as Header. Evidence: `WriterCommands.xcu:118-124`; `swriter.sdi:3569`.
- **Text Box / Draw Text Box** — `.uno:DrawText`, "~Text Box", "Insert Text Box" (SID_DRAW_TEXT). Evidence: `GenericCommands.xcu:4366-4371`; `svx.sdi:8749`.
- **Draw Vertical Text Box** — `.uno:VerticalText` (SID_DRAW_TEXT_VERTICAL), "Vertical Text", "Insert Vertical Text"; visibility gated by `SvtCJKOptions::IsVerticalTextEnabled()`. Evidence: `GenericCommands.xcu:3034-3040`; `svx.sdi:9161`; `svx/source/tbxctrls/verttexttbxctrl.cxx:103`.
- **AutoText** — `.uno:EditGlossary`, "AutoTe~xt…" (FN_GLOSSARY_DLG), F3_MOD1 (Ctrl+F3); expansion via `.uno:ExpandGlossary` on plain F3. Evidence: `WriterCommands.xcu:22-25`; `swriter.sdi:1058,1233`; `Accelerators.xcu:2445-2454`.
- **Field…** — `.uno:InsertFieldCtrl`, "Fiel~d", "Insert Field" (FN_INSERT_FIELD_CTRL). (A distinct `.uno:InsertField` = "~More Fields…" also exists; the dialog-entry choice is appropriate.) Evidence: `WriterCommands.xcu:1165-1170`; `swriter.sdi:3085`; `WriterCommands.xcu:677-679`.
- **WordArt / Fontwork** — `.uno:FontworkGalleryFloater`, "Insert Fontwork" / ContextLabel "Fontwork…", "Insert Fontwork Text" (SID_FONTWORK_GALLERY_FLOATER). Evidence: `GenericCommands.xcu:86-94`; `svx.sdi:10315`.
- **Drop Cap / Drop Cap Options** — `.uno:FormatDropcap`, "Drop Caps" (FN_FORMAT_DROPCAPS); the dialog page exposes only Whole word / Number / Lines / Space to text — **no margin/placement option**, confirming the "no In Margin" claim. Evidence: `WriterCommands.xcu:1603-1605`; `swriter.sdi:1431`; `sw/uiconfig/swriter/ui/dropcapspage.ui`.
- **Signature Line** — `.uno:InsertSignatureLine`, "Signat~ure Line…" (SID_INSERT_SIGNATURELINE); single command, not split-button (`.uno:EditSignatureLine`, `.uno:SignSignatureLine` also exist). Evidence: `GenericCommands.xcu:7864-7878`; `svx.sdi:13089`.
- **Date & Time** — split into `.uno:InsertDateField` ("~Date (fixed)") + `.uno:InsertTimeField` ("~Time (fixed)") (+ variable variants); no single combined Date&Time dialog command. Evidence: `WriterCommands.xcu:1176-1214`; `swriter.sdi:2999,3784`.
- **Object / Object…** — `.uno:InsertObject`, "Insert OLE Object" / "~OLE Object…", "Open dialog to insert OLE object" (SID_INSERT_OBJECT). Evidence: `GenericCommands.xcu:3695-3704`; `svx.sdi:5067`.
- **Equation / Insert New Equation** — `.uno:InsertObjectStarMath`, "~Formula Object…", "Insert Formula Object" (FN_INSERT_SMA). Evidence: `WriterCommands.xcu:1111-1116`; `swriter.sdi:3498`.
- **Symbol / More Symbols** — both exist: `.uno:InsertSymbol` ("Symbol" / "Special Character…", tooltip "Insert Special Character", SID_CHARMAP) and `.uno:CharmapControl` (tooltip "Insert Special Characters", SID_CHARMAP_CONTROL). Evidence: `GenericCommands.xcu:5547-5556,5561-5570`; `svx.sdi:5105`; `sfx.sdi:268`.
- **Barcode** — `.uno:InsertQrCode`, "QR and ~Barcode…" (SID_INSERT_QRCODE); `.uno:EditQrCode` exists with label "~Edit Barcode…" (command name is QrCode). Evidence: `GenericCommands.xcu:7888-7898`; `svx.sdi:13175`.
- **Extensions / Add-ins reference** — `.uno:AdditionsDialog`, "~Additions…" / "~Additional Extensions…", "Additional Extensions"; accurate reference, but the Add-ins-group LO-missing verdict stands (this is the OXT surface, not a web-add-ins store). Evidence: `GenericCommands.xcu:7904-7912`.

**Uncertain (UNCERTAIN) — not treated as authoritative:**

- **Document Property → `.uno:InsertFieldCtrl`** — reasonable at the command level (it is the only Fields-dialog entry command; there is no dedicated document-property command), but the specific "DocInformation tab" routing cannot be verified from `.xcu`/`.sdi` alone. Evidence: `WriterCommands.xcu:1165-1170`.

**Minor label-precision notes (verdicts unchanged):** `.uno:InsertAVMedia` Label is "Media" (verbose form is ContextLabel/tooltip); `.uno:EditQrCode` user-facing label is "Edit Barcode…"; `.uno:CharmapControl` tooltip is plural ("Insert Special Characters") vs `.uno:InsertSymbol` singular.

> **Scope caveat from the LO-verify pass.** The many "LO-missing" rows for genuinely MS-only
> features (Loop, 3D Models, SmartArt, Office Add-ins store, Screenshot, Ink Equation, Japanese
> greetings, mobile/stock/online pictures, all Building-Blocks galleries) were **not exhaustively
> re-verified** against the LO tree — no matching `.uno` nodes were found in targeted searches,
> and the absence claims are consistent with the catalog, but verification budget was spent on
> present-command facts and the suspect Page Number claim.

---

## Conditional / version-sensitive controls

There is **no owner screenshot for the Insert tab yet**, so the following are flagged
**expected-conditional, unverified against a live build** — a screenshot sweep would confirm
whether (and how) they surface. They are not contradicted by the inventory; they simply depend on
language/region/SKU/version state.

- **Collaborate group (Loop)** — entire group is modern M365-only (Microsoft Loop). Expected absent without an M365 Loop-enabled tenant.
- **Add-ins group (Office.js)** — depends on M365 + store availability; the Featured Add-in slots and store entry points are version/account-sensitive.
- **Barcode group** — China/region-specific; expected absent outside the relevant region build.
- **Japanese greetings** (Greeting menu + Insert Greeting / Opening / Closing Sentence) — East-Asian-build-only.
- **Number** (Symbols) — East-Asian-build-only insert-number command.
- **Draw Vertical Text Box** — surfaces only when Asian/CJK vertical-text support is enabled (LO side confirmed gated by `SvtCJKOptions::IsVerticalTextEnabled()`; the Word control is correspondingly CJK-conditional).
- **idMso version-sensitivity** — several idMsos are M365-Current-Channel values; the official set-diff also flagged **`ClipArtInsert`** as off-ribbon ("Not in the Ribbon") in 2013/2016/2019/M365 — present here as a legacy note, not a live modern Insert-tab control. A live screenshot would confirm it no longer appears.

---

## Out of scope

- **Engine gap — Building Blocks + rich-media objects (the true engine blockers, 33 controls).**
  Two clusters: (1) **Word's Building-Blocks / save-to-gallery system** — cover-page / text-box /
  equation / page-number **design galleries** and **every** "Save Selection to … Gallery" command,
  plus the Building Blocks Organizer; LO has no Building-Blocks subsystem at all. (2) **Modern
  rich-media objects** — SmartArt, Icons, 3D Models (local), Screenshot / Screen Clipping, web
  Online Pictures, the drawing canvas, Ink Equation, and drop-cap-in-margin / margin page numbers.
  Cut now, or accept reduced fidelity. This is the band that would matter if the engine were ever
  reconsidered.
- **Cloud / AI / M365 (cut by product choice).** Microsoft Loop (the whole Collaborate group),
  Office.js web Add-ins (group + store + Featured slots + experimentation), M365/Stock/Online
  media sources (Picture from Mobile, Stock/M365 Pictures, Stock 3D Models Online), and
  third-party Signature Services. No engine equivalent and not part of a local clone's scope.
- **Niche / region-specific (cut by scope).** Japanese greetings, the East-Asian "Number" command,
  the China-specific Document Label, and the legacy off-ribbon Clip Art entry — mostly conditional
  / rarely used.

---

## QA flags & resolutions

From `result.qa`. The Word/idMso side was set-diffed against the official `wordcontrols.xlsx`
(M365 + 2013/2016/2019) and is ~99% complete; the LO-source pass resolved the one material LO
defect. Because there is **no owner screenshot for this tab**, several structural items remain
**screenshot-pending**.

| QA flag | Status | Resolution |
|---|---|---|
| Page Number group claims "no placement menu / no auto-placement"? | **Resolved (LO source)** | Wrong — LO ships `.uno:PageNumberWizard` (Position/Alignment/mirror/page-total/format/fit-into-margins + live preview, auto-places into header/footer). Page Number / Top of Page / Bottom of Page softened LO-missing → differs; Save-Selection children stay Engine gap; margin-placement stays Engine gap. |
| `SaveSelectionToCoverPageGallery` idMso nulled in inventory? | **Resolved (source set-diff)** | The idMso is real (present in M365 + 2013/2016/2019); set in this doc. The only Save-Selection row whose idMso had been dropped. Verdict (Engine gap, no Building Blocks) unchanged. |
| `ThemeSearchOfficeOnline` ("More … from Office.com") missing entirely? | **Open (screenshot-pending)** | Genuinely absent — no inventory row. The official list shows it under Cover Page, Header (×2) and Footer (×2) galleries as the Office.com search link (~5 rows). It would be LO-missing → Engine/Cut (no Office.com building-block search), but the control itself should be added. A screenshot of the open Cover Page / Header / Footer galleries would confirm placement. |
| `ClipArtInsert` presented as a live Insert-tab button? | **Open (screenshot-pending)** | `ClipArtInsert` is "Not in the Ribbon" in 2013/2016/2019/M365 — the modern entry point is the Pictures flyout → Online Pictures (`ClipArtInsertDialog`). Marked legacy/off-ribbon in this doc; a current-Word screenshot would confirm it no longer appears. |
| Pictures flyout split across two anchors (`FlyoutAnchorInsertPictures` vs `InsertPictureFlyoutAnchor`) and child set? | **Open (screenshot-pending)** | The official list parents children under both anchors; several children (Mobile, Stock, Online) are SKU/sign-in gated. A screenshot of the live Pictures dropdown would verify the exact child set and which are conditional. Does not change buckets. |
| Odd/typo'd idMsos (`PageNambers…`, `OleObjectctInsert`, `OfficeExtensionsGallery2`)? | **Resolved (source)** | Microsoft's actual (misspelled) identifiers — transcribed verbatim and correct. Do **not** "fix". |
| Null-idMso "gallery items (child of X)" rows correct? | **Resolved (source)** | Built-in gallery thumbnails legitimately have no idMso; leaving them null matches Microsoft's empty-Name rows. |
| `Document Property → .uno:InsertFieldCtrl` "DocInformation tab" routing? | **Open (LO-side, low risk)** | Command-level mapping is sound (only Fields-dialog entry command); the per-tab routing is unverified from `.xcu`/`.sdi`. Does not change the bucket. |
| Exhaustiveness of the many "LO-missing" absence claims (Loop, 3D, SmartArt, Screenshot, Ink Equation, etc.)? | **Open (LO-side, medium confidence)** | Not exhaustively re-audited against the LO tree; targeted searches found no matching `.uno` nodes and the claims are consistent with the catalog. `completenessConfidence`: HIGH on the Word/idMso side, MEDIUM on LO-mapping exhaustiveness. |
