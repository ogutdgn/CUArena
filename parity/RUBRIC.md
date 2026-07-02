# Parity Rubric v2 — the measurement contract (Phase A)

> Decided step-by-step with the user (2026-07-01, axis-by-axis walkthrough). This file is the
> CONTRACT for what "measured" and "done" mean. Changes to it are user-signed decisions.
> Status: ⏳ walkthrough in progress — axes 1–2 locked, 3–6 pending.

## Definition of done (per locked feature — all columns green)

| Column | Question it answers |
|---|---|
| OOXML | does the clone write the same file content as Word (both directions)? |
| STRUCTURE | is every Word control present, correctly named, right type — incl. menu items, dialog fields, enabled-states? |
| SCORECARD | does every control actually DO something correct when clicked live? |
| VISUAL | does it look like Word (side-by-side)? |
| BEHAVIOR | do the feature's key flows behave like Word? |

No column substitutes for another. Exclusions must be user-signed with a reason
(`parity/oracle/structure_scope.json` → `excluded_idmso`). "Not measured" must be reported as
NOT MEASURED — never as "no gaps".

---

## Axis 1 — OOXML (file-content parity) — ✅ LOCKED 2026-07-01

Mechanic unchanged (proven): probe→wc.docx / oracle→rw.docx / signed-baseline diff
(`run.py` + `ooxml_diff.py`, trust gate `review_differ.py`).

**D1.1 — Import round-trip added (user: "evet ekle").** Per feature, SECOND leg: open the
real-Word `rw-<id>.docx` in the clone → resave → diff against the original. Guarantees "opening
a Word file doesn't corrupt it". Both legs must pass for the OOXML column.

**D1.2 — pass-with-note verdict (user approved).** Functionally-harmless byte differences
(e.g. `\* MERGEFORMAT`, bullet glyph codepoint, explicit-default `jc=left`) = third verdict
`pass-with-note`: counts as pass, the diff record is NEVER deleted (some "harmless" turn out
real — the hyperlink-style lesson). Byte-parity backlog = the note list.

**D1.3 — dimension rule for task generation (user approved).** Every option that produces
DISTINCT file output = its own task; combinations are NOT enumerated (test each dimension —
edge/style/width/color — separately). Targeted combination tasks only where interaction is
plausible (e.g. diagonal border × merged cell); the pilot + adversarial review nominate them.
Task-list completeness is auditable against the official inventory; features with missing
tasks show as NOT MEASURED.

