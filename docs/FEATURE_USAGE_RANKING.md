# MS Word — Real-World Feature Usage Ranking

Every ribbon control ranked by real-world usage rate (T0 = ubiquitous → T4 = rare), grounded in web-researched Office usage data and calibrated for cross-tab consistency. Primary tier = the typical/general user; `segment_notes` flag features that spike for academics/legal/admin/etc.

## Usage distribution

| Tier | Meaning | Count |
|---|---|---:|
| T0 | Ubiquitous | 11 |
| T1 | High | 19 |
| T2 | Medium | 39 |
| T3 | Low | 68 |
| T4 | Rare/Negligible | 77 |

**Total controls ranked:** 214. 

_Calibration: Overall the tier assignments are well calibrated and closely track the rubric's own examples across all tabs (T2: Symbol, Word Count, Footnote, Track Changes, Comments, Page Break, Columns, Orientation/Size, Borders/Shading all correct; T3: Mail Merge, Citations, TOC, Captions, Watermark, Drop Cap, Text Box, Cross-reference all correct; T4: SmartArt, Equation, Index, Table of Authorities, Macros, 3D Models, Ink-to-Math, Block Authors, Signature Line, Add-ins, Researcher all correct). Cross-tab duplicates are consistent (Editor T1 in both Home and Review; Comment/New Comment both T2; Cross-reference T3 in both Insert and References; Header/Footer/Page Number T1). T0 is appropriately a small elite and the long tail is correctly weighted to T3/T4. The only confident inconsistencies are the three above: Format Painter is over-inflated at T1 (general users use it occasionally, not regularly), and Draft view and Blank Page are over-inflated at T3 relative to genuinely rarer-or-equal peers already sitting at T4 (Web Layout) and the rest of the long tail. I deliberately left borderline cases (Justify vs alignment cluster, Replace vs Find, Increase/Decrease Font Size, the Editor entries) unchanged because their current tiers are defensible and I am not confident a change improves global consistency._

## Controls by usage tier (priority order)

### T0 — Ubiquitous (11)

| Control | Tab · Group | Primary segment | Segment notes | Conf |
|---|---|---|---|---|
| **Paste** `paste` | home · Clipboard | general | Universal across every segment. | high |
| **Cut** `cut` | home · Clipboard | general | Universal across every segment. | high |
| **Copy** `copy` | home · Clipboard | general | Universal across every segment. | high |
| **Font (face)** `font` | home · Font | general | Universal. | high |
| **Font Size** `fontSize` | home · Font | general | Universal. | high |
| **Bold** `bold` | home · Font | general | Universal. | high |
| **Italic** `italic` | home · Font | general | Universal. | high |
| **Underline** `underline` | home · Font | general | Universal. | high |
| **Bullets** `bullets` | home · Paragraph | general | Universal. | high |
| **Align Left** `alignLeft` | home · Paragraph | general | Universal. | high |
| **Center** `center` | home · Paragraph | general | Universal. | high |

### T1 — High (19)

| Control | Tab · Group | Primary segment | Segment notes | Conf |
|---|---|---|---|---|
| **Text Highlight Color** `textHighlightColor` | home · Font | general | Higher for editors/reviewers and students. | high |
| **Font Color** `fontColor` | home · Font | general | Universal-leaning; higher in formatted/marketing docs. | high |
| **Numbering** `numbering` | home · Paragraph | general | Higher for legal/procedural docs. | high |
| **Align Right** `alignRight` | home · Paragraph | general | Universal-leaning. | high |
| **Justify** `justify` | home · Paragraph | general | Higher for print/publishing and formal reports. | medium |
| **Line and Paragraph Spacing** `lineAndParagraphSpacing` | home · Paragraph | general | Higher for academics (double-spacing requirements) and legal. | high |
| **Styles Gallery** `stylesGallery` | home · Styles | academic | High for academics/business power users (TOC, structure); underused by casual general users despite prominence. | medium |
| **Find** `find` | home · Editing | general | Universal-leaning across segments. | high |
| **Replace** `replace` | home · Editing | general | Higher for editors and bulk text cleanup. | high |
| **Editor** `editor` | home · Editor | general | Higher for students and professional writers. | high |
| **Table** `table` | insert · Tables | general | Universal; especially business/admin and academic reports. | high |
| **Pictures** `pictures` | insert · Illustrations | general | Universal; high for marketing/design and students. | high |
| **Link** `link` | insert · Links | general | Universal; especially business and digital documents. | high |
| **Header** `header` | insert · Header & Footer | general | Higher for business/academic formal documents. | high |
| **Footer** `footer` | insert · Header & Footer | general | Higher for business/academic formal documents. | high |
| **Page Number** `pageNumber` | insert · Header & Footer | general | Higher for academics (papers) and business reports. | high |
| **Margins** `margins` | Layout · Page Setup | general | Even higher for academics/business who must hit specific margin specs (e.g., 1-inch for papers). | high |
| **Editor** `editor` | review · Proofing | general | Universal across segments; students/business writers lean on it most for proofreading before submission. | medium |
| **Spelling and Grammar** `spellingGrammar` | review · Proofing | general | Heavier use by students/business writers and ESL users. | medium |

### T2 — Medium (39)

| Control | Tab · Group | Primary segment | Segment notes | Conf |
|---|---|---|---|---|
| **Format Painter** `formatPainter` | home · Clipboard | general | Higher among business/report formatters. | medium |
| **Increase Font Size** `increaseFontSize` | home · Font | general | none | medium |
| **Decrease Font Size** `decreaseFontSize` | home · Font | general | none | medium |
| **Change Case** `changeCase` | home · Font | general | Slightly higher for editors/headline writers. | medium |
| **Clear All Formatting** `clearAllFormatting` | home · Font | general | Higher for users cleaning pasted web content. | medium |
| **Strikethrough** `strikethrough` | home · Font | general | Higher for informal editing/review workflows. | medium |
| **Font dialog (launcher)** `font` | home · Font | general | Higher for typographers/advanced users. | medium |
| **Decrease Indent** `decreaseIndent` | home · Paragraph | general | none | medium |
| **Increase Indent** `increaseIndent` | home · Paragraph | general | none | medium |
| **Show/Hide ¶** `showHide` | home · Paragraph | general | Higher for editors/power users and legal formatters. | medium |
| **Shading** `shading` | home · Paragraph | general | Higher for table/business formatting. | medium |
| **Borders** `borders` | home · Paragraph | general | Higher for table/business formatting. | medium |
| **Paragraph dialog (launcher)** `paragraph` | home · Paragraph | general | Higher for academics/legal needing exact spacing/indents. | medium |
| **Styles pane (launcher)** `styles` | home · Styles | academic | Higher for academics/technical writers managing style sets. | medium |
| **Select** `select` | home · Editing | general | Higher for users editing objects/consistent formatting. | medium |
| **Page Break** `pageBreak` | insert · Pages | general | Higher for academics/business writing long documents. | medium |
| **Shapes** `shapes` | insert · Illustrations | business-admin | Higher for marketing/design and technical/diagram authors. | medium |
| **Comment** `comment` | insert · Comments | legal | Tier-1 for legal/editors/collaborative teams (93% of contracts pros prefer margin comments). | high |
| **Symbol** `symbol` | insert · Symbols | general | Higher for academic/technical writing needing special characters. | high |
| **Orientation** `orientation` | Layout · Page Setup | general | Bumps for business/admin making landscape reports, tables, or certificates. | high |
| **Size** `size` | Layout · Page Setup | general | Cross-region users (Letter vs A4) and print-shop/admin workflows raise it slightly. | high |
| **Columns** `columns` | Layout · Page Setup | general | Higher for marketing/newsletter creators and some academic two-column paper formats. | high |
| **Breaks** `breaks` | Layout · Page Setup | general | Section breaks are heavily used by business/academic power users producing structured long documents. | medium |
| **Indent Left** `indentLeft` | Layout · Paragraph | general | Higher for business/academic users formatting to precise spec (block quotes, legal sub-paragraphs). | medium |
| **Indent Right** `indentRight` | Layout · Paragraph | general | Bumps for academic block-quote formatting (MLA/APA long quotations indent from both margins). | medium |
| **Spacing Before** `spacingBefore` | Layout · Paragraph | general | Higher for academic/business users hitting exact spacing specs; casuals usually leave defaults or use styles. | medium |
| **Spacing After** `spacingAfter` | Layout · Paragraph | general | Higher for academic/business users formatting to spec; many casuals never open the Layout tab for this. | medium |
| **Insert Footnote** `insertFootnote` | references · Footnotes | academic | High/core for academics, students, researchers, and legal writers; low for casual/business users. | high |
| **Word Count** `wordCount` | review · Proofing | academic | High for students/writers with length limits and freelancers paid per word. | high |
| **New Comment** `newComment` | review · Comments | legal | Tier-1 for legal/contracts (93% of contracts pros prefer margin comments) and for editors, teachers, and collaborative teams. | high |
| **Delete** `deleteComment` | review · Comments | legal | High for editors/legal who clean up redlines before finalizing. | medium |
| **Display for Review** `displayForReview` | review · Markup | legal | High for legal/editors who toggle between redline and clean views constantly. | medium |
| **Track Changes** `trackChanges` | review · Tracking | legal | Tier-1 for legal/contracts (91% of negotiators redline with Track Changes) and for editors/collaborative teams. | high |
| **Accept** `accept` | review · Tracking | legal | Tier-1 for legal/editors accepting redlines; the core finalize-revisions action. | high |
| **Reject** `reject` | review · Tracking | legal | Tier-1 for legal/editors negotiating contract revisions. | medium |
| **Print Layout** `printLayout` | view · Views | general | Universal default across all segments; clicked mainly after using Read Mode/Web/Outline. | medium |
| **Ruler** `ruler` | view · Show | general | Higher for users doing precise layout, tab stops, and indentation (business/admin, academic formatting). | medium |
| **Navigation Pane** `navigationPane` | view · Show | academic | Higher for academics, legal, and business users working with long structured documents; tied to heading-style adoption. | medium |
| **Zoom** `zoom` | view · Zoom | general | Broadly relevant; status-bar slider absorbs most actual zoom changes. | medium |

### T3 — Low (68)

