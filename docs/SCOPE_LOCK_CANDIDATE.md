# Step 3 — Scope Lock Candidate: Usage × Functionality

Joins **real-world usage tier** (T0 ubiquitous → T4 rare, from the usage-ranking workflow) with **actual functionality status** (from the code-traced parity audit) for all 214 ranked controls. This is the decision surface for locking scope.

## The matrix — how much of what people USE is actually DONE

| Usage tier | ✅ full | 🟡 partial | 🟠 wrong | ❌ stub | ⬜ missing | Total | Weighted %done |
|---|--:|--:|--:|--:|--:|--:|--:|
| **T0 Ubiquitous** | 9 | 2 | 0 | 0 | 0 | 11 | 90.9% |
| **T1 High** | 7 | 12 | 0 | 0 | 0 | 19 | 68.4% |
| **T2 Medium** | 24 | 14 | 0 | 1 | 0 | 39 | 79.5% |
| **T3 Low** | 18 | 42 | 0 | 8 | 0 | 68 | 57.4% |
| **T4 Rare/Negligible** | 11 | 45 | 1 | 20 | 0 | 77 | 43.8% |

_Weighted %done: full=1.0, partial=0.5, wrong=0.25, stub/missing=0._

## Completeness if you lock scope at each threshold

| Lock | Controls in scope | Weighted %done | ✅ full | ✅+🟡 do something real | Hard gaps (stub/wrong/missing) |
|---|--:|--:|--:|--:|--:|
| **T0–T0** (Ubiquitous and up) | 11 | 90.9% | 9 (82%) | 11 (100%) | 0 |
| **T0–T1** (High and up) | 30 | 76.7% | 16 (53%) | 30 (100%) | 0 |
| **T0–T2** (Medium and up) | 69 | 78.3% | 40 (58%) | 68 (99%) | 1 |
| **T0–T3** (Low and up) | 137 | 67.9% | 58 (42%) | 128 (93%) | 9 |
| **T0–T4** (Rare/Negligible and up) | 214 | 59.2% | 69 (32%) | 184 (86%) | 30 |

## High-value gaps — controls people USE that are NOT full parity

These are where scope-locking pays off: high usage, not yet done.

### T0 Ubiquitous — 2 gaps

| Control | Tab · Group | Status | Segment |
|---|---|---|---|
| **Paste** `paste` | home · Clipboard | 🟡 partial | general |
| **Font (face)** `font` | home · Font | 🟡 partial | general |

### T1 High — 12 gaps

| Control | Tab · Group | Status | Segment |
|---|---|---|---|
| **Line and Paragraph Spacing** `lineAndParagraphSpacing` | home · Paragraph | 🟡 partial | general |
| **Styles Gallery** `stylesGallery` | home · Styles | 🟡 partial | academic |
| **Editor** `editor` | home · Editor | 🟡 partial | general |
| **Table** `table` | insert · Tables | 🟡 partial | general |
| **Pictures** `pictures` | insert · Illustrations | 🟡 partial | general |
| **Link** `link` | insert · Links | 🟡 partial | general |
| **Header** `header` | insert · Header & Footer | 🟡 partial | general |
| **Footer** `footer` | insert · Header & Footer | 🟡 partial | general |
| **Page Number** `pageNumber` | insert · Header & Footer | 🟡 partial | general |
| **Margins** `margins` | Layout · Page Setup | 🟡 partial | general |
| **Editor** `editor` | review · Proofing | 🟡 partial | general |
| **Spelling and Grammar** `spellingGrammar` | review · Proofing | 🟡 partial | general |

### T2 Medium — 15 gaps

