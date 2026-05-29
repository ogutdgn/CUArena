# References tab — Word ↔ LibreOffice

> **Status.** Word build: Microsoft 365 (target). **Word-side: web-sourced + LO-verified —
> screenshot-pending.** LO-side: high. Produced by the per-tab pipeline: 3 independent
> extractors → reconciled canonical → mapped to LO `.uno:` → verified against the LibreOffice
> source tree. The Word/idMso side was set-diffed against the official `wordcontrols.xlsx`
> (Office 2019 + Microsoft 365 Current Channel, filtered to `Tab=TabReferences`): all 44 named
> References-tab controls Microsoft lists are present, nothing is missing, and every idMso is a
> valid official identifier. The LO command facts were checked against the vendored LO tree. **No
> owner screenshot exists for this tab yet**, so M365-only / temporally-drifting controls below
> (Acronyms, Researcher, Smart Lookup) are *expected-conditional, unverified against a live
> build*. Two mappings carry a **material LO-source correction** (footnote/endnote shortcuts; and
> Remove Table of Contents → `.uno:RemoveTableOf`, not absent); 14 more facts are confirmed (see
> [LO-source verification](#lo-source-verification)).

This is **Word-clone decision-research**, not LibreOffice documentation. It diffs every Word
References-tab control against LO's command surface and classifies the **work** each diff implies.
Bucket vocabulary and verdict meanings are in [README.md](README.md#legend).

---

## Outcome

Of 44 catalogued Word References-tab controls, only **4 wire straight through** to an existing LO
`.uno:` command (Free: Insert Footnote, Insert Endnote, Insert Caption, Update Index). The largest
band — 18 — is **our-layer UI**: re-presenting commands LO already has but exposes through its
**single unified index dialog** (`.uno:InsertMultiIndex` serves TOC, Index, Table of Figures and
Bibliography from one place) plus the footnote-navigation commands, the caption/cross-reference
dialogs, and the index Mark-Entry dialog. A meaningful **behavior-shim** band (7) covers the cases
where LO has a command but the *semantics* diverge — its no-prompt "always full rebuild" index
update, its bibliography-DB citation model (no style-formatted in-text citations), and its
partial-overlap "Edit Footnote/Endnote" jump. The decisive number for the engine decision is
**Engine gap = 7**, and unlike the Insert tab (where the gap was Building-Blocks galleries +
rich-media), the References-tab gap is **Word's scholarly-apparatus stack**: the
citation-**style** engine, the **Table of Authorities** feature,
and the save-to-gallery building blocks. The **Cut** pile (5) is the M365/Graph-backed
Acronyms group plus the cloud research controls (Smart Lookup / Researcher / the Research group
host). Three controls are app-state we could *optionally* build.

| Work bucket | Count | What it is |
|---|---:|---|
| **Free** | 4 | wire the existing LO `.uno:` command, no UI work |
| **Our-layer UI** | 18 | build the Word-faithful menu/dialog/host; dispatch the LO command |
| **Behavior shim** | 7 | intercept/massage in our dispatch layer; LO's result/semantics differ |
| **Engine gap** | 7 | LO engine genuinely can't; cut or accept reduced fidelity |
| **Cut** | 5 | out of scope by product choice (cloud/AI/M365) |
| **Optional our-layer feature** | 3 | LO lacks it but it's app-state we could build |
| **Total** | **44** | |

**Decisive learning:** on References the engine gap is small in count but high in importance —
**Engine gap = 7 / 44 (~16%)** — and it is the genuine *document-engine* gap, three clean clusters:
**(1)** Word's **citation-style engine + placeholder** (`Style` APA/MLA/Chicago switching, `Add
New Placeholder`) — LO's bibliography is a manual local database with no named-style reformatting,
the single largest gap; **(2)** the entire **Table of Authorities** legal feature (Mark Citation,
Insert/Update TOA) — LO has no TA marks, categories, or `passim` at all; **(3)**
the **save-to-gallery building blocks** (Save Selection to TOC / Bibliography Gallery) — same
Building-Blocks engine gap seen on every tab. (Cloud research — Smart Lookup, Researcher, the
Research group host — is now bucketed **Cut** by product choice, like every other tab's
cloud/AI/online features, not a document-engine gap.) LO covers the *core scholarly verbs* (footnotes,
endnotes, captions, cross-references, index marking, and a consolidated index/TOC/figures/
bibliography dialog) — the gap is the **research + citation-style + legal-authorities layer on
top**, not the underlying note/index machinery. → still supports **LO-via-LOK + scoped parity**,
with the citation-style engine, Table of Authorities, and web research explicitly out of scope.

> **Recurring our-layer theme.** Word's References tab exposes a *feature-specific dialog per
> verb* (a TOC dialog, an Index dialog, a Table of Figures dialog, a Bibliography gallery). LO
> consolidates almost all of these into **one** command — `.uno:InsertMultiIndex` ("Table of
> Contents, Index or Bibliography…") — where you pick the type. The repeated shape of work is
> therefore **fanning one LO dialog out into Word's several entry points**, plus rebuilding the
> Word galleries/split menus on top. Most index/TOC/bibliography rows below resolve to that one
> `.uno:`.

---

## Inventory

One subsection per Word ribbon group. `LO .uno:` is the mapped LibreOffice command (`—` = none).
`work` is the bucket from the table above. Rows touched by the LO-source corrections are marked
**✓ verified vs LO source** in the note.

### Table of Contents (GroupTableOfContents)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Table of Contents (group) | GroupTableOfContents | group | — | UI-only | Our-layer UI | Ribbon group container for table-of-contents controls. — **LO:** Group containers are ribbon-layout constructs, not commands; LO's tabbed/notebookbar UI groups TOC entries differently and no `.uno` maps to a group. |
| Table of Contents | TableOfContentsGallery | gallery | `.uno:InsertMultiIndex` | differs | Our-layer UI | Top half inserts a default automatic TOC from the document's heading styles; the dropdown opens a gallery of built-in automatic/manual TOC presets plus Custom Table of Contents, Remove, and Save Selection to Gallery. — **LO:** `.uno:InsertMultiIndex` opens the unified "Table of Contents, Index or Bibliography" dialog (pick type=Table of Contents and configure) — no preset gallery, no one-click default-insert, no manual-TOC building blocks, no save-to-gallery. One dialog also serves Index/Figures/Bibliography — a far more consolidated model. ✓ verified vs LO source. (Official type is **gallery**, not split-button — see QA flags.) |
| Custom Table of Contents… / Insert Table of Contents | TableOfContentsDialog | button | `.uno:InsertMultiIndex` | differs | Our-layer UI | Child of the gallery menu; opens the Table of Contents dialog to insert/customize a TOC (show page numbers, right-align, tab leader, format, show-levels). — **LO:** `.uno:InsertMultiIndex` IS the customize-and-insert path (the only TOC entry point — no separate quick-insert vs custom split). Its dialog covers show-page-numbers, tab leader, "Evaluate up to level", alignment, and an Entries/Styles tab. Comparable coverage; Word splits quick-insert from custom, LO has only the dialog. ✓ verified vs LO source. |
| Remove Table of Contents | TableOfContentsRemove | button | `.uno:RemoveTableOf` | differs | Our-layer UI | Child of the gallery menu; removes the existing table of contents. — **LO:** **Corrected:** a dedicated command exists — `.uno:RemoveTableOf` (FN_REMOVE_CUR_TOX, label "Delete Index"), flagged AccelConfig/MenuConfig/ToolBoxConfig=TRUE, so fully dispatchable to menu/toolbar/shortcut. It deletes the index the cursor is in; default surfacing is the context menu rather than a ribbon button. NOT LO-missing. ✓ verified vs LO source. |
| Save Selection to Table of Contents Gallery… | SaveSelectionToTableOfContentsGallery | button | — | LO-missing | Engine gap | Child of the gallery menu; saves the current selection as a reusable TOC building block. — **LO:** No Building Blocks / Quick Parts gallery concept at all; a TOC preset cannot be saved (AutoText is the nearest analogue but cannot store a live TOC field as a gallery entry). |
| Add Text | TableOfContentsAddTextGallery | gallery / dropdown menu | — | LO-missing | Optional our-layer feature | Dropdown that sets the current paragraph's TOC outline level (Do Not Show, Level 1–3) so the text is included in / excluded from the TOC. — **LO:** No single command sets a paragraph's outline/TOC level. Outline level is a paragraph property (Format > Paragraph > Outline & List), set implicitly by Heading N styles, or via Tools > Chapter Numbering; no "Add Text"-style dropdown. App-state we could wrap over the existing outline-level property. |
| Update Table | TableOfContentsUpdate | button | `.uno:UpdateCurIndex` | differs | Behavior shim | Updates the TOC, prompting to update page numbers only or the entire table. — **LO:** `.uno:UpdateCurIndex` ("Update Index") rebuilds the index/TOC the cursor is in, but **always does a full rebuild** — there is NO "page numbers only vs entire table" prompt. `.uno:UpdateAllIndexes` ("Update All") updates every index at once. Functionally close; the partial-update semantics differ → dispatch-layer shim. ✓ verified vs LO source. |

### Footnotes (GroupFootnotes)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Footnotes (group) | GroupFootnotes | group | — | UI-only | Our-layer UI | Ribbon group container for footnote/endnote controls. — **LO:** Layout-only group container; no `.uno`. |
| Insert Footnote | FootnoteInsert | button | `.uno:InsertFootnote` | same | Free | Inserts a numbered footnote reference at the cursor and places the matching note at the bottom of the page (auto-renumbering); Word default Alt+Ctrl+F. — **LO:** Direct equivalent — inserts an auto-numbered footnote at page bottom and moves the cursor into the note. **Corrected:** `.uno:InsertFootnote` has **no default shortcut** in this tree (absent from Accelerators.xcu; the earlier "Ctrl+Alt+F matches Word" claim is wrong). Core insert behavior matches. ✓ verified vs LO source. |
| Insert Endnote | EndnoteInsertWord | button | `.uno:InsertEndnote` | same | Free | Inserts a numbered endnote reference at the cursor and places the matching note at the end of the document/section (auto-renumbering); Word default Alt+Ctrl+D. — **LO:** Direct equivalent — inserts an auto-numbered endnote at document end. **Corrected:** `.uno:InsertEndnote` has **no default shortcut** in this tree (the earlier "Ctrl+Alt+D matches Word" claim is wrong; Ctrl+D is UnderlineDouble). LO collects endnotes at the very document end and lacks Word's per-section endnote placement choice; otherwise behavior matches. ✓ verified vs LO source. |
| Next Footnote | FootnoteNext | splitButton | `.uno:JumpToNextFootnote` | differs | Our-layer UI | Primary click jumps to the next footnote reference; dropdown offers Next/Previous Footnote and Next/Previous Endnote navigation. — **LO:** The four jumps exist individually (`.uno:JumpToNextFootnote` / `.uno:JumpToPrevFootnote`, labels "To Next/Previous Footnote") but there is **no combined split-button** bundling next/prev foot- and endnote; LO's normal navigation is the Navigator (F5) footnote category. Mapped to the primary-action equivalent; the grouped UI affordance is ours to build. ✓ verified vs LO source. |
| Next Footnote (menu child) | FootnoteNextWord | button | `.uno:JumpToNextFootnote` | differs | Our-layer UI | Child of the FootnoteNext split-button menu; navigates to the next footnote. — **LO:** `.uno:JumpToNextFootnote` ("To Next Footnote") exists as a standalone command, not a split-button child (LO has no such menu). Function present, packaging differs. ✓ verified vs LO source. |
| Previous Footnote (menu child) | FootnotePreviousWord | button | `.uno:JumpToPrevFootnote` | differs | Our-layer UI | Child of the FootnoteNext split-button menu; navigates to the previous footnote. — **LO:** `.uno:JumpToPrevFootnote` ("To Previous Footnote") exists as a standalone command, not a split-button child. Function present, packaging differs. ✓ verified vs LO source. |
| Next Endnote (menu child) | EndnoteNextWord | button | — | LO-missing | Optional our-layer feature | Child of the FootnoteNext split-button menu; navigates to the next endnote. — **LO:** No endnote-specific next/previous jump command — `.uno:JumpToNextFootnote`/`JumpToPrevFootnote` target footnotes only; endnote navigation is via the Navigator. No dedicated command, but next/prev-endnote navigation is app-state we could build over endnote anchors. ✓ verified vs LO source. |
| Previous Endnote (menu child) | EndnotePreviousWord | button | — | LO-missing | Optional our-layer feature | Child of the FootnoteNext split-button menu; navigates to the previous endnote. — **LO:** Same as Next Endnote — no endnote-specific previous-jump command; only footnote jumps exist. Navigation buildable in our layer. ✓ verified vs LO source. |
| Show Notes | FootnotesEndnotesShow | button | `.uno:JumpToFootnoteArea` | differs | Behavior shim | Scrolls to / displays the note area; if the document has both footnotes and endnotes it first prompts (in draft view) which to view. — **LO:** `.uno:JumpToFootnoteArea` ("Edit Footnote/Endnote") jumps from a reference mark into its note text and back; it operates **only** on a footnote/endnote anchor and toggles anchor↔note — it is NOT a general "show the notes area" command and has **no foot-vs-endnote chooser** (LO has no Draft-view notes pane). Partial functional overlap only → shim. ✓ verified vs LO source. |
| Footnote & Endnote (dialog box launcher) | FootnoteEndnoteDialog | dialog box launcher | `.uno:FootnoteDialog` | differs | Our-layer UI | Group-corner launcher; opens the Footnote and Endnote dialog (note location, number format, custom mark/symbol, start-at, numbering scheme, apply-to scope, Convert). — **LO:** Scope split — `.uno:FootnoteDialog` ("Footnote/Endnote Settings…") sets document-wide numbering/format/position but does NOT insert a note, set a custom mark/start-at for one note, or offer Convert/apply-to scope; a single custom mark uses the separate `.uno:InsertFootnoteDialog` ("Insert Special Footnote/Endnote…"), and Convert is right-click only. One Word dialog ≈ two LO dialogs + a context-menu action. ✓ verified vs LO source. |

### Research (GroupResearch)

> **Expected-conditional / version-sensitive** — web/cloud-backed; Smart Lookup was retired
> 2025-01-01 and Researcher availability is education/subscription-gated. Unverified against a
> live build.

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Research (group) | GroupResearch | group | — | LO-missing | Cut | Ribbon group container for research/search controls. — **LO:** Beyond the layout container, the whole group's web-backed functionality (Smart Lookup / Researcher) has no LO analogue; the concept plus its contents are absent. |
| Search / Smart Lookup | Insights | button | — | LO-missing | Cut | Opens the Search (formerly Smart Lookup) insights pane showing web definitions, Wikipedia entries, and related results for the selected term. (Microsoft retired Smart Lookup 2025-01-01 — see QA flags.) — **LO:** No Bing/web-insights pane. Nearest local tools are different in kind: `.uno:ThesaurusDialog` (offline thesaurus), `.uno:Translate` (translation), or a context-menu "Search the Internet" that hands the term to an external browser — none provide an in-app insights pane. ✓ verified vs LO source. |
| Researcher | Researcher | button | — | LO-missing | Cut | Opens the Researcher pane (M365) to enter a topic and get vetted, citable web sources; inserting content auto-creates a citation/source entry. — **LO:** No service that searches vetted web sources and auto-creates citation entries; LO's citation/bibliography system is a manual local database only. |

### Citations & Bibliography (GroupCitationsAndBibliography)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Citations & Bibliography (group) | GroupCitationsAndBibliography | group | — | UI-only | Our-layer UI | Ribbon group container for citation and bibliography controls. — **LO:** Layout-only container; no `.uno`. |
| Insert Citation | CitationInsert | gallery | `.uno:InsertAuthoritiesEntry` | differs | Behavior shim | Inserts an in-text citation in the current style; dropdown lists existing sources plus Add New Source and Add New Placeholder. — **LO:** Deep model difference — `.uno:InsertAuthoritiesEntry` (label "~Citation…", dialog `.uno:AuthoritiesEntryDialog`) inserts a short citation marker tied to a bibliography-DB record, **not** Word's style-formatted in-text citation; you pick from the DB or document content and may define an entry inline — no gallery of existing sources, no Source/Placeholder split, no "fill in later" concept. Same purpose, very different mechanism → shim. ✓ verified vs LO source. (Official type is **gallery**, not split-button — see QA flags.) |
| Add New Source… | BibliographyAddNewSource | button | `.uno:AuthoritiesEntryDialog` | differs | Behavior shim | Child of the Insert Citation menu; opens the Create Source dialog to enter full source details. — **LO:** No standalone "create source" command — you define a new entry from within the `.uno:AuthoritiesEntryDialog` "New" button, or edit the Bibliography Database (`.uno:BibliographyComponent`). The field set is LO's fixed schema, not Word's per-type (Book/Journal/…) templates. Reachable but not a discrete control and a different data model → shim. ✓ verified vs LO source. |
| Add New Placeholder… | BibliographyAddNewPlaceholder | button | — | LO-missing | Engine gap | Child of the Insert Citation menu; inserts a tagged citation placeholder (marked with ? in Source Manager) to fill in later. — **LO:** No citation-placeholder concept — every entry must reference an actual database record; there is no "mark with ? and complete later" workflow. Part of Word's citations/sources manager that LO's engine lacks. |
| Manage Sources | BibliographyManageSources | button | `.uno:BibliographyComponent` | differs | Behavior shim | Opens the Source Manager dialog with a Master List (reusable) and Current List (this doc), plus Copy/New/Edit/Delete/Browse, search/sort, and preview. — **LO:** `.uno:BibliographyComponent` ("Bibliography Database") opens LO's table editor — a SINGLE shared database (no Master vs per-document Current-list copy UI), a grid editor rather than a citation-preview manager, and **no live citation-style preview**. Same goal, flat-database UI vs Word's two-list manager → shim. ✓ verified vs LO source. |
| Style | BibliographyStyle | comboBox / dropdown | — | LO-missing | Engine gap | Selects the citation/bibliography style (APA, MLA, Chicago, IEEE, GOST, ISO 690, Turabian); changing it instantly reformats all in-text citations and the bibliography. — **LO:** No built-in citation-style engine and no style selector — no APA/MLA/Chicago switching. LO bibliography formatting is controlled manually via paragraph/character styles and the index-dialog Entries tab, not a named citation style. **One of the largest gaps vs Word.** |
| Bibliography | BibliographyGallery | gallery | `.uno:InsertMultiIndex` | differs | Behavior shim | Inserts a formatted reference list compiled from sources in the current style; dropdown gallery offers built-in formats (Bibliography, References, Works Cited) plus Insert Bibliography and Save Selection to Gallery. — **LO:** Inserted via the SAME unified `.uno:InsertMultiIndex` dialog (type = Bibliography) — **no** gallery of named formats, no heading-vs-no-heading split, no save-to-gallery; the list is compiled from entry markers + the database and formatted by LO's bibliography styles rather than a citation style. Same end product, different invocation and formatting model → shim. ✓ verified vs LO source. (Official type is **gallery**, not split-button — see QA flags.) |
| Insert Bibliography | BibliographyInsert | button | `.uno:InsertMultiIndex` | differs | Our-layer UI | Child of the Bibliography menu; inserts a bibliography field/list without a heading. — **LO:** Maps to the same `.uno:InsertMultiIndex` dialog (type = Bibliography); LO does not separate "with heading" from "without heading" as distinct commands — the title is a checkbox inside the dialog. No standalone command and no gallery parent. ✓ verified vs LO source. |
| Save Selection to Bibliography Gallery… | SaveSelectionToBibliographyGallery | button | — | LO-missing | Engine gap | Child of the Bibliography menu; saves the current selection as a reusable bibliography building block. — **LO:** No Building Blocks gallery — cannot save a bibliography preset. |

### Captions (GroupCaptions)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Captions (group) | GroupCaptions | group | — | UI-only | Our-layer UI | Ribbon group container for caption, table-of-figures, and cross-reference controls. — **LO:** Layout-only container; no `.uno`. |
| Insert Caption | CaptionInsert | button | `.uno:InsertCaptionDialog` | same | Free | Opens the Caption dialog to add a numbered label (Figure, Table, Equation, or custom) to the selected object — Position, Exclude label, Numbering, AutoCaption — inserting an auto-updating SEQ field. — **LO:** Strong equivalent — `.uno:InsertCaptionDialog` (label "Caption…", tooltip "Insert Caption") opens LO's Caption dialog with Category (+ New label), Numbering, Position, separator, and an Options sub-dialog (chapter-number prefix, character style); inserts an auto-updating number range. One nuance: no per-object AutoCaption toggle here (it lives in Tools > Options > Writer); core insert matches well. ✓ verified vs LO source. |
| Insert Table of Figures | TableOfFiguresInsert | button | `.uno:InsertMultiIndex` | differs | Our-layer UI | Opens the Table of Figures dialog to build a list of captioned items of a chosen label sorted by page, with page numbers, alignment, tab leader, format, and Options/Modify. — **LO:** Built via the unified `.uno:InsertMultiIndex` dialog (type = Illustration Index, or Table Index for tables); keyed off LO caption categories / object types rather than Word's caption-label-only model, and the From: chooser (captions vs object names vs a style) is structured differently. Same outcome, different dialog and source model. |
| Update Table | TableOfFiguresUpdate | button | `.uno:UpdateCurIndex` | differs | Behavior shim | Refreshes the selected table of figures, prompting page-numbers-only or entire table; enabled only when a figure table is selected. — **LO:** Same generic `.uno:UpdateCurIndex` ("Update Index") used for ALL index types — no figure-list-specific update, and (as with the TOC) **no "page numbers only vs entire table" prompt** (always a full rebuild). `.uno:UpdateAllIndexes` refreshes all. Functionally equivalent, partial-update semantics differ → shim. |
| Cross-reference | CrossReferenceInsert | button | `.uno:InsertReferenceField` | differs | Our-layer UI | Opens the Cross-reference dialog to insert a field linking to another item (heading, bookmark, figure, table, footnote, endnote, numbered item), with Reference type, Insert reference to, For which, and Insert as hyperlink. — **LO:** `.uno:InsertReferenceField` ("Cross-reference…", tooltip "Insert Cross-reference") opens the Insert Field dialog's Cross-references tab; targets are LO's own categories (Headings, Numbered paragraphs, Bookmarks, caption sequences, Foot/Endnotes, Set Reference marks) and the "Insert reference to" set is LO's. No explicit "Insert as hyperlink" checkbox — LO cross-references are always clickable. Same purpose, LO-specific taxonomy. (`.uno:JumpToReference` exists for navigation, not insertion.) ✓ verified vs LO source. |

### Index (GroupIndex)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Index (group) | GroupIndex | group | — | UI-only | Our-layer UI | Ribbon group container for index controls. — **LO:** Layout-only container; no `.uno`. |
| Mark Entry | IndexMarkEntry | button | `.uno:InsertIndexesEntry` | differs | Our-layer UI | Opens the Mark Index Entry dialog (main entry/subentry, cross-reference or page-range, bold/italic page-number format, Mark / Mark All), inserting hidden XE fields; shortcut Alt+Shift+X. — **LO:** `.uno:InsertIndexesEntry` ("Insert Index Entry") opens LO's dialog: Index = "Alphabetical Index", main entry + 1st/2nd key (subentries), "Apply to all similar texts" (≈ Mark All), stays open. Differences: only two sub-levels, **no bold/italic page-number-format option** (page-number weight comes from index styles), page-ranges handled differently, and **no default shortcut** (no Alt+Shift+X equivalent). Same purpose, reduced per-entry formatting. ✓ verified vs LO source. |
| Insert Index | IndexInsert | button | `.uno:InsertMultiIndex` | differs | Our-layer UI | Opens the Index dialog to compile all marked XE entries — type (indented/run-in), columns, language, right-align page numbers, tab leader, Formats gallery/preview, AutoMark, Modify. — **LO:** Again the unified `.uno:InsertMultiIndex` dialog (type = Alphabetical Index): columns, language/key sorting, combine-identical-entries, case sensitivity, AutoMark via a concordance file, Entries/Styles tabs. Differences: indented-vs-run-in expressed differently, the Formats gallery replaced by editable index styles, and it is the same multi-purpose dialog. Comparable capability, different packaging. |
| Update Index | IndexUpdate | button | `.uno:UpdateCurIndex` | same | Free | Regenerates the existing index so newly marked/edited XE entries and current page numbers are reflected; no dialog. — **LO:** Close equivalent — `.uno:UpdateCurIndex` ("Update Index") regenerates the index the cursor is in with no dialog. Unlike TOC/figures Update Table, Word's Index update is also a no-prompt in-place refresh, so the parity here is genuine. ✓ verified vs LO source. |

### Table of Authorities (GroupTableOfAuthorities)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Table of Authorities (group) | GroupTableOfAuthorities | group | — | UI-only | Our-layer UI | Ribbon group container for table-of-authorities controls. — **LO:** Layout-only container; no `.uno` (the feature it hosts is itself LO-missing — see the rows below). |
| Mark Citation | CitationMark | button | — | LO-missing | Engine gap | Opens the Mark Citation dialog to mark a legal citation (long citation text, category such as Cases/Statutes, short citation, Next Citation, Mark / Mark All), inserting hidden TA fields; shortcut Alt+Shift+I. — **LO:** No legal table-of-authorities feature at all — no concept of long/short legal citations, legal categories, Next Citation, or TA fields. (The bibliography `.uno:InsertAuthoritiesEntry` is literature references, NOT legal authorities, despite the name.) No Alt+Shift+I equivalent. ✓ verified vs LO source. |
| Insert Table of Authorities | TableOfAuthoritiesInsert | button | — | LO-missing | Engine gap | Opens the Table of Authorities dialog to compile marked TA citations into a table grouped by legal category, with selected/All categories, use "passim", keep original formatting, Formats style, and tab leader. — **LO:** No table-of-authorities feature — the unified index dialog has **no "Table of Authorities" type** and there are no TA marks to compile. Do NOT map to the LO bibliography despite the similar name. ✓ verified vs LO source. |
| Update Table | TableOfAuthoritiesUpdate | button | — | LO-missing | Engine gap | Rebuilds the selected table of authorities so added/deleted/moved/edited citations and page numbers are current; enabled only when the TOA is selected. — **LO:** With no table-of-authorities feature, nothing to update — the generic `.uno:UpdateCurIndex` has no authorities-table type to act on. ✓ verified vs LO source. |

### Acronyms (GroupAcronyms)

> Modern Microsoft 365 organization/Graph-backed group. **Expected-conditional / version-sensitive**
> — present on TabReferences in the M365 Current Channel control list (verified) but absent from
> Office 2019 and org/Graph-gated; unverified against a live build.

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Acronyms (group) | GroupAcronyms | group | — | LO-missing | Cut | Ribbon group container for the Acronyms control; present only in Microsoft 365 Current Channel builds, not Office 2016/2019. — **LO:** Both a layout container and a feature with no LO analogue — LO has no organization-wide acronyms service. (Conditional — M365 / Graph-gated.) |
| Acronyms | Acronyms | button | — | LO-missing | Cut | Opens the Acronyms task pane (M365-only) showing acronyms defined across the organization's documents. — **LO:** No equivalent — a cloud/M365-graph-backed feature; LO has no organizational acronyms pane or cross-document term service. (Conditional — M365 / Graph-gated.) |

---

## LO-source verification

These mappings were checked against the vendored LibreOffice tree at
`apps/ms-word/libreoffice-codebase/` and **override** the mapped rows where they conflicted.
Two are **material corrections** (footnote/endnote shortcuts; Remove Table of Contents); the rest
**confirm** the mapped command, label, slot and verdict. No item came back UNCERTAIN.

**Material corrections (CORRECTED):**

- **Insert Footnote — shortcut** — the mapping claimed "Ctrl+Alt+F matches Word." Wrong:
  `.uno:InsertFootnote` has **no default keyboard shortcut** in this tree — it is absent from both
  PrimaryKeys and SecondaryKeys in `Accelerators.xcu`. In the Writer block, F_MOD1_MOD2 (Ctrl+Alt+F)
  maps to `.uno:SearchDialog` (macosx/de only), not footnote insertion. Command name and insert
  behavior (auto-numbered note, cursor moves to note) are correct. Evidence:
  `Accelerators.xcu` (no InsertFootnote node; F_MOD1_MOD2 → SearchDialog at line 6654);
  `sw/sdi/swriter.sdi:3121` (FN_INSERT_FOOTNOTE); `sw/source/uibase/shells/textsh1.cxx:1183-1193`.
- **Insert Endnote — shortcut** — the mapping claimed "Ctrl+Alt+D matches Word." Wrong:
  `.uno:InsertEndnote` has **no default keyboard shortcut** in this tree (absent from
  `Accelerators.xcu`). D_MOD1 (Ctrl+D) maps to `.uno:UnderlineDouble`; there is no D_MOD1_MOD2
  binding at all. Command name and insert-at-document-end behavior are correct. Evidence:
  `Accelerators.xcu` (no InsertEndnote node; D_MOD1 → UnderlineDouble at line 6395);
  `sw/sdi/swriter.sdi:3033` (FN_INSERT_ENDNOTE); `textsh1.cxx:1184,1193`.
- **Remove Table of Contents — loUno / verdict** — the mapping asserted LO has "no dedicated
  remove-index command… LO-missing." Wrong: `.uno:RemoveTableOf` exists (slot FN_REMOVE_CUR_TOX,
  label "Delete Index"), flagged AccelConfig=TRUE, MenuConfig=TRUE, ToolBoxConfig=TRUE — fully
  dispatchable to menu/toolbar/shortcut. It deletes the index the cursor is in. Verdict softened
  **LO-missing → differs**; loUno set to `.uno:RemoveTableOf` (default surfacing is the context
  menu / no Word-style gallery). Evidence: `WriterCommands.xcu:238-245`;
  `sw/sdi/swriter.sdi:5420-5435`.

**Confirmed (CONFIRMED) — command/label/slot/verdict match the mapping:**

- **Insert Citation / Add New Source — label** — in this tree the visible label for **both**
  `.uno:InsertAuthoritiesEntry` and `.uno:AuthoritiesEntryDialog` is "~Citation…" (not the older
  "Insert Bibliography Entry" wording the notes cited). Command names, slots
  (FN_INSERT_AUTH_ENTRY_DLG / FN_EDIT_AUTH_ENTRY_DLG) and the bibliography-DB-backed mapping are
  correct; only the cited label text was off. Evidence: `WriterCommands.xcu:178-181`, `:576-579`;
  `sw/sdi/swriter.sdi:2613`, `:311`.
- **Mark Entry — shortcut** — `.uno:InsertIndexesEntry` (FN_INSERT_IDX_ENTRY_DLG, label "Insert
  Index Entry") has **no default keyboard shortcut** (no Alt+Shift+X equivalent), confirming the
  mapping. Evidence: `WriterCommands.xcu:913-916`; `sw/sdi/swriter.sdi:3224`; `Accelerators.xcu`
  (no InsertIndexesEntry node).
- **Table of Contents — loUno / label** — `.uno:InsertMultiIndex` exists (FN_INSERT_MULTI_TOX),
  label "Table of Contents", tooltip "Insert Table of Contents, Index or Bibliography", dispatched
  with a SwTOXBase pointer — confirming the single multi-type TOX entry point. Evidence:
  `WriterCommands.xcu:164-176`; `sw/sdi/swriter.sdi:3427`; `sw/source/uibase/utlui/content.cxx:7005-7008`.
- **Update Table (TOC) — loUno / label** — `.uno:UpdateCurIndex` (FN_UPDATE_CUR_TOX) label "Update
  Index"; `.uno:UpdateAllIndexes` label "Update All". Both match. Evidence: `WriterCommands.xcu:224-233`,
  `:210-219`; `sw/sdi/swriter.sdi:6863`.
- **Next/Previous Footnote — loUno / label** — `.uno:JumpToNextFootnote` ("To Next Footnote") and
  `.uno:JumpToPrevFootnote` ("To Previous Footnote") both exist as standalone slots
  (FN_NEXT_FOOTNOTE / FN_PREV_FOOTNOTE) — not a split-button. Evidence: `WriterCommands.xcu:2746-2749`,
  `:2756-2759`; `sw/sdi/swriter.sdi:3954`, `:4039`.
- **Next/Previous Endnote — loUno / verdict** — confirmed LO-missing: no JumpToNextEndnote /
  JumpToPrevEndnote (or any endnote-specific jump) slot exists; only the footnote jumps. Evidence:
  `sw/sdi/swriter.sdi` (no endnote-jump matches; only JumpToNextFootnote :3954 / JumpToPrevFootnote :4039).
- **Show Notes — loUno / label** — `.uno:JumpToFootnoteArea` (FN_TO_FOOTNOTE_AREA) label "Edit
  Footnote/Endnote". Evidence: `WriterCommands.xcu:2849-2852`; `sw/sdi/swriter.sdi:7328`.
- **Footnote & Endnote dialog — split** — confirmed: `.uno:FootnoteDialog` (FN_FORMAT_FOOTNOTE_DLG,
  "~Footnote/Endnote Settings…") and `.uno:InsertFootnoteDialog` (FN_INSERT_FOOTNOTE_DLG, "Insert
  Special F~ootnote/Endnote…") — the two-command split is real (`.uno:EndnoteDialog` /
  `.uno:CurrentFootnoteDialog` also alias the settings dialog). Evidence: `WriterCommands.xcu:1652-1654`,
  `:707-710`, `:1660-1666`, `:1671-1673`; `sw/sdi/swriter.sdi:1359,3103,1377`.
- **Insert Caption — loUno / label** — `.uno:InsertCaptionDialog` confirmed; node label "Caption…",
  tooltip "Insert Caption", PopupLabel "Insert Caption…" (FN_INSERT_CAPTION). Evidence:
  `WriterCommands.xcu:693-705`; `sw/sdi/swriter.sdi:2801`.
- **Cross-reference — loUno / label** — `.uno:InsertReferenceField` (FN_INSERT_REF_FIELD)
  "Cross-~reference…", tooltip "Insert Cross-reference"; `.uno:JumpToReference` ("To Reference")
  exists separately for navigation. Evidence: `WriterCommands.xcu:712-717`, `:2592-2595`;
  `sw/sdi/swriter.sdi:3658`.
- **Manage Sources — loUno / label** — `.uno:BibliographyComponent` label "~Bibliography Database"
  (defined in GenericCommands.xcu, not WriterCommands.xcu). Evidence: `GenericCommands.xcu:2585-2588`.
- **Table of Authorities (group) — verdict** — confirmed LO-missing for the legal-TOA feature: no
  MarkCitation/TableOfAuthorities slot exists; the only "Authorities" slots are the bibliography
  ones (InsertAuthoritiesEntry / AuthoritiesEntryDialog), which are literature references, not
  legal authorities — consistent with the mapping's warning. Evidence: `sw/sdi/swriter.sdi` (no
  TableOfAuthorities/MarkCitation matches; only AuthoritiesEntryDialog :311 and InsertAuthoritiesEntry :2613).
- **Search / Smart Lookup — nearest analogues** — confirmed the cited LO commands exist:
  `.uno:ThesaurusDialog` ("~Thesaurus…") and `.uno:Translate` ("Translate…"). The LO-missing
  verdict for a web-insights pane stands — no such command found. (Translate's DeepL backing is a
  runtime detail not verifiable from config/slot files; command existence is confirmed.) Evidence:
  `WriterCommands.xcu:1587-1590` (Translate), `:3125-3128` (ThesaurusDialog).

> **Scope caveat from the LO-verify pass.** The "LO-missing" rows for genuinely MS-only features
> (Researcher, Smart Lookup web-insights, citation Style engine, Add New Placeholder, the whole
> Table of Authorities feature, the Save-to-Gallery building blocks, Acronyms) were verified by
> targeted searches finding **no** matching `.uno` nodes; the absence claims are consistent with
> the catalog. Verification budget was concentrated on present-command facts and the suspect
> shortcut / Remove-TOC claims.

---

## Conditional / version-sensitive controls

There is **no owner screenshot for the References tab yet**, so the following are flagged
**expected-conditional, unverified against a live build** — a screenshot sweep would confirm
whether (and how) they surface. They are not contradicted by the inventory; they simply depend on
SKU / version / tenant state, or have drifted temporally.

- **Acronyms group (Acronyms group + Acronyms)** — Microsoft 365 Current Channel only (verified
  present in the M365 control list, Policy IDs 33612/33613; absent from Office 2019). Org/Graph-
  gated — may be hidden when no organizational acronyms service is provisioned.
- **Search / Smart Lookup (Insights)** — Microsoft **retired Smart Lookup effective 2025-01-01**.
  The idMso still exists in the M365 list and the button may still render, but it no longer
  performs its web-insights lookup. The inventory's present-tense behavior note reflects the
  historical function; a current-Word screenshot would confirm present rendering/behavior.
- **Researcher** — availability has been narrowing in M365 and is education/subscription-gated; a
  screenshot confirms whether the button still appears in the Research group in the targeted build.
- **Control-type / split-vs-gallery rendering** — `TableOfContentsGallery`, `CitationInsert`, and
  `BibliographyGallery` are official type **gallery** (a dropdown button that opens a gallery/menu),
  **not** split-buttons; on TabReferences the only true splitButton is `FootnoteNext`. A screenshot
  disambiguates that their top half opens the gallery rather than firing a split primary action.
- **BibliographyStyle (Style combo)** — the available citation-style list changes by Word
  version/build and the combo can be greyed depending on the selected source format; a screenshot
  confirms its present rendering and current style list.

---

## Out of scope

- **Engine gap — scholarly apparatus (the true engine blockers, 7 controls).** Three clusters:
  (1) **Word's citation-style engine + placeholder** — the `Style` APA/MLA/Chicago/IEEE selector
  that instantly reformats all citations and the bibliography, and `Add New Placeholder` ("mark
  with ? and complete later"); LO's bibliography is a manual local database with no named-style
  reformatting and no placeholder concept (the single largest gap). (2) **Table of Authorities** —
  Mark Citation, Insert Table of Authorities, Update Table; LO has no legal TA marks, categories,
  `passim`, or TOA index type at all (do not confuse with LO's literature bibliography). (3)
  **Save-to-gallery building blocks** — Save Selection to TOC / Bibliography Gallery; the same
  Building-Blocks engine gap seen on every tab. Cut now, or accept reduced fidelity. This is the
  band that would matter if the engine were ever reconsidered.
- **Cloud / AI / M365 (cut by product choice).** **Research panes** — Smart Lookup (retired
  2025-01-01) / Researcher / the Research group host, all web/cloud-backed with no LO analogue —
  plus the **Acronyms** group (group + button), an organization/Graph-backed M365 service. No
  engine equivalent and no place in a local clone's scope.
- **Optional our-layer features (LO lacks the discrete control, but it's app-state we could
  build).** **Add Text** (set a paragraph's TOC outline level — LO already stores outline level as
  a paragraph property; we'd wrap a dropdown over it) and **Next/Previous Endnote** navigation (LO
  has footnote jumps and a Navigator endnote category; endnote next/prev is buildable over endnote
  anchors).

---

## QA flags & resolutions

From `result.qa`. The Word/idMso side was set-diffed against the official `wordcontrols.xlsx`
(Office 2019 + M365 Current Channel, filtered to `Tab=TabReferences`): **all 44 named controls are
present, none missing**, and every idMso is a valid official identifier. The LO-source pass
resolved the shortcut and Remove-TOC defects. Because there is **no owner screenshot for this
tab**, the M365-only / temporally-drifting rows remain **screenshot-pending**.

| QA flag | Status | Resolution |
|---|---|---|
| Three controls typed "split-button / gallery"? | **Resolved (source set-diff)** | `TableOfContentsGallery`, `CitationInsert`, `BibliographyGallery` are official type **gallery** (a dropdown button opening a gallery/menu), not split-buttons (verified in 2019 + M365). On TabReferences the only `splitButton` is `FootnoteNext`. Type corrected to "gallery" in the inventory; the "top-half / split primary action" framing softened — clicking a gallery opens the dropdown. Buckets unchanged. |
| Footnote/Endnote default shortcuts "match Word"? | **Resolved (LO source)** | Wrong — neither `.uno:InsertFootnote` nor `.uno:InsertEndnote` has any default accelerator in this tree (Accelerators.xcu has no such bindings; Ctrl+D = UnderlineDouble). The "Ctrl+Alt+F / Ctrl+Alt+D matches Word" parity claims removed. Verdict (same) and core insert behavior unchanged. |
| Remove Table of Contents = LO-missing? | **Resolved (LO source)** | Wrong — `.uno:RemoveTableOf` (FN_REMOVE_CUR_TOX, "Delete Index", AccelConfig/MenuConfig/ToolBoxConfig=TRUE) is a discrete dispatchable command. Verdict softened LO-missing → differs; loUno = `.uno:RemoveTableOf`. Bucket Our-layer UI. |
| Citation/bibliography LO label "Insert Bibliography Entry"? | **Resolved (LO source)** | In this tree both `.uno:InsertAuthoritiesEntry` and `.uno:AuthoritiesEntryDialog` carry the visible label "~Citation…". Notes updated; command names/slots and the bibliography-DB-backed mapping (Add New Source → `.uno:AuthoritiesEntryDialog`, Add New Placeholder → LO-missing) are sound. |
| `Insights` (Smart Lookup) described as a live web pane? | **Open (screenshot-pending)** | Microsoft retired Smart Lookup 2025-01-01; the idMso persists and the button may still render but no longer performs the web lookup. Behavior note flags the retirement; the LO-missing verdict is unaffected. A current-Word screenshot would confirm present rendering. |
| Acronyms / GroupAcronyms idMso speculative? | **Resolved (source set-diff)** | Verified, not speculative — absent from Office 2019 but present on TabReferences in M365 Current Channel (GroupAcronyms Policy ID 33612, Acronyms 33613). "M365-only" annotation and LO-missing/Cut verdict correct; org/Graph-gating still warrants a screenshot. |
| Researcher still on the tab? | **Open (screenshot-pending)** | Researcher availability has narrowed in M365 (education/subscription-gated); a screenshot of the targeted build confirms whether it still renders in the Research group. Engine-gap bucket unaffected. |
| Anonymous gallery children (Built-In TOC styles, Office.com, Manual Table) not enumerated? | **Resolved (source)** | Correct to omit — these are gallery *contents*, not separately-idMso'd ribbon controls (matching Microsoft's empty-Name rows). The Word built-in gallery does include a "Manual Table" preset, so the LO-vs-Word manual-TOC gap note is accurate. |
| Non-References idMsos excluded? | **Resolved (source)** | Verified "Not in the Ribbon" and rightly absent (e.g. EndnoteOrFootnoteConvert, GoToFootnote/GoToEndnote, TableOfContentsRebuild, **CustomTableOfContentsGallery**, AutoMarkIndexEntries, CaptionInsertWord). In particular CustomTableOfContentsGallery is off-ribbon — so mapping "Custom Table of Contents…" to `TableOfContentsDialog` (the in-ribbon button) was right. |
| Completeness confidence? | **HIGH (named-control set)** | All 44 named TabReferences controls present in 2019 + M365; nothing missing; every idMso valid. Residual uncertainty is not completeness but: (1) the three control-TYPE mislabels (now corrected); (2) temporal drift (Smart Lookup retired, Researcher gating); (3) a few LO-side notes already fixed by the LO-source pass. M365-only conditional-visibility per tenant is the main reason Acronyms/Researcher/Insights warrant a real-Word screenshot. |