| Control | Tab · Group | Primary segment | Segment notes | Conf |
|---|---|---|---|---|
| **Clipboard (pane launcher)** `clipboard` | home · Clipboard | general | none | medium |
| **Subscript** `subscript` | home · Font | academic | Higher for STEM/science writing. | medium |
| **Superscript** `superscript` | home · Font | academic | Higher for STEM/math and citation-heavy writing. | medium |
| **Text Effects and Typography** `textEffectsAndTypography` | home · Font | marketing | Slightly higher for design/title work. | medium |
| **Multilevel List** `multilevelList` | home · Paragraph | legal | Higher for legal contracts and technical/academic outlines. | medium |
| **Sort** `sort` | home · Paragraph | business-admin | Higher for list/table-heavy admin docs. | medium |
| **Cover Page** `coverPage` | insert · Pages | business-admin | Slightly higher for students (report covers) and business proposals, still occasional. | medium |
| **Icons** `icons` | insert · Illustrations | marketing | Higher for marketing/design creating visual collateral. | medium |
| **Bookmark** `bookmark` | insert · Links | business-admin | Higher for technical/legal long-form authors and mail-merge/field workflows. | medium |
| **Cross-reference** `crossReference` | insert · Links | academic | Higher for academics and technical writers referencing figures/headings. | high |
| **Text Box** `textBox` | insert · Text | marketing | Higher for marketing/design and flyer/newsletter layouts. | high |
| **Quick Parts** `quickParts` | insert · Text | business-admin | Higher for business/legal power users building boilerplate and fields. | medium |
| **Drop Cap** `dropCap` | insert · Text | marketing | Higher for publishing/newsletter design, still rare. | high |
| **Date & Time** `dateTime` | insert · Text | business-admin | Higher for letters/templates with auto-updating date fields. | medium |
| **Pens Gallery** `pensGallery` | draw · Pens | accessibility | Meaningfully used by tablet/Surface, education (teacher annotation, student note-taking), and design/markup users; near-zero for typical office desktop users. | medium |
| **Themes** `themes` | design · Document Formatting | marketing | Higher for marketing/design and template-builders making branded/visually consistent docs; near-zero for legal/academic who use prescribed formatting. | medium |
| **Paragraph Spacing** `paragraphSpacing` | design · Document Formatting | academic | Bump for students/academics setting double/relaxed spacing for assignments and manuscripts. | medium |
| **Watermark** `watermark` | design · Page Background | legal | Higher for legal/business/corporate marking drafts as Confidential/Draft; rare for academics and casual users. | high |
| **Page Color** `pageColor` | design · Page Background | marketing | Minor bump for digital/marketing documents meant for screen viewing; near-zero for print and professional docs. | medium |
| **Page Borders** `pageBorders` | design · Page Background | general | Bump for education/admin making certificates, flyers, and award documents; rare in standard business/legal/academic body text. | medium |
| **Position** `position` | Layout · Arrange | marketing | Higher for design/marketing and report authors who place images precisely; irrelevant to text-only docs. | medium |
| **Wrap Text** `wrapText` | Layout · Arrange | general | Notably higher for anyone inserting images (reports, marketing, design); the default-go-to when a picture disrupts layout. | medium |
| **Bring Forward** `bringForward` | Layout · Arrange | marketing | Used by design/marketing creating layered graphics; rare in typical text documents. | medium |
| **Send Backward** `sendBackward` | Layout · Arrange | marketing | Design/marketing layering and 'behind text' watermark-style backdrops; rare otherwise. | medium |
| **Align** `align` | Layout · Arrange | marketing | Higher for design/marketing arranging shapes and images; rare in plain documents. | medium |
| **Group** `group` | Layout · Arrange | marketing | Design/marketing assembling shape compositions; negligible for text docs. | medium |
| **Rotate** `rotate` | Layout · Arrange | marketing | Design/marketing image and shape adjustments; rare in typical documents. | medium |
| **Table of Contents** `tableOfContents` | references · Table of Contents | academic | High for academics, students writing theses/reports, and business/technical authors of long documents. Near-zero for casual/general users. | high |
| **Update Table** `updateTable` | references · Table of Contents | academic | Routine for academics/long-doc authors who maintain a TOC; negligible for general users. | medium |
| **Insert Endnote** `insertEndnote` | references · Footnotes | academic | Used by some academics/humanities authors; rare in general and business use. | high |
| **Insert Citation** `insertCitation` | references · Citations & Bibliography | academic | High for students/academics who use Word's built-in citations; competes with external reference managers. Negligible for general/business/legal. | high |
| **Insert Caption** `insertCaption` | references · Captions | academic | Common for thesis/report/technical writers; negligible for general/business. | high |
| **Cross-reference** `crossReference` | references · Captions | academic | Common among technical/academic/long-doc authors; rare for casual users. | high |
| **Envelopes** `envelopes` | Mailings · Create | business-admin | T2 for business/admin and home-office users who print correspondence; T4 for students/academics. | medium |
| **Labels** `labels` | Mailings · Create | business-admin | T2 for business/admin/education-admin (badges, shipping, mailing labels); rare for casual/academic. | medium |
| **Start Mail Merge** `startMailMerge` | Mailings · Start Mail Merge | business-admin | T2 for business/HR/marketing/admin doing bulk letters/labels/certificates; T4 general/academic. | high |
| **Select Recipients** `selectRecipients` | Mailings · Start Mail Merge | business-admin | T2 for admin/marketing performing merges; near-zero general/academic. | high |
| **Edit Recipient List** `editRecipientList` | Mailings · Start Mail Merge | business-admin | T2 within admin/marketing merge work; effectively never for general users. | high |
| **Address Block** `addressBlock` | Mailings · Write & Insert Fields | business-admin | T2 for admin/marketing letter merges; T4 general. | medium |
| **Greeting Line** `greetingLine` | Mailings · Write & Insert Fields | business-admin | T2 for admin/marketing personalized letters; rare elsewhere. | medium |
| **Insert Merge Field** `insertMergeField` | Mailings · Write & Insert Fields | business-admin | T2 (effectively core) within admin/marketing merge work; T4 general/academic. | high |
| **Preview Results** `previewResults` | Mailings · Preview Results | business-admin | T2 within admin/marketing merge work; T4 general. | medium |
| **Finish & Merge** `finishMerge` | Mailings · Finish | business-admin | T2 (required) within admin/marketing merges; T4 general/academic. | high |
| **Thesaurus** `thesaurus` | review · Proofing | academic | Slightly higher for students/writers polishing prose; still low overall. | medium |
| **Read Aloud** `readAloud` | review · Speech | accessibility | High for accessibility users, dyslexic readers, and proofreaders who catch errors aurally. | medium |
| **Translate** `translate` | review · Language | business-admin | Higher for multilingual/international business, NGOs, and ESL users. | medium |
| **Language** `language` | review · Language | business-admin | More common for bilingual writers and international teams switching proofing locales. | medium |
| **Previous** `previousComment` | review · Comments | legal | Higher for reviewers/editors processing many comments sequentially. | medium |
| **Next** `nextComment` | review · Comments | legal | Higher for editors/legal reviewers triaging long comment threads. | medium |
| **Show Comments** `showComments` | review · Comments | legal | Modestly higher for heavy collaborators managing dense comment sets. | medium |
| **Filter All Markup** `filterMarkup` | review · Markup | legal | Higher for legal/editorial reviewers isolating specific change types. | low |
| **Show Markup** `showMarkup` | review · Markup | legal | High for legal/multi-reviewer workflows filtering by author or change type. | medium |
| **Reviewing Pane** `reviewingPane` | review · Markup | legal | Higher for legal/editorial QA confirming no tracked changes remain. | low |
| **Previous** `previousChange` | review · Tracking | legal | Higher for legal/editors auditing revisions sequentially. | low |
| **Next** `nextChange` | review · Tracking | legal | Higher for legal/editorial reviewers walking through every change. | low |
| **Compare** `compare` | review · Compare | legal | High for legal/contracts producing blacklines between versions; part of the core legal toolkit. | medium |
| **Read Mode** `readMode` | view · Views | general | Slightly higher for casual readers/reviewers consuming (not editing) documents. | medium |
| **Outline** `outline` | view · Views | academic | Higher for academics/authors writing long structured documents (theses, books, reports). | medium |
| **Focus** `focus` | view · Immersive | general | Higher among long-form writers/authors who want a clean writing surface. | medium |
| **Gridlines** `gridlines` | view · Show | marketing | Higher for design/marketing users aligning shapes and graphics. | medium |
| **100%** `100` | view · Zoom | general | No strong segment bump. | medium |
| **One Page** `onePage` | view · Zoom | general | Mild bump for users checking page layout before printing. | medium |
| **Multiple Pages** `multiplePages` | view · Zoom | general | Mild bump for layout/print-review workflows. | medium |
| **Page Width** `pageWidth` | view · Zoom | general | No strong segment bump. | medium |
| **Split** `split` | view · Window | general | Higher for editors and long-form writers cross-referencing within a document. | medium |
| **View Side by Side** `viewSideBySide` | view · Window | legal | Higher for legal/editorial reviewers comparing document versions. | medium |
| **Switch Windows** `switchWindows` | view · Window | general | Mild bump for users juggling many open documents. | medium |
| **Help** `help` | Help · Help | general | Marginally higher for novice/casual users learning Word; near-zero for power users who self-serve via web search. | medium |

### T4 — Rare/Negligible (77)