**D1.4 — ground-truth method rule.** When in doubt, ExecuteMso (the ribbon's real code path);
plain COM only where proven identical to the ribbon; galleries/building blocks via one-shot
visible-Word capture.

---

## Axis 2 — STRUCTURE (ribbon/UI inventory parity) — ✅ LOCKED 2026-07-01

Word side = official idMso workbook + GetLabelMso labels (locked build). Clone side = the LIVE
rendered ribbon. 5 buckets: matched / label-differs / type-mismatch / missing / extra + signed
scope-outs. Known honest limit: name-based matching needs a human pass over first-run "missing"
lists (synonym pairs) — pin them in `structure_scope.json`.

**D2.1 — menu-item-level diff: YES (user: "evet").** Compare INSIDE every dropdown/menu/
gallery: the inventory's parent-nesting = the answer key for which items each menu contains.
Kills the "menu exists but has 2 of Word's 14 options" gap class.

**D2.2 — dialog-field diff: YES (user: "evet").** One-time UIA dump of each Word dialog
(fields, labels, tabs) as the answer key → compare against the clone's dialog DOM.
SCOPE: only dialogs belonging to the 111 locked features.

**D2.3 — contextual tab sets: DEFERRED with a HARD GATE (user decision).** Picture Tools /
Header & Footer Tools / Draw etc. are NOT mapped for the Tables pilot — **but mapping them is
MANDATORY before the measurement sweep moves past Tables to other features.** This is a
blocking precondition of Phase C, not a nice-to-have. (User: "diğer feature'lara geçecek
olursak kesinlikle eklememiz gerekiyor.")

**D2.4 — enabled-state (STATE) matrix: ADDED (user: "çok önemli", upgraded from deferred).**
This is state-management fidelity and part of the CUA/RL observation space: a button clickable
in the clone but grayed in real Word teaches an agent wrong behavior. Mechanic: define ~10
canonical contexts; per context ask real Word `GetEnabledMso` for every control (the proven
hang-free metadata call) → state×control matrix; probe the clone in the same contexts; diff.
Canonical contexts v1: (1) blank doc caret-in-text, (2) text selected, (3) caret in table,
(4) picture selected, (5) header-edit mode, (6) tracked changes present, (7) comments present,
(8) undo history non-empty, (9) clipboard full, (10) no selection/object mode.
Tables pilot uses contexts 1–3; the rest activate in the sweep.

---

## Axis 3 — SCORECARD (live functionality) — ✅ LOCKED 2026-07-01

Mechanic: click every control in the running app, classify the outcome (flyout-with-items /
dialog / doc-changed / honest-stub-toast / inline-gallery vs DEAD / SILENT). Scorecard proves
"something happens"; STRUCTURE D2.1 proves the menu CONTENT is right; OOXML proves the EFFECT
is right — the axes are complementary by design.

**D3.1 — FLOW merges into SCORECARD (user: "evet").** The old flow verifier (declared-type vs
actual interaction, item-label presence) becomes part of the scorecard probe; FLOW is no longer
a separate axis. The 5-column ledger becomes: OOXML / STRUCTURE(+STATE) / SCORECARD / VISUAL /
BEHAVIOR.

**D3.2 — menu-ITEM-level clicking added (user: "evet").** Two modes:
- FAST: top-level controls only (~261 clicks) — per-commit gate.
- DEEP: every menu item clicked too (~1.5k clicks, ~15-20 min) — pilot + nightly runs.
Item click classified like controls (doc-changed / dialog / toast / NOTHING=dead-item).

**D3.3 — SILENT bucket gets special verifiers (user: "evet").** Controls whose work is
invisible on the document get dedicated checks instead of human triage: clipboard readback
(Copy/Cut), zoom value (zoom presets), view-mode class (view switches), selection change
(Select controls), pane/panel presence (panes). Goal: SILENT shrinks to genuinely-suspect only.

## Axis 4 — FLOW — ✅ MERGED into Axis 3 (D3.1); no longer separate
## Axis 5 — VISUAL (side-by-side vs real Word) — ✅ LOCKED 2026-07-01

Replaces the clone-only judge. Mechanic: capture BOTH sides (Word: `_capture_word_ribbon.ps1`
family; clone: `ribbon-shot-probe.js`) → an LLM judge sees the pair: "same screen of the same
program? would a Word user notice? list differences" → pass/fail + reasons ALWAYS logged.

**D5.1 — scope: all 4 levels (user approved), priority 4→1→2→3:**
(1) ribbon per tab, (2) open menus/galleries, (3) dialogs, (4) DOCUMENT RESULT rendering
(e.g. a styled table side-by-side) — level 4 is the most important for the RL environment.

**D5.2 — the bar (user approved):** "would a Word user notice at a glance?" — pixel-diff is
deliberately rejected (different rendering stack). A fail must state the visible reason.

**D5.3 — judge trust gate (user approved):** like review_differ — the judge must pass planted
golden pairs (identical→pass, seeded-difference→must catch) before its verdicts count.

**D5.4 — capture discipline (from the resolution/quality discussion):** both sides maximized
at the SAME window size (1920-wide; the ribbon reflows/condenses when narrow — proven in the
tables loop), Windows display scaling pinned/verified at capture time, both light theme,
document shots at 100% zoom, lossless PNG only. Per-group crops may be fed to the judge.

**D5.5 — icons:** real Word icons extracted via GetImageMso = the ground truth for icon
comparison. The clone KEEPS the open-source Fluent set; only icons the judge flags as
user-noticeable get hand-fixed. (Embedding extracted MS icons = rejected for licensing
cleanliness unless the user signs otherwise.)

## Axis 6 — BEHAVIOR (does it ACT like Word?) — ✅ LOCKED 2026-07-01 (user-amended)

TWO TIERS (the user's amendment: not only top journeys — detail-level behavior must be
testable too, e.g. "one cell's one edge turns red ON SCREEN"):

**D6.1 — Tier 1: journey flows (3-10 per feature, hand-crafted).** Multi-step UX narratives
(live preview while hovering the grid picker, caret lands in first cell, contextual tabs
appear, one undo step). Format = the flow card: steps + expected observation per step.
Expectations come from a REAL-Word recording (CUA-driven), NEVER from memory — unknowns stay
"❓ FROM RECORDING" until observed. I draft; the USER signs the flow list (like this rubric).

**D6.2 — Tier 2: micro-behavior twins (GENERATED, not hand-written).** Every OOXML task from
the D1.3 dimension rule automatically gets a live-behavior twin: drive the SAME action through
the REAL ribbon UI (clicks, not API calls), then verify the LIVE PAINT/state — right cell,
right edge, right color, neighbors untouched, selection preserved. This is the instrument for
the "file is clean but the screen is wrong" class (the border-collapse lesson). Expectations
derive from the action itself; no recording needed for most.

**D6.3 — ambiguity flags.** Where Word's behavior is not derivable (toggle-off on second
click? does selection survive? does hover preview apply?), the twin carries a ❓ flag and a
TARGETED real-Word recording resolves it. Flags may not be guessed closed.

**D6.4 — honesty rule.** BEHAVIOR is a sample, and the ledger says so ("N/N flows + M twins
pass (sampled)") — never "behavior 100%". Every bug found anywhere becomes a new flow/twin
(regressions can't return).

---

# ✅ RUBRIC COMPLETE — all 6 axes locked 2026-07-01 (FLOW merged into SCORECARD → 5 ledger columns)

---

## Process rules (standing)

- Measurement sweeps run autonomously; FIXES stay loop-gated (spec → fix → re-measure →
  adversarial review).
- Verdicts reported per locked feature (111 rows) with per-control drill-down.
- Phase B acceptance (Tables pilot): the pipeline must independently rediscover the KNOWN
  Tables gaps (2/247 gallery, cnfStyle, Draw/Eraser/Painter stubs, Insert Cells…, label
  mismatches) with zero false full-parity verdicts on hand spot-checks.
