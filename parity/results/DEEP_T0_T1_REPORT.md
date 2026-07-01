# Deep T0/T1 Fidelity Report — full dialog + variation enumeration (IDENTIFY-ONLY)

**Phase:** identify every clone-vs-Word difference across the top-usage Home/T1 controls at FULL depth
(main action + parameter variations + every meaningful dialog field), measured on all 3 axes. **Nothing is
fixed** — gaps are recorded for a later, separate fix pass. Branch `parity-pipeline` (not merged).

**3 axes per sub-task:**
- **OOXML** — apply the field's effect via the `WC.PM` bridge, export `.docx`, diff document.xml + styles.xml +
  numbering.xml vs real Word (COM ground truth). The differ is regression-locked (`review_differ.py` ALL PASS).
- **FLOW** — open the dialog at runtime, confirm the field control is present + an OK/apply exists
  (`dialog_flow.py` → `DIALOG_FLOW_LEDGER.md`).
- **VISUAL** — light spot-check that the clone renders the effect (not a no-op); for 0/0-OOXML fields the
  byte-identity itself guarantees Word-identical rendering.

---

## 1. Scorecard

| Group | tasks | OOXML clean (0/0) | OOXML findings |
|---|---|---|---|
| T0 mains (Bold…Center) | 8 | 7 | bullets (numbering.xml COM-artifact) |
| T1 mains (Color…Spacing + pilots) | 7 | 3 | highlight / numbering / pagenum / table (COM-artifacts) |
| **Variations** (underline×6, size×3, spacing×2) | 11 | **11** | — |
| **Font dialog** (FD) | 10 | 9 | fd-allcaps |
| **Paragraph dialog** (PD) | 13 | 12 | fd-spacing-after |
| **Color / More Colors** (CD) | 2 | 1 | fd-fontcolor-theme |
| **Find/Replace** (RD) | 1 | 1 | — |
| **Insert/Layout** (ID) | 3 | 2 | fd-link |
| **Code-traced gaps (not captured)** | 16 | — | see §4 |

**Captured this phase (variations + 5 dialog batches): 40 tasks → 36 clean (0/0), 4 with findings.**

---

## 2. OOXML axis — the clean results (faithful: 0 missing / 0 extra)

The clone's OOXML is **byte-identical to Word** for every one of these — confirming the effect AND its encoding:

- **Variations (11/11):** underline single/double/dotted/dashed/wavy/words; font size 10.5/8/72; line spacing 1.0/1.5.
- **Font dialog (9/10):** strikethrough, underline-color, superscript, subscript, small-caps, **character spacing**
  (pt→twips ✓), **character scale** (w:w ✓), **character position** (pt→half-point ✓), **ligatures** (the 022 fix
  holds inline). *(The investigation flagged spacing/position conversions as "VERIFY" — measurement resolves them: exact.)*