| Control | Tab · Group | Primary segment | Segment notes | Conf |
|---|---|---|---|---|
| **Blank Page** `blankPage` | insert · Pages | general | No segment meaningfully elevates it. | medium |
| **3D Models** `3dModels` | insert · Illustrations | none | No segment meaningfully uses it. | high |
| **SmartArt** `smartart` | insert · Illustrations | marketing | Higher for marketing/design (org charts, process diagrams) but still low overall. | high |
| **Chart** `chart` | insert · Illustrations | business-admin | Slightly higher for business reporting, still very low; most paste from Excel. | medium |
| **Screenshot** `screenshot` | insert · Illustrations | none | Mild use for technical/how-to doc authors. | medium |
| **Get Add-ins** `getAddIns` | insert · Add-ins | none | None. | high |
| **My Add-ins** `myAddIns` | insert · Add-ins | developer | Higher for users with deployed add-ins (e.g. reference managers, but those install own toolbars). | high |
| **Online Video** `onlineVideo` | insert · Media | none | Mild use for educational/interactive content authors. | medium |
| **WordArt** `wordart` | insert · Text | marketing | Mild use for marketing/decorative titles; generally legacy. | high |
| **Signature Line** `signatureLine` | insert · Text | business-admin | Mild use for formal/legal contract documents. | high |
| **Object** `object` | insert · Text | business-admin | Mild use for embedding spreadsheets/merging files. | medium |
| **Equation** `equation` | insert · Symbols | academic | High for STEM students/researchers; near-zero for general population. | high |
| **Select Objects** `selectObjects` | draw · Tools | none | Slightly higher for tablet/Surface/education users who annotate with ink and need to reposition strokes. | high |
| **Lasso Select** `lassoSelect` | draw · Tools | none | Modest use among tablet/stylus users editing handwritten notes/diagrams. | high |
| **Eraser** `eraser` | draw · Tools | none | Higher for education/tablet users correcting handwritten ink; the stroke/segment eraser sub-items are even more specialized. | high |
| **Add Pen** `addPen` | draw · Pens | none | Slightly higher for heavy stylus users who customize ink tools. | high |
| **Draw with Trackpad** `drawWithTrackpad` | draw · Pens | none | Marginal use among laptop users without a stylus who still want to ink. | high |
| **Drawing** `drawing` | draw · Pens | none | Used by tablet/touch and education users entering/leaving ink mode. | high |
| **Ink to Shape** `inkToShape` | draw · Convert | none | Niche value for tablet diagramming/education; still rare. | high |
| **Ink to Math** `inkToMath` | draw · Convert | academic | STEM students/researchers on stylus devices are the only meaningful users; near-zero generally. | high |
| **Drawing Canvas** `drawingCanvas` | draw · Insert | none | Slightly higher for users assembling multi-stroke drawings or grouped shapes. | high |
| **Ink Replay** `inkReplay` | draw · Replay | none | Occasional use by educators demonstrating handwriting/step-by-step solutions on tablets. | high |
| **Style Set** `styleSet` | design · Document Formatting | none | Slightly higher for business power users and template designers who build on Word's Styles system; negligible for casual users. | medium |
| **Colors** `colors` | design · Document Formatting | marketing | Modest bump for marketing/brand-design work enforcing palette consistency; negligible general usage. | medium |
| **Fonts** `fonts` | design · Document Formatting | marketing | Higher for design/template authors establishing typographic systems; negligible for general/legal/academic users. | medium |
| **Effects** `effects` | design · Document Formatting | marketing | Minor relevance for design/marketing docs heavy with shapes; effectively unused otherwise. | medium |
| **Set as Default** `setAsDefault` | design · Document Formatting | none | Slight relevance for power users/admins standardizing a template; negligible generally. | high |
| **Line Numbers** `lineNumbers` | Layout · Page Setup | legal | High within legal/litigation (pleading paper requires line numbers) and some manuscript/script editing workflows; near-zero general use. | high |
| **Hyphenation** `hyphenation` | Layout · Page Setup | marketing | Slight bump for print/typesetting/publishing and justified-column layouts; negligible for everyone else. | high |
| **Selection Pane** `selectionPane` | Layout · Arrange | marketing | Minor use by design power users managing many stacked objects; negligible generally. | medium |
| **Add Text** `addText` | references · Table of Contents | academic | Occasional use by academic/technical authors fine-tuning a TOC; negligible elsewhere. | high |
| **Next Footnote** `nextFootnote` | references · Footnotes | academic | Marginal use by editors/academics reviewing note-heavy documents. | high |
| **Show Notes** `showNotes` | references · Footnotes | academic | Negligible across all segments. | high |
| **Search** `search` | references · Research | none | Occasional curiosity use; no segment elevates it materially. | high |
| **Researcher** `researcher` | references · Research | academic | Slight student appeal for topic research, but adoption is minimal even there. | high |
| **Manage Sources** `manageSources` | references · Citations & Bibliography | academic | Used by academics maintaining a Word source list; near-zero general use. | medium |
| **Style** `style` | references · Citations & Bibliography | academic | Meaningful to citation-using students/academics (style is required by their institution); irrelevant to others. | medium |
| **Bibliography** `bibliography` | references · Citations & Bibliography | academic | Used by students/academics completing a native-citation workflow; negligible general use. | medium |
| **Insert Table of Figures** `insertTableOfFigures` | references · Captions | academic | Occasional thesis/technical-manual use; negligible elsewhere. | high |
| **Update Table** `updateTable` | references · Captions | academic | Tied to table-of-figures users only. | high |
| **Mark Entry** `markEntry` | references · Index | academic | Only authors of books/manuals/long reference works; negligible everywhere else. | high |
| **Insert Index** `insertIndex` | references · Index | academic | Book/manual authors only. | high |
| **Update Index** `updateIndex` | references · Index | academic | Book/manual authors only. | high |
| **Mark Citation** `markCitation` | references · Table of Authorities | legal | Mandatory/recurring for litigators preparing court briefs (required by appellate/court rules); negligible for everyone else. | high |
| **Insert Table of Authorities** `insertTableOfAuthorities` | references · Table of Authorities | legal | Required for many litigation/appellate briefs; otherwise unused. | high |
| **Update Table** `updateTable` | references · Table of Authorities | legal | Litigators only. | high |
| **Highlight Merge Fields** `highlightMergeFields` | Mailings · Write & Insert Fields | business-admin | Minor helper even within the admin merge segment; not a primary action. | high |
| **Rules** `rules` | Mailings · Write & Insert Fields | business-admin | Power-merge feature; only advanced admin/marketing users; negligible general. | high |
| **Match Fields** `matchFields` | Mailings · Write & Insert Fields | business-admin | Occasional within admin merge setup when data columns mismatch; otherwise unused. | high |
| **Update Labels** `updateLabels` | Mailings · Write & Insert Fields | business-admin | Used by admin doing label merges specifically; negligible general. | high |
| **First Record** `firstRecord` | Mailings · Preview Results | business-admin | Minor nav within admin merge preview; negligible general. | high |
| **Previous Record** `previousRecord` | Mailings · Preview Results | business-admin | Minor nav within admin merge preview; negligible general. | high |
| **Go to Record** `goToRecord` | Mailings · Preview Results | business-admin | Occasional within admin merge preview; negligible general. | high |
| **Next Record** `nextRecord` | Mailings · Preview Results | business-admin | Minor nav within admin merge preview; negligible general. | high |
| **Last Record** `lastRecord` | Mailings · Preview Results | business-admin | Minor nav within admin merge preview; negligible general. | high |
| **Find Recipient** `findRecipient` | Mailings · Preview Results | business-admin | Rare even within admin merges (large lists); negligible general. | high |
| **Check for Errors** `checkForErrors` | Mailings · Preview Results | business-admin | Occasional safeguard for admin doing large merges; negligible general. | high |
| **Check Accessibility** `checkAccessibility` | review · Accessibility | accessibility | Regular/mandated for accessibility specialists, gov/public-sector publishers, and orgs with WCAG/Section 508 requirements. | medium |
| **Track Changes Options** `trackChangesOptions` | review · Markup | legal | Occasionally adjusted by legal/editorial power users customizing redline appearance. | low |
| **Block Authors** `blockAuthors` | review · Protect | none | Marginally relevant to enterprise co-authoring admins; negligible elsewhere. | high |
| **Restrict Editing** `restrictEditing` | review · Protect | business-admin | Higher for business/admin form-builders and legal teams distributing locked documents. | medium |
| **Hide Ink** `hideInk` | review · Ink | accessibility | Marginal relevance to pen/tablet users reviewing inked annotations. | medium |
| **Web Layout** `webLayout` | view · Views | none | Negligible across all segments. | high |
| **Draft** `draft` | view · Views | general | Slightly higher among long-time/power users who learned the old Normal view. | medium |
| **Immersive Reader** `immersiveReader` | view · Immersive | accessibility | High for accessibility users, students with reading difficulties (dyslexia), and language learners; negligible for general. | medium |
| **Vertical** `vertical` | view · Page Movement | none | Negligible across segments. | high |
| **Side to Side** `sideToSide` | view · Page Movement | none | Marginally higher on touch/tablet usage; still rare. | high |
| **New Window** `newWindow` | view · Window | none | Slightly higher for power users editing long documents in two places. | high |
| **Arrange All** `arrangeAll` | view · Window | none | Negligible across segments. | high |
| **Synchronous Scrolling** `synchronousScrolling` | view · Window | legal | Mildly higher for legal/editorial comparison workflows; still rare overall. | high |
| **Reset Window Position** `resetWindowPosition` | view · Window | none | Negligible across segments. | high |
| **Macros** `macros` | view · Macros | developer | High for VBA developers and automation power users in business/admin; negligible for everyone else. | high |
| **Properties** `properties` | view · SharePoint | business-admin | Higher in enterprise/SharePoint-governed environments managing metadata; negligible for general users. | high |
| **Contact Support** `contactSupport` | Help · Help | general | Slightly more relevant for IT-supported enterprise/admin users, but still rare; consumer users rarely use in-app support. | high |
| **Feedback** `feedback` | Help · Help | general | No segment meaningfully elevates this; only enthusiast/insider users submit feedback. | high |
| **Show Training** `showTraining` | Help · Help | general | Marginally higher for brand-new/learner users onboarding to Word; negligible for everyone else. | high |
| **What's New** `whatSNew` | Help · Help | general | Slightly higher for tech enthusiasts/Insiders tracking feature releases; negligible for typical users. | high |

## Per-tab detail

### home