| Control | Tab · Group | Status | Segment |
|---|---|---|---|
| **Format Painter** `formatPainter` | home · Clipboard | 🟡 partial | general |
| **Font dialog (launcher)** `font` | home · Font | 🟡 partial | general |
| **Show/Hide ¶** `showHide` | home · Paragraph | 🟡 partial | general |
| **Borders** `borders` | home · Paragraph | 🟡 partial | general |
| **Paragraph dialog (launcher)** `paragraph` | home · Paragraph | 🟡 partial | general |
| **Styles pane (launcher)** `styles` | home · Styles | 🟡 partial | academic |
| **Select** `select` | home · Editing | 🟡 partial | general |
| **Page Break** `pageBreak` | insert · Pages | 🟡 partial | general |
| **Breaks** `breaks` | Layout · Page Setup | 🟡 partial | general |
| **Insert Footnote** `insertFootnote` | references · Footnotes | 🟡 partial | academic |
| **Display for Review** `displayForReview` | review · Markup | 🟡 partial | legal |
| **Track Changes** `trackChanges` | review · Tracking | 🟡 partial | legal |
| **Navigation Pane** `navigationPane` | view · Show | 🟡 partial | academic |
| **Zoom** `zoom` | view · Zoom | 🟡 partial | general |
| **Shapes** `shapes` | insert · Illustrations | ❌ stub | business-admin |

### T3 Low — 50 gaps

| Control | Tab · Group | Status | Segment |
|---|---|---|---|
| **Text Effects and Typography** `textEffectsAndTypography` | home · Font | 🟡 partial | marketing |
| **Multilevel List** `multilevelList` | home · Paragraph | 🟡 partial | legal |
| **Sort** `sort` | home · Paragraph | 🟡 partial | business-admin |
| **Cover Page** `coverPage` | insert · Pages | 🟡 partial | business-admin |
| **Icons** `icons` | insert · Illustrations | 🟡 partial | marketing |
| **Cross-reference** `crossReference` | insert · Links | 🟡 partial | academic |
| **Text Box** `textBox` | insert · Text | 🟡 partial | marketing |
| **Quick Parts** `quickParts` | insert · Text | 🟡 partial | business-admin |
| **Pens Gallery** `pensGallery` | draw · Pens | 🟡 partial | accessibility |
| **Themes** `themes` | design · Document Formatting | 🟡 partial | marketing |
| **Paragraph Spacing** `paragraphSpacing` | design · Document Formatting | 🟡 partial | academic |
| **Page Color** `pageColor` | design · Page Background | 🟡 partial | marketing |
| **Page Borders** `pageBorders` | design · Page Background | 🟡 partial | general |
| **Position** `position` | Layout · Arrange | 🟡 partial | marketing |
| **Wrap Text** `wrapText` | Layout · Arrange | 🟡 partial | general |
| **Bring Forward** `bringForward` | Layout · Arrange | 🟡 partial | marketing |
| **Send Backward** `sendBackward` | Layout · Arrange | 🟡 partial | marketing |
| **Align** `align` | Layout · Arrange | 🟡 partial | marketing |
| **Rotate** `rotate` | Layout · Arrange | 🟡 partial | marketing |
| **Table of Contents** `tableOfContents` | references · Table of Contents | 🟡 partial | academic |
| **Update Table** `updateTable` | references · Table of Contents | 🟡 partial | academic |
| **Insert Endnote** `insertEndnote` | references · Footnotes | 🟡 partial | academic |
| **Insert Citation** `insertCitation` | references · Citations & Bibliography | 🟡 partial | academic |
| **Insert Caption** `insertCaption` | references · Captions | 🟡 partial | academic |
| **Cross-reference** `crossReference` | references · Captions | 🟡 partial | academic |
| **Envelopes** `envelopes` | Mailings · Create | 🟡 partial | business-admin |
| **Labels** `labels` | Mailings · Create | 🟡 partial | business-admin |
| **Start Mail Merge** `startMailMerge` | Mailings · Start Mail Merge | 🟡 partial | business-admin |
| **Select Recipients** `selectRecipients` | Mailings · Start Mail Merge | 🟡 partial | business-admin |
| **Edit Recipient List** `editRecipientList` | Mailings · Start Mail Merge | 🟡 partial | business-admin |
| **Address Block** `addressBlock` | Mailings · Write & Insert Fields | 🟡 partial | business-admin |
| **Greeting Line** `greetingLine` | Mailings · Write & Insert Fields | 🟡 partial | business-admin |
| **Finish & Merge** `finishMerge` | Mailings · Finish | 🟡 partial | business-admin |
| **Thesaurus** `thesaurus` | review · Proofing | 🟡 partial | academic |
| **Language** `language` | review · Language | 🟡 partial | business-admin |
| **Filter All Markup** `filterMarkup` | review · Markup | 🟡 partial | legal |
| **Show Markup** `showMarkup` | review · Markup | 🟡 partial | legal |
| **Compare** `compare` | review · Compare | 🟡 partial | legal |
| **Read Mode** `readMode` | view · Views | 🟡 partial | general |
| **Outline** `outline` | view · Views | 🟡 partial | academic |
| **Multiple Pages** `multiplePages` | view · Zoom | 🟡 partial | general |
| **Help** `help` | Help · Help | 🟡 partial | general |
| **Clipboard (pane launcher)** `clipboard` | home · Clipboard | ❌ stub | general |
| **Watermark** `watermark` | design · Page Background | ❌ stub | legal |
| **Group** `group` | Layout · Arrange | ❌ stub | marketing |
| **Translate** `translate` | review · Language | ❌ stub | business-admin |
| **Show Comments** `showComments` | review · Comments | ❌ stub | legal |
| **Split** `split` | view · Window | ❌ stub | general |
| **View Side by Side** `viewSideBySide` | view · Window | ❌ stub | legal |
| **Switch Windows** `switchWindows` | view · Window | ❌ stub | general |

