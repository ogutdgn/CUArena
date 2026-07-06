# P0 — Home-Tab Pilot Exit Report (ui-crawl)

**Status:** P0 implementation complete; awaiting user schema ratification (the P0 exit gate).
**Date:** 2026-07-06. **Parity build (live):** Word for Windows **16.0.20131** (see §1).
**Branch:** `ui-structure`. **Oracle output:** `parity/oracle/ui-structure/` (25 JSON + 70 PNG).
**Harness:** `parity/tools/ui_crawl/` (13 modules; `python -m pytest parity/tools/ui_crawl/tests` → 26 pass).

This report is the P0 gate deliverable (DESIGN §9): Home 100 % captured, UIA exposure map built,
AutomationId=idMso validated, press-mechanism + reset rules proven, throughput measured, schema
ratified by the user **on real data**. All numbers below are from the authoritative final run
`run-20260706-022149` (emitted to the repo); reproducibility was proven against a second run (§6).

---

## 0. Environment deviations discovered live (require user awareness)

| # | Finding | Handling in P0 | Follow-up |
|---|---|---|---|
| D-a | **Build drift**: Office auto-updated **16.0.20026.20168 → 16.0.20131**, past the intended freeze. The launcher's build-assert caught it. | User approved re-pinning `config.BUILD_PREFIX` to `16.0.20131` (commit `chore(test): re-pin…`). | **Reconcile ADR-0006 + DESIGN §3.4** (still cite 20026) to 20131, or re-freeze Office. |
| D-b | **Acrobat COM add-in** injects an `Adobe Acrobat` group (`Create a PDF`) + an `Acrobat` tab into Home; it survived the launch-time COM-add-in disconnect. | Boundary-declared **D8** (`ribbon.home.adobe-acrobat.*`), never pressed. | Disable the Acrobat COM add-in for a pristine P1 environment (or keep the D8 boundary). |
| D-c | One COM add-in stays connected after `_disconnect_addins()` (recorded honestly in `app_fingerprint.addins_connected`). | Recorded; the only visible effect is D-b. | Same as D-b. |

---

## 1. Capture counts (Home tab)