| Control | Group | Tier | Rationale | Segment | Conf | Sources |
|---|---|---|---|---|---|---|
| **Paste** | Clipboard | T0 | #1 most-used command in Word telemetry, >11% of all command invocations, more than 2x #2. The single most-clicked toolbar button; Microsoft made it the first/largest Home button. | general | high | ms-official CEIP (Jensen Harris no-distaste-for-paste): Paste #1, >11% |
| **Cut** | Clipboard | T0 | Core clipboard op; Ctrl+X universal. Conspicuously absent from published top-5 but inferred top-tens; clipboard group is the single most important Home group. | general | high | ms-official CEIP (clipboard dominance; Cut rank not individually published) |
| **Copy** | Clipboard | T0 | #3 most-used command in Word telemetry. Core clipboard op used in nearly every session. | general | high | ms-official CEIP: Copy #3 |
| **Font (face)** | Font | T0 | Font name is a Mini-Toolbar 'most-used formatting' command; changing typeface is a near-universal action. Listed as T0 example in rubric (font face). | general | high | ms-official (Mini Toolbar most-used formatting); rubric T0 example |
| **Font Size** | Font | T0 | 'Change Font Size' is explicitly anchored at rank #11 in Word telemetry, top of the steep head. Mini-Toolbar core command. | general | high | ms-official CEIP: Change Font Size #11 |
| **Bold** | Font | T0 | #5 most-used command in Word telemetry; only character-format command with a hard rank. Mini-Toolbar core. | general | high | ms-official CEIP: Bold #5 |
| **Italic** | Font | T0 | Core character format inferred in top-tens via Mini-Toolbar most-used formatting; ubiquitous alongside Bold/Underline. | general | high | ms-official (Mini Toolbar); rubric T0 example |
| **Underline** | Font | T0 | Core character format, Mini-Toolbar most-used; very widely used though slightly below Bold. The split-dropdown styles are themselves lower-use. | general | high | ms-official (Mini Toolbar most-used formatting) |
| **Bullets** | Paragraph | T0 | Bullet list is a rubric T0 example; near-universal for structured docs. | general | high | rubric T0 example (bullet list) |
| **Align Left** | Paragraph | T0 | Alignment is a rubric T0 example; left is the default and toggled routinely. Mini-Toolbar/core. | general | high | rubric T0 example (alignment) |
| **Center** | Paragraph | T0 | Centering titles/headings is near-universal; alignment is a rubric T0 example. | general | high | rubric T0 example (alignment) |
| **Format Painter** | Clipboard | T2 | Well-known, commonly used formatting-copy tool; regularly used by most users though far below clipboard core. Sits in the mid-to-high band, not ubiquitous. | general | medium | rubric+reasoning; not individually telemetered |
| **Text Highlight Color** | Font | T1 | Highlighter is a commonly used review/emphasis tool; rubric lists Highlight as a T1 example. | general | high | rubric T1 example (Highlight) |
| **Font Color** | Font | T1 | Mini-Toolbar most-used formatting; rubric lists font Color as a T1 example. Used regularly by most. | general | high | ms-official (Mini Toolbar); rubric T1 example (font Color) |
| **Numbering** | Paragraph | T1 | Numbered lists very widely used though slightly less ubiquitous than bullets; regularly used by most. | general | high | rubric (bullets/numbering near T0/T1) |
| **Align Right** | Paragraph | T1 | Right alignment used regularly (dates, headers) but less than left/center; part of the alignment cluster. | general | high | rubric (alignment cluster) |
| **Justify** | Paragraph | T1 | Justify is commonly applied to body text in formal/print docs; regularly used by a large share though below left/center. | general | medium | rubric (alignment cluster) |
| **Line and Paragraph Spacing** | Paragraph | T1 | Line/paragraph spacing (single/1.5/double) is a very common adjustment for essays, reports, legal docs; regularly used by most. | general | high | rubric+reasoning; segments (academic formatting) |
| **Styles Gallery** | Styles | T1 | Heading/Styles is a rubric T1 example and high-value, but evidence shows it is heavily UNDERused by casual users who format manually. Tiered T1 as primary due to prominence and academic/business reliance. | academic | medium | rubric T1 (Heading/Styles); surveys-analytics & segments (Styles underused but high-value) |
| **Find** | Editing | T1 | Find (Ctrl+F) is a rubric T1 example; used regularly by most to locate text. | general | high | rubric T1 example (Find) |
| **Replace** | Editing | T1 | Find & Replace (Ctrl+H) is commonly used to fix repeated text; basic replace is high-use, advanced options T2. | general | high | rubric (Find/Replace); evidence T1-segment list |
| **Editor** | Editor | T1 | Spelling & grammar (F7/Editor pane) is a rubric T1 example; used regularly though many rely on inline squiggles rather than opening the pane. | general | high | rubric T1 example (Spelling); segments (spell/grammar T2-mainstream) |
| **Increase Font Size** | Font | T2 | Incremental size buttons are used occasionally; most users set size via the size box directly. Convenience variant of a T0 action. | general | medium | rubric+reasoning |
| **Decrease Font Size** | Font | T2 | Incremental size buttons used occasionally; size box is the dominant path. Convenience variant. | general | medium | rubric+reasoning |
| **Change Case** | Font | T2 | Occasionally used to fix capitalization (UPPER/lowercase/Title); a meaningful minority touches it but not routine. | general | medium | rubric+reasoning |
| **Clear All Formatting** | Font | T2 | Used occasionally to strip formatting after paste; useful but not part of routine document creation for most. | general | medium | rubric+reasoning |
| **Strikethrough** | Font | T2 | Occasionally used for edits/markup-by-hand and list crossing-out; meaningful minority, well below the core triad. | general | medium | rubric+reasoning |
| **Font dialog (launcher)** | Font | T2 | Ctrl+D Font dialog for advanced character spacing/OpenType; used occasionally when ribbon buttons are insufficient. Most formatting happens on the ribbon/Mini-Toolbar. | general | medium | rubric+reasoning |
| **Decrease Indent** | Paragraph | T2 | Indent buttons used occasionally; many users indent via Tab or rely on list levels. Meaningful minority. | general | medium | rubric+reasoning |
| **Increase Indent** | Paragraph | T2 | Indent buttons used occasionally, slightly more than decrease; still below core formatting. Many indent via Tab. | general | medium | rubric+reasoning |
| **Show/Hide ¶** | Paragraph | T2 | Formatting-marks toggle used by intermediate/power users to debug layout; a meaningful minority, unknown to many casuals. | general | medium | rubric+reasoning |
| **Shading** | Paragraph | T2 | Paragraph/cell background color used occasionally, often with tables; meaningful minority, well below core. | general | medium | rubric+reasoning (Borders/Shading T2) |
| **Borders** | Paragraph | T2 | Rubric lists Borders/Shading as T2; used occasionally for tables and rule lines. | general | medium | rubric T2 example (Borders/Shading) |
| **Paragraph dialog (launcher)** | Paragraph | T2 | Paragraph dialog (indents, spacing, line/page breaks, widow control) is used occasionally by users needing precise control beyond ribbon buttons. | general | medium | rubric+reasoning |
| **Styles pane (launcher)** | Styles | T2 | The full Styles task pane (manage/modify styles) is used occasionally by power users; most apply styles from the gallery, fewer open the pane. | academic | medium | rubric+reasoning |
| **Select** | Editing | T2 | Select All is common via Ctrl+A, but the ribbon dropdown (Select Objects, Select Similar Formatting, Selection Pane) is used occasionally by a minority. | general | medium | rubric+reasoning |
| **Clipboard (pane launcher)** | Clipboard | T3 | The Office Clipboard task pane (collect-and-paste multiple items) is rarely opened; most users rely on single-item Ctrl+V. Dialog launchers are low-traffic. | general | medium | rubric+reasoning |
| **Subscript** | Font | T3 | Niche; mainly chemical formulae/footnote-like notation. Few general users ever apply it. | academic | medium | rubric+reasoning |
| **Superscript** | Font | T3 | Niche; ordinals, exponents, footnote markers. Slightly more common than subscript but still low for general users. | academic | medium | rubric+reasoning |
| **Text Effects and Typography** | Font | T3 | Decorative shadow/glow/outline and OpenType ligatures/stylistic sets; rarely used in professional docs, decorative niche. | marketing | medium | rubric+reasoning; segments brief (decorative features niche) |
| **Multilevel List** | Paragraph | T3 | Outline/multilevel numbering is fiddly and niche; mostly legal/technical/academic outlining. Few general users configure it. | legal | medium | rubric+reasoning; segments (legal numbering) |
| **Sort** | Paragraph | T3 | Alphabetical/numeric sort of lists/tables is a specific occasional workflow; most users never invoke it. | business-admin | medium | rubric+reasoning |

### insert

