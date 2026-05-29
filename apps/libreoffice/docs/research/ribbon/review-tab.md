# Review tab — Word ↔ LibreOffice

> **Status.** Word build: Microsoft 365 (target). **Word-side: web-sourced + LO-verified —
> screenshot-pending.** LO-side: high. Produced by the per-tab pipeline: 3 independent extractors →
> reconciled canonical → mapped to LO `.uno:` → verified against the LibreOffice source tree. The
> Word/idMso side was set-diffed against the official `wordcontrols.xlsx` (M365 Current Channel,
> `Tab='TabReviewWord'`) and is complete — every one of the 99 distinct non-group controls is
> present, **zero real controls missing**; one inventory idMso (`ReviewSpellingAndGrammar` on the
> Editor row) is **fabricated** (see [QA flags](#qa-flags--resolutions)). The LO command facts were
> checked against the vendored LO tree. **No owner screenshot exists for this tab yet**, so
> conditional/version-sensitive controls below are *expected-conditional, unverified against a live
> build*. Three mappings carry **material LO-source corrections** (Thesaurus shortcut, Delete-All
> loUno, Translate scope); 16 more are confirmed and 2 remain UNCERTAIN (see
> [LO-source verification](#lo-source-verification)).

This is **Word-clone decision-research**, not LibreOffice documentation. It diffs every Word
Review-tab control against LO's command surface and classifies the **work** each diff implies.
Bucket vocabulary and verdict meanings are in [README.md](README.md#legend).

---

## Outcome

Of 104 catalogued Word Review-tab controls, **18 wire straight through** to an existing LO `.uno:`
command (Free), and the dominant band — **37 — is behavior shim**: LO has the underlying
redline / comment / compare / protect capability, but Word splits it into split-button menus,
markup-category filters, per-author scopes, balloon presentations, and compose-and-stop combos that
we have to orchestrate in our dispatch layer. A further 23 are **our-layer UI** (the command exists;
only the dialog/menu/pane host differs). The decisive number for the engine decision is
**Engine gap = 11** — and unlike the Insert tab (where the gap was Word's Building-Blocks system),
the Review-tab gap is **narrow and specific: Ink (handwriting) and Read-Aloud TTS**. The **Cut**
pile (12) is cloud/co-authoring/version-history (Editor AI scan, Translator pane / Mini Translator,
co-authoring Block-Authors locks, server version-history compare). Three controls are app-state we
could *optionally* build.

| Work bucket | Count | What it is |
|---|---:|---|
| **Free** | 18 | wire the existing LO `.uno:` command, no UI work |
| **Our-layer UI** | 23 | build the Word-faithful menu/pane/dialog host; dispatch the LO command |
| **Behavior shim** | 37 | intercept/massage in our dispatch layer; LO has the capability but semantics/host differ |
| **Engine gap** | 11 | LO engine genuinely can't; cut or accept reduced fidelity |
| **Cut** | 12 | out of scope by product choice (cloud/AI, co-authoring, server version history) |
| **Optional our-layer feature** | 3 | LO lacks it but it's app-state we could build |
| **Total** | **104** | |

**Decisive learning:** on Review the engine gap is the **smallest of any tab so far — Engine gap =
11 / 104 (~11%)** — and it is **entirely two clusters: Ink/handwriting (8: ink comments + ink markup
toggle + the whole Ink group) and a thin "no LO equivalent at all" set (Read Aloud TTS, Focus-mode
view, Japanese consistency checker)**. Crucially, LO's engine **fully backs Word's core
Track-Changes workflow** — record, show, accept/reject (this/next/all), navigate prev/next, manage,
comments + resolve, compare, merge, protect-changes all exist as real `.uno:` commands. Every other
Review diff is shim/UI work over commands LO already has. → strongly supports **LO-via-LOK + scoped
parity**, with Ink and Read-Aloud the only honest engine cuts.

> **Recurring behavior-shim theme.** Word's Review tab is dominated by **split buttons**
> (Track Changes, Accept, Reject, Reviewing Pane, Delete-comment, Show-Comments) and **markup
> presentation controls** (Display-for-Review's 4 modes, the Show-Markup category menu, Balloons
> submenu, per-reviewer filter). LO provides the *atomic* commands — a single record toggle, flat
> Accept/Reject/Accept-All buttons, one Show-Tracked-Changes toggle, one Show-Comments toggle, a
> modal Manage-Tracked-Changes dialog — but **none of the split-button containers, no markup
> filter, no balloons, no per-author scope**. The repeated shape of work is therefore *orchestrating
> existing LO commands behind a Word-faithful menu/filter/scope shim*, not adding engine capability.

---

## Inventory

One subsection per Word ribbon group. `LO .uno:` is the mapped LibreOffice command (`—` = none).
`work` is the bucket from the table above. Rows touched by the LO-source corrections are marked
**✓ verified vs LO source** in the note.

### Proofing (GroupProofing)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Editor | ReviewSpellingAndGrammar | button | `.uno:SpellingAndGrammarDialog` | differs | Behavior shim | Opens the M365 Editor task pane (right side) that scans the whole doc for spelling, grammar plus refinement categories (clarity, conciseness, formality, inclusiveness) as grouped issue cards. — **LO:** No "Editor" concept; the closest entry is `.uno:SpellingAndGrammarDialog` (label "Spelling"), a classic modal one-error-at-a-time dialog. No refinement/clarity/inclusiveness categories, no right-side issue-card pane, no whole-document score — only the underlying spell+grammar pass is comparable, so we orchestrate the AI-pane layer ourselves. ✓ verified vs LO source. (Note: idMso `ReviewSpellingAndGrammar` is **fabricated** — see QA flags.) |
| Spelling & Grammar / Check Document | SpellingAndGrammar | button | `.uno:SpellingAndGrammarDialog` | same | Free | F7 proofing pass; classic mode opens the Spelling & Grammar dialog one error at a time with Change/Ignore/Add to Dictionary. — **LO:** Strong 1:1 — `.uno:SpellingAndGrammarDialog` is also F7 (label "Spelling"), one error at a time with Correct/Ignore Once/Ignore All/Add. LO grammar uses a bundled checker and never surfaces in a side pane, but as a button-that-launches-the-dialog this is `same`. ✓ verified vs LO source. |
| Editor / Check Document | WritingAssistanceCheckDocument | button | `—` | LO-missing | Cut | Runs the Editor writing-assistance document check. — **LO:** No Editor service and no document-level writing-assistance check — this is the cloud/AI Editor scan, out of scope by product choice. |
| Thesaurus | Thesaurus | button | `.uno:ThesaurusDialog` | same | Free | Opens Thesaurus pane for the cursor/selected word; synonyms grouped by sense plus antonyms; Insert replaces the word; Shift+F7. — **LO:** Good match — `.uno:ThesaurusDialog` shows synonyms grouped by meaning with a language picker and Replace. Two LO deltas: it is a **modal dialog** (not a docked pane), and its shortcut is **Ctrl+F7**, not Word's Shift+F7 (Shift+F7 in LO is Auto Spellcheck). ✓ verified vs LO source. |
| Word Count | WordCount | button | `.uno:WordCountDialog` | same | Free | Word Count dialog: pages/words/characters (with and without spaces)/paragraphs/lines for document or selection. — **LO:** Close — `.uno:WordCountDialog` (label "Word Count…") reports words and characters (with/without spaces) for document and selection, live. Leaner: no pages/paragraphs/lines breakout and no textbox/footnote option (those live on the status bar). ✓ verified vs LO source. |
| Quick Check (split) | SplitButtonQuickCheck | splitButton | `—` | LO-missing | Behavior shim | Split button toggling a quick proofing check with a menu of quick-check options. — **LO:** No split control, but the one overlapping piece — as-you-type spelling — is the standalone `.uno:SpellOnline` toggle; we orchestrate the "quick check" container over it. (Source-A-only Word control.) |
| Quick Check | QuickCheck | button | `—` | LO-missing | Behavior shim | Primary action of the Quick Check split button. — **LO:** No 1:1 command; backed by the `.uno:SpellOnline` as-you-type toggle in our dispatch layer. (Source-A-only.) |
| Check Spelling As You Type | QuickCheckSpelling | toggleButton | `.uno:SpellOnline` | same | Free | Toggles as-you-type spelling (red squiggles). — **LO:** Functional match — `.uno:SpellOnline` (label "Auto Spellcheck", a toggle, also Shift+F7) draws the red wavy underlines. Different placement (standalone toggle vs inside Word's Quick-Check menu); `same` at the action level. ✓ verified vs LO source. |
| Check All Proofing | QuickCheckAll | toggleButton | `—` | LO-missing | Behavior shim | Toggles checking all proofing categories. — **LO:** No single "all proofing categories" toggle; auto grammar follows the spell-as-you-type / Options setting, so we shim a combined toggle over the existing pieces. |

### Speech (GroupSpeech)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Read Aloud | ReadAloud | button | `—` | LO-missing | Engine gap | Text-to-speech playback from the cursor with word highlighting and a floating play/pause/next control; Ctrl+Alt+Space. — **LO:** No Read Aloud, no TTS, no Speech group anywhere in the 1520-command catalog (only the separate "Read Text" extension, not a core command). Genuine engine absence. (Word controlType is officially `button`, not toggleButton — see QA flags.) |

### Accessibility (GroupAccessibility)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Check Accessibility (split) | MenuAccessibility | splitButton | `.uno:AccessibilityCheck` | differs | Our-layer UI | Split button: primary runs the checker and opens the Accessibility Assistant pane with explained issues and one-click fixes; arrow opens an accessibility menu (Alt Text, navigation, Focus, Options). — **LO:** `.uno:AccessibilityCheck` (label "Accessibility Check…", TargetURL `.uno:SidebarDeck.A11yCheckDeck`) is a **single button**, not a split — no attached menu, no Alt Text / Navigation / Focus / Options items, and it lists issues without Word's guided one-click fix cards. ✓ verified vs LO source. |
| Check Accessibility | AccessibilityChecker | button | `.uno:AccessibilityCheck` | differs | Our-layer UI | Primary action: runs the Accessibility Checker and opens its results pane. — **LO:** `.uno:AccessibilityCheck` runs the checker and opens the A11y sidebar deck — a flat issue list to fix manually, not Word's categorized "Accessibility Assistant" with inline remediation. LO also has a companion `.uno:AccessibilityCheckOnline` toggle with no Word counterpart. ✓ verified vs LO source. |
| Alt Text | AltTextPaneRibbon | toggleButton | `—` | LO-missing | Behavior shim | Toggles the Alt Text pane for the selected object. — **LO:** No toggleable Alt Text pane, but the **capability exists**: alt text (Text Alternative / Description) is edited per-object via the object's right-click "Description…" dialog, which we orchestrate behind a pane. |
| Navigation Pane | ShowNavigationPaneNewInAccCheckerSplitButton | toggleButton | `.uno:Navigator` | differs | Our-layer UI | Toggles the Navigation pane (from the accessibility menu). — **LO:** `.uno:Navigator` (F5) toggles a docked headings/tables/objects panel — comparable pane, but not reachable from any accessibility menu and lives on the View tab/sidebar; Word's reading-order emphasis has no LO equivalent. ✓ verified vs LO source. |
| Focus | ViewFocusModeView | toggleButton | `—` | LO-missing | Engine gap | Toggles Focus mode view. — **LO:** No Focus-mode command; LO has no distraction-free reading view. Genuine absence. |
| Accessibility Options | OpenOptionsEaseOfAcess | button | `—` | differs | Our-layer UI | Opens the Ease of Access page of Word Options. — **LO:** Accessibility settings exist under Tools > Options > LibreOffice > Accessibility, but no `.uno` jumps straight there (Options opens at the last-used page). Settings exist; only the one-click jump is our-layer. |

### Language (GroupLanguage)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Translate | TranslateMenu | menu | `.uno:Translate` | differs | Our-layer UI | Menu of translation commands (Translate Selection → Translator pane, Translate Document → new copy, Mini Translator, options). — **LO:** `.uno:Translate` ("Translate…", LO 24.2+) machine-translates via a configured DeepL key, but it is a **single command, not a menu**; no Translator pane, no Mini Translator, no built-in cloud service. The menu container is our-layer over the one command. ✓ verified vs LO source. |
| Translate Selection | TranslatorLookup | button | `.uno:Translate` | differs | Behavior shim | Translates the current selection (Translator lookup) with an option to Insert the result. — **LO:** `.uno:Translate` translates the selection in place (DeepL) — no preview/Translator pane, no per-result Insert button; it opens a target-language dialog then replaces directly. Same intent, different mechanism → shim. ✓ verified vs LO source. |
| Translate Document (Translator) | TranslatorDocument | button | `.uno:Translate` | LO-missing | Behavior shim | Translates the whole document via Translator into a new copy. — **LO:** **Corrected:** `.uno:Translate` is **not** selection-only — its handler (`SwTranslateHelper::TranslateDocument`) translates the whole document when there is no selection, so whole-document machine translation already exists via the one command (no separate command, no new copy). The earlier "LO-missing" framing was too strong. ✓ verified vs LO source. |
| Translate Document | TranslateDocument | button | `.uno:Translate` | LO-missing | Behavior shim | Translates the document. — **LO:** **Corrected:** same as above — the single `.uno:Translate` already covers whole-document translation (likely a Word-side duplicate of TranslatorDocument). ✓ verified vs LO source. |
| Translation Pane | TranslationPane | button | `—` | LO-missing | Cut | Opens the translation task pane. — **LO:** No Translator task pane; `.uno:Translate` acts on the document without a pane. Cloud/AI pane, out of scope. |
| Mini Translator | MiniTranslator | toggleButton | `—` | LO-missing | Cut | Toggles the on-hover Mini Translator. — **LO:** No hover-to-translate Mini Translator. Cloud/AI feature, out of scope. |
| Translator Preferences | TranslatorPreferences | button | `—` | LO-missing | Optional our-layer feature | Opens Translator preferences. — **LO:** LO's only translation setting (DeepL API URL/key) lives in Tools > Options, not as a Review control — app-state we could surface ourselves. |
| Set Translation Language | TranslationLanguageOptions | button | `—` | LO-missing | Optional our-layer feature | Opens translation language options. — **LO:** No command to choose a translation target language as a Review control; the DeepL target is configured in Options — app-state we could build. |
| Language | LanguageCommands | menu | `.uno:LanguageMenu` | differs | Our-layer UI | Menu of proofing/language commands (Set Proofing Language, Language Preferences, East-Asian tools). — **LO:** `.uno:LanguageMenu` ("Language") is a comparable menu container (plus `.uno:LanguageStatus`), but its children are LO-specific — For Selection / Paragraph / All Text, "More…" → Character dialog, "None (Do not check spelling)". ✓ verified vs LO source. |
| Set Proofing Language | SetLanguage | button | `.uno:SetLanguageSelectionMenu` | differs | Our-layer UI | Opens the Language dialog to mark the selection's proofing language and toggle "Do not check spelling". — **LO:** `.uno:SetLanguageSelectionMenu` (label "For Selection") is a cascading language-list submenu (language list, "None (Do not check spelling)", "Reset to Default", "More…") rather than one checkbox dialog; same end effect, different UI. ✓ verified vs LO source. |
| Language Preferences | LanguagePreferences | button | `—` | differs | Our-layer UI | Opens the Language page of Word Options (editing/authoring/display languages). — **LO:** Equivalent settings live at Tools > Options > Language Settings > Languages, but no `.uno` opens that page directly. Settings exist; only the one-click control is our-layer. |
| Japanese Consistency Checker | ReviewJapaneseConsistencyChecker | button | `—` | LO-missing | Engine gap | Runs the Japanese consistency checker (East-Asian only). — **LO:** LO has Asian tools (Ruby, Hangul/Hanja, Chinese conversion) but no Japanese consistency/usage checker. Genuine absence. (Conditional — East-Asian build.) |
| Update IME Dictionary | ImeDictionaryUpdate | button | `—` | LO-missing | Cut | Updates the IME dictionary (East-Asian only). — **LO:** LO relies on the OS-level IME and has no command to sync/update an IME dictionary. Niche East-Asian, out of scope. (Conditional.) |
| Hangul/Hanja Conversion | HangulHanjaConversion | button | `.uno:HangulHanjaConversion` | same | Free | Opens Hangul/Hanja conversion (Korean, East-Asian only). — **LO:** Direct match — `.uno:HangulHanjaConversion` ("Hangul/Hanja Conversion…") opens the equivalent Korean conversion dialog; both contextual on Asian support. ✓ verified vs LO source. (Conditional — East-Asian build.) |

### Chinese Translation (GroupChineseTranslation) — contextual, East-Asian editing only

> East-Asian-only Word group. **Expected-conditional / version-sensitive** — present only when Asian-language editing is enabled, and unverified against a live build.

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Chinese: To Simplified | TranslateToSimplifiedChinese | button | `.uno:ChineseConversion` | differs | Behavior shim | Converts the selection to Simplified Chinese (East-Asian contextual). — **LO:** `.uno:ChineseConversion` ("Chinese Conversion…") is a single dialog where direction (Traditional→Simplified or reverse) is a radio choice; Word's one-click "To Simplified" button becomes a dialog-direction shim. ✓ verified vs LO source. (Conditional.) |
| Chinese: To Traditional | TranslateToTraditionalChinese | button | `.uno:ChineseConversion` | differs | Behavior shim | Converts the selection to Traditional Chinese (East-Asian contextual). — **LO:** Same `.uno:ChineseConversion` dialog with the Simplified→Traditional radio; no standalone one-click button → direction shim. ✓ verified vs LO source. (Conditional.) |
| Chinese Translation Options | ChineseTranslationDialog | button | `.uno:ChineseConversion` | differs | Our-layer UI | Opens the Chinese Translation dialog. — **LO:** The `.uno:ChineseConversion` dialog itself contains the options (direction + Taiwan/Hong-Kong variants + Edit Terms); no separate options-only command, so it folds into the same dialog host. ✓ verified vs LO source. (Conditional.) |

### Comments (GroupComments)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| New Comment | ReviewNewComment | button | `.uno:InsertAnnotation` | same | Free | Inserts a comment anchored to the selection/cursor and opens a card for typing; supports reply/resolve. — **LO:** Good match — `.uno:InsertAnnotation` (Ctrl+Alt+C, label "Comment", tooltip "Insert Comment") anchors a comment and opens an editable margin box; LO supports author/timestamp, threaded Reply, Resolve. LO always renders as right-margin notes (no separate Comments-pane list). ✓ verified vs LO source. |
| Delete (split) | ReviewDeleteCommentsMenu | splitButton | `.uno:DeleteComment` | differs | Our-layer UI | Split button: primary deletes the current comment; menu offers Delete / Delete All Shown / Delete All in Document / Delete All Resolved. — **LO:** Not a split button — LO exposes flat commands `.uno:DeleteComment`, `.uno:DeleteCommentThread`, `.uno:DeleteAllNotes`; no "Delete All Shown" (no markup filter) and no "Delete All Resolved". Container + two children are our-layer. ✓ verified vs LO source. |
| Delete | ReviewDeleteComment | button | `.uno:DeleteComment` | same | Free | Deletes the current comment. — **LO:** Direct match — `.uno:DeleteComment` ("Delete Comment") deletes the comment at the cursor. (LO also has `.uno:DeleteCommentThread`, "Delete Comment Thread".) ✓ verified vs LO source. |
| Delete All Comments Shown | ReviewDeleteAllCommentsShown | button | `—` | LO-missing | Behavior shim | Deletes all currently shown comments (respects markup filters). — **LO:** No markup-filter concept, so no "delete only the shown" command — but delete-this and delete-all exist, so we orchestrate the filtered subset in our layer. |
| Delete All Comments in Document | ReviewDeleteAllCommentsInDocument | button | `.uno:DeleteAllNotes` | same | Free | Deletes every comment in the document. — **LO:** **Corrected:** the Writer delete-all-comments command is `.uno:DeleteAllNotes` (FN_DELETE_ALL_NOTES, label "Delete All Comments"), **not** `.uno:DeleteAllAnnotation` (that is the Draw/Impress command). Same effect. ✓ verified vs LO source. |
| Delete All Resolved Comments | DeleteAllResolvedComments | button | `—` | LO-missing | Behavior shim | Deletes all resolved comments. — **LO:** LO can resolve comments (`.uno:ResolveComment`) and show/hide resolved ones, but has no bulk-delete-only-resolved command — we compose it from resolve-state + delete in our layer. |
| Previous (Comment) | ReviewPreviousCommentWord | button | `—` | LO-missing | Behavior shim | Navigates to the previous comment. — **LO:** No dedicated previous-comment ribbon button, but comment navigation exists via the Navigator's Comments category — we orchestrate a prev button over it. |
| Next (Comment) | ReviewNextCommentWord | button | `—` | LO-missing | Behavior shim | Navigates to the next comment. — **LO:** Same as Previous — comment nav exists via the Navigator; we orchestrate a next button over it. |
| Show Comments (gutter toggle) | ShowCommentGutter | toggleButton | `.uno:ShowAnnotations` | differs | Our-layer UI | Shows/hides the comment gutter. — **LO:** `.uno:ShowAnnotations` ("Show Comments") toggles display of all margin notes; LO has no separate "comment gutter" distinct from showing the comments themselves — one toggle vs Word's gutter-specific toggle. ✓ verified vs LO source. |
| Show Comments (split) | ShowCommentsMenu | splitButton | `.uno:ShowAnnotations` | differs | Our-layer UI | Split button: toggles comment display and switches Contextual (margin cards) vs List (Comments pane); menu of view options. — **LO:** Only the plain `.uno:ShowAnnotations` toggle (plus `.uno:ShowResolvedAnnotations`); not a split button and no Contextual-vs-List switch (margin cards are the only mode). Split host is our-layer. ✓ verified vs LO source. |
| Contextual | ShowCommentsContextualView | toggleButton | `—` | LO-missing | Behavior shim | Toggles contextual (inline/margin) comment view. — **LO:** Margin cards are LO's only mode, so there is nothing to toggle to — we present this as the default-state shim over the existing comments display. |
| List | ShowCommentsPane | toggleButton | `—` | LO-missing | Behavior shim | Toggles the Comments pane (list view). — **LO:** No Comments task-pane list view (closest is the Navigator's Comments list); the comments themselves exist, so a list-view pane is a shim over them. |
| New Ink Comment | ReviewInkCommentNew | button | `—` | LO-missing | Engine gap | Inserts a handwritten (ink) comment. — **LO:** LO Writer has no ink/handwritten comment feature. Genuine engine absence. |
| Ink Comment Pen | ReviewInkCommentPen | toggleButton | `—` | LO-missing | Engine gap | Toggles the ink-comment pen tool. — **LO:** No ink-comment subsystem. Genuine absence. |
| Ink Comment Eraser | ReviewInkCommentEraser | toggleButton | `—` | LO-missing | Engine gap | Toggles the ink-comment eraser tool. — **LO:** No ink-comment subsystem. Genuine absence. |

### Tracking (GroupChangesTracking)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Track Changes (split) | ReviewTrackChangesMenu | splitButton | `.uno:TrackChanges` | differs | Our-layer UI | Split button: toggles recording (Ctrl+Shift+E); menu adds Lock Tracking, For Everyone / Just Mine. — **LO:** `.uno:TrackChanges` (label "Record", tooltip "Record Tracked Changes") is a plain toggle, not a split; Lock Tracking is a separate command (`.uno:ProtectTraceChangeMode`, in the Protect group) and there is no per-author scope. The split menu host is our-layer. (LO shortcut is **not** Ctrl+Shift+E — see verification.) ✓ verified vs LO source. |
| Track Changes | ReviewTrackChanges | toggleButton | `.uno:TrackChanges` | same | Free | Toggles change recording on/off. — **LO:** Direct match — `.uno:TrackChanges` ("Record", FN_REDLINE_ON) toggles recording of insertions/deletions/formatting with author-color attribution. (LO shortcut Ctrl+Shift+C is documented but UNVERIFIED in-tree — see verification.) ✓ verified vs LO source. |
| Lock Tracking | RevisionsLockTracking | toggleButton | `.uno:ProtectTraceChangeMode` | differs | Our-layer UI | Locks tracking with a password so others cannot disable it. — **LO:** `.uno:ProtectTraceChangeMode` ("Protect…", tooltip "Protect Track Changes") password-protects the track-changes state; same capability, but filed under the Protect group rather than a child of a Track-Changes split menu. ✓ verified vs LO source. |
| For Everyone | RevisionsTrackEveryone | toggleButton | `—` | LO-missing | Behavior shim | Track changes made by everyone. — **LO:** No per-author tracking-scope toggle — LO always records all authors. Redline exists; the per-author scope is a shim over it. |
| Just Mine | RevisionsTrackMine | toggleButton | `—` | LO-missing | Behavior shim | Track only the current user's changes. — **LO:** No per-author tracking scope — redline records all authors. Scope filtering is a shim in our layer. |
| Change User Name | _(none)_ | button | `—` | differs | Optional our-layer feature | Opens Word Options to change the user name used for revision attribution. — **LO:** The revision author name comes from Tools > Options > LibreOffice > User Data, but no `.uno` jumps there directly — app-state we could surface as a control. (Real Word id is `ReviewChangeUserName`, off-ribbon — see QA flags.) |
| Change Tracking Options (menu item) | _(none)_ | button | `.uno:TrackChangesBar` | differs | Our-layer UI | Opens the Track Changes Options dialog (markup colors, balloon/display settings). — **LO:** Track-changes display/color settings live at Tools > Options > LibreOffice Writer > Changes; no single `.uno` opens a "Track Changes Options" dialog. (Likely a phantom duplicate of the dialog-launcher row, and the `.uno:TrackChangesBar` mapping is suspect — that toggles the margin change-bar, not an options dialog — see QA flags.) |
| Display for Review | ReviewDisplayForReview | dropDown | `.uno:ShowTrackedChanges` | differs | Our-layer UI | Dropdown selecting markup display mode (Simple Markup / All Markup / No Markup / Original) without altering revisions. — **LO:** Only a binary `.uno:ShowTrackedChanges` ("Show Tracked Changes") toggle — no Simple Markup (change-bar-only) and no Original (preview-as-rejected); the 4-mode dropdown maps onto a 2-state toggle we host. ✓ verified vs LO source. |
| Show Markup | ReviewShowMarkupMenu | menu | `—` | LO-missing | Behavior shim | Checkbox menu controlling which markup types are shown (Comments, Insertions/Deletions, Formatting, Ink) with Balloons and Reviewers submenus. — **LO:** No per-category markup-filter menu — show-comments (`.uno:ShowAnnotations`) and show-tracked-changes (`.uno:ShowTrackedChanges`) are two all-or-nothing toggles. We shim the category menu over them. |
| Comments (markup) | ReviewShowComments | toggleButton | `.uno:ShowAnnotations` | differs | Our-layer UI | Toggle showing comments markup. — **LO:** `.uno:ShowAnnotations` is a standalone Comments-group toggle, not a child of a Show-Markup category menu and not per-reviewer filterable; same atomic effect, different control context. ✓ verified vs LO source. |
| Ink (markup) | _(none)_ | toggleButton | `—` | LO-missing | Engine gap | Toggle showing ink markup. — **LO:** LO has no ink markup, so there is nothing to show/hide. Genuine engine absence. |
| Insertions and Deletions | ReviewShowInsertionsAndDeletions | toggleButton | `.uno:ShowTrackedChanges` | differs | Behavior shim | Toggle showing insertions/deletions markup. — **LO:** LO cannot toggle insertions/deletions independently — `.uno:ShowTrackedChanges` shows/hides ALL tracked-change markup at once; we shim the fine-grained category toggle over the coarse one. ✓ verified vs LO source. |
| Formatting | ReviewShowFormatting | toggleButton | `—` | LO-missing | Behavior shim | Toggle showing formatting-change markup. — **LO:** No independent formatting-change toggle — formatting redlines are recorded but their display is bundled into `.uno:ShowTrackedChanges`; we shim the category toggle. |
| Balloons | ReviewBalloonsMenu | menu | `—` | LO-missing | Behavior shim | Submenu of balloon-display options for revisions. — **LO:** No margin "balloons" for revisions — LO shows tracked changes inline with a margin change-bar. Redline display exists; the balloon presentation is a shim. |
| Show Revisions in Balloons | ReviewShowRevisionsInBalloons | toggleButton | `—` | LO-missing | Behavior shim | Show all revisions in balloons. — **LO:** No revision balloons; redline display exists inline, so balloon mode is a presentation shim. |
| Show All Revisions Inline | ReviewShowRevisionsInline | toggleButton | `—` | LO-missing | Behavior shim | Show all revisions inline. — **LO:** LO always shows revisions inline (no balloon alternative), so the choice is a no-op presentation shim over the existing inline display. |
| Show Only Comments and Formatting in Balloons | ReviewShowOnlyCommentsAndFormattingInBaloons | toggleButton | `—` | LO-missing | Behavior shim | Show only comments and formatting in balloons. — **LO:** No balloons; comments and redline display exist, so this mixed-balloon mode is a presentation shim. |
| Specific People / Reviewers | ReviewShowReviewersMenu | menu | `—` | LO-missing | Behavior shim | Submenu to choose which reviewers' markup is shown. — **LO:** No per-reviewer show/hide from a Review menu — revisions are color-coded by author and the Manage dialog lists authors, so we shim the per-reviewer filter over the existing redline. |
| Highlight Updates | ReviewHighlightUpdates | toggleButton | `—` | LO-missing | Cut | Toggle highlighting of co-author updates. — **LO:** A co-authoring (real-time collaboration) feature; desktop LO has no co-author-update highlighting. Out of scope. |
| Other Authors | ReviewOtherAuthors | toggleButton | `—` | LO-missing | Cut | Toggle showing other authors' changes. — **LO:** Co-authoring feature, not present in desktop LO. Out of scope. |
| Reviewing Pane (split) | ReviewReviewingPaneMenu | splitButton | `.uno:AcceptTrackedChanges` | differs | Our-layer UI | Split button: toggles the Reviewing Pane summarizing every change/comment with author and count; menu picks vertical/horizontal orientation. — **LO:** Nearest is the **Manage Tracked Changes** dialog (`.uno:AcceptTrackedChanges`, label "Manage…") with List/Filter tabs and per-row accept/reject — a modal dialog, not a dockable pane, not a split button, no orientation choice, and it does not list comments. Host differs substantially. ✓ verified vs LO source. |
| Reviewing Pane | ReviewReviewingPane | toggleButton | `.uno:AcceptTrackedChanges` | differs | Our-layer UI | Toggles the Revisions pane. — **LO:** The Manage Tracked Changes dialog (`.uno:AcceptTrackedChanges`) is a modal dialog covering tracked changes only (not comments); comparable purpose, different form. ✓ verified vs LO source. |
| Reviewing Pane Vertical | ReviewReviewingPaneVertical | toggleButton | `—` | LO-missing | Behavior shim | Dock the reviewing pane vertically (left). — **LO:** The Manage dialog has no docking/orientation options; the change-review capability exists, so orientation is a host shim. |
| Reviewing Pane Horizontal | ReviewReviewingPaneHorizontal | toggleButton | `—` | LO-missing | Behavior shim | Dock the reviewing pane horizontally (bottom). — **LO:** Same — the manage-changes dialog has no orientation; orientation is a host shim over the existing review list. |
| Change Tracking Options (dialog launcher) | ReviewChangeTrackingOptions | dialogBoxLauncher | `—` | differs | Our-layer UI | Group dialog launcher opening the Track Changes Options dialog (markup colors, balloon/display settings). — **LO:** No `.uno` and no dialog launcher; the equivalent settings are an Options page (Tools > Options > LibreOffice Writer > Changes). Settings exist; only the launcher form is our-layer. |

### Changes (GroupChanges)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Accept (split) | ReviewAcceptChangeMenu | splitButton | `.uno:AcceptTrackedChange` | differs | Our-layer UI | Split button: primary accepts the current change and moves next; menu offers Accept This / All Shown / All / All and Stop Tracking. — **LO:** Flat ribbon buttons, not a split: `.uno:AcceptTrackedChange` ("Accept"), `.uno:AcceptTrackedChangeToNext` ("Accept and Move to Next"), `.uno:AcceptAllTrackedChanges` ("Accept All"); no "All Shown" (no markup filter) and no "All and Stop Tracking". Split host + two children are our-layer. ✓ verified vs LO source. |
| Accept and Move to Next | ReviewAcceptChangeAndMoveToNext | button | `.uno:AcceptTrackedChangeToNext` | same | Free | Accept this change and advance to the next. — **LO:** Direct match — `.uno:AcceptTrackedChangeToNext` ("Accept and Move to Next"). ✓ verified vs LO source. |
| Accept This Change | ReviewAcceptChange | button | `.uno:AcceptTrackedChange` | same | Free | Accept the current change only. — **LO:** Direct match — `.uno:AcceptTrackedChange` ("Accept") accepts the current revision without advancing. ✓ verified vs LO source. |
| Accept All Changes Shown | ReviewAcceptAllChangesShown | button | `—` | LO-missing | Behavior shim | Accept all currently shown (filtered) changes. — **LO:** No markup/reviewer filter, so no "accept only shown" command — Accept-this and Accept-All exist, so we orchestrate the filtered subset. |
| Accept All Changes | ReviewAcceptAllChangesInDocument | button | `.uno:AcceptAllTrackedChanges` | same | Free | Accept every change in the document. — **LO:** Direct match — `.uno:AcceptAllTrackedChanges` ("Accept All"). ✓ verified vs LO source. |
| Accept All Changes and Stop Tracking | AcceptAllChangesInDocAndStopTracking | button | `—` | LO-missing | Behavior shim | Accept all changes and turn Track Changes off. — **LO:** No combined command — Accept-All (`.uno:AcceptAllTrackedChanges`) + toggle-off (`.uno:TrackChanges`) both exist, so we compose them in our layer. |
| Reject (split) | ReviewRejectChangeMenu | splitButton | `.uno:RejectTrackedChange` | differs | Our-layer UI | Split button: primary rejects the current change and moves next; menu offers Reject This / All Shown / All / All and Stop Tracking. — **LO:** Mirror of Accept — flat buttons `.uno:RejectTrackedChange` ("Reject"), `.uno:RejectTrackedChangeToNext` ("Reject and Move to Next"), `.uno:RejectAllTrackedChanges` ("Reject All"); no "All Shown", no "All and Stop Tracking". Split host is our-layer. ✓ verified vs LO source. |
| Reject and Move to Next | ReviewRejectChangeAndMoveToNext | button | `.uno:RejectTrackedChangeToNext` | same | Free | Reject this change and advance to the next. — **LO:** Direct match — `.uno:RejectTrackedChangeToNext` ("Reject and Move to Next"). ✓ verified vs LO source. |
| Reject This Change | ReviewRejectChange | button | `.uno:RejectTrackedChange` | same | Free | Reject the current change only. — **LO:** Direct match — `.uno:RejectTrackedChange` ("Reject"). ✓ verified vs LO source. |
| Reject All Changes Shown | ReviewRejectAllChangesShown | button | `—` | LO-missing | Behavior shim | Reject all currently shown (filtered) changes. — **LO:** No markup/reviewer filter — only Reject-this and Reject-All exist, so we orchestrate the filtered subset. |
| Reject All Changes | ReviewRejectAllChangesInDocument | button | `.uno:RejectAllTrackedChanges` | same | Free | Reject every change in the document. — **LO:** Direct match — `.uno:RejectAllTrackedChanges` ("Reject All"). ✓ verified vs LO source. |
| Reject All Changes and Stop Tracking | RejectAllChangesInDocAndStopTracking | button | `—` | LO-missing | Behavior shim | Reject all changes and turn Track Changes off. — **LO:** No combined command — Reject-All + toggle-off both exist, composed in our layer. |
| Previous (Change) | ReviewPreviousChange | button | `.uno:PreviousTrackedChange` | same | Free | Navigate to the previous tracked change without accepting/rejecting. — **LO:** Direct match — `.uno:PreviousTrackedChange` ("Previous") moves to the prior revision without acting on it. ✓ verified vs LO source. |
| Next (Change) | ReviewNextChange | button | `.uno:NextTrackedChange` | same | Free | Navigate to the next tracked change without accepting/rejecting. — **LO:** Direct match — `.uno:NextTrackedChange` ("Next"). ✓ verified vs LO source. |

### Compare (GroupCompare)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Compare | ReviewCompareMenu | menu | `.uno:CompareDocuments` | differs | Our-layer UI | Menu of compare/combine commands; Compare (legal blackline) opens Compare Documents dialog producing a third doc; Combine merges revisions. — **LO:** Two separate flat buttons, not a menu: `.uno:CompareDocuments` ("Compare") and `.uno:MergeDocuments` ("Merge"); LO shows differences as tracked changes IN the current document (no third doc), and there are no version-history children. Menu host is our-layer. ✓ verified vs LO source. |
| Compare Major Version | ReviewCompareMajorVersion | button | `—` | LO-missing | Cut | Compare to a major version. — **LO:** LO compares against a chosen file on disk, not SharePoint/version-history major/minor versions. Server/cloud version history, out of scope. |
| Compare Last Version | ReviewCompareLastVersion | button | `—` | LO-missing | Cut | Compare to the last version. — **LO:** No server version-history compare (LO's own Edit > Versions is separate and not a Review command). Out of scope. |
| Compare Specific Version | ReviewCompareSpecificVersion | button | `—` | LO-missing | Cut | Compare to a specific version. — **LO:** No server version-history compare. Out of scope. |
| View Changes in the Source Document | ReviewViewChangesInTheSourceDocument | button | `—` | LO-missing | Behavior shim | View changes in the source document. — **LO:** LO's compare result shows changes inline in the working document; no source/target toggle, but the compare/redline capability exists, so this is a presentation shim. |
| Compare Two Versions (Compare...) | ReviewCompareTwoVersions | button | `.uno:CompareDocuments` | differs | Behavior shim | Opens the Compare Documents dialog to compare two documents (legal blackline). — **LO:** `.uno:CompareDocuments` ("Compare") is the real match: it prompts for a second document and injects the differences as accept/rejectable tracked changes into the CURRENT document rather than producing a new third doc — same intent, different output model → shim. ✓ verified vs LO source. |
| Combine (Combine Revisions...) | ReviewCombineRevisions | button | `.uno:MergeDocuments` | same | Free | Opens the Combine Documents dialog to merge revisions from multiple authors. — **LO:** Good match — `.uno:MergeDocuments` ("Merge") merges the tracked changes from another document into the current one; mostly a naming difference (Merge vs Combine). ✓ verified vs LO source. |
| Show Source Documents | ReviewShowSourceDocumentsMenu | gallery | `—` | LO-missing | Behavior shim | Gallery choosing how source documents are shown (hide source / show source / show both). — **LO:** LO's compare/merge keeps no separate original+revised source panes, but the compare/merge capability exists, so the source-display gallery is a presentation shim. |

### Protect (GroupProtect)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Block Authors (split) | BlockAuthorsMenu | splitButton | `—` | LO-missing | Cut | Split button to block other co-authors from editing a region in a shared document; menu to apply/release locks. — **LO:** No co-authoring author-block/region-lock feature (section write-protection exists but is not author-scoped and not a Review control). Co-authoring/cloud, out of scope. |
| Block Authors (apply lock) | ApplyCoAuthoringLock | toggleButton | `—` | LO-missing | Cut | Apply a co-authoring lock to the selection. — **LO:** No co-authoring locks. Out of scope. |
| Release All My Locks | ReleaseAllMyLocks | button | `—` | LO-missing | Cut | Release all locks applied by the current user. — **LO:** No co-authoring locks. Out of scope. |
| Restrict Editing | ReviewRestrictFormatting | toggleButton | `.uno:EditDoc` | differs | Behavior shim | Toggles the Restrict Editing pane: limit formatting, set editing restrictions (read-only/comments/tracked-changes/forms), grant per-region exceptions, enforce with optional password. — **LO:** No unified Restrict-Editing pane; the pieces are scattered — `.uno:EditDoc` ("Edit Mode", Ctrl+Shift+M, read-only toggle), `.uno:ProtectTraceChangeMode` (protect track changes), and section protection. We orchestrate the granular restriction flow over these existing commands. ✓ verified vs LO source. |

### Ink (GroupInk)

> Pen/handwriting Word group. **Engine gap** — LO Writer has no ink/handwriting subsystem at all.

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Start Inking | InkingStart | button | `—` | LO-missing | Engine gap | Starts ink/drawing mode. — **LO:** LO Writer has no pen/ink annotation mode (the whole Ink group is absent). Genuine engine absence. |
| Hide Ink (split) | HideInkSplitButton | splitButton | `—` | LO-missing | Engine gap | Split button toggling ink visibility; menu has Delete All Ink. — **LO:** No ink subsystem. Genuine absence. |
| Hide Ink | HideInk | toggleButton | `—` | LO-missing | Engine gap | Toggle visibility of ink annotations. — **LO:** No ink subsystem. Genuine absence. |
| Delete All Ink | InkDeleteAll | button | `—` | LO-missing | Engine gap | Delete all ink in the document. — **LO:** No ink subsystem. Genuine absence. |

### Markup (Source C only — not a separate group in A or B)

> Source-C-only / newer experimental control with a **null idMso** — absent from the official `wordcontrols.xlsx` Current-Channel snapshot, so unconfirmable against the catalog and flagged as non-standard.

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Filter All Markup | _(none)_ | dropDown | `—` | LO-missing | Behavior shim | Dropdown to filter shown comments/markup (Reset All Filters, Filter by @mentions me, Active only, Resolved only). — **LO:** No markup-filtering dropdown and no @mention/active/resolved filter on the ribbon; the only adjacent piece is `.uno:ShowResolvedAnnotations` (a single show/hide-resolved toggle). Comments/resolve state exist, so we shim the multi-option filter over them (no @mentions concept). ✓ verified vs LO source. |

---

## LO-source verification

These mappings were checked against the vendored LibreOffice tree at
`apps/libreoffice/libreoffice-codebase/` (UI paths
`officecfg/registry/data/org/openoffice/Office/UI/{GenericCommands,WriterCommands}.xcu`; shortcuts in
`Accelerators.xcu`; slots in `sw/sdi/swriter.sdi`, `svx/sdi/svx.sdi`; behavior in
`sw/source/uibase/shells/{textsh1,translatehelper}.cxx`). They **override** the mapped rows where
they conflicted. **Three are material corrections** (Thesaurus shortcut, Delete-All loUno, Translate
scope); the rest **confirm** the mapped command/label/tooltip/shortcut. **Two items remain
UNCERTAIN** and are not treated as authoritative.

**Material corrections (CORRECTED):**

- **Thesaurus shortcut** — the mapping carried over Word's **Shift+F7**; LO binds Thesaurus to
  **Ctrl+F7** (`F7_MOD1` → `.uno:ThesaurusDialog` in the Writer block). Shift+F7 (`F7_SHIFT`, the
  only Shift+F7 binding in the whole file) is `.uno:SpellOnline` (Auto Spellcheck). Behavior text
  fixed to Ctrl+F7. Evidence: `Accelerators.xcu:960-963` (F7_MOD1 → ThesaurusDialog); `:87-91`
  (F7_SHIFT → SpellOnline); `:2493-2497` (F7 → SpellingAndGrammarDialog).
- **Delete All Comments in Document → `.uno:DeleteAllNotes`** — the mapping used
  `.uno:DeleteAllAnnotation`, but for **Writer** the delete-all-comments command is
  `.uno:DeleteAllNotes` (slot FN_DELETE_ALL_NOTES, label "Delete All Comments").
  `.uno:DeleteAllAnnotation` exists **only** as the Draw/Impress command (SID_DELETEALL_POSTIT). loUno
  corrected. Evidence: `GenericCommands.xcu:6956-6958` (DeleteAllNotes → "Delete All Comments");
  `swriter.sdi:7908`; `svx.sdi:4855` (DeleteAllAnnotation SID_DELETEALL_POSTIT);
  `DrawImpressCommands.xcu:1982` (DeleteAllAnnotation is Draw/Impress only).
- **Translate scope** — the mapping asserted `.uno:Translate` is "selection-only", "translates
  directly", and listed Translate-Document rows as LO-missing. In fact the `SID_FM_TRANSLATE`
  handler calls `SwTranslateHelper::TranslateDocument`, whose worker translates the **selection if
  one exists, otherwise the WHOLE DOCUMENT** (node 0 to last node), and it first opens a
  target-language selection dialog (`SwTranslateLangSelectDlg` / `translationdialog.ui`) when no
  TargetLang arg is supplied — so it does **not** translate directly and the "Translate Document =
  LO-missing" framing is too strong (no separate command, but the one command already covers
  whole-document). The DeepL-backend / no-Translator-pane / no-Mini-Translator claims remain
  correct. Verdicts on the two Translate-Document rows softened LO-missing → Behavior shim. Evidence:
  `textsh1.cxx:2351-2367` (SID_FM_TRANSLATE → TranslateDocument; else opens lang-select dialog);
  `translatehelper.cxx:98-101, 104-113, 132-144`; `svx.sdi:1645` (Translate SID_FM_TRANSLATE).

**Confirmed (CONFIRMED) — command/label/tooltip (and cited shortcut) match the mapping:**

- **Spelling & Grammar** — `.uno:SpellingAndGrammarDialog`, Label "Spelling" (ContextLabel
  "~Spelling…", Tooltip "Check Spelling"), F7. (Separate `.uno:SpellingDialog` and
  `.uno:RecheckDocument` also exist; the dialog-entry choice is right.) Evidence:
  `GenericCommands.xcu:4269-4278`; `Accelerators.xcu:2493-2497`.
- **Check Spelling As You Type** — `.uno:SpellOnline`, Label "Auto Spellcheck" (Tooltip "Toggle
  Automatic Spell Checking"), a toggle, also globally bound to Shift+F7. Evidence:
  `GenericCommands.xcu:5498-5510`; `Accelerators.xcu:87-91`.
- **Thesaurus (command/label)** — `.uno:ThesaurusDialog`, Label "~Thesaurus…", present in both
  GenericCommands and WriterCommands; only the shortcut was wrong (see correction). Evidence:
  `GenericCommands.xcu:4358-4361`; `WriterCommands.xcu:3125-3128`.
- **Word Count** — `.uno:WordCountDialog` (Writer), Label "~Word Count…". Evidence:
  `WriterCommands.xcu:3702-3705`.
- **Check Accessibility** — `.uno:AccessibilityCheck` (Writer), Label "~Accessibility Check…",
  TargetURL `.uno:SidebarDeck.A11yCheckDeck`; companion `.uno:AccessibilityCheckOnline` ("Automatic
  Accessibility Checking"). Single button, not a split. Evidence: `WriterCommands.xcu` (node);
  `GenericCommands.xcu` (AccessibilityCheckOnline).
- **Navigation Pane** — `.uno:Navigator`, Label "Na~vigator", F5 in the Writer block. Evidence:
  `GenericCommands.xcu`; `Accelerators.xcu:457-460, 930-933`.
- **Lock Tracking** — `.uno:ProtectTraceChangeMode`, Label "~Protect…", Tooltip/Popup "Protect Track
  Changes". Evidence: `GenericCommands.xcu`.
- **Display for Review** — `.uno:ShowTrackedChanges`, Label "Show Tracked Changes"; menu alias
  `.uno:ViewTrackChanges` (TargetURL `.uno:ShowTrackedChanges`). A single toggle, consistent with
  "differs vs Word's 4-mode dropdown". Evidence: `WriterCommands.xcu` (+ `:426-435`).
- **Accept/Reject family + Previous/Next** — all flat (no split button): `.uno:AcceptTrackedChange`
  "Accept", `.uno:AcceptTrackedChangeToNext` "Accept and Move to Next", `.uno:AcceptAllTrackedChanges`
  "Accept All", and the Reject mirror, plus `.uno:PreviousTrackedChange` "Pr~evious",
  `.uno:NextTrackedChange` "Next" — confirmed verbatim. Evidence: `WriterCommands.xcu` nodes.
- **Reviewing Pane** — `.uno:AcceptTrackedChanges`, Label "~Manage…" (the Manage Tracked Changes
  dialog command — a dialog, not a dockable pane; supports "differs"). Evidence: `WriterCommands.xcu`.
- **Compare / Combine** — `.uno:CompareDocuments` Label "Compare"; `.uno:MergeDocuments` Label
  "Merge" — two separate flat commands. Evidence: `GenericCommands.xcu`.
- **Restrict Editing** — `.uno:EditDoc`, Label "E~dit Mode", Ctrl+Shift+M (`M_SHIFT_MOD1`); supports
  "no unified Restrict-Editing pane". Evidence: `GenericCommands.xcu`; `Accelerators.xcu:81-85`.
- **New Comment** — `.uno:InsertAnnotation`, Label "Comme~nt", Popup/Tooltip "Insert Comment",
  Ctrl+Alt+C (`C_MOD1_MOD2`). Evidence: `GenericCommands.xcu`; `Accelerators.xcu:66-72`.
- **Delete / Resolve / Show comments family** — `.uno:DeleteComment` "Delete Comment",
  `.uno:DeleteCommentThread` "Delete Comment Thread", `.uno:ResolveComment` "Resolved",
  `.uno:ShowAnnotations` "Show Comme~nts", `.uno:ShowResolvedAnnotations` "Show resolved comme~nts"
  (also `.uno:DeleteAuthor`, unused). Evidence: `GenericCommands.xcu` (+ `:6972-6974`);
  `WriterCommands.xcu`.
- **Hangul/Hanja & Chinese Conversion** — `.uno:HangulHanjaConversion` "Hangul/Hanja Conversion…";
  `.uno:ChineseConversion` "Chinese Conversion…" — both single-dialog commands (direction is a
  choice). Evidence: `GenericCommands.xcu`.
- **Language menu / Set Proofing Language** — `.uno:LanguageMenu` "Language" (+ `.uno:LanguageStatus`,
  `.uno:SetLanguageSelectionMenu` "For Selection", `.uno:SetLanguageParagraphMenu`,
  `.uno:SetLanguageAllTextMenu`). Evidence: `GenericCommands.xcu`.
- **Track Changes (label)** — `.uno:TrackChanges`, Label "~Record", Tooltip "Record Tracked Changes",
  slot FN_REDLINE_ON. The corrective sub-claim that it is **NOT** Ctrl+Shift+E is **confirmed**
  (Ctrl+Shift+E = `.uno:JumpToFootnoteOrAnchor` in the Writer block). Evidence:
  `WriterCommands.xcu:390-399`; `swriter.sdi:56`; `Accelerators.xcu:6407-6411`.

**Uncertain (UNCERTAIN) — not treated as authoritative:**

- **Track Changes → Ctrl+Shift+C** — the *positive* shortcut value could **not** be confirmed in-tree:
  `.uno:TrackChanges` / FN_REDLINE_ON has no `Accelerators.xcu` entry, and the only Ctrl+Shift+C
  (`C_SHIFT_MOD1`) binding maps to `.uno:Combine` (German locale only). Ctrl+Shift+C is documented LO
  behavior but unevidenced in this stripped checkout — confirm in a running build (Tools > Customize >
  Keyboard, or the Record tooltip). Evidence: `Accelerators.xcu:1742-1746`; no TrackChanges entry.
- **The many "LO-missing" negative claims (Read Aloud / TTS, Ink, co-authoring locks, per-author
  scope, balloons, per-category/per-reviewer markup filters)** — absence cannot be positively proven
  from a stripped tree. Spot-searches of GenericCommands.xcu / WriterCommands.xcu found **no contrary
  commands** (no ReadAloud/TTS, no ink-comment, no co-authoring/balloon/markup-filter commands), and
  `.uno:ShowResolvedAnnotations` (cited in the Filter-All-Markup row) is confirmed to exist — but the
  negatives are marked UNCERTAIN since proving non-existence is not definitive.

> **Scope caveat from the LO-verify pass.** Present-command facts and the three suspect claims
> (Thesaurus shortcut, Delete-All loUno, Translate scope) were re-derived from primary sources; the
> numerous MS-only "LO-missing" rows (Ink, Read Aloud, co-authoring, balloons, markup filters) were
> **not exhaustively re-verified** against the LO tree — no matching `.uno` nodes were found in
> targeted searches, and the absence claims are consistent with the catalog.

---

## Conditional / version-sensitive controls

There is **no owner screenshot for the Review tab yet**, so the following are flagged
**expected-conditional, unverified against a live build** — a screenshot sweep would confirm whether
(and how) they surface. They are not contradicted by the inventory; they simply depend on
language/region/SKU/version/account state.

- **Chinese Translation group** — entire group is East-Asian-only; expected absent unless
  Asian-language editing is enabled.
- **Hangul/Hanja Conversion, Japanese Consistency Checker, Update IME Dictionary** — East-Asian-build
  / Asian-support-only Language-group commands.
- **Editor / "Editor" button (`ReviewSpellingAndGrammar`)** — modern M365 (Word 2021/365); older
  builds show "Spelling & Grammar" instead. The idMso is fabricated (see QA), so a screenshot is the
  fastest way to confirm the leftmost Proofing button.
- **Read Aloud (Speech group)** — modern M365; presence and the control type (button vs visually
  toggling) want a screenshot/QAT-tooltip check.
- **Translate menu children** — the child set varies by M365 channel (Translator vs older Mini
  Translator); a live screenshot confirms which render today.
- **Show Comments (gutter toggle + split, `ShowCommentGutter`)** — `ShowCommentGutter` is the only
  control that appears twice on `TabReviewWord` (standalone and under `ShowCommentsMenu`); the
  Comments-group layout has shifted across recent M365 builds.
- **Co-authoring controls** — Block Authors / locks / Highlight-Updates / Other-Authors depend on a
  shared/co-authored document context.

---

## Out of scope

- **Engine gap — Ink + Read-Aloud, the only true engine blockers (11 controls).** Two clusters: (1)
  **Ink / handwriting** — the whole Ink group (Start Inking, Hide Ink split + toggle, Delete All Ink),
  the three ink-comment controls (New Ink Comment, pen, eraser), and the Ink markup toggle; LO Writer
  has no pen/ink subsystem at all. (2) **A thin "no LO equivalent" set** — Read Aloud (TTS), Focus-mode
  view, and the Japanese consistency checker. Cut now, or accept reduced fidelity. This is the only
  band that would matter if the engine were ever reconsidered — and notably **none of Word's core
  Track-Changes workflow is in it**.
- **Cloud / AI / co-authoring (cut by product choice, 12 controls).** The Editor cloud document scan
  (`WritingAssistanceCheckDocument`), the Translator task pane + Mini Translator, IME-dictionary
  update, co-authoring (Block Authors + locks, Highlight Updates, Other Authors), and server
  version-history compare (Compare Major / Last / Specific Version). No engine equivalent and not part
  of a local clone's scope.
- **Optional our-layer app-state (3 controls).** Translator Preferences and Set Translation Language
  (DeepL key/target live in Options) and Change User Name (revision author lives in Options) — LO lacks
  the one-click Review control, but these are app-state we could surface ourselves.

---

## QA flags & resolutions

From `result.qa`. The Word/idMso side was set-diffed against the official `wordcontrols.xlsx`
(M365 Current Channel, `Tab='TabReviewWord'`): **every one of the 99 distinct non-group controls is
present — zero real controls missing**; the set-diff returned exactly one unmatched inventory idMso
(the fabricated `ReviewSpellingAndGrammar`). The LO-source pass resolved the three material LO
defects. Because there is **no owner screenshot for this tab**, several structural items remain
**screenshot-pending**.

| QA flag | Status | Resolution |
|---|---|---|
| Any genuinely missing Review-tab controls? | **Resolved (source set-diff)** | None. All 99 official `TabReviewWord` idMsos are present in the inventory; complete at the idMso level. |
| "Editor" row idMso `ReviewSpellingAndGrammar`? | **Resolved — fabricated idMso (screenshot to relabel)** | `ReviewSpellingAndGrammar` does not exist anywhere in `wordcontrols.xlsx`. The real Editor experience is already covered by `SpellingAndGrammar` (F7 button) + `WritingAssistanceCheckDocument` (cloud scan) — both already separate rows. The Editor row is a phantom/double-count; a screenshot of the Proofing group would confirm whether to drop or remap it. Buckets unchanged. |
| `ReadAloud` controlType = toggleButton? | **Resolved (source)** | Officially `button` in GroupSpeech, not toggleButton (it renders a pressed state but the registered type is button). Noted on the row; bucket (Engine gap) unchanged. |
| "Change Tracking Options (menu item)" (null idMso, loUno `.uno:TrackChangesBar`)? | **Open (screenshot-pending) + LO mapping suspect** | Likely a phantom duplicate of the `ReviewChangeTrackingOptions` dialog launcher (Word has only one options entry point). Also `.uno:TrackChangesBar` is the wrong LO mapping — it toggles the margin change-bar, not an options dialog. A screenshot of the Tracking group's dialog-launcher corner confirms there is only one entry point. |
| "Change User Name" null idMso? | **Resolved (source) — real id off-ribbon** | The real Word identifier is `ReviewChangeUserName`, but it sits under `Tab='Not in the Ribbon'` (reached via Options). Null is defensible for a Review-tab control; noted for traceability. |
| Group naming (`Tracking`, `Chinese Translation`)? | **Resolved (source) — cosmetic** | `Tracking` = official `GroupChangesTracking`; `Chinese Translation` = `GroupChineseTranslation`. Word's UI labels match; the inventory's split into separate `Tracking` + `Changes` inventory groups is **correct** (Word genuinely has two ribbon groups, GroupChangesTracking and GroupChanges). |
| Thesaurus shortcut Shift+F7? | **Resolved (LO source)** | Wrong — LO binds Thesaurus to **Ctrl+F7** (`F7_MOD1`); Shift+F7 is `.uno:SpellOnline`. Word's Shift+F7 was carried over. Behavior text fixed. |
| Delete All Comments loUno `.uno:DeleteAllAnnotation`? | **Resolved (LO source)** | Wrong for Writer — the Writer command is `.uno:DeleteAllNotes` (FN_DELETE_ALL_NOTES); `.uno:DeleteAllAnnotation` is Draw/Impress only (SID_DELETEALL_POSTIT). loUno corrected. |
| Translate rows overstate the LO gap? | **Resolved (LO source)** | Yes — `.uno:Translate` is not selection-only and does not translate directly: it does whole-document when no selection and opens a target-language dialog first. The two Translate-Document rows softened LO-missing → Behavior shim. DeepL/no-pane claims stand. |
| Track Changes LO shortcut = Ctrl+Shift+C? | **Open (LO-side, UNCERTAIN)** | Unverifiable in the stripped tree (no `Accelerators.xcu` entry for `.uno:TrackChanges`; only Ctrl+Shift+C → `.uno:Combine`, de-locale). The negative (NOT Ctrl+Shift+E) **is** confirmed. Confirm in a running build. |
| `ShowCommentGutter` appears twice? | **Open (screenshot-pending)** | It is the only official control that appears twice on `TabReviewWord` (standalone + under `ShowCommentsMenu`); the Comments-group layout has changed across recent M365 builds. A screenshot confirms both rows are still live. Does not change buckets. |
| Exhaustiveness of the many "LO-missing" absence claims (Read Aloud, Ink, co-authoring, balloons, per-category/per-reviewer filters)? | **Open (LO-side, medium confidence)** | Not exhaustively re-audited; targeted searches found no matching `.uno` nodes and the claims are consistent with the catalog. `completenessConfidence`: **HIGH** on the Word/idMso side (0 missing, 1 fabricated idMso, ReadAloud type re-derived), **MEDIUM** on LO-mapping exhaustiveness; one residual UNCERTAIN (Track Changes shortcut). |
| Null-idMso "Source C only" / "Filter All Markup" row? | **Resolved (source) — non-catalog** | Newer/experimental control absent from the Current-Channel snapshot; correctly null-idMso and flagged non-standard. Cannot be confirmed against the official list. |
