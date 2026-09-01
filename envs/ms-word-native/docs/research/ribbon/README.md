# Word ribbon ↔ LibreOffice comparison

> **Purpose.** This folder is **MS Word clone decision-research**, not LibreOffice-app
> documentation. It enumerates Microsoft Word's ribbon surface **tab by tab**, diffs every
> control against LibreOffice's `.uno:` command surface, and classifies the **work** each
> difference implies — so we can decide the clone's **engine / core structure** on evidence
> and lock the **parity scope** (what we build now vs. what we cut).
>
> This is the **Word↔LibreOffice comparison** (Word's ribbon vs. LO's `.uno:` command
> surface) — not LibreOffice's own UI documentation.
>
> Note on location: it lives under `apps/ms-word/` because the LibreOffice **engine**
> (kept via LOK) lives here. The eventual home may move to wherever the clone app lives.

---

## Goal — the pipeline

1. **Enumerate** every Word feature per ribbon tab (Microsoft's official `idMso` control list + docs).
2. **Diff** against LibreOffice (`.uno:` command surface).
3. **Classify the work** each diff implies (see Legend).
4. → **Decide the engine / core** (LO-via-LOK vs. alternatives) on evidence.
5. → **Lock parity scope** (in vs. cut).

## How each tab is produced (verified pipeline)

A multi-agent workflow per tab:

```
3 independent web extractors          reconcile      map to LO       verify against        adversarial
(official idMso list · MS docs ·  →   into one    →  .uno:       →   the LO source     →   QA (completeness
 reference sites)                     canonical      command         tree (.sdi/.xcu)      + flags)
```

…then a **real-Word screenshot** (owner) confirms the visible control set. Confidence is recorded per tab.
The cross-checking is the point: on the Home tab, the layers corrected each other's errors.

## Legend

**Verdict** — Word control vs. LibreOffice:

| Verdict | Meaning |
|---|---|
| `same` | LO has an equivalent that behaves like Word |
| `differs` | LO can do it, but via a different dialog/UX or with different semantics |
| `LO-missing` | no LO equivalent |
| `UI-only` | group header / overflow host; no engine action |

**Work bucket** — what building it actually costs:

| Bucket | Cost | Engine work? |
|---|---|---|
| **Free** | wire the existing LO `.uno:` command | none |
| **Our-layer UI** | build the Word-faithful gallery/dialog in our UI, dispatch the LO command | none (front-end) |
| **Behavior shim** | intercept/massage in our dispatch layer because LO's result differs | small, our layer |
| **Cut** | out of scope; remove the entry point (cloud/AI/M365, niche) | none (by design) |
| **Engine gap** | LO engine genuinely can't; cut or accept reduced fidelity | the only true engine blocker |
| **Optional our-layer feature** | LO lacks it but it's app-state we could build (e.g. 24-item clipboard) | none (our layer) |

## Tabs

| Tab | Status | Confidence | Doc |
|---|---|---|---|
| **Home** | ✅ verified (extraction + LO-source + Word screenshot, M365) | LO-side: high · Word-side: confirmed | [home-tab.md](home-tab.md) |
| **Insert** | ✅ web-sourced + LO-verified · screenshot-pending | Word: high (official xlsx set-diff, ~99%) · LO: high | [insert-tab.md](insert-tab.md) |
| **References** | ✅ web-sourced + LO-verified · screenshot-pending | Word: high (xlsx set-diff) · LO: high | [references-tab.md](references-tab.md) |
| **Mailings** | ✅ web-sourced + LO-verified · screenshot-pending (re-bucketed, refined rule) | Word: high (xlsx set-diff) · LO: high | [mailings-tab.md](mailings-tab.md) |
| **Review** | ✅ web-sourced + LO-verified · screenshot-pending | Word: high (xlsx set-diff) · LO: high | [review-tab.md](review-tab.md) |
| **Layout** | ✅ web-sourced + LO-verified · screenshot-pending | Word: high (xlsx set-diff) · LO: high | [layout-tab.md](layout-tab.md) |
| **Design** | ✅ web-sourced + LO-verified · screenshot-pending | Word: med-high · LO: high (corrected) | [design-tab.md](design-tab.md) |
| **View** | ✅ web-sourced + LO-verified · screenshot-pending | Word: high (xlsx set-diff) · LO: high | [view-tab.md](view-tab.md) |
| **Draw** | ✅ web-sourced + LO-verified · screenshot-pending | Word: high (xlsx set-diff) · LO: high | [draw-tab.md](draw-tab.md) |
| **Help** | ✅ web-sourced + LO-verified · screenshot-pending | Word: very high · LO: high | [help-tab.md](help-tab.md) |
| _File / Backstage · contextual tabs_ | not started (out of current scope) | — | — |

**All 10 ribbon tabs complete — 692 controls.** Full tally + verdict below.

## Running decision status

- **Fidelity bar:** scoped parity — *indistinguishable within scope; entry points removed outside it*.
- **Direction:** clone (not real-Word automation).
- **Engine (leaning, evidence-gated):** LibreOffice via **LOK** + scoped parity, sealed/pinned,
  **no core-logic edits** (the guardrail; only sanctioned engine touch is *exposing* existing
  dialogs/commands).
  - **Full cross-tab tally (all 10 tabs, 692 controls):** Free **89** (13%) · Our-layer UI **231** (33%) ·
    Behavior shim **144** (21%) · **Engine gap 114** (16%) · Cut **91** (13%) · Optional **23** (3%).
    The build surface we own (Free + Our-layer UI + Behavior shim + Optional) = **487 (~70%)**.

    | Tab | Ctrls | Free | Our-UI | Shim | Engine gap | Cut | Opt |
    |---|--:|--:|--:|--:|--:|--:|--:|
    | Home | 118 | 22 | 51 | 10 | 10 | 22 | 3 |
    | Insert | 141 | 15 | 54 | 3 | 33 | 32 | 4 |
    | References | 44 | 4 | 18 | 7 | 7 | 5 | 3 |
    | Mailings | 73 | 7 | 12 | 42 | 0 | 12 | 0 |
    | Review | 104 | 18 | 23 | 37 | 11 | 12 | 3 |
    | Layout | 78 | 18 | 30 | 25 | 2 | 0 | 3 |
    | Design | 26 | 0 | 12 | 6 | 7 | 1 | 0 |
    | View | 43 | 5 | 15 | 5 | 9 | 2 | 7 |
    | Draw | 57 | 0 | 13 | 9 | 35 | 0 | 0 |
    | Help | 8 | 0 | 3 | 0 | 0 | 5 | 0 |

  - **Engine gap is entirely cuttable feature families, never core editing:** Draw whole-tab (35,
    stylus-only) · Insert building-blocks + rich-media (33) · Review Ink/TTS (11) · Home typography (10) ·
    View M365 reading-modes (9) · References TOA/citations (7) · Design Style-Sets (7) · Layout
    section-artifacts (2). Exclude the wholesale-cut Draw tab and engine gap is **~12%** of the rest.
  - **DECISION (LOCKED — owner-confirmed 2026-05-29):**
    **LibreOffice-via-LOK + Boundary A + scoped parity + no-core-edits.** Zero engine gaps in core
    editing / formatting / **Track Changes** / **Mail Merge** / References / Layout — confirmed against
    LO source. The project is a large **front-end + orchestration build** (~487 our-layer controls;
    hotspots: Mailings 42 shims, Review 37, Layout 25, plus the live-preview/gallery UI pattern),
    **not an engine reimplementation.**