| Control | Group | Tier | Rationale | Segment | Conf | Sources |
|---|---|---|---|---|---|---|
| **Table** | Tables | T1 | Insert Table is explicitly named in the rubric as a T1 high-use control; tables are common across nearly all document types. | general | high | rubric (Insert Table=T1); segments brief Tier-2 common |
| **Pictures** | Illustrations | T1 | Insert Picture is named in the rubric as a T1 control; inserting images is one of the most common non-text actions. | general | high | rubric (Insert Picture=T1) |
| **Link** | Links | T1 | Hyperlink is named in the rubric as a T1 control (Ctrl+K). Common in web-aware and reference documents. | general | high | rubric (Hyperlink=T1) |
| **Header** | Header & Footer | T1 | Header/Footer named in rubric as T1; common in formal/business/academic documents. | general | high | rubric (Header/Footer=T1) |
| **Footer** | Header & Footer | T1 | Header/Footer named in rubric as T1; footers commonly hold page numbers and document info. | general | high | rubric (Header/Footer=T1) |
| **Page Number** | Header & Footer | T1 | Page Number explicitly named in rubric as a T1 control; near-essential for multi-page documents. | general | high | rubric (Page Number=T1) |
| **Page Break** | Pages | T2 | Page Break is a commonly needed structural action for multi-page documents; rubric lists Page Break as T2. Often done via Ctrl+Enter but the ribbon button sees meaningful use. | general | medium | rubric (Page Break=T2) |
| **Shapes** | Illustrations | T2 | Shapes (lines, arrows, boxes) see moderate use for diagrams and annotations but most documents have none. A meaningful minority uses them. | business-admin | medium | rubric+reasoning; segments brief (design cluster) |
| **Comment** | Comments | T2 | Comments are a mainstream collaboration feature; rubric lists Comments as T2 for general users. Heavily used in review workflows. | legal | high | rubric (Comments=T2); segments brief (Contract Nerds 93%) |
| **Symbol** | Symbols | T2 | Symbol explicitly listed in rubric as T2 medium; used occasionally to insert special characters (©, accents, em dash, etc.). | general | high | rubric (Symbol=T2) |
| **Cover Page** | Pages | T3 | Decorative cover pages are a niche feature used mostly for reports/proposals; most documents never get one. Gallery-driven, low recurring use. | business-admin | medium | rubric+reasoning; segments brief (design/visual features niche) |
| **Blank Page** | Pages | T4 | Most users press Enter/Ctrl+Enter rather than the Blank Page button, which inserts two breaks. Rarely clicked. | general | medium | rubric+reasoning |
| **Icons** | Illustrations | T3 | Modern icon-picker feature; nice for visual docs but most users never insert icons. Newer than the legacy core. | marketing | medium | rubric+reasoning; segments brief (design features niche) |
| **Bookmark** | Links | T3 | Bookmarks are a niche navigation/linking aid used in long structured documents and as targets for cross-references; most users never create them. | business-admin | medium | rubric+reasoning |
| **Cross-reference** | Links | T3 | Cross-reference explicitly listed in rubric as T3 low/niche; used in structured academic/technical/legal documents. | academic | high | rubric (Cross-reference=T3) |
| **Text Box** | Text | T3 | Text Box explicitly listed in rubric as T3 low/niche; used for callouts and design layouts. | marketing | high | rubric (Text Box=T3) |
| **Quick Parts** | Text | T3 | Quick Parts/AutoText/Fields/Building Blocks is a power-user feature; cited as underused. Most users never open it. | business-admin | medium | rubric+reasoning; surveys brief (AutoText/Building Blocks underutilized) |
| **Drop Cap** | Text | T3 | Drop Cap explicitly listed in rubric as T3 low/niche; decorative paragraph styling for newsletters/print design. | marketing | high | rubric (Drop Cap=T3) |
| **Date & Time** | Text | T3 | Inserting a date/time field is occasional; most users just type the date. Modest use for letters/templates. | business-admin | medium | rubric+reasoning |
| **3D Models** | Illustrations | T4 | 3D Models explicitly listed in rubric as T4 rare/negligible; extremely few users ever insert one. | none | high | rubric (3D Models=T4) |
| **SmartArt** | Illustrations | T4 | SmartArt explicitly listed in rubric as T4 rare/negligible. Design-oriented diagram feature most never touch. | marketing | high | rubric (SmartArt=T4); segments brief (SmartArt/WordArt marketing niche) |
| **Chart** | Illustrations | T4 | Inserting native Word charts is rare; most users build charts in Excel and paste. Niche feature. | business-admin | medium | rubric+reasoning |
| **Screenshot** | Illustrations | T4 | Built-in screenshot capture is rarely used; users typically use OS snipping tools and paste. Negligible ribbon use. | none | medium | rubric+reasoning |
| **Get Add-ins** | Add-ins | T4 | Office Store / Add-ins explicitly listed in rubric as T4 rare/negligible. | none | high | rubric (Add-ins/Office Store=T4) |
| **My Add-ins** | Add-ins | T4 | Inserting installed add-ins is a power-user/admin action; the vast majority of users never open this. Rubric T4 (Add-ins). | developer | high | rubric (Add-ins=T4) |
| **Online Video** | Media | T4 | Embedding online video in a Word doc is very rare; Word is a print/static medium for most. Negligible use. | none | medium | rubric+reasoning |
| **WordArt** | Text | T4 | WordArt explicitly listed in rubric as T3/T4; widely regarded as legacy/decorative and rarely used in professional docs. | marketing | high | rubric (WordArt=T3/T4); segments brief (WordArt legacy/rare) |
| **Signature Line** | Text | T4 | Signature Line explicitly listed in rubric as T4 rare/negligible; digital signature workflow few use. | business-admin | high | rubric (Signature Line=T4) |
| **Object** | Text | T4 | Embedding OLE objects / Text from File is a power-user feature rarely used; most paste content instead. | business-admin | medium | rubric+reasoning |
| **Equation** | Symbols | T4 | Equation explicitly listed in rubric as T4 rare/negligible for general users; STEM-academic niche. | academic | high | rubric (Equation=T4); segments brief (Equation STEM niche) |

### draw

| Control | Group | Tier | Rationale | Segment | Conf | Sources |
|---|---|---|---|---|---|---|
| **Pens Gallery** | Pens | T3 | The headline control of the Draw tab and the entry point for all inking (pen/pencil/highlighter). It is the single most-used control within this tab, but the tab itself is device-dependent and niche, so it lands at low rather than rare. Bumped above the rest of the tab because anyone who uses Draw at all uses this first. | accessibility | medium | rubric+reasoning; segments brief (ink = device-specific) |
| **Select Objects** | Tools | T4 | Selects ink/shape objects within the Draw inking context. The entire Draw tab is touchscreen/stylus-oriented and rarely visited by the mouse-and-keyboard majority; selecting ink objects is a secondary action inside an already-niche workflow. No telemetry rank, but firmly in the flat negligible tail. | none | high | rubric+reasoning; segments brief (ink features are device-dependent niche) |
| **Lasso Select** | Tools | T4 | Lasso selection of ink strokes is an advanced sub-action of an already niche inking tab. Only relevant once a user is actively drawing ink and needs free-form selection; effectively never touched by general users. | none | high | rubric+reasoning |
| **Eraser** | Tools | T4 | Erases ink strokes. Only meaningful to users who are inking with a pen/touch; the general mouse-keyboard population never enters the Draw tab. Negligible overall usage. | none | high | rubric+reasoning |
| **Add Pen** | Pens | T4 | Adds a new customized pen/pencil/highlighter/action pen to the gallery. A configuration action within the niche inking workflow; the default pens suffice for nearly everyone who inks. Negligible overall usage. | none | high | rubric+reasoning |
| **Draw with Trackpad** | Pens | T4 | A fallback inking mode for users without touchscreen/pen, drawing via trackpad. Extremely awkward and rarely used; a niche-within-a-niche feature. | none | high | rubric+reasoning |
| **Drawing** | Pens | T4 | Toggles ink drawing mode on/off. Only relevant to the small population that inks; general users never engage it. Negligible overall usage. | none | high | rubric+reasoning |
| **Ink to Shape** | Convert | T4 | Auto-converts hand-drawn ink into clean geometric shapes. Specialized inking conversion feature, only meaningful when actively drawing with a pen. Effectively never used by the general population. | none | high | rubric+reasoning |
| **Ink to Math** | Convert | T4 | Converts handwritten math into a typeset equation. Doubly niche: requires both inking (Draw tab) and equation/STEM workflows. Comparable to Ink Equation; among the rarest controls in Word. | academic | high | rubric+reasoning; segments brief (equations = STEM niche) |
| **Drawing Canvas** | Insert | T4 | Inserts a container to group ink/drawing parts. A structural helper for drawings; most users who add shapes never bother with a canvas, and within the Draw tab it remains a secondary action. Negligible overall usage. | none | high | rubric+reasoning |
| **Ink Replay** | Replay | T4 | Animates ink strokes back in drawn order. A novelty/presentation feature inside the niche inking tab; essentially never used by general users. | none | high | rubric+reasoning |

### design