- **Paragraph dialog (12/13):** indent left/right/first-line/**hanging**; spacing-before; line-spacing
  **At-least / Exactly / Multiple**; and all 4 **pagination** fields (widow-off, keep-with-next, keep-lines,
  page-break-before) — OOXML faithful even though those fields aren't in the dialog UI yet (see FLOW §3).
- **Color (1/2):** custom RGB font color (#3A7BD5).
- **Find/Replace (1/1):** Replace All (`Revenue`→`Income`) — clean text delta, run rPr preserved.
- **Insert/Layout (2/3):** Page Setup top-margin (1.25in→1800tw) and left-margin (1.5in→2160tw).

---

## 3. FLOW axis — dialog open / field present / OK (runtime)

From `DIALOG_FLOW_LEDGER.md` (runtime-confirmed; 3/6 dialogs flow-complete):

| Dialog | opens | OK | fields present | missing (Word-has, clone-lacks) |
|---|---|---|---|---|
| Font | ✅ | ✅ | 12/17 | underline-color, double-strikethrough, hidden, ligatures, kerning |
| Paragraph | ✅ | ✅ | 7/11 | widow/orphan, keep-with-next, keep-lines, page-break-before (no Line-and-Page-Breaks tab) |
| Find/Replace | ✅ | ✅ | 7/7 | — (Special/Format present as buttons) |
| Insert Table | ✅ | ✅ | 2/2 | — |
| Insert Hyperlink | ✅ | ✅ | 2/2 | — |
| Page Setup margins | (code-traced) | — | 1 uniform field | independent top/bottom/left/right (single 'Margin' input) |

The flow axis **runtime-confirms** the code-traced field-absences: the Font dialog's missing effects and the
Paragraph dialog's missing pagination tab are the same gaps §4 lists. Find/Replace + the two Insert dialogs are
flow-complete. Page-margins didn't auto-drive via the flyout in the probe; its single-uniform-field limitation is
established by code trace.

---

## 4. Identified gaps catalog (NOTHING FIXED)

Every finding below was **adversarially verified** (7 skeptic agents, each trying to refute it as an
artifact, reading the clone source + the fixtures). Verdicts: **CONFIRMED real gap** vs **artifact**
(COM-method / my-value-choice / differ-limitation). Two of my initial classifications were corrected.

### 4a. CONFIRMED real clone gaps (10) — ✅ ALL FIXED (specs 024–029)

> **🏁 Fix pass complete (2026-06-30, on `parity-pipeline`, NOT merged).** All 10 fixed with TDD (RED→GREEN) +
> a `run.py --only`-0/0 or `test:pm`-numbering.xml acceptance + the 3 clone gates + a per-fix adversarial review.
> Two reviews caught real bugs that were then fixed: the `fd-link` "13 missing" was mostly a differ baseline-
> subtraction artifact (→ the styles styleId-presence refactor, §4c) and the 026 effects had a clearing-leak
> (`RUN_PROPERTIES_DERIVED_FROM_MARKS`). Commits: 024 `a21d38f`/`9a82452`, 025 `e2ec38d`, 026 `ecadee9`,
> 027 `9334cfd`, 028 `65bf229`, 029 `1522b37`. Gates: test:pm 515/515, roundtrip 27/0.


| # | id | the gap | severity | smallest fix (later) |
|---|---|---|---|---|
| 1 | `fd-allcaps` | over-emits `<w:caps w:val="1"/>`; Word writes bare `<w:caps/>` (caps-translator hand-writes `w:val` on ON; strike/smallCaps use the bare toggle) | cosmetic over-emit | caps-translator decode: bare element on the ON case |
| 2 | `fd-fontcolor-theme` | run font-color is **sRGB-only** — no `w:themeColor`/tint/shade; theme picks bake the resolved hex (won't recolor on theme change) | **fidelity** | add `themeColor` attr to the color mark + exporter + dialog |
| 3 | `fd-link` (extra-u) | emits a redundant **direct `<w:u single>` alongside** `<w:rStyle Hyperlink>`; Word emits only the rStyle | cosmetic over-emit | suppress direct `w:u` when `rStyle=Hyperlink` (link.js:257) |
| 4 | `fd-double-strike` | **no author path** for `<w:dstrike/>` — no checkbox, no attr, no verb (translator round-trips import only) | missing feature | textStyle `dstrike` attr + Effects checkbox |
| 5 | `fd-hidden` | **no author path** for `<w:vanish/>` (Hidden) | missing feature | textStyle `vanish` attr + Effects checkbox |
| 6 | `fd-kerning` | **no author path** for `<w:kern/>` (Kerning ≥ N pt) | missing feature | textStyle `kern` attr + Advanced control |
| 7 | `fd-bullet-font` | Define-New-Bullet **strips `w:rFonts`** + no Symbol/font picker → Symbol/Wingdings bullets unreachable | missing feature | `levels[].font` + Symbol picker (stop stripping rFonts) |
| 8 | `fd-bullet-align` | **narrow:** no Center/Right alignment field (the clone DOES emit `lvlJc=left`, Word's default) | narrow feature | `levels[].align` → `w:lvlJc` + a dropdown |
| 9 | `fd-special-replace` | `^p`/`^t`/`^l` in the **Replace** box inserted **literally** (Word makes a paragraph/tab/break) | behavior gap | parse the replacement into a Slice (touches the fork replace cmd) |
| 10 | `fd-margin-uniform` | Custom Margins dialog has **one uniform field** → independent T/B/L/R impossible via the dialog (the bridge verb supports it — `fd-margin-top/left` = 0/0) | dialog completeness | 4–6 independent inputs → `dePageMargins({top,bottom,left,right})` |

### 4b. Artifacts — NOT clone gaps (verified)

| id | verdict | why it is not a clone gap |
|---|---|---|
| `fd-spacing-after` | MEASUREMENT | 8pt-after **is Word's docDefault** → Word inherits/omits it; the clone writes it inline. Mechanism faithful (`fd-spacing-before` @12pt = 0/0). Identical render. |
| `fd-link` (Hyperlink style, 8 sigs) | **DIFFER LIMITATION** | The clone **preloads** the Hyperlink char style (content-identical to Word) in its blank template; Word **lazily** materializes it on insert. Baseline-subtraction zeroes the clone's styles-delta → Word's lazily-added style reads as *false-missing*. The clone is NOT missing the style. (see §4c) |
| `fd-link` (UnresolvedMention, 5 sigs) | COM/Word boilerplate | Word auto-adds the `@mention` "Unresolved Mention" style on any insert; never referenced by the run. Not a clone obligation. |
| `fd-num-format/style-text/gallery/start-at/restart/continue` (6) | COM-method | COM `ApplyNumberDefault` writes a **singleLevel** abstractNum; the clone (ribbon-faithful) mints a **hybridMultilevel** 9-level def → numbering.xml diverges, but the document.xml body (`w:numPr`) is at parity. A true numbering.xml comparison needs a **vsto/UIA** ribbon ground truth. |
| `fd-highlight-custom` | NOT A GAP | Word's highlighter is **also 15-keyword-only** (no custom-RGB path); the clone restricts to the same 15. The `w:shd` downgrade is **import-only dead code**. Clone == Word. |

### 4b-bis. Dialog-completeness flow gaps (3) — effect works, the dialog control is absent

Recorded as findings per the completeness check (previously only in `DIALOG_FLOW_LEDGER.md`). The OOXML effect
is faithful (0/0) but Word's dialog exposes a control the clone's dialog omits, so the field is unreachable
from the clone UI:

| id | gap | OOXML status |
|---|---|---|
| `fd-underline-color-ui` | Font dialog Underline row sets style only — no Underline-color dropdown | effect 0/0 (`fd-underline-color`) |
| `fd-ligatures-ui` | Advanced tab has Scale/Spacing/Position only — no OpenType Ligatures dropdown | effect 0/0 (`fd-ligatures`) |
| `fd-paragraph-pagination-ui` | Paragraph dialog has no Line-and-Page-Breaks tab | all 4 effects 0/0 (`fd-pag-*`) |

### 4c. Engine limitation surfaced (differ) — ✅ RESOLVED (styles styleId-presence diff)

**Status: FIXED** (`ooxml_diff.py` `_styles_diff` + `collect_styles`; regression-locked by 4 new `review_differ`
golden cases incl. `styles_preloaded_match`). `styles.xml` is now diffed by **styleId presence/content scoped to
the styleIds the bodies reference** — NOT baseline-subtracted — so a preloaded-but-identical style (clone) matches
a lazily-materialized one (Word), and unreferenced latent styles (UnresolvedMention) are ignored. `fd-link`'s false
13-missing collapsed to its one real signature (`body:u`). The original limitation, for the record:

The `fd-link` false-13 exposed a **soundness gap in the styles.xml diff**: the clone **preloads its full
styles.xml** in the blank template while Word **lazily materializes** styles on first use. Baseline-subtraction
then (a) zeroes the clone's styles-delta for any preloaded style and (b) reports Word's lazily-added style as
*missing from the clone* — a **false-missing**. **body / header / footer / numbering diffs are unaffected**
(only styles.xml has the preloaded-vs-lazy asymmetry). `review_differ` stays green because it checks differ
*correctness* (Word==self, clone==self, golden), not this preloaded-vs-lazy *semantic*. **Follow-up:** diff the
styles part by `styleId` **presence/content** (does the clone have a style with this id + equal rPr?) instead of
baseline-subtracted signature buckets, and add a golden case. Until then, **interpret any `styles:*` "missing"
by checking whether the clone's blank already carries that style.**

---

## 5. Intentionally skipped / not measured (honest coverage)

- **numbering.xml-only fields** (Define-New number format/style, gallery 1./a)/i./A., Set-Value start/restart/continue):
  the defining signal lives only in numbering.xml; the COM `ApplyListTemplate` ground truth is a singleLevel-vs-
  multilevel artifact + a minted numId value — a faithful comparison needs a **vsto/UIA ribbon** ground truth. The
  document.xml signal (`w:numPr` + 023 `pStyle`) is already at parity.
- **Theme-color resolution & highlight-custom** have **no clean Word COM oracle** (theme link / shading downgrade).
- **Find + search modifiers** (match-case, whole-word, wildcards, Format) produce **no document delta** → flow axis only.
- **Cartesian value sweeps** — only DISTINCT-OOXML representative values per field (e.g. one Expanded spacing, not
  every point value); symmetric twins (left/right indent, before/after, raised/lowered) measured once each.
- **Font/Advanced niche OpenType** — Number spacing (proportional/tabular), Number forms (lining/old-style),
  Stylistic sets: clone-unimplemented, very low usage → explicitly skipped (`tasks.json._dialog_skip_log`).
  "Use Contextual Alternates" folds into the ligatures/022 handling; "Set As Default" is a settings action, not a field.

**Coverage is now provably exhaustive:** every meaningful Font-dialog field is measured, recorded as a gap, or in
the skip log; the 3 non-flow-complete dialogs' (Font/Paragraph/Color) flow gaps are all recorded as findings (§4a/§4b-bis).

---

## 6. Next (deferred to the user): the fix pass

Once the classifications are accepted, the real clone gaps (not COM/measurement artifacts) become spec-kit /
direct-TDD fix candidates, batched like the 022/023 fidelity fixes. **No fixing was done in this phase.**
