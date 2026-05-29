# Mailings tab — Word ↔ LibreOffice

> **Status.** Word build: Microsoft 365 (target). **Word-side: web-sourced + LO-verified —
> screenshot-pending.** LO-side: high. Produced by the per-tab pipeline: 3 independent
> extractors → reconciled canonical → mapped to LO `.uno:` → verified against the LibreOffice
> source tree. The Word/idMso side was set-diffed against the official `wordcontrols.xlsx`
> (M365 Current Channel + 2013/2016/2019) — the TabMailings sheet lists exactly 51 idMso-bearing
> controls and all are accounted for after one idMso fix (Address Block). The LO command facts
> were checked against the vendored LO tree. **No owner screenshot exists for this tab yet**, so
> the CJK and postal-barcode controls below are *expected-conditional / not-on-default-ribbon,
> unverified against a live build*. The LO-source pass returned **no material LO correction** —
> two descriptive corrections and 14 confirmations (see
> [LO-source verification](#lo-source-verification)).

This is **Word-clone decision-research**, not LibreOffice documentation. It diffs every Word
Mailings-tab control against LO's command surface and classifies the **work** each diff implies.
Bucket vocabulary and verdict meanings are in [README.md](README.md#legend).

---

## Outcome

Of 73 catalogued Word Mailings-tab controls, **7 wire straight through** to an existing LO
`.uno:` command (Free) and **12 are our-layer UI** (the 5 group containers plus the
Envelopes/Labels dialogs, the Start-Mail-Merge → Wizard surface, the New-List/Existing-List
registration entry points, the Go-to-Record box, and the email-output dialog). The dominant band
is **Behavior shim = 42**: every Word mail-merge control whose **capability already exists** in
LO's Mail Merge Wizard + the `com.sun.star.text.MailMerge` UNO service, but which Word exposes as
a discrete ribbon command and LO does not (the six merge-type toggles, Address Block, Greeting
Line, Insert Merge Field + its field children, the whole Rules menu + children, Match Fields,
Highlight Merge Fields, Update Labels, Find Recipient, Check for Errors, the Preview-Results
toggle, the Finish & Merge menu, and Select/Edit Recipients). **Engine gap = 0** — LO ships a
complete mail-merge engine, so there is no document capability on this tab that LO genuinely
lacks. The **Cut** pile (12) is product-choice / niche: the language-conditional CJK
envelope/greeting/postcard commands, the discontinued US/Japanese postal barcodes, and the
cloud-bound Outlook-contacts source.

| Work bucket | Count | What it is |
|---|---:|---|
| **Free** | 7 | wire the existing LO `.uno:` command, no UI work |
| **Our-layer UI** | 12 | build the Word-faithful dialog/menu/host; dispatch the LO command |
| **Behavior shim** | 42 | orchestrate LO's existing wizard/UNO engine in our dispatch layer; LO has no 1:1 ribbon command |
| **Engine gap** | 0 | LO engine genuinely can't (none on this tab) |
| **Cut** | 12 | out of scope by product choice (CJK, discontinued postal barcodes, Outlook/cloud) |
| **Optional our-layer feature** | 0 | LO lacks it but it's app-state we could build (none on this tab) |
| **Total** | **73** | |

**Decisive learning:** on Mailings the **Engine gap is 0 / 73** — LibreOffice already has a
**complete mail-merge engine**: the Mail Merge Wizard (`.uno:MailMergeWizard`) plus the
`com.sun.star.text.MailMerge` UNO service cover data-source connection, Insert (merge) Field,
preview navigation (First/Prev/Current/Next/Last), Edit Individual Documents, and
Save/Print/Email Merged Documents, and the Envelopes/Labels dialogs back the Create group. The
real cost of this tab is therefore **not** an engine gap — it is **our-layer orchestration**: the
**42-control Behavior-shim band** is us re-exposing the engine that already exists as the discrete
ribbon commands Word has but LO never surfaced (merge-type toggles, Address Block / Greeting Line
composite fields, the Insert-Merge-Field dropdown + default columns, the Rules WordField menu,
Match Fields, Highlight/Update/Find/Check, the Preview toggle, the Finish & Merge umbrella). Every
one of these is "drive the existing wizard/UNO engine from our dispatch layer," not "build an
engine LO doesn't have." → strongly supports **LO-via-LOK + scoped parity**: the mail-merge core
is free, the work is surfacing it.

> **Recurring our-layer theme.** Word's Mailings tab is a **ribbon of discrete commands over one
> engine**; LO ships the same engine behind **one wizard + one toolbar + the MailMerge UNO
> service**. So the repeated shape of work is *fan-out*: take a single LO capability that lives
> inside the wizard (insert merge field, address block, salutation, conditional/Rules fields,
> match fields, record navigation, finish-to-doc/print/email) and re-present it as the
> individual ribbon buttons Word users expect, translating Word's field-token model
> (`«AddressBlock»`, MERGEFIELD, IF/SKIPIF/NEXTIF WordFields, the Office Address List default
> columns) onto LO's Database-field model. That translation layer — not a missing engine — is
> the cost.

---

## Inventory

One subsection per Word ribbon group. `LO .uno:` is the mapped LibreOffice command (`—` = none
exposed as a discrete command; the capability may still live inside the wizard/UNO engine —
that is exactly what makes the row a Behavior shim rather than an Engine gap). `work` is the
bucket from the table above. Rows touched by the LO-source corrections / QA idMso fixes are
marked **✓ verified vs LO source** in the note.

### Create (GroupEnvelopeLabelCreate)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Create group | GroupEnvelopeLabelCreate | group | — | UI-only | Our-layer UI | Container group at the far left of the Mailings tab; holds the Envelopes/Labels creation commands (plus language-conditional CJK commands). — **LO:** Pure ribbon-organization container; LO has no native ribbon so there is no group object at all. The project's synthetic `ribbon.json` defines a 'Create' group under its Mailings tab containing only `.uno:InsertEnvelope` (no Labels). Layout artifact, no `.uno`. |
| Envelopes | EnvelopesAndLabelsDialog | button | `.uno:InsertEnvelope` | differs | Our-layer UI | Opens the Envelopes and Labels dialog on the Envelopes tab to compose and print a single envelope (Delivery/Return address; Options sets size and feed; Print, or Add to Document as Page 1). — **LO:** `.uno:InsertEnvelope` ("En~velope…") opens LO's Envelope dialog with **three tabs** — Envelope (addressee/sender, with database-field drag-in), Format (size/position), Printer. Word puts Envelopes + Labels as two tabs of one dialog; LO splits envelopes and labels into two separate dialogs. LO offers 'New Doc.' (insert as page 1) vs Word's 'Add to Document'/'Print'. This is the one Create control the project actually wired into its ribbon. ✓ verified vs LO source. |
| Labels | LabelsDialog | button | `.uno:InsertLabels` | differs | Our-layer UI | Opens the Envelopes and Labels dialog on the Labels tab to create a full sheet (or single) of mailing labels. — **LO:** `.uno:InsertLabels` ("Insert Labels") opens a **separate** Labels dialog (not a tab of the envelope dialog), tabs Labels / Format / Options, with its own Avery/Europe-centric brand list. LO always produces a new labels document; no per-record single-label print-to-printer flow identical to Word. (`.uno:InsertLabels` is an sfx2 app-level slot, `FN_LABEL`.) ✓ verified vs LO source. |
| Chinese Envelope | EnvelopeChineseDialog | button | — | LO-missing | Cut | Chinese envelope wizard (CJK builds). — **LO:** No CJK-specific envelope command; the single `.uno:InsertEnvelope` dialog is the only envelope path regardless of language. (Conditional — East-Asian build; not on a default English ribbon.) ✓ verified vs LO source. |
| Insert Greeting (Japanese) | JapaneseGreetingsInsertMenu | menu | — | LO-missing | Cut | Japanese greeting (aisatsubun) submenu (CJK builds). — **LO:** No aisatsubun greeting feature anywhere in the command catalog; Word-only CJK feature. (Conditional — East-Asian build.) ✓ verified vs LO source. |
| Greeting (Aisatsubun) | MailMergeJapaneseGreetingInsert | button | — | LO-missing | Cut | Inserts a Japanese greeting phrase. — **LO:** No aisatsubun/greeting-phrase command. (Conditional — East-Asian build.) ✓ verified vs LO source. |
| Opening Sentence | MailMergeJapaneseGreetingJapaneseOpeningSentenceInsert | button | — | LO-missing | Cut | Inserts a Japanese opening sentence. — **LO:** No equivalent; Word-only CJK feature. (Conditional — East-Asian build.) ✓ verified vs LO source. |
| Closing Sentence | MailMergeJapaneseGreetingClosingSentenceInsert | button | — | LO-missing | Cut | Inserts a Japanese closing sentence. — **LO:** No equivalent; Word-only CJK feature. (Conditional — East-Asian build.) ✓ verified vs LO source. |
| Japanese Postcard | JapanesePostcardMenu | menu | — | LO-missing | Cut | Japanese postcard submenu (CJK builds). — **LO:** No postcard wizard of any kind in the command catalog. (Conditional — East-Asian build.) ✓ verified vs LO source. |
| Create Address Side | JapanesePostcardCreateAddressSide | button | — | LO-missing | Cut | Japanese postcard address-side wizard. — **LO:** No equivalent; Word-only CJK feature. (Conditional — East-Asian build.) ✓ verified vs LO source. |
| Create Letter Side | JapanesePostcardCreateLetterSide | button | — | LO-missing | Cut | Japanese postcard letter-side wizard. — **LO:** No equivalent; Word-only CJK feature. (Conditional — East-Asian build.) ✓ verified vs LO source. |

### Start Mail Merge (GroupMailMergeStart)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Start Mail Merge group | GroupMailMergeStart | group | — | UI-only | Our-layer UI | Container group for the merge-type dropdown, Select Recipients, and Edit Recipient List. — **LO:** Layout container only; no `.uno`. The project's synthetic ribbon has a 'Start Mail Merge' group populated with `.uno:MailMergeWizard` + `.uno:ViewDataSourceBrowser`, but the group itself maps to nothing. |
| Start Mail Merge | MailMergeStartMailMergeMenu | menu | `.uno:MailMergeWizard` | differs | Our-layer UI | Dropdown that sets the persistent per-document merge type (Letters/Email/Envelopes/Labels/Directory/Normal) and offers the step-by-step wizard. — **LO:** No per-document merge-type concept and no such dropdown; the single closest entry point is `.uno:MailMergeWizard` ("Mail Merge Wi~zard…"), an ~8-step modal wizard. Document type (letter vs email) is wizard step 2, not a ribbon toggle. Our layer hosts the dropdown over the one wizard command. (QA fix: controlType corrected `splitButton/menu` → **`menu`** — the official Control Type is a plain dropdown menu, not a split button.) ✓ verified vs LO source. |
| Letters | MailMergeStartLetters | toggleButton | — | LO-missing | Behavior shim | Sets the document merge type to Letters. — **LO:** No standalone merge-type-toggle command, but the **capability exists**: 'Letter' is a radio option inside the Mail Merge Wizard ('Select document type' step). Our layer surfaces the toggle and drives the wizard / sets state; no engine work. ✓ verified vs LO source. |
| E-mail Messages | MailMergeStartEmail | toggleButton | — | LO-missing | Behavior shim | Sets the document merge type to E-mail. — **LO:** No selector command, but 'E-mail message' is a radio option inside the wizard, and output-to-email exists as `.uno:MailMergeEmailDocuments`. Capability present; our layer adds the toggle. ✓ verified vs LO source. |
| Envelopes… | MailMergeStartEnvelopes | toggleButton | — | LO-missing | Behavior shim | Switches the document into envelope-merge mode. — **LO:** No merge-type toggle, but the engine path exists — create an envelope via `.uno:InsertEnvelope` and bind database fields. Our layer would model the 'envelope merge' state over that. ✓ verified vs LO source. |
| Labels… | MailMergeStartLabels | toggleButton | — | LO-missing | Behavior shim | Switches the document into label-merge mode. — **LO:** No merge-type toggle, but LO's label merge runs via `.uno:InsertLabels` (synchronize + database fields) producing a labels document. Capability present; our layer models the mode. ✓ verified vs LO source. |
| Directory | MailMergeStartDirectory | toggleButton | — | LO-missing | Behavior shim | Sets the merge type to Directory/catalog (all records on one page). — **LO:** No Directory toggle, but the engine supports it — insert a Next-record field so records flow on one page. Our layer surfaces the mode over the existing field/engine. ✓ verified vs LO source. |
| Normal Word Document | MailMergeClearMergeType | toggleButton | — | LO-missing | Behavior shim | Clears the merge type / detaches the document from the merge. — **LO:** LO never attaches a persistent merge-type, so the 'clear' is purely our-layer state management over the same engine; no missing capability. ✓ verified vs LO source. |
| Step-by-Step Mail Merge Wizard… | MailMergeWizard | toggleButton | `.uno:MailMergeWizard` | same | Free | Opens the mail-merge wizard. — **LO:** Direct functional equivalent: `.uno:MailMergeWizard` ("Mail Merge Wi~zard…", `FN_MAILMERGE_WIZARD`) is LO's primary mail-merge entry point — the central command this whole tab maps to. Both walk document type → recipients → content → preview → finish; step count/order differs but the role is identical. The cleanest 'same' on the tab. ✓ verified vs LO source. |
| Select Recipients | MailMergeSelectRecipients | menu | `.uno:ViewDataSourceBrowser` | differs | Behavior shim | Dropdown to attach a recipient data source (Type a New List / Use an Existing List / Choose from Outlook Contacts). — **LO:** Different model — LO uses globally **registered** data sources. `.uno:ViewDataSourceBrowser` ("~Data Sources", **Ctrl+Shift+F4** — not plain F4) browses registered DBs; the wizard's 'Select address list' step picks/adds one. Capability fully present in the engine; our layer re-presents Word's per-document attach dropdown over it. ✓ verified vs LO source. |
| Type a New List… | MailMergeCreateList | button | `.uno:AutoPilotAddressDataSource` | differs | Our-layer UI | Opens the New Address List dialog to type a fresh recipient list. — **LO:** `.uno:AutoPilotAddressDataSource` ("AutoPilot: Address Data Source") registers an address source, and the wizard's 'Create' button opens a New-Address-List entry dialog. LO stores as a database/CSV, not Word's `.mdb` Office Address List; our layer wraps the create-list surface. ✓ verified vs LO source. |
| Use an Existing List… | MailMergeRecepientsUseExistingList | button | `.uno:AutoPilotAddressDataSource` | differs | Our-layer UI | Opens the Select Data Source dialog to connect an existing data file. — **LO:** LO connects existing data by **registering** it (`.uno:AutoPilotAddressDataSource` / `.uno:AddressBookSource` / `.uno:DatasourceAdministration`); the wizard's address-list step can Add a spreadsheet/CSV/dBase/database. Supports Calc/CSV/dBase/JDBC/ODBC rather than Word's Excel/Access/CSV; our layer provides the file-picker surface over registration. ✓ verified vs LO source. |
| Choose from Outlook Contacts… | MailMergeRecepientsUseOutlookContacts | button | — | LO-missing | Cut | Uses an Outlook contacts folder as the recipient source. — **LO:** No Outlook integration. LO can register a system/Thunderbird/Evolution/LDAP address book, but there is no Outlook-contacts command — Outlook-specific, cloud-bound; cut. ✓ verified vs LO source. |
| Edit Recipient List | MailMergeRecipientsEditList | button | `.uno:ViewDataSourceBrowser` | differs | Behavior shim | Opens the Mail Merge Recipients dialog (per-document check/sort/filter/find-duplicates/validate). — **LO:** No single consolidated dialog, but every capability exists in the engine — edit/sort/filter in the registered-data-source browser (`.uno:ViewDataSourceBrowser`, **Ctrl+Shift+F4**) or the wizard's address-list step (Filter + checkbox grid); per-record include/exclude during preview is `.uno:MailMergeExcludeEntry`. Our layer would consolidate these into Word's one dialog. ✓ verified vs LO source. |

### Write & Insert Fields (GroupMailMergeWriteInsertFields)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Write & Insert Fields group | GroupMailMergeWriteInsertFields | group | — | UI-only | Our-layer UI | Container group for Highlight Merge Fields, Address Block, Greeting Line, Insert Merge Field, Rules, Match Fields, Update Labels. — **LO:** Layout container only. The project's synthetic ribbon names this group and fills it with a single `.uno:InsertFieldCtrl`. No `.uno` corresponds to the group itself. |
| Highlight Merge Fields | MailMergeHighlightMergeFields | toggleButton | — | LO-missing | Behavior shim | Toggles grey shading on merge fields so they stand out from static text. — **LO:** No merge-field-selective highlighter, but the engine has the capability via `.uno:Marks` ("Fie~ld Shadings"), a global field-shading view toggle. Our layer would scope it to merge fields. ✓ verified vs LO source. |
| Address Block | MailMergeAddressBlockInsert | button | — | LO-missing | Behavior shim | Inserts a single formatted address-block merge field (Insert Address Block dialog). — **LO:** No `«AddressBlock»` composite-field button, but the **capability exists** inside the engine — the Mail Merge Wizard's 'Insert address block' step has its own block-layout editor + Match Fields. Our layer would expose it as a discrete command driving that engine step. (QA fix: idMso corrected `MailMergeInsertAddressBlock` → **`MailMergeAddressBlockInsert`** — verified against the official wordcontrols.xlsx, all four versions.) ✓ verified vs LO source. |
| Greeting Line | MailMergeGreetingLineInsert | button | — | LO-missing | Behavior shim | Inserts a single `«GreetingLine»` merge field (Insert Greeting Line dialog). — **LO:** No `«GreetingLine»` field object, but the salutation **capability exists** in the wizard's 'Create salutation' step (male/female/neutral variants + fallback). Our layer surfaces it as a discrete command over the existing engine step. ✓ verified vs LO source. |
| Insert Merge Field | MailMergeMergeFieldInsertMenu | splitButton | `.uno:InsertFieldCtrl` | differs | Behavior shim | Split button: dropdown lists the attached source's fields for one-click insertion + opens the dialog. — **LO:** LO inserts database/merge fields via `.uno:InsertFieldCtrl` ("Fiel~d", tooltip "Insert Field"); the capability is fully present, just reached through the Fields dialog's Database tab rather than a direct field dropdown. Our layer builds the quick dropdown over the engine. ✓ verified vs LO source. |
| Insert Merge Field (dialog) | MailMergeMergeFieldInsert | button | `.uno:InsertField` | differs | Behavior shim | Opens the Insert Merge Field dialog (Address Fields vs Database Fields). — **LO:** `.uno:InsertField` ("~More Fields…") opens LO's general Fields dialog whose 'Database' tab inserts merge fields (database > table > column). Capability present; our layer would re-skin it as Word's dedicated merge-field dialog. ✓ verified vs LO source. |
| Title | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts the Title default Office-Address-List field. — **LO:** No fixed default-field set, but the engine inserts any column from the connected source via the Fields dialog Database tab. Our layer would synthesize Word's default column menu over whatever source is registered. ✓ verified vs LO source. |
| First_Name | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts the First Name default field. — **LO:** No built-in default column, but the engine inserts source columns dynamically; our layer supplies the default-column menu. ✓ verified vs LO source. |
| Last_Name | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts the Last Name default field. — **LO:** Dynamic data-source columns only; engine handles insertion, our layer supplies the menu. ✓ verified vs LO source. |
| Company_Name | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts the Company Name default field. — **LO:** No built-in default schema; columns come from the connected source. Our-layer menu over the engine. ✓ verified vs LO source. |
| Address_Line_1 | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts the Address Line 1 default field. — **LO:** No standing default-column command; engine inserts from the source. Our-layer menu. ✓ verified vs LO source. |
| Address_Line_2 | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts the Address Line 2 default field. — **LO:** No standing default-column command; engine inserts from the source. Our-layer menu. ✓ verified vs LO source. |
| City | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts the City default field. — **LO:** No standing default-column command; engine inserts from the source. Our-layer menu. ✓ verified vs LO source. |
| State | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts the State default field. — **LO:** No standing default-column command; engine inserts from the source. Our-layer menu. ✓ verified vs LO source. |
| Zip_Code | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts the ZIP Code default field. — **LO:** No standing default-column command; engine inserts from the source. Our-layer menu. ✓ verified vs LO source. |
| Country_or_Region | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts the Country or Region default field. — **LO:** No standing default-column command; engine inserts from the source. Our-layer menu. ✓ verified vs LO source. |
| Home_Phone | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts the Home Phone default field. — **LO:** No standing default-column command; engine inserts from the source. Our-layer menu. ✓ verified vs LO source. |
| Work_Phone | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts the Work Phone default field. — **LO:** No standing default-column command; engine inserts from the source. Our-layer menu. ✓ verified vs LO source. |
| Email_Address | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts the Email Address default field. — **LO:** No standing default-column command; engine inserts from the source. Our-layer menu. ✓ verified vs LO source. |
| Rules | MailMergeRules | menu | — | LO-missing | Behavior shim | Dropdown of merge WordFields (Ask, Fill-in, If…Then…Else, Merge Record #, Next, Skip, etc.). — **LO:** No 'Rules' menu, but the conditional/flow **capability exists** in the engine via field types (Conditional text, Hidden Paragraph/Text, Next record, Input field, Set variable) reached through the Fields dialog. Our layer would expose Word's Rules menu translated onto those field types. ✓ verified vs LO source. |
| Ask… | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts an ASK field (prompt once, store in a bookmark). — **LO:** No ASK field, but LO has input/placeholder fields; our layer maps Word's ASK semantics onto them. ✓ verified vs LO source. |
| Fill-in… | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts a FILLIN field (prompt for text per record). — **LO:** LO's 'Input field' (Functions tab) prompts for text; our layer wires it to Word's FILLIN behavior. ✓ verified vs LO source. |
| If…Then…Else… | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts an IF conditional field. — **LO:** LO's 'Conditional text' field provides if/then/else output (different condition syntax); reached via the Fields dialog. Our layer translates the Word IF WordField onto it. ✓ verified vs LO source. |
| Merge Record # | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts a MERGEREC field (current record number). — **LO:** No printable merge-record-number field, but `.uno:MailMergeCurrentEntry` tracks the record; our layer would emit a field bound to that engine state. ✓ verified vs LO source. |
| Merge Sequence # | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts a MERGESEQ field (output sequence number). — **LO:** No merge-sequence field, but the merge engine knows the sequence; our layer would synthesize the field. ✓ verified vs LO source. |
| Next Record | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts a NEXT field (advance record without a new doc). — **LO:** LO **has** a 'Next record' database field (used by label/directory layouts) via the Fields dialog Database tab; our layer just surfaces it as the Rules-menu command. ✓ verified vs LO source. |
| Next Record If… | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts a NEXTIF conditional field. — **LO:** LO has 'Any record'/'Next record' database fields with a condition (different model) in the Fields dialog; our layer maps NEXTIF onto them. ✓ verified vs LO source. |
| Set Bookmark… | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts a SET field assigning a value to a bookmark. — **LO:** `.uno:InsertBookmark` makes a static bookmark; the merge-time value concept maps to LO's 'Set variable' field (Variables tab). Our layer composes Word's SET behavior from those engine pieces. ✓ verified vs LO source. |
| Skip Record If… | _(none)_ | menu item | — | LO-missing | Behavior shim | Inserts a SKIPIF field excluding a record on a condition. — **LO:** No SKIPIF field, but record exclusion exists via the recipient grid / `.uno:MailMergeExcludeEntry`; our layer translates conditional-skip onto the engine. ✓ verified vs LO source. |
| Match Fields | MailMergeMatchFields | button | — | LO-missing | Behavior shim | Opens the Match Fields dialog (map standard address components to source columns). — **LO:** No top-level command, but the Match-Fields **capability exists** embedded in the wizard's address-block and salutation steps ('Match Fields' button). Our layer would lift it out as a discrete command over the same engine. ✓ verified vs LO source. |
| Update Labels | MailMergeUpdateLabels | button | — | LO-missing | Behavior shim | Replicates the first label cell to all labels with Next-record fields. — **LO:** No persistent ribbon command, but the 'Synchronize contents'/'Synchronize Labels' button (shown when a label sheet is created via `.uno:InsertLabels` with Synchronize on) does exactly this propagation. Capability present; our layer surfaces a stable command over it. ✓ verified vs LO source. |
| Insert Postal Bar Code | MailMergeInsertBarcodeMenu | menu | — | LO-missing | Cut | Barcode submenu (US POSTNET / Japanese postal). — **LO:** No POSTNET/Japanese *postal* barcode command (LO does have generic `.uno:InsertQrCode` "QR and Barcode…" / `.uno:EditQrCode`, but those are not postal-address barcodes). Discontinued for USPS automation discounts (Jan 2013); not on the default modern ribbon. Cut. ✓ verified vs LO source. |
| Insert Postal Bar Code (US) | MailMergeInsertBarcode | button | — | LO-missing | Cut | Inserts a US POSTNET barcode field. — **LO:** No postal-address barcode command (generic QR/Barcode aside). Discontinued; not on the default ribbon. Cut. ✓ verified vs LO source. |
| Japanese Postal Bar Code | MailMergeJapanesePostalBarcode | button | — | LO-missing | Cut | Inserts a Japanese postal barcode field. — **LO:** No Japanese postal-barcode command. Conditional (CJK) and niche. Cut. ✓ verified vs LO source. |

### Preview Results (GroupMailMergePreviewResults)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Preview Results group | GroupMailMergePreviewResults | group | — | UI-only | Our-layer UI | Container group for the preview toggle, record navigators, Find Recipient, and Check for Errors. — **LO:** Layout container only; no `.uno`. Not present in the project's synthetic Mailings ribbon (which has no Preview Results group). |
| Preview Results | MailMergeResultsPreview | toggleButton | — | differs | Behavior shim | Toggles between field placeholders and merged data values. — **LO:** No single on/off toggle command, but the **capability exists** — View > 'Field Names' switches placeholders vs values, and the mail-merge toolbar (active in merge context) shows record data via `.uno:MailMergeCurrentEntry`. Our layer would bind one persistent toggle to that engine state. ✓ verified vs LO source. |
| First Record | MailMergeGoToFirstRecord | button | `.uno:MailMergeFirstEntry` | same | Free | Go to the first recipient record. — **LO:** Direct equivalent: `.uno:MailMergeFirstEntry` ("First Mail Merge Entry"). Same function; lives on LO's mail-merge toolbar rather than a ribbon group. ✓ verified vs LO source. |
| Previous Record | MailMergeGoToPreviousRecord | button | `.uno:MailMergePrevEntry` | same | Free | Go to the previous recipient record. — **LO:** Direct equivalent: `.uno:MailMergePrevEntry` ("Previous Mail Merge Entry"). Same behavior; on LO's mail-merge toolbar. ✓ verified vs LO source. |
| Go to Record | MailMergeGoToRecord | control (editBox/spin box) | `.uno:MailMergeCurrentEntry` | differs | Our-layer UI | Numeric box to jump to a record number. — **LO:** `.uno:MailMergeCurrentEntry` ("Current Mail Merge Entry") is a toolbar spin/edit box that both reports and sets the active record — functionally the same (type a number, jump there). Differs only as a toolbar widget vs a ribbon editBox; our layer re-hosts it. ✓ verified vs LO source. |
| Next Record | MailMergeGoToNextRecord | button | `.uno:MailMergeNextEntry` | same | Free | Go to the next recipient record. — **LO:** Direct equivalent: `.uno:MailMergeNextEntry` ("Next Mail Merge Entry"). Same behavior; on LO's mail-merge toolbar. ✓ verified vs LO source. |
| Last Record | MailMergeGotToLastRecord | button | `.uno:MailMergeLastEntry` | same | Free | Go to the last recipient record. — **LO:** Direct equivalent: `.uno:MailMergeLastEntry` ("Last Mail Merge Entry"). Same behavior; on LO's mail-merge toolbar. (Word's idMso carries the famous 'GotTo' typo; LO's spelling is clean.) ✓ verified vs LO source. |
| Find Recipient | MailMergeFindRecipient | button | — | LO-missing | Behavior shim | Opens the Find Entry dialog to search recipients during preview. — **LO:** No dedicated 'find recipient' command, but the **capability exists** — record search in the Data Sources browser (`.uno:ViewDataSourceBrowser`, **Ctrl+Shift+F4**) or via the wizard. Our layer would expose a Find-Entry command over that engine search. ✓ verified vs LO source. |
| Check for Errors | MailMergeAutoCheckForErrors | button | — | LO-missing | Behavior shim | Runs Auto Check for Errors (simulate the merge and report problems) before merging. — **LO:** No pre-flight error-simulation command in the catalog; the wizard runs the merge directly. Our layer would add a simulate-and-report pass over the existing merge engine (a thin orchestration, not a missing engine). ✓ verified vs LO source. |

### Finish (GroupMailMergeFinish)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Finish group | GroupMailMergeFinish | group | — | UI-only | Our-layer UI | Container group at the far right holding the Finish & Merge dropdown. — **LO:** Layout container only. The project's synthetic ribbon has a 'Finish' group but populates it with `.uno:Print` (generic print), not a merge-finish command — even the project's mapping is a stand-in. |
| Finish & Merge | MailMergeFinishAndMergeMenu | menu | — | differs | Behavior shim | Dropdown choosing the output: Edit Individual Documents / Print Documents / Send Email Messages. — **LO:** No consolidated 'Finish & Merge' menu, but all three outputs **exist as engine commands** (`.uno:MailMergeCreateDocuments` edit, `.uno:MailMergePrintDocuments` print, `.uno:MailMergeEmailDocuments` email, plus `.uno:MailMergeSaveDocuments` save), surfaced only in the wizard's final step / merge toolbar. Our layer wraps them in Word's one umbrella dropdown. ✓ verified vs LO source. |
| Edit Individual Documents… | MailMergeMergeToDocument | button | `.uno:MailMergeCreateDocuments` | same | Free | Merge to a new editable document. — **LO:** Direct equivalent: `.uno:MailMergeCreateDocuments` is **literally labeled "Edit Individual Documents"** — same label and function. Available via the wizard finish step / merge toolbar. (LO additionally exposes `.uno:MailMergeSaveDocuments` "Save Merged Documents", which Word folds into the Edit dialog.) ✓ verified vs LO source. |
| Print Documents… | MailMergeMergeToPrinter | button | `.uno:MailMergePrintDocuments` | same | Free | Merge directly to the printer. — **LO:** Direct equivalent: `.uno:MailMergePrintDocuments` ("Print Merged Documents") merges straight to the printer with a record-range option. Same function; on the merge toolbar. (Note: the project's synthetic ribbon mapped the Finish group to generic `.uno:Print` instead of this merge-specific command.) ✓ verified vs LO source. |
| Send Email Messages… | MailMergeMergeToEMail | button | `.uno:MailMergeEmailDocuments` | differs | Our-layer UI | Merge to email (To/Subject/format, per-recipient send). — **LO:** `.uno:MailMergeEmailDocuments` is labeled "Send Email Messages" (same label) and prompts for To/Subject/format/range. Differs because LO sends via its own SMTP configuration (Tools > Options > Writer > Mail Merge E-mail), not via Outlook, and the format/dialog layout differ. Same intent, different transport; our layer re-skins the dialog. ✓ verified vs LO source. |

---

## LO-source verification

These mappings were checked against the vendored LibreOffice tree at
`apps/ms-word/libreoffice-codebase/` and **override** the mapped rows where they conflicted.
The pass returned **no material LO correction** for this tab (unlike Insert's Page-Number defect):
the mail-merge command surface the mapping asserted is real and was confirmed end-to-end. Two
**descriptive** corrections (neither changes a verdict) and the headline F4 fix are folded in
below, plus the two QA idMso/type fixes.

**QA fixes applied (authoritative, from `result.qa`):**

- **Address Block idMso** — corrected `MailMergeInsertAddressBlock` → **`MailMergeAddressBlockInsert`**.
  Verified against the official `wordcontrols.xlsx` for M365 Current Channel **and** Office
  2013/2016/2019 — all four versions list `MailMergeAddressBlockInsert` on TabMailings;
  `MailMergeInsertAddressBlock` does not exist in any version (the sibling 'Greeting Line' was
  already correct as `MailMergeGreetingLineInsert`). The row's bucket is unaffected.
- **Start Mail Merge controlType** — corrected `splitButton/menu` → **`menu`**. The official
  Control Type is a plain dropdown menu, not a split button (the body click opens the menu; there
  is no separate default-action face). This also resolves the inventory's internal inconsistency
  with the Wizard row's "there is no split button" note.

**Headline correction (CORRECTED) — keyboard shortcut:**

- **`.uno:ViewDataSourceBrowser` is bound to Ctrl+Shift+F4, not plain F4.** The mapping
  repeatedly called it "the F4 panel" / "the F4 Data Sources view." In Writer it is bound to
  `F4_SHIFT_MOD1` (**Ctrl+Shift+F4**); plain F4 in the Writer TextDocument context maps to
  `.uno:GraphicDialog`. Fixed in the Select Recipients, Edit Recipient List, and Find Recipient
  rows above. Evidence: `Accelerators.xcu:118` and `:7080` (inside the
  `com.sun.star.text.TextDocument` block starting `:6102`) bind `F4_SHIFT_MOD1` →
  `.uno:ViewDataSourceBrowser`; `Accelerators.xcu:6546` binds plain F4 → `.uno:GraphicDialog`;
  command at `GenericCommands.xcu:5589` (label "~Data Sources").

**Descriptive corrections (CORRECTED) — no verdict change:**

- **Postal-barcode "no barcode feature of any kind" overstated.** Narrowly true that LO has no
  POSTNET/Japanese *postal* barcode command, but LO does ship a generic barcode/QR insert
  (`.uno:InsertQrCode`, "QR and ~Barcode…") and `.uno:EditQrCode` ("~Edit Barcode…"). These are
  not postal-address barcodes, so the per-row Cut verdict on the postal-barcode rows stands; the
  catalog is simply not barcode-free. Evidence: `GenericCommands.xcu:7888`, `:7896`; no
  POSTNET/postal command anywhere in `officecfg/.../UI/`.
- **"Grep of all 1520 commands" count inaccurate.** The CJK-absent conclusion is **confirmed**
  (no Chinese/aisatsubun/postcard command exists — only `.uno:ChineseConversion` and the
  QR/barcode pair turned up), but the stated catalog size is wrong: the actual distinct `.uno`
  command-node count in `officecfg/.../UI` is **2155**, not 1520. Verdicts unchanged.

**Confirmed (CONFIRMED) — command/label/tooltip (and cited shortcut) match the mapping:**

- **Envelopes** — `.uno:InsertEnvelope`, label "En~velope…"; dialog has exactly 3 tabs
  (envelope / format / printer); slot `InsertEnvelope` (`FN_ENVELOP`) takes a `NewDocument` bool.
  Evidence: `WriterCommands.xcu:549-551`; `sw/source/ui/envelp/envlop1.cxx:132-137`;
  `sw/sdi/swriter.sdi:3050-3051`.
- **Labels** — `.uno:InsertLabels`, label "Insert Labels"; standalone sfx2 slot (`FN_LABEL`);
  separate dialog (`labeldialog.ui`) with tabs labels / format / options. Evidence:
  `GenericCommands.xcu:4483-4485`; `sfx2/sdi/sfx.sdi:5387`; `sw/source/ui/envelp/label1.cxx:138,148,150`;
  `sw/uiconfig/swriter/ui/labeldialog.ui:96`.
- **Mail Merge Wizard** — `.uno:MailMergeWizard`, label "Mail Merge Wi~zard…"; slot
  `FN_MAILMERGE_WIZARD` with no params (single modal entry point). Evidence:
  `WriterCommands.xcu:1015-1017`; `sw/sdi/swriter.sdi:4330-4331`.
- **Preview navigation (First/Prev/Current/Next/Last)** — all five confirmed verbatim:
  `.uno:MailMergeFirstEntry` "First Mail Merge Entry", `.uno:MailMergePrevEntry` "Previous Mail
  Merge Entry", `.uno:MailMergeCurrentEntry` "Current Mail Merge Entry", `.uno:MailMergeNextEntry`
  "Next Mail Merge Entry", `.uno:MailMergeLastEntry` "Last Mail Merge Entry". Evidence:
  `WriterCommands.xcu:1023-1057`; slots `sw/sdi/swriter.sdi:4347`, `:4415`.
- **Edit Individual Documents** — `.uno:MailMergeCreateDocuments` is literally labeled "Edit
  Individual Documents"; `.uno:MailMergeSaveDocuments` is "Save Merged Documents". Evidence:
  `WriterCommands.xcu:1071-1081`; slot `sw/sdi/swriter.sdi:4449`.
- **Print / Email merged documents** — `.uno:MailMergePrintDocuments` "Print Merged Documents";
  `.uno:MailMergeEmailDocuments` "Send Email Messages". Evidence: `WriterCommands.xcu:1087-1097`;
  email slot `sw/sdi/swriter.sdi:4500`.
- **Insert Merge Field** — `.uno:InsertFieldCtrl` label "Fiel~d", TooltipLabel "Insert Field";
  `.uno:InsertField` label "~More Fields…". Evidence: `WriterCommands.xcu:1165-1171`, `:677-679`.
- **Highlight Merge Fields → Field Shadings** — `.uno:Marks`, label "Fie~ld Shadings"; a global
  field-shading view toggle, no merge-field-selective highlight command exists. Evidence:
  `WriterCommands.xcu:3261-3263`.
- **Set Bookmark reference** — `.uno:InsertBookmark`, label "Bookmar~k…"; the static-bookmark
  insert, not a merge-time SET-value mechanism. Evidence: `WriterCommands.xcu:595-597`.
- **Type a New List / Use an Existing List** — `.uno:AutoPilotAddressDataSource` "AutoPilot:
  Address Data Source"; `.uno:AddressBookSource` "~Address Book Source…". Evidence:
  `GenericCommands.xcu:3492-3494`, `:5531-5533`.
- **Select Recipients / Data Sources label** — `.uno:ViewDataSourceBrowser`, label "~Data
  Sources". Evidence: `GenericCommands.xcu:5589-5591`.
- **Word-only standalone mail-merge commands absent** — a search across all UI `.xcu` for
  MailMergeMatchFields / HighlightMergeFields / InsertAddressBlock / GreetingLine / Rules /
  UpdateLabels / FindRecipient / CheckForErrors / ResultsPreview / MergeRec / MergeSeq / SkipIf /
  NextIf returned **zero matches** — confirming these capabilities live only inside the wizard/UNO
  engine, not as discrete commands (which is exactly why they bucket as **Behavior shim**, not
  Engine gap). Only the entry-navigation, exclude-entry, wizard, and four finish/save commands
  exist as standalone mail-merge `.uno` commands. Evidence: grep across
  `officecfg/.../UI/`; existing commands enumerated in `WriterCommands.xcu:1015-1098`.
- **Merge-type toggle commands absent** — no MailMergeStartLetters/Email/Envelopes/Labels/Directory
  or ClearMergeType command nodes exist; the only merge-type-adjacent commands are the wizard and
  the four finish commands. (Confirms the toggles are Behavior shims over the wizard, not engine
  gaps.) Evidence: `officecfg/.../UI/*.xcu`; `WriterCommands.xcu:1015`, `:1071-1097`.
- **CJK envelope/greeting/postcard commands absent** — confirmed (only `.uno:ChineseConversion`
  and the QR/barcode pair turned up); these correctly bucket as Cut. Evidence: case-insensitive
  search across `officecfg/.../UI/`.

> **Scope caveat from the LO-verify pass.** Command-surface facts (command names, labels, the
> envelope 3-tab and label 3-tab dialog structures, the `InsertEnvelope` `NewDocument` param, the
> absence of every Word-only standalone mail-merge command, and the absence of merge-type-toggle
> commands) all checked out CONFIRMED. Runtime-flow specifics that depend on launching soffice —
> the exact wizard step count/order and the salutation male/female/neutral variants — were **not**
> source-verified and are left as the mapping stated. soffice was not launched.

---

## Conditional / not-on-default-ribbon controls

There is **no owner screenshot for the Mailings tab yet**, so the following are flagged
**expected-conditional / not-on-default-ribbon, unverified against a live build** — they are valid
catalog entries (present in `wordcontrols.xlsx` on TabMailings) but will **not** appear on a
default English Word install, so a screenshot sweep must not "fail to find" them and wrongly
conclude the inventory invented them.

- **CJK Create-group controls** — Chinese Envelope, the Japanese Greeting menu + Aisatsubun /
  Opening / Closing Sentence, and the Japanese Postcard menu + Address-Side / Letter-Side require
  **East-Asian language support** enabled. Absent on a default English ribbon.
- **Insert Postal Bar Code (menu + US + Japanese)** — removed from the visible Mailings ribbon
  years ago (POSTNET was discontinued for USPS automation discounts in January 2013); the
  Japanese variant additionally requires CJK. Present in the catalog, not on a default ribbon.
- **Choose from Outlook Contacts** — requires an Outlook profile; sign-in / cloud-adjacent.
- **Start Mail Merge controlType** — the official Control Type is `menu` (plain dropdown); a live
  screenshot would confirm the six merge-type toggle children + Wizard layout.
- **Go to Record** — the official Control Type is the generic `control` (edit/spin box); the
  "editBox/spin box" rendering and its placement between Previous/Next are screenshot-pending.
- **Insert Merge Field default columns & Rules items** — these carry `idMso = null` (correct —
  they are dynamic/data-driven, absent from the static catalog); a screenshot would confirm the
  default Office-Address-List column set and the exact Rules submenu contents.

---

## Out of scope

- **Engine gap — none (0 controls).** This is the headline of the tab: there is **no document
  capability on Mailings that LO genuinely lacks**. LO ships a full mail-merge engine — the Mail
  Merge Wizard (`.uno:MailMergeWizard`) plus the `com.sun.star.text.MailMerge` UNO service —
  covering data-source connection, Insert (merge) Field, preview navigation, conditional/Next-record
  fields, Edit Individual Documents, and Save/Print/Email Merged Documents, with the
  Envelopes/Labels dialogs backing the Create group. Nothing here would require building a new
  engine.
- **Behavior shim — the real cost (42 controls).** Every Word mail-merge control whose capability
  already exists in LO's wizard/UNO engine but which LO never surfaced as a discrete ribbon
  command: the six merge-type toggles, Address Block, Greeting Line, Insert Merge Field + its
  default-column children, the whole Rules menu + children, Match Fields, Highlight Merge Fields,
  Update Labels, Find Recipient, Check for Errors, the Preview-Results toggle, the Finish & Merge
  menu, and Select/Edit Recipients. These are **our-layer orchestration of the existing engine** —
  fanning one wizard/UNO capability out into Word's individual ribbon commands and translating
  Word's field-token model onto LO's Database-field model. This band, not an engine gap, is the
  build cost of the tab.
- **Cut by product choice / niche (12 controls).** The language-conditional CJK
  envelope/greeting/postcard commands (East-Asian builds only), the discontinued US/Japanese
  postal barcodes (POSTNET removed 2013), and the cloud-bound Outlook-contacts source. No local
  clone needs these.

---

## QA flags & resolutions

From `result.qa`. The Word/idMso side was set-diffed against the official `wordcontrols.xlsx`
(M365 + 2013/2016/2019); TabMailings lists exactly 51 idMso-bearing controls and all are
accounted for after the one Address-Block idMso fix. The LO-source pass found **no material LO
defect** (only descriptive corrections). Because there is **no owner screenshot for this tab**,
several structural items remain **screenshot-pending**.

| QA flag | Status | Resolution |
|---|---|---|
| Address Block idMso wrong (`MailMergeInsertAddressBlock`)? | **Resolved (source set-diff)** | Corrected to `MailMergeAddressBlockInsert` — the official id in all four versions; the inverted `Insert*` word-order does not exist. Sibling Greeting Line (`MailMergeGreetingLineInsert`) was already correct. Bucket unchanged (Behavior shim). |
| Start Mail Merge controlType (`splitButton/menu`)? | **Resolved (source set-diff)** | Official Control Type is plain `menu`; corrected. Resolves the internal inconsistency with the Wizard row's "no split button" note. |
| `.uno:ViewDataSourceBrowser` called "the F4 panel"? | **Resolved (LO source)** | Wrong — it is bound to **Ctrl+Shift+F4** (`F4_SHIFT_MOD1`); plain F4 = `.uno:GraphicDialog`. Fixed in the Select Recipients / Edit Recipient List / Find Recipient rows. No bucket change. |
| Postal-barcode "no barcode feature of any kind"? | **Resolved (LO source)** | Overstated — LO has generic `.uno:InsertQrCode` / `.uno:EditQrCode`, just no POSTNET/Japanese *postal* barcode. Cut verdict on the postal rows stands. |
| Chinese-Envelope "grep of all 1520 commands" count? | **Resolved (LO source)** | Count inaccurate — actual distinct `.uno` node count is 2155. The CJK-absent conclusion itself is confirmed; Cut verdicts unchanged. |
| CJK + postal-barcode rows presented as normal visible Mailings controls? | **Open (screenshot-pending)** | Valid catalog entries but NOT on a default English ribbon — CJK needs East-Asian support; postal barcode was removed (POSTNET discontinued 2013). Flagged so a screenshot pass doesn't wrongly conclude they were invented. |
| Insert-Merge-Field default columns / Rules items with `idMso = null`? | **Resolved (source)** | Correct — these are dynamic/data-driven items absent from the static catalog; leaving them null matches Microsoft's empty-Name rows. A screenshot would confirm the default column set + Rules submenu. |
| `Go to Record` controlType ("editBox/spin box")? | **Open (screenshot-pending)** | Official Control Type is the generic `control`; the edit/spin-box rendering and placement between Previous/Next are screenshot-pending. Does not change the bucket. |
| Misspelled idMsos (`MailMergeRecepientsUse…`, `MailMergeGotToLastRecord`)? | **Resolved (source)** | Microsoft's actual (misspelled) identifiers — transcribed verbatim and correct. Do **not** "fix". |
| Exhaustiveness of LO mail-merge mapping? | **Open (LO-side, high confidence)** | `completenessConfidence`: HIGH on the Word/idMso side (all 51 official controls accounted for); the LO command surface was source-verified end-to-end (no material defect). Runtime wizard-flow specifics (step count, salutation variants) were not soffice-verified. |