| Control | Group | Tier | Rationale | Segment | Conf | Sources |
|---|---|---|---|---|---|---|
| **Themes** | Document Formatting | T3 | Changes the entire document's color/font/effect design. The most prominent Design-tab control, but the whole tab is low-traffic: most users never open Design and format manually instead. Theme switching is a deliberate, occasional act tied to visual polish, not routine editing. No hard telemetry; falls in the flat long tail well below core formatting. | marketing | medium | segments brief (design cluster: themes/colors/fonts directionally low, marketing-leaning); ms-official flat long-tail; rubric+reasoning |
| **Paragraph Spacing** | Document Formatting | T3 | One-click whole-document line/paragraph spacing presets. More discoverable and useful than the theme controls, and overlaps a genuinely common need (spacing), but it's a document-wide shortcut on a low-traffic tab; most users adjust spacing via the Home paragraph-spacing button or Paragraph dialog instead. Occasional use by a minority. | academic | medium | rubric+reasoning; ms-official flat long-tail |
| **Watermark** | Page Background | T3 | Inserts ghosted background text (Confidential, Draft, etc.). Explicitly cited as a T3 niche example in the rubric. Used in specific document-control workflows but rarely by the typical user; recurring in business/legal contexts. | legal | high | rubric (Watermark = T3 example); segments brief (watermark in design cluster, low general); reasoning |
| **Page Color** | Page Background | T3 | Sets the page background fill color. Rarely useful for printed documents (wastes ink, doesn't print by default) and only occasionally used for on-screen/digital documents. A niche cosmetic choice; firmly low-usage. | marketing | medium | segments brief (page color in design cluster, low usage); rubric+reasoning |
| **Page Borders** | Page Background | T3 | Adds a decorative border around the page (opens Borders and Shading). The most-used of the Page Background controls, used for certificates, flyers, title pages, and cover sheets, but still a specific-occasion feature rather than routine. Sits just below the T2 Borders/Shading text-level control the rubric references because page-level bordering is more decorative and rarer. | general | medium | rubric (Borders/Shading = T2 reference, page-level lower); reasoning |
| **Style Set** | Document Formatting | T4 | Gallery swapping the heading/body style package for the whole document. Depends on users actually using Styles (already heavily underused) AND knowing this gallery exists on a rarely-visited tab. Effectively invisible to the general population; a power-user/template refinement. | none | medium | segments/surveys briefs (Styles heavily underused); ms-official flat long-tail; rubric+reasoning |
| **Colors** | Document Formatting | T4 | Changes the theme color palette (not direct font color, which is the T1 Home-tab control). A theme-level abstraction most users don't understand or seek out; sits deep in the unused long tail. Distinct from and far rarer than direct color application. | marketing | medium | segments brief (theme color/font cluster low, design-leaning); rubric+reasoning |
| **Fonts** | Document Formatting | T4 | Sets the theme heading/body font PAIR document-wide. Easily confused with but completely separate from the T0 Home-tab Font picker; this theme-level control is rarely touched. Most users change fonts directly via Home, never via the Design theme abstraction. | marketing | medium | segments brief (theme font cluster low); rubric+reasoning |
| **Effects** | Document Formatting | T4 | Changes the theme's shape/object effect style (shadows, reflections). Only matters when a document contains themed shapes/SmartArt, and even then is rarely deliberately changed. Among the most ignored controls on an already-ignored tab. | marketing | medium | segments brief (design cluster low); rubric+reasoning |
| **Set as Default** | Document Formatting | T4 | Writes the current document's theme/style formatting into the Normal template as the default for new documents. A one-time, advanced configuration action most users never perform and many fear (it permanently alters defaults). Deep in the unused tail. | none | high | rubric+reasoning; surveys brief (90% use <10% of features) |

### Layout

| Control | Group | Tier | Rationale | Segment | Conf | Sources |
|---|---|---|---|---|---|---|
| **Margins** | Page Setup | T1 | Page margins are explicitly named as a T1/High control in the rubric. Adjusting margins is one of the most common page-setup actions for general users (fitting content to a page, meeting formatting requirements). The preset gallery (Normal/Narrow/Wide) makes it a frequent one-click action. | general | high | rubric+reasoning; evidence brief lists Page Layout/margins as Tier-2 common (segments brief), rubric elevates Page Margins to T1 |
| **Orientation** | Page Setup | T2 | Rubric explicitly lists Page Orientation as T2. Switching portrait/landscape is occasional - needed for wide tables, certificates, or specific layouts, but most documents stay portrait so a meaningful minority touch it. | general | high | rubric (Page Orientation/Size = T2) |
| **Size** | Page Setup | T2 | Rubric lists Page Size as T2. Most users accept the regional default (Letter/A4); paper-size changes happen occasionally (Legal, A4 vs Letter cross-region, printing needs). | general | high | rubric (Page Orientation/Size = T2) |
| **Columns** | Page Setup | T2 | Rubric lists Columns as T2 (and the Columns dialog as T3). Multi-column layouts are an occasional need (newsletters, brochures, some academic formats); the simple presets get moderate use while the full dialog is rarer. | general | high | rubric (Columns = T2; Columns dialog = T3) |
| **Breaks** | Page Setup | T2 | The Breaks dropdown covers page breaks (rubric T2) plus section/column/text-wrapping breaks. Page breaks are common; section breaks are a meaningful-minority feature critical for differing headers/orientation. Overall medium usage, with section breaks pulling toward the niche end. | general | medium | rubric (Page Break, Columns, section breaks = T2); segments brief notes section-break errors are a common formatting issue |
| **Indent Left** | Paragraph | T2 | Setting a precise left indent value is occasional. Most indentation is done via the Home tab Increase/Decrease Indent buttons, Tab, or the ruler, so this exact spinner sees medium-to-low traffic among users who want exact measurements. | general | medium | rubric+reasoning; dominant indent path is Home tab (evidence brief mini-toolbar/Home formatting) |
| **Indent Right** | Paragraph | T2 | Right-indent spinner is used slightly less than left indent (right indents are less common than left). Still an occasional precise-formatting tool, e.g., for block quotes that indent both sides. | general | medium | rubric+reasoning |
| **Spacing Before** | Paragraph | T2 | Precise before-paragraph spacing is an occasional formatting adjustment. Most users rely on the Home tab Line/Paragraph Spacing dropdown or styles, so the exact spinner gets medium use among users tuning vertical rhythm. | general | medium | rubric+reasoning; styles/spacing underused by casuals (segments brief) |
| **Spacing After** | Paragraph | T2 | Space-after-paragraph is the more commonly tuned of the two spacing spinners (controls inter-paragraph gaps), but still an occasional precise-formatting action versus the Home spacing dropdown and styles. | general | medium | rubric+reasoning |
| **Position** | Arrange | T3 | Object positioning presets only matter when a floating picture/shape is selected. A minority of documents contain floating objects, and most users drag objects manually rather than use the preset grid. | marketing | medium | rubric+reasoning; design cluster = Tier-3 (segments brief) |
| **Wrap Text** | Arrange | T3 | The most-used Arrange control: anyone who inserts a picture and wants text to flow around it touches Wrap Text. Still gated on having a floating object, so it is a meaningful-minority feature rather than universal. Leans toward T2 for image-heavy users. | general | medium | rubric+reasoning; Insert Picture is T1 but its layout follow-ups are occasional |
| **Bring Forward** | Arrange | T3 | Z-order layering only applies when multiple overlapping objects exist - a niche scenario in Word (more a PowerPoint/design task). Low general usage, concentrated in design-heavy documents. | marketing | medium | rubric+reasoning; design cluster = Tier-3 (segments brief) |
| **Send Backward** | Arrange | T3 | Counterpart to Bring Forward; same niche layering use case. Often used to push an image Behind Text as a backdrop. Low general usage. | marketing | medium | rubric+reasoning |
| **Align** | Arrange | T3 | Aligning/distributing multiple objects requires a multi-object selection - a design-oriented task uncommon in everyday Word documents. Used by a minority producing diagrams or laid-out graphics. | marketing | medium | rubric+reasoning; design cluster = Tier-3 (segments brief) |
| **Group** | Arrange | T3 | Grouping objects into a single unit is a design/diagramming convenience used by the minority who build multi-shape graphics in Word. Low general usage. | marketing | medium | rubric+reasoning |
| **Rotate** | Arrange | T3 | Rotating/flipping objects is an occasional object-manipulation action gated on having a shape/picture selected. Many users rotate via the on-canvas handle instead. Low general usage. | marketing | medium | rubric+reasoning |
| **Line Numbers** | Page Setup | T4 | Line numbering is a niche feature almost no general user touches. It is primarily required in legal pleadings (court-mandated line-numbered paper), some scripts, and reviewed manuscripts. | legal | high | rubric+reasoning; segments brief (legal court-rule-mandated features) |
| **Hyphenation** | Page Setup | T4 | Automatic/manual hyphenation is rarely toggled by general users (off by default). Only typography-conscious users producing justified/columned print layouts adjust it. | marketing | high | rubric+reasoning (long flat tail, defaults-off feature) |
| **Selection Pane** | Arrange | T4 | The Selection pane (list/show/hide objects) is a power-user object-management tool very few Word users ever open. Mostly relevant only in documents with many overlapping objects. | marketing | medium | rubric+reasoning (niche object tools sit in the flat long tail) |

### references

| Control | Group | Tier | Rationale | Segment | Conf | Sources |
|---|---|---|---|---|---|---|
| **Insert Footnote** | Footnotes | T2 | The most-used References command overall. Footnotes are very common in academic, scholarly, and legal writing and appear in the rubric's T2 examples. Still occasional for the general population, so primary tier T2 rather than higher. | academic | high | rubric (Footnote = T2 example); segments brief |
| **Table of Contents** | Table of Contents | T3 | TOC is the headline References feature but used only in longer/structured docs. Rubric explicitly cites Table of Contents as a T3 example. The whole References tab sits in the flat low-usage long tail; auto-TOC requires heading styles which most casual users never apply. | academic | high | rubric+reasoning; segments brief (TOC very common in academic writing) |
| **Update Table** | Table of Contents | T3 | Tightly coupled to TOC usage — anyone who inserts a TOC clicks Update Table to refresh page numbers, often repeatedly. Inherits TOC's T3 footprint but no broader than the TOC-using population. | academic | medium | rubric+reasoning |
| **Insert Endnote** | Footnotes | T3 | Endnotes are a less-common alternative to footnotes, used by a subset of academic/scholarly writers who prefer notes at the document end. Lower frequency than Insert Footnote. | academic | high | rubric+reasoning |
| **Insert Citation** | Citations & Bibliography | T3 | Entry point to Word's native citation system. Rubric cites Citations as T3 general / high for academics. Importantly, ~two-thirds of students self-report as non-users of reference management, and many citation users prefer external tools (Zotero/Mendeley/EndNote), capping native usage. | academic | high | rubric+reasoning; segments brief (reference-manager adoption surveys) |
| **Insert Caption** | Captions | T3 | Rubric lists Captions as a T3 example. Used by academic/technical authors labeling figures and tables (Figure 1, Table 2); rare for casual users. | academic | high | rubric (Captions = T3 example) |
| **Cross-reference** | Captions | T3 | Rubric lists Cross-reference as a T3 example. Used to link to headings/figures/tables in structured documents; valued by technical and academic authors, niche generally. | academic | high | rubric (Cross-reference = T3 example) |
| **Add Text** | Table of Contents | T4 | Niche sub-control that tags the current paragraph with a TOC outline level. Even among TOC users most rely on heading styles rather than this button. Deep in the flat long tail. | academic | high | rubric+reasoning |
| **Next Footnote** | Footnotes | T4 | Navigation helper for jumping between footnotes/endnotes. Even heavy footnote users rarely use it (they scroll/click directly). Deep long tail. | academic | high | rubric+reasoning |
| **Show Notes** | Footnotes | T4 | Scrolls the view to footnote/endnote area. Obscure utility command rarely invoked even by note users. | academic | high | rubric+reasoning |
| **Search** | Research | T4 | Smart Lookup / Search pane is an online-lookup feature few users invoke from the ribbon. Marked infeasible in the clone and falls in the rare/negligible band akin to Researcher. | none | high | rubric+reasoning |
| **Researcher** | Research | T4 | Explicitly listed as a T4 example in the rubric. Online research aggregator that very few users ever touch; cloud-dependent feature. | academic | high | rubric (Researcher = T4 example) |
| **Manage Sources** | Citations & Bibliography | T4 | Source Manager is a downstream maintenance dialog used only by the subset of users building native citations — a fraction of an already-niche feature. | academic | medium | rubric+reasoning |
| **Style** | Citations & Bibliography | T4 | Citation-style picker (APA/MLA/Chicago) only matters to users actively using native citations; set once per document. Niche within a niche. | academic | medium | rubric+reasoning |
| **Bibliography** | Citations & Bibliography | T4 | Generates a Works Cited / References list from native citations. Only used by the citation-building subset; many academics produce bibliographies via external managers instead. | academic | medium | rubric+reasoning; segments brief |
| **Insert Table of Figures** | Captions | T4 | Aggregates captions into a list; only relevant to the small set of long-document authors who caption figures and want an index of them. Long tail. | academic | high | rubric+reasoning |
| **Update Table** | Captions | T4 | Refreshes the table of figures — used only by the table-of-figures subset, a fraction of the captioning minority. | academic | high | rubric+reasoning |
| **Mark Entry** | Index | T4 | Rubric lists Index among T4 examples. Marking index entries is a laborious, book-publishing-style workflow that very few users ever perform. | academic | high | rubric (Index = T4 example) |
| **Insert Index** | Index | T4 | Generates a back-of-book index from marked entries. Rare specialized publishing workflow. | academic | high | rubric (Index = T4 example) |
| **Update Index** | Index | T4 | Refreshes an index — used only by the tiny set of users who build indexes. | academic | high | rubric+reasoning |
| **Mark Citation** | Table of Authorities | T4 | Rubric lists Table of Authorities as a T4 example. Marking legal citations is the single most legal-specific Word feature — near-zero usage in the general population. | legal | high | rubric (TOA = T4 example); segments brief (TOA legal-only niche) |
| **Insert Table of Authorities** | Table of Authorities | T4 | Builds the litigation table of cases/statutes from marked citations. Single-profession feature with effectively zero general usage. | legal | high | rubric (TOA = T4 example); segments brief |
| **Update Table** | Table of Authorities | T4 | Refreshes the table of authorities — used only by the litigation subset already building a TOA. | legal | high | rubric+reasoning; segments brief |

### Mailings

| Control | Group | Tier | Rationale | Segment | Conf | Sources |
|---|---|---|---|---|---|---|
| **Envelopes** | Create | T3 | Printing a single envelope is the most mainstream Mailings action and is reachable by general users, but envelope printing is still an occasional office/admin task, not something most users ever do. Sits in the flat long tail of command usage. | business-admin | medium | segments brief (Mailings tab = Tier-2 business/admin, Tier-3/unused casual); rubric+reasoning |
| **Labels** | Create | T3 | Label printing (address labels, name badges) is a recognizable office staple but a niche, occasional task for the general population. More accessible than full mail merge since a single sheet of labels needs no data source. | business-admin | medium | segments brief (Labels/Envelopes = admin staple, Mailings cluster); rubric+reasoning |
| **Start Mail Merge** | Start Mail Merge | T3 | Entry point to mail merge — the canonical 'low general / high admin' feature. Described as 'dreaded'/intimidating and recurring-but-specialist. Most general users never start a merge. | business-admin | high | segments brief (mail merge concentrated in business/HR/marketing/admin, no public usage %); rubric |
| **Select Recipients** | Start Mail Merge | T3 | Mandatory second step of any mail merge (point Word at the data list). Usage tracks Start Mail Merge — niche overall, routine within the admin merge workflow. | business-admin | high | segments brief (mail merge admin-segment); rubric+reasoning |
| **Edit Recipient List** | Start Mail Merge | T3 | Used within a merge to sort/filter/dedupe recipients. Only ever touched by users already doing a merge, so it inherits the niche business-admin profile. | business-admin | high | segments brief (mail merge segment); rubric+reasoning |
| **Address Block** | Write & Insert Fields | T3 | Common building block in letter/label merges (drops a formatted recipient address). Routine within merges but unused by the general population. | business-admin | medium | segments brief (mail merge letters/labels); rubric+reasoning |
| **Greeting Line** | Write & Insert Fields | T3 | Inserts a personalized salutation in merge letters. Standard in letter merges but a niche, segment-specific control overall. | business-admin | medium | segments brief (mail merge letters); rubric+reasoning |
| **Insert Merge Field** | Write & Insert Fields | T3 | The core action of building a merge template (drop individual data fields). The most-used Write & Insert control, but still confined to users actually performing a merge. | business-admin | high | segments brief (mail merge admin segment); rubric+reasoning |
| **Preview Results** | Preview Results | T3 | Toggle to view merged data in place — a natural and commonly used step for anyone running a merge, but still confined to the merge audience. | business-admin | medium | segments brief (mail merge segment); rubric+reasoning |
| **Finish & Merge** | Finish | T3 | The mandatory final step (print, email, or generate individual docs) of every merge. Always used by anyone completing a merge, but the merge audience itself is niche overall. | business-admin | high | segments brief (mail merge admin segment); rubric+reasoning |
| **Highlight Merge Fields** | Write & Insert Fields | T4 | A convenience toggle used deep inside merge editing to visually spot fields. Even most users who do merges skip it; negligible general usage. | business-admin | high | rubric+reasoning (deep mail-merge sub-feature; no telemetry) |
| **Rules** | Write & Insert Fields | T4 | Adds conditional logic (If...Then...Else, Skip Record, Fill-in) to merges. A power-user feature within an already-niche feature; very few even of admin merge users touch it. | business-admin | high | rubric+reasoning (advanced mail-merge sub-feature; no telemetry) |
| **Match Fields** | Write & Insert Fields | T4 | Maps data-source columns to Word's expected field names — a troubleshooting/setup step within merges. Rarely surfaced; negligible overall usage. | business-admin | high | rubric+reasoning (deep mail-merge sub-feature) |
| **Update Labels** | Write & Insert Fields | T4 | Only active during label merges (propagate fields across the label grid). Narrow sub-feature of an already-niche workflow. | business-admin | high | rubric+reasoning (label-merge-only control) |
| **First Record** | Preview Results | T4 | Record-navigation arrow used only while previewing a merge. Tiny sub-feature; most merge users just spot-check rather than step through every record. | business-admin | high | rubric+reasoning (merge preview navigation) |
| **Previous Record** | Preview Results | T4 | Merge-preview navigation arrow; only relevant mid-merge. Negligible overall usage. | business-admin | high | rubric+reasoning (merge preview navigation) |
| **Go to Record** | Preview Results | T4 | Spinner to jump to a specific merge record during preview. Niche-within-niche; very few users invoke it. | business-admin | high | rubric+reasoning (merge preview navigation) |
| **Next Record** | Preview Results | T4 | Merge-preview navigation arrow; only used while stepping through a merge. Negligible overall usage. | business-admin | high | rubric+reasoning (merge preview navigation) |
| **Last Record** | Preview Results | T4 | Jumps to the final merge record during preview. Tiny navigation control; negligible usage. | business-admin | high | rubric+reasoning (merge preview navigation) |
| **Find Recipient** | Preview Results | T4 | Searches recipient records during preview — a rarely needed helper inside the merge workflow. Negligible overall usage. | business-admin | high | rubric+reasoning (merge preview sub-feature) |
| **Check for Errors** | Preview Results | T4 | Validates/simulates a merge before completion. Useful but obscure; only a fraction of merge users run it. Negligible general usage. | business-admin | high | rubric+reasoning (merge validation sub-feature) |

### review

| Control | Group | Tier | Rationale | Segment | Conf | Sources |
|---|---|---|---|---|---|---|
| **Editor** | Proofing | T1 | Spell/grammar check is the single most-used Review-tab feature for the general population; F7 is a well-known habit and the rubric explicitly lists Spelling as T1. In M365 the Editor pane is the entry point for spelling/grammar, so it inherits that broad usage even though the 'refinements/style' suggestions are used less. | general | medium | segments brief (Spell/Grammar listed Tier-2 common but mainstream); rubric lists Spelling as T1; reasoning |
| **Spelling and Grammar** | Proofing | T1 | Classic Spelling & Grammar check is a core, broadly-used proofing action invoked by most users at least occasionally and by many on every document. Rubric anchors Spelling at T1. It largely overlaps with Editor in M365 but remains a distinct, heavily-used command. | general | medium | rubric (Spelling=T1); segments brief; reasoning |
| **Word Count** | Proofing | T2 | Used occasionally by a meaningful minority; rubric explicitly cites Word Count as a T2 example. The live status-bar count covers most casual needs, so the ribbon dialog is a periodic check rather than per-session. | academic | high | rubric (Word Count=T2 example) |
| **New Comment** | Comments | T2 | Comments are the most mainstream collaboration feature on the Review tab; used occasionally by a meaningful minority of general users and heavily in any review/collaboration workflow. Below basic formatting but a clear step above the rest of the tab. | legal | high | segments brief (Contract Nerds: 93% use Comments); rubric (Comments=T2) |
| **Delete** | Comments | T2 | Resolving/clearing comments is the natural counterpart to adding them and recurs throughout any commented document. Tracks New Comment usage but slightly less frequent. | legal | medium | segments brief; rubric+reasoning |
| **Display for Review** | Markup | T2 | When Track Changes is active, switching markup view (Simple/All/No Markup) is a common companion action for reviewers reading clean vs. marked-up text. Tied to track-changes adoption, so T2 general / higher for editors. | legal | medium | segments brief (Track Changes legal-dominant); rubric+reasoning |
| **Track Changes** | Tracking | T2 | The flagship collaboration/editing feature, but in Microsoft's CEIP telemetry the related 'Accept Change' sat at ~#100 — firmly in the flat low-usage tail for the general population. T2 general, but it defines entire professional workflows. | legal | high | ms-official (Accept Change ~#100 anchor); segments brief (Contract Nerds 91%) |
| **Accept** | Tracking | T2 | 'Accept Change' is the named ~#100 command in Microsoft's telemetry — measurable but in the flat mid-tail, well below basic formatting. Essential wherever Track Changes is used, hence T2 general. | legal | high | ms-official (Accept Change = ~#100 telemetry anchor) |
| **Reject** | Tracking | T2 | Counterpart to Accept; reviewers reject changes as part of any redline workflow. Slightly less frequent than Accept but in the same telemetry band. | legal | medium | ms-official (Accept Change ~#100, Reject inferred adjacent); segments brief |
| **Thesaurus** | Proofing | T3 | Synonym lookup is a niche convenience most users rarely invoke from the ribbon (right-click synonyms or external tools are more common). Specific writing workflows use it, but overall frequency is low. | academic | medium | rubric+reasoning |
| **Read Aloud** | Speech | T3 | Text-to-speech is used by a small subset for proofreading-by-ear and accessibility. Awareness is rising but general per-session usage stays low. | accessibility | medium | rubric+reasoning |
| **Translate** | Language | T3 | Occasional use for multilingual documents; most users translate via browser/dedicated tools instead. Niche but more than negligible. | business-admin | medium | rubric+reasoning |
| **Language** | Language | T3 | Setting the proofing language is a configuration action most users touch rarely (only when spellcheck flags the wrong language). Low overall frequency. | business-admin | medium | rubric+reasoning |
| **Previous** | Comments | T3 | Comment navigation buttons are used by reviewers stepping through feedback, but most users scroll or click comments directly. Lower than the core add/delete actions. | legal | medium | rubric+reasoning |
| **Next** | Comments | T3 | Same as Previous — sequential comment navigation used by a reviewing minority; most interact with comments directly in the margin. | legal | medium | rubric+reasoning |
| **Show Comments** | Comments | T3 | Toggling contextual vs. list view of comments is an occasional view-management action; most users leave the default. Used by some collaborators but not frequently. | legal | medium | rubric+reasoning |
| **Filter All Markup** | Markup | T3 | Filtering displayed markup is a refinement used by a subset of reviewers managing complex revisions; general users rarely touch it. | legal | low | rubric+reasoning |
| **Show Markup** | Markup | T3 | Choosing which markup categories/reviewers to display is a power-reviewer control; the average user accepts defaults. Niche within an already-specialized tab. | legal | medium | rubric+reasoning |
| **Reviewing Pane** | Markup | T3 | The separate revisions pane is used by thorough reviewers verifying all changes are cleared, but most rely on inline markup. Low general usage. | legal | low | rubric+reasoning |
| **Previous** | Tracking | T3 | Stepping backward through tracked changes is used during review but less than Accept/Reject (which auto-advance). Niche to the track-changes minority. | legal | low | rubric+reasoning |
| **Next** | Tracking | T3 | Forward navigation through tracked changes; partly redundant with Accept/Reject's move-to-next behavior, so used less. Confined to track-changes workflows. | legal | low | rubric+reasoning |
| **Compare** | Compare | T3 | Document Compare/Combine (blackline) is a specialized workflow most general users never run; they eyeball differences or use Track Changes instead. Niche but established. | legal | medium | segments brief (Compare/Combine core legal toolkit); rubric+reasoning |
| **Check Accessibility** | Accessibility | T4 | Very few general users ever run the accessibility checker; it is a compliance/publishing step. Rubric groups accessibility-type tooling in the rare tier. | accessibility | medium | rubric+reasoning |
| **Track Changes Options** | Markup | T4 | Dialog-launcher to configure markup colors/balloons/measurements — a one-time-setup affair that almost no one revisits. Rare even among heavy track-changes users. | legal | low | rubric+reasoning |
| **Block Authors** | Protect | T4 | Co-authoring lock feature explicitly listed in the rubric's rare tier; requires SharePoint/OneDrive shared editing and is touched by an extremely small number of users. | none | high | rubric (Block Authors listed as T4 example) |
| **Restrict Editing** | Protect | T4 | Locking formatting/editing or building protected forms is a power/admin feature rarely used by general users. Niche document-control workflow. | business-admin | medium | rubric+reasoning |
| **Hide Ink** | Ink | T4 | Only appears with ink content or on pen/touch devices and merely toggles ink visibility — almost no one ever uses it. Ink features are rare per the rubric. | accessibility | medium | rubric+reasoning |

### view

| Control | Group | Tier | Rationale | Segment | Conf | Sources |
|---|---|---|---|---|---|---|
| **Print Layout** | Views | T2 | Print Layout is Word's default view, so it is what nearly everyone sees, but the button itself is only clicked when returning from another view. As an explicit command it is medium-frequency; its ubiquity is passive (default state) rather than an active click. | general | medium | rubric+reasoning |
| **Ruler** | Show | T2 | Ruler toggle is used occasionally to set tabs, indents, and margins visually; a meaningful minority of layout-conscious users keep it on or toggle it, but most leave the default. | general | medium | rubric+reasoning |
| **Navigation Pane** | Show | T2 | Heading/page/search navigation pane is genuinely useful for moving around long documents and is used by a meaningful minority; relies on Styles/headings which limits casual uptake. | academic | medium | rubric+reasoning; segments brief (long-doc/heading usage) |
| **Zoom** | Zoom | T2 | Zoom is a commonly adjusted setting, but as the tooltip notes most users use the status-bar zoom slider instead of this ribbon dialog. Medium usage for the ribbon control specifically. | general | medium | rubric+reasoning |
| **Read Mode** | Views | T3 | A full-screen reading view; occasionally used to read long docs comfortably, but most users stay in Print Layout and read inline. Not a frequent click. The View tab as a whole sits in the flat long tail of the 2003 telemetry. | general | medium | rubric+reasoning; ms-official flat-long-tail evidence |
| **Outline** | Views | T3 | Outline view helps restructure heading hierarchies and move large blocks; used by a minority of structured/long-document writers but ignored by casual users. | academic | medium | rubric+reasoning |
| **Draft** | Views | T4 | Simplified text-only view that hides headers/footers/graphics for fast editing; a legacy 'Normal' view used by a small set of fast typists, largely forgotten by general users. | general | medium | rubric+reasoning |
| **Focus** | Immersive | T3 | Newer distraction-free mode hiding the ribbon on a dark background; appreciated by some writers but a low-frequency toggle for the general base. | general | medium | rubric+reasoning |
| **Gridlines** | Show | T3 | Non-printing alignment grid for positioning objects; used by a small subset doing object/graphic layout, ignored by typical text writers. | marketing | medium | rubric+reasoning |
| **100%** | Zoom | T3 | One-click reset to 100% zoom; convenient but infrequently clicked, and the status-bar control handles most zoom resets. | general | medium | rubric+reasoning |
| **One Page** | Zoom | T3 | Fits one full page in the window; occasional layout-check action, low overall frequency. | general | medium | rubric+reasoning |
| **Multiple Pages** | Zoom | T3 | Shows two-plus pages at once for layout overview; niche, used rarely when reviewing overall document flow. | general | medium | rubric+reasoning |
| **Page Width** | Zoom | T3 | Zooms so page width fills the window; a handy preset but low-frequency, again overshadowed by the status-bar slider. | general | medium | rubric+reasoning |
| **Split** | Window | T3 | Splits one window into two scrollable panes to see/edit distant parts simultaneously; a useful but minority feature for long-document editing. | general | medium | rubric+reasoning |
| **View Side by Side** | Window | T3 | Places two documents side by side for comparison; used by a minority doing manual document comparison, but most rely on OS window snapping or the Review > Compare tool. | legal | medium | rubric+reasoning |
| **Switch Windows** | Window | T3 | Dropdown to jump between open documents; OS taskbar/Alt-Tab handles most window switching, so the ribbon control sees low usage, slightly above the rarest items because multi-doc switching is common. | general | medium | rubric+reasoning |
| **Web Layout** | Views | T4 | Legacy view emulating how a doc would look as a webpage; almost never used now that Word is not a primary web-authoring tool. Deep in the unused tail. | none | high | rubric+reasoning |
| **Immersive Reader** | Immersive | T4 | Accessibility/reading-aid feature (text spacing, syllables, read aloud, line focus); very few general users invoke it. Niche but high-value for its target segment. | accessibility | medium | rubric+reasoning |
| **Vertical** | Page Movement | T4 | Sets vertical scrolling, which is already the default; almost no one clicks it because it is the existing state. Only touched to revert from Side to Side. | none | high | rubric+reasoning |
| **Side to Side** | Page Movement | T4 | Horizontal page-flipping mode, mostly a novelty/touch-device feature; rarely toggled by the general base. | none | high | rubric+reasoning |
| **New Window** | Window | T4 | Opens a second window on the same document; a power-user multi-view trick rarely used by the general base. | none | high | rubric+reasoning |
| **Arrange All** | Window | T4 | Tiles all open Word windows; OS-level window management has largely supplanted this, so it is rarely clicked. | none | high | rubric+reasoning |
| **Synchronous Scrolling** | Window | T4 | Sub-feature of View Side by Side that scrolls both docs together; only the small set using side-by-side comparison ever touches it. | legal | high | rubric+reasoning |
| **Reset Window Position** | Window | T4 | Equalizes the split between two side-by-side documents; a sub-feature of an already-niche feature, essentially never used by general users. | none | high | rubric+reasoning |
| **Macros** | Macros | T4 | VBA macro list/record/run; a developer/power-automation feature that the vast majority of users never open. Macros/VBA UI is explicitly called out as rare in the rubric. | developer | high | rubric+reasoning |
| **Properties** | SharePoint | T4 | View/edit SharePoint document properties; only appears for files stored in a SharePoint library and is touched by a tiny enterprise subset. | business-admin | high | rubric+reasoning |

### Help

| Control | Group | Tier | Rationale | Segment | Conf | Sources |
|---|---|---|---|---|---|---|
| **Help** | Help | T3 | F1/Help is occasionally invoked by users stuck on a task, but the modern reflex is to web-search rather than open in-app Help. No telemetry rank exists for it; it sits well below core formatting/clipboard commands in the flat long tail. Most sessions never open Help. Slightly above the other Help-tab buttons because F1 is a universally-known shortcut and the only entry here a general user might press. | general | medium | rubric+reasoning; ms-official long-tail flattening (no Help command in published top anchors) |
| **Contact Support** | Help | T4 | Contacting Microsoft Support from within Word is a last-resort action taken by a tiny fraction of users, typically only when something is broken. Not part of any document-editing workflow and absent from all usage telemetry anchors. Effectively negligible across the user base. | general | high | rubric+reasoning |
| **Feedback** | Help | T4 | Sending feedback/suggestions to Microsoft is an opt-in action a very small minority ever performs. It has no bearing on producing a document and never appears in usage rankings. Negligible general usage. | general | high | rubric+reasoning |
| **Show Training** | Help | T4 | Launching built-in training videos is a one-time or never action for most users; the evidence shows ~68% of office workers use Word 'intuitively' without formal training, meaning the in-app training surface is largely ignored. Very few sessions ever touch it. | general | high | rubric+reasoning; segments brief (TUM ~68% use intuitively, no training) |
| **What's New** | Help | T4 | A 'What's New' changelog view is curiosity-driven and viewed rarely, usually once after an update if at all. It plays no role in document creation and never surfaces in command-frequency data. Negligible across the user base. | general | high | rubric+reasoning |