## Drop candidates — T4 rare/negligible (77 controls)

Lowest-usage controls; candidates to defer/ignore for now regardless of status.

| Control | Tab · Group | Status | Segment notes |
|---|---|---|---|
| **Contact Support** `contactSupport` | Help · Help | ❌ stub | Slightly more relevant for IT-supported enterprise/admin users, but still rare; consumer users rarely use in-app support. |
| **Feedback** `feedback` | Help · Help | 🟡 partial | No segment meaningfully elevates this; only enthusiast/insider users submit feedback. |
| **Show Training** `showTraining` | Help · Help | 🟡 partial | Marginally higher for brand-new/learner users onboarding to Word; negligible for everyone else. |
| **What's New** `whatSNew` | Help · Help | 🟡 partial | Slightly higher for tech enthusiasts/Insiders tracking feature releases; negligible for typical users. |
| **Hyphenation** `hyphenation` | Layout · Page Setup | 🟡 partial | Slight bump for print/typesetting/publishing and justified-column layouts; negligible for everyone else. |
| **Line Numbers** `lineNumbers` | Layout · Page Setup | 🟡 partial | High within legal/litigation (pleading paper requires line numbers) and some manuscript/script editing workflows; near-zero general use. |
| **Selection Pane** `selectionPane` | Layout · Arrange | 🟡 partial | Minor use by design power users managing many stacked objects; negligible generally. |
| **Check for Errors** `checkForErrors` | Mailings · Preview Results | 🟡 partial | Occasional safeguard for admin doing large merges; negligible general. |
| **Find Recipient** `findRecipient` | Mailings · Preview Results | ✅ full | Rare even within admin merges (large lists); negligible general. |
| **First Record** `firstRecord` | Mailings · Preview Results | ✅ full | Minor nav within admin merge preview; negligible general. |
| **Go to Record** `goToRecord` | Mailings · Preview Results | ✅ full | Occasional within admin merge preview; negligible general. |
| **Highlight Merge Fields** `highlightMergeFields` | Mailings · Write & Insert Fields | ✅ full | Minor helper even within the admin merge segment; not a primary action. |
| **Last Record** `lastRecord` | Mailings · Preview Results | ✅ full | Minor nav within admin merge preview; negligible general. |
| **Match Fields** `matchFields` | Mailings · Write & Insert Fields | ✅ full | Occasional within admin merge setup when data columns mismatch; otherwise unused. |
| **Next Record** `nextRecord` | Mailings · Preview Results | ✅ full | Minor nav within admin merge preview; negligible general. |
| **Previous Record** `previousRecord` | Mailings · Preview Results | ✅ full | Minor nav within admin merge preview; negligible general. |
| **Rules** `rules` | Mailings · Write & Insert Fields | 🟡 partial | Power-merge feature; only advanced admin/marketing users; negligible general. |
| **Update Labels** `updateLabels` | Mailings · Write & Insert Fields | ❌ stub | Used by admin doing label merges specifically; negligible general. |
| **Colors** `colors` | design · Document Formatting | 🟡 partial | Modest bump for marketing/brand-design work enforcing palette consistency; negligible general usage. |
| **Effects** `effects` | design · Document Formatting | ❌ stub | Minor relevance for design/marketing docs heavy with shapes; effectively unused otherwise. |
| **Fonts** `fonts` | design · Document Formatting | 🟡 partial | Higher for design/template authors establishing typographic systems; negligible for general/legal/academic users. |
| **Set as Default** `setAsDefault` | design · Document Formatting | ❌ stub | Slight relevance for power users/admins standardizing a template; negligible generally. |
| **Style Set** `styleSet` | design · Document Formatting | 🟡 partial | Slightly higher for business power users and template designers who build on Word's Styles system; negligible for casual users. |
| **Add Pen** `addPen` | draw · Pens | 🟡 partial | Slightly higher for heavy stylus users who customize ink tools. |
| **Draw with Trackpad** `drawWithTrackpad` | draw · Pens | ❌ stub | Marginal use among laptop users without a stylus who still want to ink. |
| **Drawing** `drawing` | draw · Pens | ✅ full | Used by tablet/touch and education users entering/leaving ink mode. |
| **Drawing Canvas** `drawingCanvas` | draw · Insert | 🟡 partial | Slightly higher for users assembling multi-stroke drawings or grouped shapes. |
| **Eraser** `eraser` | draw · Tools | ✅ full | Higher for education/tablet users correcting handwritten ink; the stroke/segment eraser sub-items are even more specialized. |
| **Ink Replay** `inkReplay` | draw · Replay | 🟡 partial | Occasional use by educators demonstrating handwriting/step-by-step solutions on tablets. |
| **Ink to Math** `inkToMath` | draw · Convert | ❌ stub | STEM students/researchers on stylus devices are the only meaningful users; near-zero generally. |
| **Ink to Shape** `inkToShape` | draw · Convert | ❌ stub | Niche value for tablet diagramming/education; still rare. |
| **Lasso Select** `lassoSelect` | draw · Tools | 🟡 partial | Modest use among tablet/stylus users editing handwritten notes/diagrams. |
| **Select Objects** `selectObjects` | draw · Tools | 🟡 partial | Slightly higher for tablet/Surface/education users who annotate with ink and need to reposition strokes. |
| **3D Models** `3dModels` | insert · Illustrations | ❌ stub | No segment meaningfully uses it. |
| **Blank Page** `blankPage` | insert · Pages | 🟡 partial | No segment meaningfully elevates it. |
| **Chart** `chart` | insert · Illustrations | 🟡 partial | Slightly higher for business reporting, still very low; most paste from Excel. |
| **Equation** `equation` | insert · Symbols | 🟠 wrong | High for STEM students/researchers; near-zero for general population. |
| **Get Add-ins** `getAddIns` | insert · Add-ins | ❌ stub | None. |
| **My Add-ins** `myAddIns` | insert · Add-ins | ❌ stub | Higher for users with deployed add-ins (e.g. reference managers, but those install own toolbars). |
| **Object** `object` | insert · Text | 🟡 partial | Mild use for embedding spreadsheets/merging files. |
| **Online Video** `onlineVideo` | insert · Media | 🟡 partial | Mild use for educational/interactive content authors. |
| **Screenshot** `screenshot` | insert · Illustrations | 🟡 partial | Mild use for technical/how-to doc authors. |
| **Signature Line** `signatureLine` | insert · Text | ❌ stub | Mild use for formal/legal contract documents. |
| **SmartArt** `smartart` | insert · Illustrations | ❌ stub | Higher for marketing/design (org charts, process diagrams) but still low overall. |
| **WordArt** `wordart` | insert · Text | 🟡 partial | Mild use for marketing/decorative titles; generally legacy. |
| **Add Text** `addText` | references · Table of Contents | 🟡 partial | Occasional use by academic/technical authors fine-tuning a TOC; negligible elsewhere. |
| **Bibliography** `bibliography` | references · Citations & Bibliography | 🟡 partial | Used by students/academics completing a native-citation workflow; negligible general use. |
| **Insert Index** `insertIndex` | references · Index | 🟡 partial | Book/manual authors only. |
| **Insert Table of Authorities** `insertTableOfAuthorities` | references · Table of Authorities | 🟡 partial | Required for many litigation/appellate briefs; otherwise unused. |
| **Insert Table of Figures** `insertTableOfFigures` | references · Captions | 🟡 partial | Occasional thesis/technical-manual use; negligible elsewhere. |
| **Manage Sources** `manageSources` | references · Citations & Bibliography | 🟡 partial | Used by academics maintaining a Word source list; near-zero general use. |
| **Mark Citation** `markCitation` | references · Table of Authorities | 🟡 partial | Mandatory/recurring for litigators preparing court briefs (required by appellate/court rules); negligible for everyone else. |
| **Mark Entry** `markEntry` | references · Index | 🟡 partial | Only authors of books/manuals/long reference works; negligible everywhere else. |
| **Next Footnote** `nextFootnote` | references · Footnotes | 🟡 partial | Marginal use by editors/academics reviewing note-heavy documents. |
| **Researcher** `researcher` | references · Research | ❌ stub | Slight student appeal for topic research, but adoption is minimal even there. |
| **Search** `search` | references · Research | ❌ stub | Occasional curiosity use; no segment elevates it materially. |
| **Show Notes** `showNotes` | references · Footnotes | 🟡 partial | Negligible across all segments. |
| **Style** `style` | references · Citations & Bibliography | 🟡 partial | Meaningful to citation-using students/academics (style is required by their institution); irrelevant to others. |
| **Update Index** `updateIndex` | references · Index | 🟡 partial | Book/manual authors only. |
| **Update Table** `updateTable` | references · Captions | 🟡 partial | Tied to table-of-figures users only. |
| **Update Table** `updateTable` | references · Table of Authorities | 🟡 partial | Litigators only. |
| **Block Authors** `blockAuthors` | review · Protect | ❌ stub | Marginally relevant to enterprise co-authoring admins; negligible elsewhere. |
| **Check Accessibility** `checkAccessibility` | review · Accessibility | 🟡 partial | Regular/mandated for accessibility specialists, gov/public-sector publishers, and orgs with WCAG/Section 508 requirements. |
| **Hide Ink** `hideInk` | review · Ink | 🟡 partial | Marginal relevance to pen/tablet users reviewing inked annotations. |
| **Restrict Editing** `restrictEditing` | review · Protect | 🟡 partial | Higher for business/admin form-builders and legal teams distributing locked documents. |
| **Track Changes Options** `trackChangesOptions` | review · Markup | 🟡 partial | Occasionally adjusted by legal/editorial power users customizing redline appearance. |
| **Arrange All** `arrangeAll` | view · Window | ❌ stub | Negligible across segments. |
| **Draft** `draft` | view · Views | 🟡 partial | Slightly higher among long-time/power users who learned the old Normal view. |
| **Immersive Reader** `immersiveReader` | view · Immersive | 🟡 partial | High for accessibility users, students with reading difficulties (dyslexia), and language learners; negligible for general. |
| **Macros** `macros` | view · Macros | ❌ stub | High for VBA developers and automation power users in business/admin; negligible for everyone else. |
| **New Window** `newWindow` | view · Window | ❌ stub | Slightly higher for power users editing long documents in two places. |
| **Properties** `properties` | view · SharePoint | 🟡 partial | Higher in enterprise/SharePoint-governed environments managing metadata; negligible for general users. |
| **Reset Window Position** `resetWindowPosition` | view · Window | ❌ stub | Negligible across segments. |
| **Side to Side** `sideToSide` | view · Page Movement | 🟡 partial | Marginally higher on touch/tablet usage; still rare. |
| **Synchronous Scrolling** `synchronousScrolling` | view · Window | ❌ stub | Mildly higher for legal/editorial comparison workflows; still rare overall. |
| **Vertical** `vertical` | view · Page Movement | ✅ full | Negligible across segments. |
| **Web Layout** `webLayout` | view · Views | 🟡 partial | Negligible across all segments. |

