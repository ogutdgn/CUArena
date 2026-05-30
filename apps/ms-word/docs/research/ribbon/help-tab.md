# Help tab — Word ↔ LibreOffice

> **Status.** Word build: Microsoft 365 (target). **Word-side: web-sourced + LO-verified —
> screenshot-pending.** LO-side: high. Produced by the per-tab pipeline: 3 independent
> extractors → reconciled canonical → mapped to LO `.uno:` → verified against the LibreOffice
> source tree. The Word/idMso side was set-diffed against the official `wordcontrols.xlsx`
> (M365 Current Channel, sheet `wordcontrols`, 5639 rows): `HelpTab(27543)` →
> `GroupHelpAndSupport(27544)` → exactly six buttons {Help 984, ContactUs 7903,
> OfficeFeedbackHelpTab 33241, OfficeFeedbackIcon 34024, ShowTraining 27442,
> WhatsNewRecentUpdates 27055}, zero omissions and zero extras. The LO command facts were
> checked against the vendored LO tree. **No owner screenshot exists for this tab yet**, so the
> runtime/version-sensitive controls below (Feedback-button duplication, Show Training presence,
> in-app-pane-vs-browser behaviors) are *expected-conditional, unverified against a live build*.
> Two mappings carry **material LO-source corrections** (the project-Help-tab "2 controls" claim →
> 3 controls; F1 binding mechanism); 10 more are confirmed (see
> [LO-source verification](#lo-source-verification)).

This is **Word-clone decision-research**, not LibreOffice documentation. It diffs every Word
Help-tab control against LO's command surface and classifies the **work** each diff implies.
Bucket vocabulary and verdict meanings are in [README.md](README.md#legend).

---

## Outcome

Of 8 catalogued Word Help-tab controls (2 containers + 6 buttons), **none wire straight through**
as a free pass (Free = 0) and **none expose a document-capability engine gap** (Engine gap = 0).
The Help tab is not a document-editing surface — it is a **help / support / feedback launcher**,
so the work splits cleanly into two bands: **3 controls are our-layer UI** (the tab container, the
named group, and the in-app Help entry point, all of which LO has the underlying capability for —
`.uno:HelpMenu` / `.uno:HelpIndex` / F1 — but renders differently), and **5 controls are Cut**
(Contact Support, both Feedback buttons, Show Training, What's New) because they are
cloud/online vendor services tied to Microsoft's support, telemetry-feedback, training, and
M365 update-channel infrastructure, which a local clone does not reproduce.

| Work bucket | Count | What it is |
|---|---:|---|
| **Free** | 0 | wire the existing LO `.uno:` command, no UI work |
| **Our-layer UI** | 3 | build the Word-faithful tab/group/pane host; dispatch the LO command |
| **Behavior shim** | 0 | intercept/massage in our dispatch layer; LO's result/semantics differ |
| **Engine gap** | 0 | LO engine genuinely can't; cut or accept reduced fidelity |
| **Cut** | 5 | out of scope by product choice (cloud/online support, feedback, training, update channel) |
| **Optional our-layer feature** | 0 | LO lacks it but it's app-state we could build |
| **Total** | **8** | |

**Decisive learning:** the Help tab contributes **Engine gap = 0** to the clone decision — there
is no document capability here that LO's engine lacks. Every gap is either a **presentation
difference over a capability LO already has** (Word's docked in-app Help task pane vs LO's
separate help viewer / online help in the default browser — `.uno:HelpIndex`/F1 covers the
intent) or a **cloud/online product-choice Cut** (Microsoft support-agent chat, the in-app
smile/frown feedback flow that posts to Microsoft, curated training videos, the M365
update-channel "What's New"). LO does have community-flavoured counterparts for three of the Cut
items (`.uno:QuestionAnswers` → community Q&A/forum, `.uno:SendFeedback` → feedback web page,
`.uno:WhatsNew` → release notes), all of which open the **default browser** rather than an in-app
surface — they are intentionally Cut as vendor/online product choices, not engine blockers.
→ the Help tab does **not** influence the engine/core decision; it is a thin our-layer launcher
with most members cut.

> **Recurring our-layer theme.** Word's Help tab is intentionally **flat** — a single group
> (`Help & Support`) of plain buttons, no split-buttons, dropdowns, galleries, or menus. The only
> our-layer build is the **tab + group host** plus an **in-app Help entry** that dispatches LO's
> existing help command (`.uno:HelpIndex`, F1); everything else (support agent, feedback flow,
> training, update-channel What's New) is an online service we cut rather than reimplement.

---

## Inventory

One subsection per Word ribbon group. `LO .uno:` is the mapped LibreOffice command (`—` = none).
`work` is the bucket from the table above. Rows touched by the LO-source corrections are marked
**✓ verified vs LO source** in the note.

### (Tab and Group containers)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Help | HelpTab | tab | `.uno:HelpMenu` | differs | Our-layer UI | The Help ribbon tab itself — a permanent core tab (Tab Set 'None (Core Tab)'), always visible, not contextual; container for the single 'Help & Support' group. New in Office 365/2019+, absent in Word 2007–2016 perpetual. — **LO:** No dedicated Help ribbon tab in the default (classic-menu) UI — Help is the top-level MENU '~Help' (`.uno:HelpMenu`), which mixes help with About/License/Restart-in-Safe-Mode/Update-Check. LO's notebookbar DOES define a 'Help Tab' (label '~Help'), but there is no `.uno` that 'is' the tab itself, and its membership differs from Word's. Closest container handle is `.uno:HelpMenu`. ✓ verified vs LO source. |
| Help & Support | GroupHelpAndSupport | group | — | LO-missing | Our-layer UI | The single ribbon group on the Help tab, holding all Help-tab buttons; intentionally flat (no split-buttons, dropdowns, galleries, or menus). — **LO:** No named 'Help & Support' ribbon group entity. LO's Help menu/notebookbar is organized by separators (classic menubar) or an unnamed toolbox (`HelpToolBox`), not by named groups with idMso-style identifiers. Pure organizational shell with no LO counterpart; built in our layer as a group container. ✓ verified vs LO source. |

### Help & Support (GroupHelpAndSupport)

| Word control | idMso | type | LO .uno: | verdict | work | note |
|---|---|---|---|---|---|---|
| Help | Help | button | `.uno:HelpIndex` | differs | Our-layer UI | Opens the Help task pane (docked at the right edge) to its home/landing page with a search box and browsable Word help topics; the user types a question or browses categories to read articles in-app. Also invoked by F1. — **LO:** Closest match is `.uno:HelpIndex` (label '%PRODUCTNAME ~Help', the 'Writer Help' notebookbar button). KEY DIFFERENCE in presentation: Word renders help **in-app** in a docked task pane; LO has **no docked help pane** — F1/`.uno:HelpIndex` opens either the separate offline LibreOffice Help VIEWER (if the help pack is installed) or, more commonly, the online help in the default BROWSER. Trigger/F1 and intent match; rendering surface differs. Per the bucket rule the in-app pane vs separate viewer/browser is our-layer UI (capability exists, presentation differs), not an engine gap. ✓ verified vs LO source. |
| Contact Support | ContactUs | button | `.uno:QuestionAnswers` | differs | Cut | Opens the Help task pane in its contact/get-help mode so the user can request assistance from Microsoft, surfacing support options (search for an answer, then connect to a Microsoft support agent / chat) without leaving Word. — **LO:** No in-app vendor-support flow. Word's ContactUs connects to a paid Microsoft support agent / chat; LO is community-supported. The nearest LO command, `.uno:QuestionAnswers` ('~Get Help Online'), just opens the community Ask-LibreOffice Q&A/forum site in the default BROWSER — no agent, no chat, no ticketing, no in-app pane. Cut as a cloud/online vendor-support product choice. ✓ verified vs LO source. |
| Feedback | OfficeFeedbackHelpTab | button | `.uno:SendFeedback` | differs | Cut | The primary Feedback button. Launches Word's in-app feedback flow (same entry as File > Feedback) with options 'I like something' (smile) / 'I don't like something' (frown) / 'I have a suggestion'; the user types feedback, optionally attaching a screenshot and contact email, auto-tagged to Word and sent to Microsoft. (Smile/frown UI belongs to the backstage `TabOfficeFeedback`, reached via this button — see QA flags.) — **LO:** `.uno:SendFeedback` ('Send Feedback') matches the intent (submit feedback to the vendor) but opens a feedback WEB PAGE in the default browser with no smile/frown buttons, no screenshot capture, and no in-app submission UI. Cut as a cloud/online product-choice (telemetry feedback to Microsoft). ✓ verified vs LO source. |
| Feedback | OfficeFeedbackIcon | button | — | LO-missing | Cut | A second Feedback control on the Help tab — the small feedback-icon variant — invoking the same Feedback experience as OfficeFeedbackHelpTab. The canonical M365 xlsx lists BOTH OfficeFeedbackHelpTab (33241) and OfficeFeedbackIcon (34024) as live children of the same group simultaneously; a live window typically shows only one (screenshot-pending — see QA flags). — **LO:** LO exposes exactly ONE feedback command (`.uno:SendFeedback`), already mapped above; no duplicate icon-style variant exists anywhere in the LO tree. Cut for the same cloud/online-feedback product choice as the primary button. ✓ verified vs LO source. |
| Show Training | ShowTraining | button | — | LO-missing | Cut | Opens the Help task pane showing curated Word training content — training videos and quick-start tutorials — so the user can learn features in-app. (Candidate for version/tenant gating; Microsoft has been retiring in-app training surfaces — screenshot-pending.) — **LO:** No equivalent at all. A full catalog scan (train/video/tutorial/tour/welcome/learn/getting-started) returned no LO command offering bundled training content; `ShowTraining` has no `.sdi` slot and no source match. The loosely-adjacent `.uno:TipOfTheDay` is a startup-tips dialog, not training, and would be misleading to map. Cut as cloud/online curated-content (no document capability, so not an engine gap). ✓ verified vs LO source. |
| What's New | WhatsNewRecentUpdates | button | `.uno:WhatsNew` | differs | Cut | Shows the most recently installed updates and new features for Word, surfacing the same 'What's New' details available via File > Account (the backstage `TabHelp`). Tied to the M365 update channel. (Label sometimes rendered without the apostrophe; presence can vary by build/channel and consumer vs enterprise install.) — **LO:** `.uno:WhatsNew` ('What's New', tooltip 'Open the release notes for the installed version in the default browser') is conceptually aligned but opens the version's RELEASE NOTES in the external default BROWSER — no per-update changelog tied to an auto-update channel (LO updates via OS package manager or manual download), no in-app rendering, and the command is NOT surfaced in Writer's default Help UI. Cut as an online/update-channel product choice. ✓ verified vs LO source. |

---

## LO-source verification

These mappings were checked against the vendored LibreOffice tree at
`apps/ms-word/libreoffice-codebase/` (now **pristine LibreOffice @1f1121d1** — re-vendored from
the earlier hacked/stripped tree; the project-custom `notebookbar_cua.ui` no longer exists, so
notebookbar citations below were re-anchored to stock `sw/uiconfig/swriter/ui/notebookbar.ui`)
and **override** the mapped rows where they conflicted.
Two are **material corrections** (the project Help-tab control count; the F1 binding mechanism);
the rest **confirm** the mapped command, label, tooltip, slot, and (where cited) behavior. All
Help-related commands live in `GenericCommands.xcu` (shared/generic), **not** `WriterCommands.xcu`
— they are inherited generic commands, with no Writer-specific Help controls.

**Material corrections (CORRECTED):**

- **Help tab membership — project Help tab "only 2 controls (Writer Help + About Writer)"** — the
  mapping's claim is wrong. LO's notebookbar Help source contains
  **THREE** controls, not two: `.uno:HelpIndex` (MenuHelp-HelpIndex), `.uno:SendFeedback`
  (MenuHelp-SendFeedback), and `.uno:About` (MenuHelp-About). The claim omits SendFeedback.
  (`ribbon.json` itself was not found anywhere under `apps/ms-word/`, so that external artifact
  could not be verified directly; the LO UI source it should mirror has 3 controls.) Evidence
  (re-verify: prior cite was to the removed project-custom `notebookbar_cua.ui:10038-10060`, which
  had a dedicated Help **tab** with a `HelpToolBox` of `GtkToolButton`s; pristine
  `notebookbar.ui` differs — it has **no** Help tab/`HelpToolBox`. The three commands instead
  live in a `GtkMenu id="Menu Help"` dropdown hung off the `_Help` menu button):
  `sw/uiconfig/swriter/ui/notebookbar.ui:489` (`Menu Help` menu), with `MenuHelp-HelpIndex:493`,
  `MenuHelp-SendFeedback:534`, `MenuHelp-About:593` — the three Help controls confirmed.
- **Help button — "bound to F1"** — F1 is NOT bound to `.uno:HelpIndex` via `Accelerators.xcu`
  (no HelpIndex entry exists there). F1 (and `KEY_HELP`) is **hardcoded in VCL's key handler**
  (`winproc.cxx:1295`), which raises a HelpEvent / routes into the help system rather than
  dispatching the `.uno` via a configurable accelerator. So 'F1 triggers help' is true in effect,
  but the binding mechanism is hardcoded in C++, not a config accelerator. The slot does declare
  `AccelConfig = TRUE` (`sfx.sdi:1920`), meaning it CAN be assigned an accelerator, but none is
  set by default. Evidence: `vcl/source/window/winproc.cxx:1295-1306`; absence in
  `officecfg/registry/data/org/openoffice/Office/Accelerators.xcu`; `sfx2/sdi/sfx.sdi:1920`.

**Confirmed (CONFIRMED) — command/label/tooltip/slot and behavior match the mapping:**

- **Help tab / `.uno:HelpMenu`** — `.uno:HelpMenu` is the menu container (label '~Help',
  `GenericCommands.xcu:7145-7152`); the classic menubar Help menu mixes help with
  SafeMode/License/About (`menubar.xml:848-866`); the notebookbar surfaces Help as a `_Help`
  menu button (`File-HelpButton:Menu Help`, `notebookbar.ui:3155`) opening the `Menu Help`
  dropdown, but no `.uno` 'is' the menu/tab itself. Evidence:
  `officecfg/registry/data/org/openoffice/Office/UI/GenericCommands.xcu:7145`;
  `sw/uiconfig/swriter/menubar/menubar.xml:848-866`; `sw/uiconfig/swriter/ui/notebookbar.ui:3155`
  (re-verify: prior cite was to the removed project-custom `notebookbar_cua.ui:10013/10094`, a
  '~Help' notebookbar **tab** label; pristine `notebookbar.ui` differs — it has no such Help tab,
  only the `_Help` ManagedMenuButton labelled `_Help` plus the `Menu Help` GtkMenu at line 489).
- **Help & Support group (no named group)** — the classic Help menu uses `<menu:menuseparator/>`
  elements (`menubar.xml:855,858,860,863`) with no named group nodes; the notebookbar groups the
  Help commands as bare `GtkMenuItem` children of the `Menu Help` GtkMenu, with no idMso-style
  group identifier. Evidence: `sw/uiconfig/swriter/menubar/menubar.xml:855-863`;
  `sw/uiconfig/swriter/ui/notebookbar.ui:489` (`Menu Help`)
  (re-verify: prior cite was to the removed project-custom `notebookbar_cua.ui:10029`, an unnamed
  `HelpToolBox` of bare `GtkToolButton`s on the Help tab; pristine `notebookbar.ui` differs — it
  has no `HelpToolBox`/Help tab, so the 'unnamed group' point now rests on the `Menu Help`
  dropdown's bare menu items instead. The conclusion — no named group identifier — still holds).
- **Help button / `.uno:HelpIndex` — command & label** — `.uno:HelpIndex` is the command; its
  label is literally '%PRODUCTNAME ~Help' (the ~ marks the mnemonic; resolves to e.g. 'LibreOffice
  Help', not 'Writer Help'). Slot is `SfxVoidItem HelpIndex SID_HELPINDEX` (`sfx.sdi:1909`).
  Evidence: `officecfg/registry/data/org/openoffice/Office/UI/GenericCommands.xcu:1782-1789`;
  `sfx2/sdi/sfx.sdi:1909`.
- **Help button — behavior (no docked pane; viewer or online help in browser)** — confirmed.
  `SID_HELPINDEX` calls `pHelp->Start('.uno:HelpIndex',…)` (`appserv.cxx:791-799`).
  `SfxHelp::Start_Impl` branches on `impl_hasHelpInstalled()`: if not installed it calls
  `impl_showOnlineHelp` → builds the HelpRootURL link → `sfx2::openUriExternally` (external
  browser, `sfxhelp.cxx:688`); if installed it opens the offline help component/viewer. No Help
  deck exists in `Sidebar.xcu`, confirming no docked help pane. Evidence:
  `sfx2/source/appl/appserv.cxx:791-799`; `sfx2/source/appl/sfxhelp.cxx:648-690,1087-1117`; no Help
  match in `officecfg/registry/data/org/openoffice/Office/UI/Sidebar.xcu`.
- **Contact Support / `.uno:QuestionAnswers`** — command + label '~Get Help Online'
  (`GenericCommands.xcu:5773-5780`); `SID_Q_AND_A` → `openUriExternally` (`appserv.cxx:631-640`).
  The target is the LibreOffice forum (QA_URL comment `//https://hub.libreoffice.org/forum/`),
  described in source as 'Askbot' — community Q&A/forum, not a vendor agent. No in-app agent/chat.
  Evidence: `officecfg/registry/data/org/openoffice/Office/UI/GenericCommands.xcu:5773`;
  `sfx2/source/appl/appserv.cxx:631-640`; slot at `sfx2/sdi/sfx.sdi:5172`.
- **Feedback (OfficeFeedbackHelpTab) / `.uno:SendFeedback`** — label 'Send Feedback'
  (`GenericCommands.xcu:5765-5772`); `SID_SEND_FEEDBACK` builds SendFeedbackURL (source comment
  `//…=> https://hub.libreoffice.org/send-feedback/`) plus version/locale/module query params and
  calls `sfx2::openUriExternally` — external browser, no in-app UI (`appserv.cxx:620-628`). Slot
  `SfxVoidItem SendFeedback SID_SEND_FEEDBACK` (`sfx.sdi:5156`). Evidence:
  `officecfg/registry/data/org/openoffice/Office/UI/GenericCommands.xcu:5765`;
  `sfx2/source/appl/appserv.cxx:620-628`; `sfx2/sdi/sfx.sdi:5156`.
- **Feedback (OfficeFeedbackIcon) — LO has exactly one feedback command** — confirmed. Only one
  feedback command exists: `.uno:SendFeedback` (single `GenericCommands.xcu` node, single
  `sfx.sdi` slot, single menubar/notebookbar reference). No second feedback command/icon variant
  found anywhere. Evidence: single occurrence in
  `officecfg/registry/data/org/openoffice/Office/UI/GenericCommands.xcu:5765` and `sfx2/sdi/sfx.sdi:5156`.
- **Show Training — genuinely LO-missing** — `ShowTraining` has no `.sdi` slot and no source match
  anywhere in the LO tree. `.uno:TipOfTheDay` exists and is referenced in the Help menu
  (`menubar.xml:853`) but is a startup-tips dialog, not training content. Evidence: no ShowTraining
  match in any `.sdi`; `.uno:TipOfTheDay` at `sw/uiconfig/swriter/menubar/menubar.xml:853`.
- **What's New / `.uno:WhatsNew`** — command, label 'What's New', and tooltip 'Open the release
  notes for the installed version in the default browser' verbatim (`GenericCommands.xcu:5805-5814`).
  `SID_WHATSNEW` builds ReleaseNotesURL + version/locale and calls `sfx2::openUriExternally`
  (`appserv.cxx:668-675`). Slot `SfxVoidItem WhatsNew SID_WHATSNEW` (`sfx.sdi:5232`). NOTE:
  `.uno:WhatsNew` is NOT in the default Writer menubar or notebookbar Help tab — the command
  exists but is not surfaced in Writer's default Help UI. Evidence:
  `officecfg/registry/data/org/openoffice/Office/UI/GenericCommands.xcu:5805-5814`;
  `sfx2/source/appl/appserv.cxx:668-675`; `sfx2/sdi/sfx.sdi:5232`.

> **Scope caveat from the LO-verify pass.** The dispatch behavior was verified in C++
> (`sfx2/source/appl/appserv.cxx`, `sfxhelp.cxx`), not from labels alone:
> SendFeedback/QuestionAnswers/WhatsNew all route through `sfx2::openUriExternally` (external
> default browser); HelpIndex routes through `SfxHelp` (offline viewer if a help pack is installed,
> else the online help link in the browser). `ribbon.json` and `command-catalog.json` could **not**
> be found anywhere under `apps/ms-word/`, so the mapping's references to '1520 commands' and
> exact `ribbon.json` membership are external artifacts not validated against the source tree;
> verification used the canonical LO UI config (`notebookbar*.ui` / `menubar.xml`) instead. The
> Word-side claims (docked task pane, smile/frown, MS support agent, File>Account home for About,
> M365 update channel) are out of scope for the LO source and were not independently verified.

---

## Conditional / version-sensitive controls

There is **no owner screenshot for the Help tab yet**, so the following are flagged
**expected-conditional, unverified against a live build** — a screenshot sweep would confirm
whether (and how) they surface. They are not contradicted by the inventory; they depend on
build/channel/tenant state. None of these change a work bucket.

- **Feedback duplication (OfficeFeedbackHelpTab + OfficeFeedbackIcon)** — highest-priority
  screenshot need. The canonical xlsx lists BOTH as live children of the same group, but a real
  Word window typically shows only ONE 'Feedback' button. A screenshot would confirm whether the
  current M365 build renders one, both, or neither, and which idMso is the visible labeled
  'Feedback' button vs. a hidden/icon-only or version-gated variant.
- **Feedback label & behavior (OfficeFeedbackHelpTab)** — docs give the on-ribbon label as
  'Feedback', but the catalog proves only idMso + type, not the rendered caption. Confirm the label
  is literally 'Feedback' (not 'Send Feedback' / 'Send a Smile') and that clicking it opens the
  backstage `TabOfficeFeedback` smile/frown flow.
- **Help button behavior (idMso Help)** — the inventory asserts Word opens a DOCKED in-app Help
  task pane on the right; recent M365 builds have shifted some Help to a browser/embedded-web
  surface. A screenshot confirms whether current Word still renders a docked in-app pane
  (load-bearing for the LO 'differs: external browser/viewer' contrast).
- **Contact Support label & behavior (idMso ContactUs)** — catalog idMso is `ContactUs`, the
  ribbon LABEL is 'Contact Support' per docs (an older reference shows the caption 'Contact Us…').
  A screenshot would confirm the current rendered label and that it opens an in-app support/agent
  pane (vs. a browser), since the inventory's vendor-agent/chat contrast with LO depends on this.
- **Show Training presence (idMso ShowTraining)** — a candidate for version/tenant gating and
  removal in newer M365 channels (Microsoft has been retiring in-app training surfaces). A current
  screenshot confirms whether the button is still present and still opens an in-app training-video
  pane.

---

## Out of scope

- **Cloud / online support & feedback services (cut by product choice, 5 controls).** Contact
  Support (Microsoft support-agent chat), both Feedback buttons (the in-app smile/frown flow that
  posts to Microsoft), Show Training (curated training videos/tutorials), and What's New (the M365
  update-channel changelog). LO has community-flavoured browser-based counterparts for three of
  these (`.uno:QuestionAnswers` → community Q&A/forum, `.uno:SendFeedback` → feedback web page,
  `.uno:WhatsNew` → release notes), all opening the default browser; the duplicate Feedback icon
  and Show Training have no LO counterpart at all. None is a document capability, so none is an
  engine gap — they are cut as vendor/online product choices for a local clone.
- **No engine gap.** Unlike content tabs (Insert/Home), the Help tab surfaces **zero**
  document-editing capabilities, so there is nothing here that would block or inform the
  engine/core decision. The only "missing" LO items (Show Training, the duplicate Feedback icon)
  are online/UI artifacts, not engine blockers.
- **Backstage / namespace-collision note (not a Help-tab gap).** A SEPARATE backstage entity
  `TabHelp` (Policy ID 20802, Tab Set 'None (Backstage View)') is NOT the ribbon `HelpTab` (27543)
  — it is the File>Account/Help backstage page (groups GroupAboutOfficeProducts,
  GroupWhatsNewInOfficeProducts, GroupClickToRunUpdateStatus, GroupUpdateChannel, etc.). The
  smile/frown feedback UI lives in yet another backstage tab, `TabOfficeFeedback` (27265), reached
  via the Help-tab Feedback buttons. About lives in File>Account (the backstage `TabHelp`), not on
  the on-ribbon Help tab. These are out of scope for the on-ribbon Help-tab inventory.

---

## QA flags & resolutions

From `result.qa`. The Word/idMso side was set-diffed against the official `wordcontrols.xlsx`
(M365 Current Channel) and is **fully** confirmed for the Help ribbon TAB (8 rows match the
authoritative set with zero omissions and zero extras). Because there is **no owner screenshot for
this tab**, several runtime/render items remain **screenshot-pending**.

| QA flag | Status | Resolution |
|---|---|---|
| `OfficeFeedbackIcon` framed as "Source-1-only / duplicate that may be absent"? | **Resolved (source set-diff) / render screenshot-pending** | The Word-side framing is wrong: the canonical M365 xlsx lists BOTH OfficeFeedbackHelpTab (33241) AND OfficeFeedbackIcon (34024) as live children of `HelpTab>GroupHelpAndSupport` simultaneously — the 'single-source variant that may be absent' phrasing is a dataset artifact, not Word reality. The LO-side verdict (one `.uno:SendFeedback`, the icon variant LO-missing → Cut) stands; only the Word-side justification was off. Which renders in a live window is screenshot-pending. |
| Tab/group completeness — could Word membership be uncertain? | **Resolved (canonical source)** | No. `HelpTab(27543)` → `GroupHelpAndSupport(27544)` has EXACTLY six buttons {Help 984, ContactUs 7903, OfficeFeedbackHelpTab 33241, OfficeFeedbackIcon 34024, ShowTraining 27442, WhatsNewRecentUpdates 27055} and no others. The 8 inventory rows (6 buttons + 2 containers) match with zero omissions/extras; idMso strings, types, and containers are verbatim-correct. |
| `HelpTab` (ribbon, 27543) vs `TabHelp` (backstage, 20802) namespace collision? | **Resolved (source) — documented** | Distinct entities. `TabHelp` is the File>Account/Help backstage page (About / What's New / update-channel groups), NOT the on-ribbon `HelpTab`. The inventory's notes that 'About lives in File>Account' and What's New mirrors File>Account are correct and trace to this backstage `TabHelp`; documented in [Out of scope](#out-of-scope) to avoid future idMso mix-ups. |
| `WhatsNewRecentUpdates` appears twice in the catalog (ribbon + 'Not in the Ribbon')? | **Resolved (source)** | Same command (Policy ID 27055) surfaced both on the Help ribbon tab and as a non-ribbon/backstage command — harmless; confirms the note that What's New mirrors File>Account behavior. Not a contradiction. |
| Smile/frown feedback UI attributed to `OfficeFeedbackHelpTab`? | **Resolved (source)** | The smile/frown/suggestion UI belongs to the backstage `TabOfficeFeedback` (27265, groups GroupOfficeSendSmile/SendFrown/SendSuggestion), reached VIA the Help-tab Feedback buttons. The OfficeFeedback family also includes OfficeFeedback (26904), OfficeFeedbackBackstage (27302), TextPredictionsFeedback (34160) — all backstage/non-ribbon, for context, not Help-tab gaps. |
| Project Help-tab "only 2 controls (Writer Help + About Writer)"? | **Resolved (LO source)** | Wrong — LO's notebookbar Help source has THREE controls (HelpIndex, SendFeedback, About); the claim omits SendFeedback. In pristine `notebookbar.ui` these live in the `Menu Help` dropdown (lines 493/534/593), not a dedicated Help tab. (`ribbon.json` not found in the tree; verified against the LO UI source it should mirror.) (Re-verify note: prior cite was to the removed project-custom `notebookbar_cua.ui`, which had a Help **tab**/`HelpToolBox`; pristine `notebookbar.ui` differs — no Help tab, the 3 commands are menu items — but the FACT (three Help controls, SendFeedback included) is unchanged.) |
| Help button "bound to F1"? | **Resolved (LO source)** | Functionally true but mechanistically corrected: F1/`KEY_HELP` is hardcoded in `vcl/source/window/winproc.cxx:1295`, not a config accelerator in `Accelerators.xcu` (no HelpIndex entry). The slot allows an accelerator (`AccelConfig=TRUE`) but none is set by default. |
| Help button behavior — does current Word still render a DOCKED in-app pane? | **Open (screenshot-pending)** | Docs say 'Displays the Help task pane displaying the home page', but recent M365 builds have shifted some Help to a browser/embedded-web surface. A screenshot confirms the docked-pane assumption that the LO 'differs: external browser/viewer' contrast rests on. Does not change the bucket. |
| Contact Support / Show Training — current label & live presence? | **Open (screenshot-pending)** | ContactUs label is 'Contact Support' per docs (older ref 'Contact Us…'); ShowTraining is a candidate for version/tenant gating and removal. Screenshots would confirm rendered labels and whether each still opens its in-app pane. Buckets (both Cut) unchanged. |
| Exhaustiveness of the LO-side absence claims (ShowTraining, second feedback variant)? | **Resolved (LO source, high)** | `completenessConfidence`: VERY HIGH for the Help ribbon tab on the Word/idMso side (verified against the authoritative M365 Current Channel `wordcontrols.xlsx`); the LO-side absence claims (no ShowTraining slot, single SendFeedback command) were source-confirmed. Caveat: completeness is asserted for static control-catalog membership, not for what a given build/tenant actually renders (flagged screenshot-pending above). |
