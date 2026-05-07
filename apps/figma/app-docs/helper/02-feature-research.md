# 02 — Feature Spec Reference

> **Status:** ✅ Completed and **substantially expanded**. Agent A originally produced ~60 specs across 12 categories per the closed list in §5. The user (with primary agent help) then expanded the corpus to **~250 specs across 34 categories**, covering essentially the full Figma Design feature surface as if everything will be implemented (FN / VO / DEF status per spec). Current canonical inventory: `helper/extracted/features/index.md`.

> **How to use this doc:** when you need to implement a feature, jump to **Workflow 1 — Implementing a feature** in `helper/00-overview.md §7a` for the recipe. Come back here for the per-category spec inventory in §3, the spec template in §4, or the entry-points list in §14. Don't read top-to-bottom unless you're onboarding.

> **Pointers from this doc into the corpus:**
> - **Output location:** `helper/extracted/features/<category>/<feature>.md` (~250 specs across 34 categories)
> - **Canonical inventory:** `helper/extracted/features/index.md`
> - **Status (FN / VO / DEF) + spec map:** `helper/analysis/feature-inventory-deep.md`
> - **Per-article reference for source material:** `helper/analysis/figma-design-deep-index.md`
> - **Cross-feature interactions:** `helper/analysis/cross-feature-relationships.md`
> - **Multi-step flows:** `helper/analysis/workflows.md`
> - **Article hubs by in-degree:** `helper/analysis/dependency-clusters.md`
> - **Source articles per spec:** listed at bottom of each spec; resolve to `helper/figma_docs/articles/Figma Design/<slug>/content.md`

## 1. Purpose

Agent A read the Figma documentation corpus and produced a per-feature behavior spec for every feature in the original Tier 2 list. The output tells the build phase *what each feature does*, *how the user triggers it*, *what changes in the scene graph*, *what UI feedback appears*, and *what semantic event(s) the logger should emit*.

Agent A did **not** write code, did **not** design the engine, did **not** design UI. It is a researcher: it read and structured.

Subsequent expansion (post-Agent-A) extended coverage to all Figma Design features — frames-deep, color picker deep, gradients, image fill modes + adjustments, vector tools (Bend/Cut/Paint/Lasso/Variable-width/Shape-builder), boolean ops, auto-layout, components, variables, styles, prototyping, comments, sharing, libraries, branching, imports, exports, AI, ui-shell — using the same template.

## 2. Inputs

Agent A read from:

1. **`helper/figma_docs/articles/Figma Design/`** — 175 articles with `content.md` per article.
2. **`helper/analysis/feature-inventory.md`** — pre-synthesized exhaustive feature list. _(This file has since been deleted; the canonical replacement is `helper/analysis/feature-inventory-deep.md` which is Figma-Design-only, deeper, status-coded, and maps each feature to its spec file.)_
3. **`helper/analysis/workflows.md`** — multi-step flows.
4. **`plan/00-overview.md §2`** — the original functional scope filter. Only features in that list got a spec file at first pass. Subsequent expansion documented the broader Figma Design surface.
5. **`helper/extracted/ui-schema/`** (Agent B's output) — used for UI cross-references in `Related UI schema entries`.
6. **`CLAUDE.md`** — project overview context.

Agent A did not read articles from Dev Mode, Figma Draw, or Projects products — out of scope for the mock.

## 3. Output — actual structure

```
helper/extracted/features/
├── ai/                    (1)
├── alignment/             (9)
├── auto-layout/           (9)
├── boolean/               (5)
├── branching/             (1)
├── canvas-navigation/     (7)
├── clipboard/             (5)
├── color/                 (14)
├── comments/              (2)
├── components/            (7)
├── effects/               (6)
├── exports/               (1)
├── fills/                 (21)
├── find-replace/          (1)
├── frames/                (18)
├── history/               (2)
├── image/                 (2)
├── imports/               (1)
├── layers/                (11)
├── libraries/             (3)
├── pages/                 (4)
├── properties/            (8)
├── prototype/             (7)
├── region-tools/          (6)
├── selection/             (6)
├── shape-creation/        (7)
├── sharing/               (1)
├── styles/                (3)
├── text/                  (29)
├── transform/             (11)
├── ui-shell/              (13)
├── variables/             (4)
├── vector/                (24)
├── z-order/               (4)
└── index.md               (top-level index — canonical inventory)
```

**~250 spec files across 34 categories.** Each follows the §4 template.

The 12-category closed list from the original §5 is now a subset. Categories added during expansion: `ai`, `alignment` (split out of transform), `auto-layout`, `boolean`, `branching`, `color` (split out of properties), `comments`, `components`, `effects` (split out of properties), `exports`, `fills` (split out of properties), `find-replace`, `frames` (split out of region-tools), `image`, `imports`, `libraries`, `prototype`, `sharing`, `styles`, `ui-shell`, `variables`, `z-order`.

## 4. Output — per-feature spec template

```
# <Feature name>

- **Category:** <folder name>
- **One-line summary:** <what this feature lets the user do>

## Triggers (all equivalent paths)
- Keyboard shortcut, toolbar, right-click / context menu, main menu, right sidebar, layer panel, on-canvas handle.

## Preconditions
- <what must be true for the trigger to produce this behavior>

## Inputs (what the user provides during the action)
- <pointer drag, click, typed character, etc.>

## Behavior (step-by-step)
1. ...
2. ...
3. ...

## Outputs (scene-graph or state changes)
- Nodes created / modified / deleted, selection changes, non-scene state changes.

## UI feedback
- Cursor, canvas overlays, panels, toolbar, transient feedback.

## Side effects
- Undo stack, clipboard, focus.

## Related UI schema entries
- <links into helper/extracted/ui-schema/>

## Semantic event(s) candidate
- <proposed event name(s) and payload fields>

## Source articles
- <article slug>: <one-line why it's relevant>

## Notes / gaps
- <ambiguous, contradictory, or not-in-corpus items>
```

Fields that don't apply are omitted. `Semantic event(s) candidate` is a proposal — final logger taxonomy is consolidated as features are implemented in the engine.

## 5. Closed feature list (original Agent A run — historical)

The original closed list of ~60 features ran across 12 categories: canvas-navigation (5), selection (6), shape-creation (7), region-tools (3), transform (5), clipboard (5), properties (7), layers (7), pages (4), text (5), vector (9), history (2).

That list is now a **subset** of the current `helper/extracted/features/` corpus. For the canonical, current inventory:

- **`helper/extracted/features/index.md`** — every spec linked, grouped by category, with totals.
- **`helper/analysis/feature-inventory-deep.md`** — same features cross-referenced with FN / VO / DEF status and source articles.

Granularity rule (still applies): **one feature = one distinct user-facing action, irrespective of trigger.** Multiple triggers for the same action live in the `Triggers` field, not as separate files.

## 6. Batching strategy (executed)

- **Run order:** Agent B first (UI schema), Agent A second.
- **Original Agent A:** one fresh invocation per category, 12 batches in this order (easy → hard, building context for later batches):
  1. canvas-navigation
  2. selection
  3. shape-creation
  4. region-tools
  5. transform
  6. clipboard
  7. properties
  8. layers
  9. pages
  10. history
  11. text
  12. vector
- After all 12 batches, primary agent wrote `helper/extracted/features/index.md`.
- **Subsequent expansion:** primary agent wrote remaining ~190 specs across the 22 added categories directly (sub-agents were tried but blocked by sandbox; main session wrote them).

## 7. Agent A brief (per-category dispatch — historical)

Each batch dispatch included:

1. Role statement — "You are a feature researcher. You do not write code or design."
2. Category + feature list — the closed list from §5 for that category.
3. Inputs — paths from §2.
4. Output template — §4 verbatim.
5. Scope filter — `plan/00 §2` functional scope.
6. Granularity rule — §5's rule.
7. Semantic event naming guidance — snake_case, verb_noun.
8. Gap handling — "If docs don't cover a field, write `not covered in corpus` and list in `Notes / gaps`."
9. Quality checklist — §8 self-check before finishing.
10. Stop condition — "When every feature in the batch has a spec file, output a completion summary and stop."

## 8. Quality gates (applied to all specs)

A batch was accepted only if:

1. ✅ Every feature in the list exists as a file under the correct category folder.
2. ✅ Every file follows the §4 template.
3. ✅ Every file cites at least one source article.
4. ✅ Every file lists at least one semantic event candidate.
5. ✅ Semantic event names are snake_case `verb_noun`.
6. ✅ No feature file references invented behavior — gaps explicitly flagged with `[gap: not in corpus]`.
7. ✅ `Notes / gaps` present in every file.

## 9. Relationship to Agent B (executed)

- Agent B finished first.
- Agent A's `Related UI schema entries` field links into Agent B's output.
- Subsequent ui-schema extension (color-picker, context-menu, unsupported-toast, panel-scroll-behavior) was driven by gaps surfaced when expanding feature specs.

## 10. Relationship to engine implementation

- Feature specs feed directly into engine implementation under `mock/`:
  - `Outputs` sections → engine operation model.
  - `Inputs` sections → input handling.
  - `Semantic event(s) candidate` → logger taxonomy (consolidated incrementally).
- Implementation order driven by `feature-checklist.md` + `execution-map.md` (per `CLAUDE.md`), not by the original 12-category sequence.

## 11. Risks and known limits (post-mortem)

- **Workflow articles cross multiple features.** Minor duplication of quoted text across files is acceptable.
- **Inconsistent event-name proposals** — consolidated as features ship.
- **Feature granularity disputes** — original §5 closed the list; expansion split categories where coverage required (e.g. `properties/set-fill.md` split into `fills/*` + `color/*`).
- **Trigger completeness** — cross-checked against existing analysis docs.
- **"Gaps" on behavioral detail** — flagged in `Notes / gaps`; engine decides at implementation time.
- **Sub-agent sandbox blocking during expansion** — expansion required main-session writes (sub-agents could read articles but not write spec files).

## 12. Decisions (resolved)

- ✅ **Order:** Agent B first, then Agent A.
- ✅ **Batching:** fresh Agent A per category (12 invocations) for original list; main-session for expansion.
- ✅ **Granularity:** one feature = one user-facing action; multi-trigger in `Triggers` field.
- ✅ **Output format:** markdown, one file per feature, folder per category.
- ✅ **Closed feature list (original):** §5 (now superseded by `helper/extracted/features/index.md`).
- ✅ **Semantic event naming style:** snake_case verb_noun; consolidated incrementally during implementation.

## 13. Exit criteria — met

- ✅ User approved the §5 list at the time of Agent A run.
- ✅ User approved the §4 template.
- ✅ User approved the category order in §6.
- ✅ All decisions in §12 marked ✅.
- ✅ Output produced; subsequently expanded to broader scope.

## 14. Current entry points (post-completion)

For new contributors / agents looking at the feature corpus:

1. **`helper/extracted/features/index.md`** — canonical inventory, grouped by category.
2. **`helper/analysis/feature-inventory-deep.md`** — same features with FN/VO/DEF status and spec mapping.
3. **`helper/analysis/cross-feature-relationships.md`** — feature-to-feature relationships (dependency chains, cascading effects, mutually-exclusive contexts).
4. **`helper/analysis/figma-design-deep-index.md`** — per-article index for finding source material.
5. Per-feature behavior: read the spec at `helper/extracted/features/<category>/<feature>.md`.