- **Groups:** 9 — Clipboard (5), Font (16), Paragraph (15), Styles (2), Editing (3), Adobe Acrobat (1), Voice (1), Editor (1), Add-ins (1).
- **Controls:** **45** — by `probe_mode`: **41 `pressed-observed`**, **4 `boundary-declared`** (never pressed).
- **Control types:** 16 button, 11 toggle, 10 split, 5 menu, 2 combo, 1 gallery.
- **Surfaces captured (first-level):** **20** — 4 dialogs (`font`, `paragraph`, `find-and-replace`, `sort-text`) + 16 dropdowns (all split flyouts, both combos, the menus, and the galleries).
- **Frontier (discovered, P1/P2):** **18** — nested dialogs from popup ellipsis items (`define-new-number-format`, `set-numbering-value`, `text-effects`, `borders-and-shading`, …) + panes (`panes/find`, `panes/showclipboard`) + dialog child-dialog buttons.
- **Boundary edges (`coverage.json`):** 4 — all **D8**: `adobe-acrobat.create-a-pdf` (feature), `voice.dictate` (feature), `editor.writingassistancecheckdocument` (opens-pane), `add-ins.officeextensionsshowaddinflyout` (opens-dialog).
- **`unused_boundary_config`:** 3 — `ribbon.file` (File tab is out of Home scope), `voice.read-aloud` (no Read-Aloud button in this build's Home), `ribbon.home.copilot.*` (no Copilot ribbon group; Copilot is a canvas floating button, out of P0 scope).

**No-gap check:** every one of the 45 controls resolves to a captured surface, a boundary, or is
honestly recorded — 41 complete + 4 boundary; of the 41, **4 are `capture.status: unresolved`** (§7).
Reference closure: **0 dangling** refs; **0 missing assets**; **0 schema errors**; manifest ↔ filesystem bijection holds.

## 2. AutomationId = idMso validation

**41/45 = 91 %** of controls carry a live UIA `AutomationId` used directly as `idMso`
(e.g. `Bold`→`Bold`, `Font…`→`FontDialog`, `Paragraph…`→`ParagraphDialog`, `ChangeCaseGallery`,
`NumberingGalleryWord`, `WritingAssistanceCheckDocument`). The **4 without a container-level idMso**
fell back to a label slug (DESIGN R2), and all 4 are explained — this is **not** a coverage gap:

| Control | Why no container idMso | idMso actually present? |
|---|---|---|
| `clipboard.paste` (SplitButton) | Split **container** reports empty aid | **Yes**, on the primary child zone (`Paste`) |
| `editing.find` (SplitButton) | Split **container** reports empty aid | **Yes**, on the primary child (`NavigationPaneFind`) |
| `voice.dictate` (SplitButton) | Split container empty aid (also a D8 boundary) | Yes, on the primary child (`Dictate`) |
| `adobe-acrobat.create-a-pdf` | **Third-party** Acrobat add-in control (no idMso) | No (out-of-scope add-in, D8 boundary) |

So of the 42 Word-native controls, the only genuine idMso absence is the two split **containers**
(whose zones do carry idMso). **AutomationId=idMso is validated.** (The plan's ≥95 % target refers to
Word-native controls; the label-slug fallbacks are the documented, stable R2 path.)

## 3. UIA exposure map (from `--enumerate-home`, §6.3 checks)

The pilot built the exposure map **before** trusting any pattern heuristic — and found Office ribbon
pattern-availability **too quirky to classify with**:

- **`iface_*` pattern accessors are useless** — every pywinauto wrapper exposes all of them. Reliable
  detection = `IUIAutomationElement.GetCurrentPropertyValue(Is<Pattern>Available…)`.
- **Bold (the canonical toggle) exposes `SelectionItem`, not `Toggle` or `Invoke`**; the non-toggle
  `Paste` *does* report `Toggle`. Ribbon buttons are driven via `LegacyIAccessible` (matching the
  DESIGN §6.1 rationale for injected input over `Invoke`/`ExecuteMso`). **Consequence:** classification
  is **press-and-observe**, not pattern-inference (Bold is `pressed-observed`, a deliberate deviation
  from the plan's `pattern-inferred` expectation).
- **Split buttons expose both zones as children** (Button primary + MenuItem `*_Dropdown` flyout) —
  10/10 splits; zone points come from those child rects.
- **Owner-drawn flyouts** (menus, galleries, color grids) expose **no item-level UIA** via tree-walk
  (control *and* raw view return only the empty top container). Recovered via
  `IUIAutomation.ElementFromPoint` grid-sampling (§5). **This is the load-bearing discovery for the
  full crawl** — popup capture must be point-sampling, not `descendants()`.
- Toggle state (for restore/verify) reads via `SelectionItem.IsSelected` (Office toggles), not `Toggle`.

## 4. Dialog cross-check vs the 7 pre-existing ground truths

Modal dialogs enumerate fully via UIA `descendants()` (unlike flyouts):

- **Font dialog:** 30 fields across tabs `[Font, Advanced]` + 5 buttons `[Close, Set As Default,
  Text Effects…, OK, Cancel]`. Field-name match vs `parity/oracle/dialogs/font.json`: **20/20 = 100 %**
  (All caps, Ligatures, Kerning, Scale, Spacing, Position, Stylistic sets, Contextual Alternates, …).
- **Paragraph dialog:** 15 fields captured (GT `paragraph.json` has 22 field-ish strings; the crawler
  captures interactive fields, not every static label — a P1 section-grouping/label pass will close the gap).
- Also captured and validated: `find-and-replace`, `sort-text` dialogs. All dialog payloads pass
  `schemas.validate_dialog` ([]).

## 5. Popup capture (owner-drawn → ElementFromPoint)

Example — Numbering flyout: **11 items in 2 sections**: a `Numbering Library` gallery (8 tiles: None,
`1,2,3…`, `I,II,III…`, `A,B,C…`, `a,b,c…`, `i,ii,iii…`) + a menu-items section where `Define New
Number Format…` / `Set Numbering Value…` become `opens-dialog` refs (journaled `surface-discovered`
→ frontier) and `Change List Level` is `feature`. Styles gallery: 19 items, flagged **`dynamic: true`**.
All popup payloads pass `schemas.validate_popup` ([]). *Caveat:* gallery tile labels carry a `U+FFFD`
where Word's accessibility name uses a special separator (ids derive cleanly; a P1 label-cleanup item).

## 6. Reproducibility (normalized structural diff)

Two independent full runs → **EMPTY structural diff after normalization** (reproducibility gate passes).
Applied normalization rules: exclude `manifest.json` (date/throughput), `icons.json`/`screenshots.json`
(hash manifests — assets compared by **existence**, not hash); drop items of `dynamic:true` sections
(Styles gallery); normalize `screenshot` filenames. Getting to an empty diff required eliminating two
real non-determinism sources, both **Word pane-persistence** artifacts (§7 / §8):

- Word **persists task-pane visibility across launches** → polluted the baseline (and *suppressed
  ribbon UIA enumeration*). Fixed by closing every pane at run start + after each control via its
  **`Close pane`** header button (docked *and* floating panes).
- Docked-pane classification made deterministic via the `_WwG` document-area **inset** signal.

## 7. Ambiguous / unresolved queue (4, deterministic) + adjudications

All 4 are `pressed-observed` with `capture.status: unresolved` and an `ambiguous` journal entry — honest
"pressed, no positive evidence" records (DESIGN §4.2 forbids silent `feature`):

| Control | Why unresolved | Adjudication |
|---|---|---|
| `clipboard.copy` | Copy mutates only the clipboard — no doc-hash / format / surface / toggle delta | Correct: no positive evidence. P1 could add a clipboard-hash sensor. |
| `font.clearformatting` | No-op on the **plain** fixture paragraph (nothing to clear) | Fixture artifact — pre-format the fixture in P1 → becomes `feature`. |
| `paragraph.indentdecreaseword` | Para 1 already at min indent → no change | Same fixture artifact. |
| `styles.stylespane` | Opens the **floating** Styles pane, which does not inset `_WwG` (docked-pane detector misses it) | Genuine detector gap → **P1 pane-detection hardening** (see §8). |

**2 of 3 pane-openers now classify correctly** (`ShowClipboard` → `opens-pane`; `Find` primary →
`opens-pane`, flyout → `opens-dropdown`); only the floating Styles pane remains unresolved.

## 8. Throughput → full-crawl budget

**4.35 s/control** (45 controls incl. surface capture + reset, single-threaded, ~196 s total).
Projected full crawl at the DESIGN's ~5 439 controls: **≈ 6.6 hours** wall-clock (upper bound — the full
crawl includes surface recursion and stimulus passes not in P0's first-level scope; parallelism is not
assumed). Resume-after-crash proven (§ below) makes a multi-hour run safe to interrupt.

## 9. Mechanisms proven

- **Press-mechanism (§6.1):** injected input only (`mouse.click` at the zone point); no
  `Invoke`/`ExecuteMso` on unclassified controls. 5-archetype live check + full run, zero deadlocks.
- **Zone-aware split probing:** primary + flyout probed separately; Paste primary=`feature`,
  flyout=`opens-dropdown`.
- **Symmetric restore + fingerprint:** ESC (dialog/popup, foreground-safe — does not steal focus from a
  modal), re-press+state-verify (toggles), `^z`+doc-hash (features), `Close pane` (panes). Every probe
  `reset-verified`; **zero orphan WINWORD across all live runs** (PID-safe teardown).
- **Journal quarantine (§6.2):** `press-attempted` journaled before injection; ≥2 attempts → ambiguous.
- **Resume:** from a truncated (mid-crash) journal → completes the remaining controls, **45 unique
  control-captured, no double-probe**, `dangling=0`, `missing_assets=0`.
- **Reconciling emitter:** entry_points = journal-inverse; coverage boundaries = journal `boundary`
  records (double-entry); reference + asset closure enforced on every emit; orphan sweep.

## 10. Deliberate P0 deferrals (none block the P0 gate)

Stimulus pass; hover-tooltip fallback (UIA `HelpText` is empty on Home controls → tooltips deferred;
`AccessKey` keytips + `AcceleratorKey` shortcuts **are** captured); `inRibbon.visibleItemRefs` join;
phash icon dedupe (existence-only in P0); white-ratio icon heuristic (all-one-color + min-size only);
dialog **section grouping** + full label set (agent pass, §8.7); deep pane capture (panes are frontier).

## 11. Open issues for P1

1. **Pane-detection hardening** — the floating Styles pane isn't caught by the `_WwG` inset signal
   (→ `stylespane` unresolved); detect panes via the `Close pane` button presence (already used for
   closing) or a UIA pane-header signal.
2. **Fixture enrichment** — pre-format the fixture paragraph so `clearformatting` / `indentdecrease`
   produce a delta (→ `feature`, not `unresolved`).
3. **ADR-0006 / DESIGN §3.4 reconciliation** to build 16.0.20131 (or re-freeze Office).
4. **Acrobat add-in** — disable for a pristine environment, or keep the D8 boundary.
5. **Group-overflow** — Home has none at 1920×1080 (Editing is fully expanded); the `group-overflow`
   path will first exercise on narrower widths / other tabs.
6. Popup label `U+FFFD` cleanup; dialog section-grouping + full static-label capture; clipboard/mode
   sensors to resolve `copy` / `format-painter`-class controls.

## 12. Requested user decision (P0 exit gate)

**Ratify the schema on this real data** (`parity/oracle/ui-structure/ribbon/home.json` + the 20 surface
files + `coverage.json` + `manifest.json`). On approval, P1 (remaining core tabs + shell) begins with
zero schema rework. Please also confirm the D-a build re-pin and the D-b Acrobat-add-in handling.
