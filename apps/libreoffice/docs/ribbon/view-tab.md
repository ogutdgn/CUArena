# View tab — Word ↔ LibreOffice

> **Status.** Word build: Microsoft 365 (target). **Word-side: web-sourced + LO-verified —
> screenshot-pending** (not yet confirmed against a live build). LO-side: high. Produced by the
> per-tab pipeline: 3 independent extractors → reconciled canonical → mapped to LO `.uno:` →
> verified against the LibreOffice source tree. The Word/idMso side was set-diffed against the
> official `wordcontrols.xlsx` (M365 Current Channel + 2013/2016/2019): TabView has exactly **9
> groups and 34 controls** and the inventory captured all of them (zero missing), so the Word-side
> is complete. The LO command facts were checked against the vendored LO tree. **No owner
> screenshot exists for this tab yet**, so conditional/version-sensitive controls below are
> *expected-conditional, unverified against a live build*. One mapping carries a **material LO-source
> correction** (Split → the `SplitHorizontal`/`SplitVertical` parenthetical is wrong and Calc-only
> `.uno:SplitWindow` was omitted); 32 more are confirmed (see
> [LO-source verification](#lo-source-verification)).

This is **Word-clone decision-research**, not LibreOffice documentation. It diffs every Word
View-tab control against LO's command surface and classifies the **work** each diff implies.
Bucket vocabulary and verdict meanings are in [README.md](README.md#legend).

---

## Outcome

Of 43 catalogued Word View-tab rows (9 group containers + 34 controls), **5 wire straight
through** to an existing LO `.uno:` command (Free), and the largest band — 15 — is **our-layer
UI**: the view-mode toggles LO already has (Print/Normal, Web, Draft), the show/hide aids LO
exposes one-per-command (Ruler, Gridlines, Navigator), the Zoom group, and the Window/Macros
menus that LO presents as classic menus rather than ribbon split-buttons. A modest **behavior-shim**
band (5) covers controls whose LO command exists but whose semantics differ (Read Mode reflow,
Outline-as-folding, app-wide vs canvas Dark Mode, editable multi-page zoom, the weaker macro
recorder). The decisive number for the engine decision is **Engine gap = 9** — and unlike Insert
(where the gap was Word's Building-Blocks system) the View-tab gap is almost entirely **Word's
M365 reading/immersive layer** plus a couple of genuinely-absent panes. The **Cut** pile (2) is the
SharePoint server-metadata group. Seven controls are window/view app-state we could *optionally*
build.

| Work bucket | Count | What it is |
|---|---:|---|
| **Free** | 5 | wire the existing LO `.uno:` command, no UI work |
| **Our-layer UI** | 15 | build the Word-faithful toggle/menu/dialog host; dispatch the LO command |
| **Behavior shim** | 5 | intercept/massage in our dispatch layer; LO's result/semantics differ |
| **Engine gap** | 9 | LO engine genuinely can't; cut or accept reduced fidelity |
| **Cut** | 2 | out of scope by product choice (SharePoint server metadata) |
| **Optional our-layer feature** | 7 | LO lacks it but it's window/view app-state we could build |
| **Total** | **43** | |

**Decisive learning:** on View the engine gap is *small and predictable* — **Engine gap = 9 / 43
(~21%)** — and it is concentrated in **Word's modern M365 reading/immersive layer**: the Modes
group (Focus, Focus Mode Background, Learning Tools / Immersive Reader) and the Page Movement
group (Vertical / Side to Side), plus two genuinely-absent panes (the legacy smart-document
Document Actions pane and the macro-recorder Pause). LO covers the *core view verbs* — Print/Normal,
Web, Draft views, zoom (dialog + 100% + One Page + Page Width), Ruler, Gridlines, Navigator, New
Window, the Window list, and the macro run/record commands — so the gap is the **reading-mode /
immersive shell on top**, not the underlying viewing engine. → still supports **LO-via-LOK +
scoped parity**, with the Immersive/Focus/Page-Movement reading layer explicitly out of scope.

> **Recurring our-layer theme.** Word's View tab is dominated by **mode toggles** (the 5-member
> Document Views radio set) and **menu/split-button hosts** (Switch Windows, the Macros split
> button) that LO already backs with real commands but presents differently — LO has independent
> View-menu items and classic Tools menus rather than one cohesive ribbon group. The repeated shape
> of work is composing LO's scattered commands (e.g. the H/V ruler pair, the Date-style split view
> toggles, the spread-out macro commands) under one Word-faithful ribbon host and dispatching the
> existing `.uno:`. Where LO genuinely lacks the capability, it is the M365 reading shell, not a
> core view verb.

---

## Inventory

One subsection per Word ribbon group. `LO .uno:` is the mapped LibreOffice command (`—` = none).
`work` is the bucket from the table above. Rows touched by the LO-source corrections are marked
**✓ verified vs LO source** in the note.

### Document Views (GroupDocumentViews)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Document Views group | GroupDocumentViews | group | — | UI-only | Our-layer UI | Ribbon group container for the document-view layout toggles. Source 1 (official `.xlsx`) names it `GroupDocumentViews`; the live caption (Sources 2-3) is "Views". — **LO:** No addressable group-container command; LO's CUA notebookbar has a "Views" group as a pure ribbon-layout label. ✓ verified vs LO source. |
| Read Mode | ViewFullScreenReadingView | toggleButton | `.uno:FullScreen` | differs | Behavior shim | Switches the document into a distraction-free, full-screen reading layout that hides the editing ribbon and reflows content into screen-sized columns; exit via View > Edit Document or Esc. (idMso conflicted across all 3 sources; Source 1's `ViewFullScreenReadingView` is authoritative. Type is toggleButton per MS data, not button.) — **LO:** Closest is `.uno:FullScreen` ("Full Screen", toggle, Ctrl+Shift+J on Win/Unix), but it differs substantially: LO Full Screen merely hides application chrome (toolbars/menus/sidebar) at the SAME editable pagination — no reflow into reading columns, no separate read-only experience. Dispatch-layer work to approximate the reading shell. ✓ verified vs LO source. |
| Print Layout | ViewPrintLayoutView | toggleButton | `.uno:PrintLayout` | differs | Our-layer UI | The default WYSIWYG authoring view (margins, headers/footers, page breaks, columns); a mutually-exclusive toggleButton in the 5-mode set. — **LO:** Strong functional match: `.uno:PrintLayout` is LO's WYSIWYG page view, but LO labels it "Normal View"/"Normal" (potential confusion — "Normal" in Word historically meant Draft), and LO has only 3 real view modes (Print/Normal, Web, Draft) not presented as one cohesive radio group. Re-present as a Word-faithful toggle in our group. ✓ verified vs LO source. |
| Web Layout | ViewWebLayoutView | toggleButton | `.uno:BrowseView` | differs | Our-layer UI | Renders the document as an unpaginated web page; text wraps to the window, backgrounds show. Mutually exclusive within the view set. — **LO:** Functional equivalent: `.uno:BrowseView` ("Web View" / "Web") renders unpaginated with text wrapping to the window; the internal name `BrowseView` (SID_BROWSER_MODE) reflects the old Online/Browse-layout concept (matching Word's legacy `ViewOnlineLayoutView`). Label differs; LO does not render editable web backgrounds/CSS. ✓ verified vs LO source. |
| Outline | ViewOutlineView | toggleButton | — | LO-missing | Behavior shim | Switches to Outline view (collapse/expand, promote/demote, reorder by heading level) and activates the contextual Outlining ribbon tab. — **LO:** LO Writer has NO Outline *view* mode and no `.uno:OutlineView`/`Outline`/`ViewOutline` command. But the capability exists, spread elsewhere: the Navigator (`.uno:Navigator`, F5) promotes/demotes/reorders headings, and in-canvas folding is `.uno:ToggleOutlineContentVisibility` ("Toggle Outline Folding") / `.uno:ShowOutlineContentVisibilityButton`. No dedicated heading-tree editing surface — our layer would compose these into an Outline-mode shim. ✓ verified vs LO source. |
| Draft | ViewDraftView | toggleButton | `.uno:DraftView` | differs | Our-layer UI | Simplified text-editing view hiding headers/footers, page boundaries, and most floating graphics for fast typing; shows breaks as labeled lines. Mutually exclusive within the view set. — **LO:** `.uno:DraftView` ("Draft View"/"Draft") is a simplified Writer mode that, like Word's Draft, hides headers/footers, floating graphics, and page chrome. Differences: it's a separate View-menu mode rather than one toggleButton in a unified 5-mode ribbon set, and it does not render breaks in the same labeled-line style. Re-present in our group. ✓ verified vs LO source. |

### Immersive / Modes (GroupModes)

> Modern M365 immersive/focus/learning reading layer. **Expected-conditional / version-sensitive** — Focus and Learning Tools are M365-only and unverified against a live build.

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Modes group | GroupModes | group | — | LO-missing | Engine gap | Ribbon group container for the M365 immersive/focus/learning reading modes (Source 1 `GroupModes`; live caption "Immersive"). — **LO:** LO has no such group and, more importantly, none of the underlying features (Focus, Immersive Reader). Engine-gap host. (Conditional — M365.) |
| Focus | ViewFocusModeView | toggleButton | `.uno:FullScreen` | differs | Engine gap | Toggles a distraction-free focus mode that hides chrome and centers the page on a dark backdrop; mouse-to-top reveals the ribbon; Esc/click exits. M365 / current-channel feature. — **LO:** No true Focus mode and no `.uno:FocusMode` command; the nearest is `.uno:FullScreen`, which just maximizes the canvas and hides toolbars on a normal background — no dark backdrop, no page-centering. The dedicated focus affordance genuinely does not exist. ✓ verified vs LO source. (Conditional — M365.) |
| Focus Mode Background | ColorPickerFocusModeBackground | gallery | — | LO-missing | Engine gap | Gallery of background color/scene choices applied while in Focus mode. (Only Source 1 lists it; mode-dependent.) — **LO:** No Focus mode in LO, therefore no focus-background gallery — no LO analogue at any level. ✓ verified vs LO source. (Conditional — M365, mode-dependent.) |
| Learning Tools / Immersive Reader | ToggleLearningTools | button | — | LO-missing | Engine gap | Opens the Immersive Reader / Learning Tools experience (Column Width, Page Color, Text Spacing, Line Focus, Syllables, Read Aloud) and surfaces a contextual Immersive Reader tab. M365 feature. — **LO:** LO has no Immersive Reader / Learning Tools — no Read Aloud, Syllables, Line Focus, Text Spacing, Column Width, or Page Color as a reading-accessibility mode. LO's Accessibility Check (`.uno:SidebarDeck.A11yCheckDeck`) audits a11y issues, unrelated to a guided reading experience. Genuinely missing. ✓ verified vs LO source. (Conditional — M365.) |

### Night Mode (GroupNightMode)

> Newer M365 document-canvas dark-mode group. **Expected-conditional / version-sensitive** — added in recent M365 builds; only Source 1 lists it.

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Night Mode group | GroupNightMode | group | — | UI-only | Our-layer UI | Ribbon group container for the dark/night reading-mode toggle. Only Source 1 (official `.xlsx`) lists this group; a newer M365 addition. — **LO:** LO has dark mode (`.uno:ChangeTheme`) but exposes it as a single toolbar/menu toggle, not a dedicated ribbon group; re-present as a group host. (Conditional — M365.) |
| Dark Mode | DarkModeOn | toggleButton | `.uno:ChangeTheme` | differs | Behavior shim | Toggles dark (night) display mode for the document canvas while content/colors are preserved on export. (Only Source 1 lists it; newer M365 feature.) — **LO:** `.uno:ChangeTheme` (Label "Dark Mode", tooltip "Toggle between dark and light modes") toggles the whole APPLICATION UI theme based on the Application Color scheme, whereas Word's `DarkModeOn` darkens the DOCUMENT CANVAS specifically. LO has a separate `FN_INVERT_BACKGROUND` that toggles only the document background — so a canvas-only night toggle needs our dispatch layer to target the right LO command. Behaviorally overlapping but scoped differently. ✓ verified vs LO source. (Conditional — M365.) |

### Page Movement (GroupPageMovement)

> Modern M365 page-scrolling-orientation group. **Expected-conditional / version-sensitive** — M365 addition, unverified against a live build.

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Page Movement group | GroupPageMovement | group | — | LO-missing | Engine gap | Ribbon group container for the vertical/side-to-side scrolling-orientation toggles. M365 addition. — **LO:** LO has no page-movement orientation feature and no such group. Engine-gap host. (Conditional — M365.) |
| Vertical | VerticalPageMovement | toggleButton | — | LO-missing | Engine gap | Sets vertical (up/down) page scrolling — the traditional default; mutually exclusive with Side to Side. (idMso conflicted; Source 1's `VerticalPageMovement` is authoritative.) — **LO:** LO Writer always scrolls vertically and has no command to set/toggle a page-movement orientation — it is the implicit, only behavior, with no addressable command. The toggle concept is absent. ✓ verified vs LO source. (Conditional — M365.) |
| Side to Side | TwoPageMode | toggleButton | — | LO-missing | Engine gap | Switches to a horizontal mode that displays whole pages and flips them left/right like a book; the document stays editable. (Source 1's `TwoPageMode` is authoritative — note it differs from the "Side to Side" caption.) — **LO:** No horizontal "flip pages like a book" navigation mode for the editable document. False-friend trap: `.uno:ShowTwoPages` ("Two Pages Preview"), `.uno:MultiplePagesPerRow`, and `.uno:BookView` only affect the read-only Print Preview, not an editable side-to-side mode. Genuinely missing. ✓ verified vs LO source. (Conditional — M365.) |

### Show (GroupViewShowHide)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Show group | GroupViewShowHide | group | — | UI-only | Our-layer UI | Ribbon group container for the show/hide on-screen aids (internal idMso `GroupViewShowHide`; live caption "Show"). — **LO:** No addressable group command; LO's View tab has a "Show" group as a layout label. ✓ verified vs LO source. |
| Ruler | ViewRulerWord | checkBox | `.uno:Ruler` | differs | Our-layer UI | Checkbox that shows/hides the horizontal (and, in Print Layout, vertical) rulers used for margins, indents, and tab stops. (idMso `ViewRulerWord` has 2-of-3 agreement incl. the official `.xlsx`.) — **LO:** `.uno:Ruler` ("Rulers", FN_RULER) toggles ruler visibility but LO SPLITS horizontal and vertical: `.uno:Ruler` controls the overall/horizontal ruler while `.uno:VRuler` ("Vertical Ruler", FN_VLINEAL) is a SEPARATE toggle. Word's single checkbox shows both at once — compose H+V under one host. ✓ verified vs LO source. |
| Gridlines | ViewGridlines | checkBox | `.uno:GridVisible` | differs | Our-layer UI | Checkbox that shows/hides a non-printing alignment grid over the page; visual aid only, does not print. (idMso `ViewGridlines` has 2-of-3 agreement.) — **LO:** `.uno:GridVisible` ("Grid", tooltip "Display Grid") toggles a non-printing alignment grid, matching the intent. Differences: LO's grid is the drawing/snap grid tied to `.uno:GridUse` ("Snap to Grid"), and LO has a distinct `.uno:BaselineGridVisible` (baseline grid) Word lacks; do not confuse with table gridlines (`.uno:TableBoundaries`). Present the visual-only toggle in our group. ✓ verified vs LO source. |
| Navigation Pane | NavigationPaneShowHide | checkBox | `.uno:Navigator` | differs | Our-layer UI | Checkbox that opens/closes the left Navigation pane, which combines a heading outline, page thumbnails, and live search results. (All 3 idMsos differ; Source 1's `NavigationPaneShowHide` is authoritative.) — **LO:** Closest match is `.uno:Navigator` (F5, "Show Navigator Window"; also `.uno:SidebarDeck.NavigatorDeck`). LO's Navigator offers heading-outline browsing/reordering plus jump-to for many object types but has NO page-thumbnail view and NO integrated find-results list, and is a floating/dockable window vs Word's fixed left task pane. Toggle maps cleanly; the thumbnail/search sub-features are the gap. ✓ verified vs LO source. |
| Document Actions Pane | ViewDocumentActionsPane | toggleButton | — | LO-missing | Engine gap | Shows/hides the legacy Document Actions (smart-document XML) task pane. (Only Source 1 lists it; legacy/context-gated.) — **LO:** LO has no smart-document / Document Actions infrastructure and no equivalent pane (the generic Sidebar via `.uno:Sidebar` hosts Properties/Styles/Navigator decks, not smart-document action XML). Genuinely missing. ✓ verified vs LO source. (Conditional — legacy smart-document context.) |

### Zoom (GroupZoom)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Zoom group | GroupZoom | group | — | UI-only | Our-layer UI | Ribbon group container for the zoom-level controls. — **LO:** No addressable group command; LO's View tab has a "Zoom" group label. ✓ verified vs LO source. |
| Thumbnails / Page Thumbnails | Thumbnails | toggleButton | — | LO-missing | Optional our-layer feature | Toggles the page-thumbnails pane (Read Mode thumbnail navigation). (Only Source 1 lists it, placed in GroupZoom; mode-dependent.) — **LO:** No `.uno:Thumbnails` command and no page-thumbnail navigation pane in Writer (thumbnails exist in Impress for slides, not in Writer; the Navigator has no thumbnail view). Page-image rendering is available via LOK, so a thumbnail navigator is app-state we could build in our layer. ✓ verified vs LO source. *(revisit)* |
| Zoom | ZoomDialog | button | `.uno:Zoom` | same | Free | Opens the Zoom dialog to pick a preset or type a custom magnification with live preview. (idMso `ZoomDialog` has 2-of-3 agreement.) — **LO:** `.uno:Zoom` ("Zoom…", SID_ATTR_ZOOM) opens LO's Zoom & View Layout dialog with presets and a custom percentage — equivalent. LO also bundles a View-layout choice (Automatic/Single/Columns/Book) and its presets differ slightly (Optimal / fit-width-and-height vs Word's Whole page/Many pages); core function is the same. ✓ verified vs LO source. |
| 100% | ZoomCurrent100 | button | `.uno:Zoom100Percent` | same | Free | One-click reset to 100% (normal size). (Source 1's `ZoomCurrent100` is authoritative; 2-of-3 favor `Zoom100`.) — **LO:** `.uno:Zoom100Percent` ("100%", SID_ZOOM_100_PERCENT) resets magnification to 100%, identical. LO also offers discrete 50/75/150/200% commands Word exposes only inside the dialog. ✓ verified vs LO source. |
| One Page | ZoomOnePage | button | `.uno:ZoomPage` | same | Free | Zooms so a single full page fits in the window. (idMso agrees across all 3.) — **LO:** `.uno:ZoomPage` (SID_ZOOM_ENTIRE_PAGE) zooms so one whole page fits — same behavior; LO labels it "Entire Page" (vs Word "One Page"). ✓ verified vs LO source. |
| Multiple Pages / Two Pages | ZoomTwoPages | button | — | differs | Behavior shim | Zooms so multiple pages (two by default) fit side by side for a spread-style overview. (idMso agrees; live caption "Multiple Pages", BetterSolutions "Two Pages".) — **LO:** No single editable-view "fit two/multiple pages" zoom command. The analogues `.uno:ShowTwoPages` and `.uno:MultiplePagesPerRow` operate only inside the read-only Print Preview; you can approximate a spread via the Zoom dialog's "Book" view layout, but there is no one-click View-tab button while editing. Our dispatch layer must compose preview/dialog options. ✓ verified vs LO source. |
| Page Width | ZoomPageWidth | button | `.uno:ZoomPageWidth` | same | Free | Zooms so the page width matches the window width, maximizing readable width. (idMso agrees across all 3.) — **LO:** `.uno:ZoomPageWidth` ("Page Width", SID_ZOOM_PAGE_WIDTH) — same intent and behavior. LO additionally has `.uno:ZoomOptimal` ("Optimal") fitting content/text width, with no exact Word View-tab counterpart. ✓ verified vs LO source. |

### Window (GroupWindow)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Window group | GroupWindow | group | — | UI-only | Our-layer UI | Ribbon group container for the window-management commands. — **LO:** No addressable group command; LO has a Window menu/group concept (label only). ✓ verified vs LO source. |
| New Window | WindowNew | button | `.uno:NewWindow` | same | Free | Opens a second window onto the same document so two parts can be viewed/edited at once; edits in either update the single file. (Source 1's `WindowNew` is authoritative; 2-of-3 favor `NewWindow`.) — **LO:** `.uno:NewWindow` ("New Window", SID_NEWWINDOW) opens a second view onto the same document — identical behavior. Minor cosmetic difference: LO titles windows by file name (": 1", ": 2") rather than "Document:N". ✓ verified vs LO source. |
| Arrange All | WindowsArrangeAll | button | — | LO-missing | Optional our-layer feature | Tiles/arranges all open Word document windows so every one is visible at once. (**idMso is `WindowsArrangeAll`** — trailing "s" on "Windows", per the official `.xlsx`; the inventory's `WindowArrangeAll` was a misspelling — see QA flags.) — **LO:** No `.uno:WindowArrangeAll` command; LibreOffice relies on the OS window manager to tile windows and provides no in-app arrange-all command. Window placement is app-state our layer could manage. ✓ verified vs LO source. |
| Split | WindowSplit | button | — | LO-missing | Optional our-layer feature | Splits the current window into two independently scrollable panes of the same document; toggles to "Remove Split" once active. (idMso agrees across all 3; acts as a split/remove-split toggle.) — **LO:** Writer has no document-scroll split — `.uno:WindowSplit` does not exist and the only Writer Split* slots are table-related (`SplitCell`=FN_TABLE_SPLIT_CELLS, `SplitTable`=FN_TABLE_SPLIT_TABLE). Note a real view-split command DOES exist as `.uno:SplitWindow` ("Split Window") but **only in Calc** (CalcCommands.xcu), not Writer — so the capability exists in LO's codebase and is app/view-state we could build for Writer. ✓ verified vs LO source. *(revisit)* |
| View Side by Side | WindowSideBySide | toggleButton | — | LO-missing | Optional our-layer feature | Places two open documents next to each other (default Synchronous Scrolling on); a Compare Side by Side chooser appears for 3+ documents. Enter/exit toggle. (All 3 idMsos differ; Source 1's `WindowSideBySide` is authoritative.) — **LO:** No "View Side by Side" comparison mode — no command to pair two open documents and no 3+-doc chooser. (LO's Edit > Track Changes > Compare/Merge is a content-diff, not a side-by-side viewing arrangement.) Window arrangement is app-state our layer could manage. ✓ verified vs LO source. |
| Synchronous Scrolling | WindowSideBySideSynchronousScrolling | toggleButton | — | LO-missing | Optional our-layer feature | Toggle (with View Side by Side) that links scrolling of the two compared documents. (All 3 idMsos differ; Source 1's value is authoritative.) — **LO:** Depends on View Side by Side, which LO lacks; no synchronous-scrolling toggle exists. Buildable in our layer alongside a side-by-side arrangement. ✓ verified vs LO source. |
| Reset Window Position | WindowResetPosition | button | — | LO-missing | Optional our-layer feature | Resizes/repositions the two compared documents to share the screen equally. Enabled only while View Side by Side is active. (idMso agrees across all 3.) — **LO:** Tied to View Side by Side, which LO lacks; no reset-position command. App-state our layer could manage. ✓ verified vs LO source. |
| Switch Windows | WindowSwitchWindowsMenuWord | menu | `.uno:WindowList` | differs | Our-layer UI | Drop-down menu listing all open document windows; selecting one brings that window to front. (idMso agrees across all 3.) — **LO:** `.uno:WindowList` (label "Window") is LO's Window-menu list of open document windows — same core switch-to-window function — but it is the classic Window menu's list (incl. a `.uno:CloseWin` "Close Window" context), not a standalone ribbon dropdown. Re-present as a Word-faithful menu host. ✓ verified vs LO source. |
| More Windows | WindowMoreWindowsDialog | button | — | LO-missing | Optional our-layer feature | Child of Switch Windows. Opens the More Windows dialog when more windows are open than the menu lists inline. (Only Source 1 lists it; MS data lists it as toggleButton, recorded as a dialog launcher — see QA flags.) — **LO:** No overflow "More Windows" dialog — LO's Window menu simply lists every open window inline, so the overflow concept does not exist (the parent switch behavior is covered by `.uno:WindowList`). An overflow list is app-state our layer could build. ✓ verified vs LO source. |

### Macros (GroupMacros)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Macros group | GroupMacros | group | — | UI-only | Our-layer UI | Ribbon group container for the macro view/record commands. — **LO:** No addressable group command. Placement difference: Word puts Macros on the View tab; LO's macro commands live under Tools > Macros. ✓ verified vs LO source. |
| Macros (split button) | MenuMacros | splitButton | `.uno:MacrosMenu` | differs | Our-layer UI | Split button: the main face opens the Macros dialog (view/run/edit/delete); the arrow opens a menu (View Macros, Record Macro, Pause Recording). (Source 1's `MenuMacros` is authoritative; 2-of-3 favor `MacrosMenu`.) — **LO:** `.uno:MacrosMenu` ("Macros") is LO's Macros menu, the structural counterpart, but it is a plain menu under Tools — not a ribbon split button with a dialog-opening main face. Re-present as a split-button host. ✓ verified vs LO source. |
| View Macros | PlayMacro | button | `.uno:RunMacro` | differs | Our-layer UI | Child of the split button's drop-down. Opens the Macros dialog to view/run/edit/create/delete macros. (Source 1's `PlayMacro` is authoritative; Source 2 folded it into the split-button.) — **LO:** `.uno:RunMacro` ("Run Macro…") opens LO's Macro Selector to select-and-run, but LO SPREADS the responsibilities: editing/creating via the Basic IDE (`.uno:BasicIDEAppear` "Edit Macros…"), organizing via `.uno:MacroOrganizer` / `.uno:MacroManager`, selecting via `.uno:ChooseMacro`. No single view+run+edit+delete dialog — compose into one host. ✓ verified vs LO source. |
| Record Macro | MacroRecordOrStop | button | `.uno:MacroRecorder` | differs | Behavior shim | Child of the split button's drop-down. Starts (or stops) recording; opens the Record Macro dialog to name/assign when starting. (Source 1's `MacroRecordOrStop` is authoritative; toggles record/stop in one control.) — **LO:** `.uno:MacroRecorder` ("Record Macro") starts recording, but differs: LO pops no up-front name/assign dialog (you name it on Stop), stopping is a SEPARATE command (`.uno:StopRecording` "Stop Recording") rather than the same toggle, and LO's recorder is weaker/optional (records fewer operations). Our dispatch layer must reconcile the single record/stop toggle against LO's two commands. ✓ verified vs LO source. (The "experimental / must enable in Tools > Options > Advanced" qualifier is UNCERTAIN — not verifiable from config/slot files.) |
| Pause Recording | MacroRecorderPause | button | — | LO-missing | Engine gap | Child of the split button's drop-down. Pauses/resumes an in-progress recording (meaningful only while recording). (Source 1's `MacroRecorderPause` is authoritative; Source 3's `MacroStopRecorder` implies stop, not pause.) — **LO:** LO's macro recorder has no pause/resume — only Record (`.uno:MacroRecorder`) and Stop (`.uno:StopRecording`); there is no command to temporarily suspend an in-progress recording. (A recorder-implementation gap, not a document-engine gap.) ✓ verified vs LO source. *(revisit)* |

### SharePoint Properties (GroupSharePointProperties)

> Contextual SharePoint-hosted-docs-only group. **Expected-conditional / version-sensitive** — surfaces only for SharePoint-stored documents; the Properties button was added ~Sept 2018 / Office 2019.

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| SharePoint Properties group | GroupSharePointProperties | group | — | LO-missing | Cut | Ribbon group container for the SharePoint document-properties panel toggle; contextual — surfaces only for SharePoint-hosted documents. (Source 1 `GroupSharePointProperties`; live caption "SharePoint".) — **LO:** LO has no SharePoint server integration and no server-metadata properties panel, so neither the group nor its contents exist. Cloud/server product-choice. ✓ verified vs LO source. (Conditional — SharePoint-hosted docs only.) |
| Properties / Document Properties Panel | DocumentInformationShowHide | button | `.uno:SetDocumentProperties` | differs | Cut | Shows/hides the SharePoint Document Information / Document Properties panel to view and edit server-side metadata (content type + column values). Present only for SharePoint-hosted documents. (All 3 idMsos differ; Source 1's `DocumentInformationShowHide` is authoritative.) — **LO:** LO's closest is `.uno:SetDocumentProperties` ("Properties…"), but it opens a modal LOCAL Document Properties dialog (Title/Subject/Keywords/Comments + custom properties), not a dockable inline SharePoint panel, and has NO server-column awareness. The SharePoint capability is server/cloud — cut by product choice. ✓ verified vs LO source. (Conditional — SharePoint-hosted docs only.) |

---

## LO-source verification

These mappings were checked against the vendored LibreOffice tree at
`apps/libreoffice/libreoffice-codebase/` and **override** the mapped rows where they conflicted.
Command labels were checked in `officecfg/registry/data/org/openoffice/Office/UI/{GenericCommands,WriterCommands,CalcCommands}.xcu`;
shortcuts in `Accelerators.xcu`; slot/command-name bindings in `sfx2/sdi/sfx.sdi` and
`sw/sdi/{swriter,_viewsh}.sdi`; behavioral handlers in `sfx2/source/view/viewfrm.cxx` (FullScreen)
and `sfx2/source/appl/appserv.cxx` (ChangeTheme). One row is **CORRECTED**; the rest **confirm** the
mapped command, label, tooltip, slot, and (where cited) shortcut. One qualifier (Record Macro
"experimental") is **PARTIAL-UNCERTAIN** and not treated as authoritative.

**Material correction (CORRECTED):**

- **Split (WindowSplit)** — the Writer LO-missing verdict (no editable document-scroll split) is
  correct, but two parenthetical details in the mapped note were wrong: (1) the example command
  names `SplitHorizontal` / `SplitVertical` do **not** exist in Writer SDI — the actual Split* slots
  are table-related (`SplitCell`=FN_TABLE_SPLIT_CELLS, `SplitTable`=FN_TABLE_SPLIT_TABLE, plus
  `RowSplit` / `DontSplitTable`); and (2) a real document-view split command **does** exist as
  `.uno:SplitWindow` ("Split Window") but it is **Calc-only** (CalcCommands.xcu), which the mapping
  omitted. Neither changes the Writer LO-missing conclusion. Evidence: `sw/sdi/swriter.sdi:6166`
  (SplitCell), `:6184` (SplitTable), `:7586` (RowSplit), `:7701` (DontSplitTable); no
  SplitHorizontal/SplitVertical/WindowSplit in `sw/sdi`; `CalcCommands.xcu:89-96`
  (`.uno:SplitWindow` "Split Window" — Calc only).

**Partial-uncertain (PARTIAL-UNCERTAIN) — not treated as authoritative:**

- **Record Macro (MacroRecorderPause / MacroRecordOrStop)** — the command names/labels
  (`.uno:MacroRecorder` "Record Macro", separate `.uno:StopRecording` "Stop Recording") are
  CONFIRMED. The note's additional claim that macro recording "is experimental and must be enabled
  in Tools > Options > Advanced" could **not** be verified from the config/slot files — the
  MacroRecorder command node carries no `IsExperimental` flag (contrast `.uno:MacroManager`, which
  does). Treat the qualifier as unverified rather than contradicted. Evidence:
  `GenericCommands.xcu:5597-5609` (MacroRecorder / StopRecording); `:5959-5969` (MacroManager +
  IsExperimental).

**Confirmed (CONFIRMED) — command/label/tooltip (and cited shortcut) match the mapping:**

- **Read Mode / Full Screen** — `.uno:FullScreen`, "F~ull Screen", toggle (SfxBoolItem FullScreen →
  SID_WIN_FULLSCREEN), J_SHIFT_MOD1 = Ctrl+Shift+J (Win/Unix), Cmd+Ctrl+F (macOS). Handler toggles
  WorkWindow full-screen + locks notebookbar + manipulates layout manager — **chrome only, no text
  reflow/repagination**, confirming the behavioral delta. Evidence: `GenericCommands.xcu:4136-4143`;
  `Accelerators.xcu:1066-1069` (unxwnt) / `:1072-1075` (macosx); `sfx.sdi:1328`;
  `viewfrm.cxx:3423-3470`.
- **Print Layout** — `.uno:PrintLayout`, Label "~Normal View", ContextLabel "~Normal"; SfxBoolItem
  PrintLayout FN_PRINT_LAYOUT, GroupId View — the WYSIWYG toggle. Evidence: `WriterCommands.xcu:30-40`;
  `swriter.sdi:5297,5312`; `_viewsh.sdi:135-138`.
- **Web Layout** — `.uno:BrowseView`, Label "~Web View", ContextLabel "~Web"; SfxBoolItem BrowseView
  SID_BROWSER_MODE — the legacy Browse-mode lineage is accurate. Evidence: `GenericCommands.xcu:3441-3451`;
  `sfx.sdi:570`; `_viewsh.sdi:130-133`.
- **Outline** — no `.uno:OutlineView` / `Outline` / `ViewOutline` command exists anywhere in the UI
  config. The cited folding commands are real: `.uno:ToggleOutlineContentVisibility` ("Toggle Outline
  Folding") and `.uno:ShowOutlineContentVisibilityButton`. Navigator (`.uno:Navigator`, F5) is a
  docking panel, not a view. Evidence: `WriterCommands.xcu:4414-4424`, `:459`;
  `GenericCommands.xcu:4830-4840` (Navigator); `Accelerators.xcu:930-933` (F5).
- **Draft** — `.uno:DraftView`, Label "~Draft View", ContextLabel "~Draft"; SfxBoolItem DraftView
  FN_DRAFT_VIEW. Evidence: `WriterCommands.xcu:41-51`; `swriter.sdi:5315`; `_viewsh.sdi:140-143`.
- **Focus** — no `.uno:FocusMode` / `ViewFocusModeView` command exists; `.uno:FullScreen` is the only
  chrome-hiding analogue. Evidence: no match for `.uno:FocusMode` in `officecfg/.../UI/`; FullScreen
  at `GenericCommands.xcu:4136`.
- **Learning Tools / Immersive Reader** — no `.uno:ImmersiveReader` / Learning Tools command exists.
  `.uno:SidebarDeck.A11yCheckDeck` is real, Label "Open the Accessibility Check Deck" (unrelated
  audit tool). Evidence: no match for ImmersiveReader in `officecfg/.../UI/`; `WriterCommands.xcu:4440-4443`.
- **Dark Mode** — `.uno:ChangeTheme`, Label "Dark Mode", tooltip "Toggle between dark and light
  modes"; SfxVoidItem ChangeTheme FN_CHANGE_THEME. Handler operates on application-wide
  scheme (GetAppColorMode/ThemeColors/AppearanceMode); a SEPARATE FN_INVERT_BACKGROUND toggles only
  the document background — confirming the app-wide-UI vs document-canvas distinction. State reported
  as SfxBoolItem (toggle). Evidence: `GenericCommands.xcu:1491-1501`; `sfx.sdi:6020`;
  `appserv.cxx:706-757`, `:759` (FN_INVERT_BACKGROUND), `:1367-1374`.
- **Vertical / Side to Side (Page Movement)** — the cited preview commands exist and are
  preview-scoped: `.uno:ShowTwoPages` ("Two Pages Preview"); `.uno:MultiplePagesPerRow` (Properties=8
  toggle); `.uno:BookView` (Properties=8 toggle). No editable side-to-side / vertical page-movement
  command exists. Evidence: `WriterCommands.xcu:1706-1713`, `:4471-4478`, `:4479-4486`;
  `_viewsh.sdi:146-159`.
- **Ruler** — `.uno:Ruler`, Label "~Rulers" (SfxBoolItem Ruler FN_RULER); `.uno:VRuler`, Label
  "Vertical Ruler" (SfxBoolItem VRuler FN_VLINEAL) — genuinely separate H/V toggles. Evidence:
  `WriterCommands.xcu:3063-3070`, `:3152-3159`; `swriter.sdi:5507`, `:6963`.
- **Gridlines** — `.uno:GridVisible`, Label "Grid", ContextLabel "~Display Grid", tooltip "Display
  Grid"; `.uno:GridUse`, Label "Snap to Grid"; `.uno:BaselineGridVisible`, Label "Display ~Baseline
  Grid". Evidence: `GenericCommands.xcu:5122-5132`, `:4120-4127`; `WriterCommands.xcu:3611-3621`.
- **Navigation Pane** — `.uno:Navigator`, Label "Na~vigator", tooltip "Show Navigator Window", slot
  SID_NAVIGATOR, shortcut F5 (one context adds F5_SHIFT_MOD1); `.uno:SidebarDeck.NavigatorDeck`,
  Label "Open the Navigator Deck". Evidence: `GenericCommands.xcu:4830-4840`; `sfx.sdi:2637`;
  `Accelerators.xcu:930-933`, `:3236-3239`; `GenericCommands.xcu:8106-8109`.
- **Thumbnails / Page Thumbnails** — no `.uno:Thumbnails` command exists in the UI config. Evidence:
  no match for `oor:name='.uno:Thumbnails'` in `officecfg/.../UI/`.
- **Zoom** — `.uno:Zoom`, Label "~Zoom...", slot SvxZoomItem Zoom SID_ATTR_ZOOM (modal Zoom & View
  Layout dialog). Evidence: `GenericCommands.xcu:1523-1530`; `sfx.sdi:5900`.
- **100%** — `.uno:Zoom100Percent`, Label "100%" (SID_ZOOM_100_PERCENT); discrete
  `.uno:Zoom50/75/150/200Percent` also exist. Evidence: `GenericCommands.xcu:2143-2156`;
  `sfx.sdi:1411-1494`.
- **One Page** — `.uno:ZoomPage`, Label "Entire Page", slot SID_ZOOM_ENTIRE_PAGE. Evidence:
  `GenericCommands.xcu:2172-2179`; `sfx.sdi:1390`.
- **Multiple Pages / Two Pages** — the two analogues are preview-scoped (see Page Movement); no
  one-click editable multi-page zoom View-tab button exists; the Zoom dialog (SID_ATTR_ZOOM) bundles
  a Book view-layout option. Evidence: `WriterCommands.xcu:1706-1713`, `:4471-4478`; `sfx.sdi:5900`.
- **Page Width** — `.uno:ZoomPageWidth`, Label "Page Width" (SID_ZOOM_PAGE_WIDTH); `.uno:ZoomOptimal`,
  Label "Optimal", ContextLabel "Optimal View" (SID_ZOOM_OPTIMAL). Evidence:
  `GenericCommands.xcu:3741-3748`, `:2188-2198`; `sfx.sdi:1348`, `:1369`.
- **New Window** — `.uno:NewWindow`, Label "~New Window", slot SfxVoidItem NewWindow SID_NEWWINDOW.
  Evidence: `GenericCommands.xcu:4091-4098`; `sfx.sdi:2815`.
- **Arrange All** — no `.uno:WindowArrangeAll` command exists in the UI config. Evidence: no match
  for `oor:name='.uno:WindowArrangeAll'`.
- **View Side by Side / Synchronous Scrolling / Reset Window Position** — no `.uno:WindowSideBySide`
  or equivalent command exists. Evidence: no match for `oor:name='.uno:WindowSideBySide'`.
- **Switch Windows** — `.uno:WindowList`, Label "~Window"; `.uno:CloseWin`, Label "Close Window".
  Evidence: `GenericCommands.xcu:7308-7312`, `:4112-4116`.
- **Macros (split button)** — `.uno:MacrosMenu`, Label "~Macros". Evidence: `GenericCommands.xcu:7292-7299`.
- **View Macros** — `.uno:RunMacro` "R~un Macro..."; `.uno:BasicIDEAppear` "Edit Macros...";
  `.uno:MacroOrganizer` "Basic Macro Organizer..."; `.uno:MacroManager` "Macro Manager..." (also
  IsExperimental=true); `.uno:ChooseMacro` "Select Macro...". Evidence: `GenericCommands.xcu:5951-5958`,
  `:1900-1907`, `:7684-7691`, `:5959-5969`, `:1602-1609`.
- **Pause Recording** — no `.uno:MacroRecorderPause` / pause-recording command exists; only
  `.uno:MacroRecorder` and `.uno:StopRecording`. Evidence: no pause command near
  `GenericCommands.xcu:5597-5609`.
- **Properties / Document Properties Panel** — `.uno:SetDocumentProperties`, Label "Propert~ies...";
  `.uno:Sidebar`, Label "Sidebar" (single Properties dialog command; no SharePoint integration).
  Evidence: `GenericCommands.xcu:3286-3293`, `:4857-4860`.
- **Group containers** (GroupDocumentViews, GroupModes, GroupNightMode, GroupPageMovement,
  GroupViewShowHide, GroupZoom, GroupWindow, GroupMacros, GroupSharePointProperties) — group
  containers are not `.uno` commands in LibreOffice; the catalog contains only individual command
  nodes (groups are notebookbar/menu layout constructs). Evidence: `officecfg/.../UI/*.xcu` contains
  only individual `oor:name='.uno:...'` command nodes; no Group* command nodes.
- **Focus Mode Background, Document Actions Pane, SharePoint Properties group, More Windows** — none
  of these features have corresponding `.uno` commands (no focus background gallery, no
  smart-document Document Actions pane, no SharePoint command, no overflow More-Windows dialog — the
  Window menu lists windows inline via `.uno:WindowList`). Evidence: no matches for
  FocusMode/DocumentActions/SharePoint/MoreWindows commands in `officecfg/.../UI/`.

> **Bit-flag note.** Properties value 8 = TOGGLEBUTTON, 1 = IMAGE only, 9 = IMAGE+TOGGLEBUTTON.
> `.uno:MultiplePagesPerRow` and `.uno:BookView` carry Properties=8 (toggles); `.uno:FullScreen` /
> `.uno:PrintLayout` / `.uno:DraftView` are SfxBoolItem toggles at the slot level even though their
> Properties=1.

---

## Conditional / version-sensitive controls

There is **no owner screenshot for the View tab yet**, so the following are flagged
**expected-conditional, unverified against a live build** — a screenshot sweep would confirm
whether (and how) they surface. They are not contradicted by the inventory; they simply depend on
SKU/version/context state.

- **Modes group (Immersive)** — Focus, Focus Mode Background, and Learning Tools / Immersive Reader
  are M365 / current-channel features; expected absent in older perpetual builds (Sources 2-3 list
  the Focus/Immersive Reader idMsos only as inferred or null).
- **Night Mode group (Dark Mode)** — a newer M365 addition; only Source 1 (official `.xlsx`) lists
  it. Whether Dark Mode coexists with or is mutually exclusive of Focus in a given build is
  screenshot-pending.
- **Page Movement group (Vertical / Side to Side)** — an M365 addition (noted by Source 3); the
  idMsos are listed only as inferred or null by Sources 2-3.
- **Document Actions Pane** — legacy smart-document-XML context; may not render on a plain local
  document in current Word.
- **SharePoint Properties group (Properties)** — surfaces only for SharePoint-hosted documents; the
  Properties button was added ~Sept 2018 / Office 2019.
- **Thumbnails / Page Thumbnails** and **Focus Mode Background** — mode-dependent (Read Mode / Focus
  mode); may not appear simultaneously in the live ribbon.
- **More Windows** — a hidden overflow child of Switch Windows that only appears when more windows
  are open than the menu lists inline.
- **idMso version-sensitivity** — `ViewFullScreenReadingView` is a legacy idMso name ("FullScreen
  Reading") while the live surface label is "Read Mode"; a screenshot would confirm they still pair.

---

## Out of scope

- **Engine gap — the M365 reading/immersive layer + two absent panes (the true engine blockers, 9
  controls).** Two clusters: (1) **Word's M365 reading shell** — the Modes group (Focus, Focus Mode
  Background, Learning Tools / Immersive Reader) and the Page Movement group (Vertical / Side to
  Side); LO has no focus mode, no Immersive Reader / Learning Tools, and no editable page-movement
  orientation at all. (2) **Two genuinely-absent affordances** — the legacy smart-document
  **Document Actions pane** and the macro-recorder **Pause Recording** (LO's recorder has only
  Record/Stop). Cut now, or accept reduced fidelity. This is the band that would matter if the
  engine were ever reconsidered. *(Pause Recording is a recorder-feature limitation, not a
  document-engine gap — flagged `(revisit)`.)*
- **Cloud / server (cut by product choice).** The **SharePoint Properties group** and its
  **Document Properties Panel** — server-side metadata (content type + column values) for
  SharePoint-hosted documents. LO has only a local Document Properties dialog
  (`.uno:SetDocumentProperties`) with no server-column awareness. No engine equivalent and not part
  of a local clone's scope.
- **Optional our-layer window/view state (build later if wanted).** Page Thumbnails, Arrange All,
  Split (Writer), View Side by Side, Synchronous Scrolling, Reset Window Position, and More Windows
  are all window-arrangement / view-pane app-state our layer could manage — LO lacks the Writer
  command but the capability is buildable (page-image rendering via LOK for thumbnails; `.uno:SplitWindow`
  already exists in Calc; window placement is ours to control). Deferred, not cut.

---

## QA flags & resolutions

From `result.qa`. The Word/idMso side was set-diffed against the official `wordcontrols.xlsx`
(M365 Current Channel, parsed from source) — TabView has exactly **9 groups and 34 controls** and
all were captured, so completeness is full. The LO-source pass CONFIRMED the mapping with one
CORRECTED row (Split). Because there is **no owner screenshot for this tab**, several structural
items remain **screenshot-pending**.

| QA flag | Status | Resolution |
|---|---|---|
| Document Views control types listed as `button`? | **Resolved (source)** | Wrong — all five (Read Mode, Print Layout, Web Layout, Outline, Draft) are `toggleButton` in Microsoft's authoritative `wordcontrols.xlsx` (mutually-exclusive 5-mode set), and the rows' own prose says so. Corrected to `toggleButton` in this doc. High confidence. |
| Arrange All idMso `WindowArrangeAll`? | **Resolved (source)** | Wrong — the real idMso is **`WindowsArrangeAll`** (trailing "s"), confirmed two ways (wordcontrols.xlsx + ribboncreator2010). Corrected here. The LO conclusion (no in-app tile-all command) still stands; only the Word-side identifier was misspelled. High confidence. |
| `WindowMoreWindowsDialog` control type? | **Open (minor / screenshot-pending)** | MS data lists it as `toggleButton`; recorded here as a dialog launcher (`button`) since it opens the More Windows dialog. Defensible but does not match the registry; a screenshot of the expanded Switch Windows menu with >9 open docs would confirm. Does not change the bucket. |
| Split mapping parentheticals (`SplitHorizontal`/`SplitVertical`; Calc `.uno:SplitWindow`)? | **Resolved (LO source)** | The mapped note's example names `SplitHorizontal`/`SplitVertical` do not exist in Writer SDI (the real Split* slots are `SplitCell`/`SplitTable`), and a real view-split `.uno:SplitWindow` exists but is **Calc-only**. Corrected. The Writer LO-missing verdict is unchanged. |
| Record Macro "experimental / must enable in Tools > Options > Advanced"? | **Open (LO-side, low risk)** | UNCERTAIN — the MacroRecorder command node carries no `IsExperimental` flag in the config/slot files; the qualifier is plausibly an options-layer runtime gate not visible here. Treat as unverified. Command names/labels are CONFIRMED. |
| Which M365-gated controls actually render (Focus, Learning Tools, Document Actions, SharePoint Properties)? | **Open (screenshot-pending)** | These are build/SKU/context-gated and may not appear in a given Word build or on a plain local document. A current-build screenshot would confirm which surface on the View tab. The LO-missing/Cut verdicts are independent of this and remain sound. |
| Completeness of LO-missing absence claims? | **Resolved (LO source)** | All Word-specific absence claims (Outline view, Focus, Immersive Reader, Page Movement, Thumbnails, Arrange All, Side by Side, Sync Scrolling, Reset Position, More Windows, Pause Recording, SharePoint, Document Actions) were CONFIRMED against the vendored LO tree. `completenessConfidence`: HIGH on the Word/idMso side; LO-mapping CONFIRMED with one CORRECTED row (Split). |
