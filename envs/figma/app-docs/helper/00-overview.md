# Plan 00 — Overview

> **Status (current):** Planning + extraction phases are complete. Code lives under `mock/`. The current source of truth for what to build is `feature-checklist.md` + `execution-map.md` (per `CLAUDE.md`). This plan is kept as historical context; the closed feature list and Tier-2-only language below has been **superseded** by the broader research output under `helper/extracted/`.

## 1. Purpose

Original purpose: a single entry point for the project's planning + extraction strategy. Reading this document plus the other `plan/*.md` files was meant to be enough for a new contributor (human or agent) to understand *what* we are building, *how* we plan to build it, and *why* this particular order.

What this plan still gives you:
- The **two-scope rule** (functional vs visual) — still applicable.
- The **guiding principles** — still applicable.
- The **out-of-functional-scope baseline** — still useful, but read with the **FN / VO / DEF** status taxonomy in `helper/analysis/feature-inventory-deep.md` as the more accurate current view.

## 2. What we are building

- **A pixel-accurate mock of Figma Design** + an **action logger** that emits raw events + semantic user-intent events, consumable by a downstream CUA test harness. Trajectories matter (drag-move ≠ copy-paste-move); the logger must distinguish them.
- **Code lives in `mock/`** (Vite + React + TS).
- **Customer-driven feature list** is in `feature-checklist.md`. Wave-by-wave order is in `execution-map.md`. These two files supersede the closed feature list previously in §5 of this document.

### Two kinds of scope — do not conflate

This project has two distinct scopes that must be tracked separately:

- **Functional scope** — features whose *behavior* we implement.
- **Visual (UI) scope** — UI elements whose *appearance* we render.

**Visual scope is a strict superset of functional scope.** UI elements for non-implemented features must still render with correct position, icon, and default appearance — without them the mock does not look like Figma.

The current spec corpus in `helper/extracted/features/` is broader than the original Tier 2 list. It documents every Figma Design feature **as if everything will be implemented**, with each spec carrying an FN / VO / DEF status (see `helper/analysis/feature-inventory-deep.md`):

- **FN** = functional in scope; engine + UI + logger built.
- **VO** = visual-only stub; UI rendered, click routes through `extracted/features/ui-shell/unsupported-feature-toast.md`.
- **DEF** = deferred; spec exists, implementation later.

The visual surface remains a strict superset of the functional surface — every VO and DEF feature still renders its UI element, just non-functionally.

## 3. Out of functional scope (UI still rendered)

The original §3 list described items visually rendered but non-functional. The mapping today:

- Items below correspond largely to the **VO** status in `feature-inventory-deep.md`. Read that doc for the canonical, per-feature status.
- Several items originally listed (Auto layout, Boolean ops, Components / Variables / Styles, Sections, etc.) **now have full specs under `helper/extracted/features/`**. Whether to implement them functionally is a wave-level decision in `execution-map.md`, not a hard "out of scope" verdict.

Original visual-only enumeration (still useful as a minimum-render checklist):

- Dev Mode toggle
- Figma Draw toggle
- Prototype tab body (tab itself renders; body content is empty / placeholder)
- Sub-header buttons not in current wave (Mask, Create component, Boolean ops icons)
- Assets tab body, Variables modal entry
- Auto layout panel entries (when not implemented in current wave)
- Comment / Annotation / Measurement tools (when not in current wave)
- Actions menu (`Cmd K`)
- Rulers, guides, pixel grid toggles in Zoom / view dropdown
- Style swatch slots in Fill / Stroke / Effects sections (when styles not implemented yet)
- Libraries modal
- Branching / version history / Share / Present buttons
- AI features
- Export trigger (config can be edited; clicking Export is no-op)
- Advanced text features (when not implemented)

Every VO click should route through `helper/extracted/features/ui-shell/unsupported-feature-toast.md` rather than silently failing — robustness requirement.

### 3a. Fully out — not rendered at all

Things outside default Figma Design chrome:

- Dev Mode-only overlays
- Prototype noodles / flow start badges (Prototype mode chrome)
- Draw mode secondary toolbars
- FigJam, Figma Buzz, Figma Slides UI
- View-only / Dev-seat chrome variants — we always render the edit-access view

### 3b. Scope guardrails

- Functional drift outside the current wave is recorded as an open question, not silently implemented.
- Adding visual UI for a VO item is **not** scope drift — it is the required baseline.
- VO clicks emit `unsupported_feature_clicked` events for CUA observability.

## 4. Guiding principles

1. **UI fidelity is driven by the docs corpus**, not guesswork. Every UI element's look + states traces back to an article image or explicit spec in `helper/figma_docs` / `helper/analysis` / `helper/extracted`. When the corpus doesn't cover a state, the spec flags `[gap: not in corpus]` rather than inventing.
2. **UI completeness.** Rendered UI reflects the full real-Figma chrome including elements for non-functional features.
3. **UI + engine + logger are co-developed per FN feature**, never in sequence.
4. **Scope discipline.** Drift is recorded; visual-only additions are baseline.
5. **Vertical slices over horizontal layers.** Each slice ships one feature end-to-end.
6. **Docs are the source of truth for behavior; images are the source of truth for appearance.**
7. **Honesty over polish.** Gaps, risks, unknowns are recorded explicitly. No fabrication.

## 5. Strategy — phases (status)

| Phase | What happened | Artifacts | Status |
|---|---|---|---|
| **1. Planning** | Wrote `plan/00-04` | `plan/*.md` | ✅ done (this doc + 01 + 02 retained as historical) |
| **2. Extraction** | Agent B (UI schema) + Agent A (per-feature) ran; user expanded substantially to ~250 feature specs across 34 categories. | `helper/extracted/ui-schema/` + `helper/extracted/features/` | ✅ done |
| **3. Engine + first slice** | Vite + React + TS app under `mock/`; canvas + selection + shapes + transform + clipboard + history scaffolded. | `mock/` | 🔄 in progress |
| **4. Feature-by-feature slicing** | Iterate per `execution-map.md`. | Incremental commits in `mock/` | 🔄 in progress (recent: frame nesting, drag-into-frame, parent-bounds overlay) |

Phase boundaries were originally hard gates. Phases 1+2 are closed; phases 3+4 are interleaved per wave.

## 6. Roles (historical)

| Role | Original responsibility | Current status |
|---|---|---|
| **Agent A — Feature researcher** | Per-feature behavior specs | ran; output expanded by user |
| **Agent B — UI schema researcher** | UI region schema | ran; output extended with deeper regions (color-picker, context-menu, panel-scroll, unsupported-toast) |
| **Primary agent (me)** | Orchestrate, integrate, build | builds in `mock/`, references `helper/extracted/` |
| **User** | Approve, scope-guard, fill gaps with screenshots | drives wave priorities via `feature-checklist.md` |

## 7. Artifact map (current)

```
apps/figma/                         the figma app within cua-bench
├── CLAUDE.md                       app-level agent guide (source of truth for scope)
├── app-docs/
│   ├── feature-checklist.md        customer feature list (current source of truth)
│   ├── execution-map.md            wave-by-wave implementation order + session log
│   └── architecture.md             engine, scene graph, ops, logger, UI shell
├── helper/
│   ├── 00-overview.md              ← this file: scope, principles, how to use the corpus
│   ├── 01-ui-schema-extraction.md  ← UI schema reference doc
│   ├── 02-feature-research.md      ← feature spec reference doc
│   ├── figma_docs/                 175 Figma Design articles + images (read-only)
│   ├── analysis/                   synthesized analysis docs:
│   │   ├── ui-map.md                                (UI3 spatial layout)
│   │   ├── panel-states.md                          (per-panel state rules)
│   │   ├── workflows.md                             (multi-step user flows)
│   │   ├── dependency-clusters.md                   (article-graph hubs + tier order)
│   │   ├── figma-design-deep-index.md               (per-article index)
│   │   ├── feature-inventory-deep.md                (FD-only feature catalog with FN/VO/DEF + spec map)
│   │   └── cross-feature-relationships.md           (feature-to-feature relationships)
│   ├── extracted/
│   │   ├── ui-schema/              UI region schema + state matrix + scroll/toast docs
│   │   └── features/               ~250 per-feature specs across 34 categories
│   └── open-source-example/        OpenPencil reference (read-only)
└── mock/                           Vite + React + TS application
```

## 7a. How to use this material — workflows for implementation agents

This section is the **practical entry guide** for an agent (or human) implementing a feature in `mock/`. It says *which file to read first*, *which to read next*, and *what to do at each branch*. It is not a summary of `helper/` contents (that's §7 above and `01-…` / `02-…`); it's a how-to.

**Golden rule:** read specs before writing code. The corpus has done the research; do not re-derive behavior from intuition or live Figma.

### Workflow 1 — Implementing a feature

Given: feature X in `feature-checklist.md` is in the current wave.

1. **Find the spec.** Look up the feature in `helper/extracted/features/index.md`. Click through to the spec file at `helper/extracted/features/<category>/<feature>.md`.
2. **Read the spec sections in this order:**
   - **Triggers** — every input path the user can take (shortcut, toolbar, panel, right-click, drag).
   - **Preconditions** — guards that gate the behavior.
   - **Inputs** — what raw events flow in.
   - **Behavior** — step-by-step what the engine does.
   - **Outputs** — exact scene-graph / selection / state mutations.
   - **UI feedback** — what re-renders.
   - **Side effects** — undo stack, clipboard, focus.
   - **Semantic event(s) candidate** — the logger event(s) to emit.
3. **Cross-link to UI schema.** Each spec lists `Related UI schema entries` pointing to `helper/extracted/ui-schema/regions/*.md` (and `state-matrix.md`, `chrome.md`, etc.). Read those before adding UI controls.
4. **Source articles for nuance.** When a spec is ambiguous or the engine choice is non-obvious, read the listed `Source articles` at `helper/figma_docs/articles/Figma Design/<slug>/content.md`. This is the original docs corpus.
5. **Cross-feature interactions.** Before implementing, scan `helper/analysis/cross-feature-relationships.md` for the relevant cluster. Cascading side effects (e.g. "move layer ⇒ snap guides recompute") are listed there.
6. **Implement engine + UI + logger together.** Per `plan/00 §4` principle 3, no feature is "done" until all three exist and pass.

### Workflow 2 — Adding a UI element (visual fidelity pass)

Given: a region or element renders incorrectly, or you're adding a missing button / panel section.

1. **Find the region:** `helper/extracted/ui-schema/regions/<region>.md`. The five primary regions are `toolbar`, `left-navigation`, `right-properties`, `canvas-overlays`, `floating-overlays`.
2. **Two deep regions** for surfaces that needed extra detail:
   - `helper/extracted/ui-schema/regions/color-picker.md` — full color picker anatomy (14 sub-areas).
   - `helper/extracted/ui-schema/regions/context-menu.md` — right-click menus per selection / context.
3. **Visibility rules:** consult `helper/extracted/ui-schema/state-matrix.md` for which right-panel sections appear per selection type. The narrative companion is `helper/analysis/panel-states.md` (longer prose).
4. **Top chrome:** `helper/extracted/ui-schema/chrome.md` (file-name bar, avatar stack, Share, Present, branch indicator).
5. **Scroll behavior:** `helper/extracted/ui-schema/panel-scroll-behavior.md`.
6. **Reference images:** every region file lists images under `helper/figma_docs/articles/Figma Design/<slug>/images/`. Open the PNG when descriptions aren't enough.

### Workflow 3 — Handling a VO (visual-only) click

UI element is in scope visually but its feature is not implemented (VO status).

1. **Do not silent-noop.** Silent failures are CUA-invisible.
2. Route through `helper/extracted/features/ui-shell/unsupported-feature-toast.md` — it specifies the toast format, semantic event, and registry pattern.
3. Add the element's id → human label mapping in the registry (see `helper/extracted/ui-schema/unsupported-toast.md` for sample mappings).
4. Toast text: `"{Feature name} is not yet supported"`.

### Workflow 4 — Encountering `[gap: not in corpus]`

A spec field flagged as a gap means the corpus didn't cover it.

1. **Do not fabricate.** Implementer's choice is allowed but record it.
2. Surface to user with: spec path, gap location, and a proposed default (with rationale).
3. If user picks a default, document the choice in the implementation (comment + commit message). Do not retroactively edit the spec to claim the corpus said so.

### Workflow 5 — Naming a semantic event

1. Each spec has a `Semantic event(s) candidate` section. Use that as the starting name.
2. Convention: snake_case `verb_noun`. Multi-trigger features use a single event with a `trigger` field (e.g. `move_layer { trigger: "drag" | "arrow_keys" | "panel_input" }`) UNLESS trajectory distinction matters for CUA.
3. Cross-check sibling specs in the same category for consistency. If the candidate name conflicts with an existing one, harmonize and update both.
4. Final taxonomy is consolidated incrementally as features ship — see `app-docs/architecture.md` for the live registry.

### Workflow 6 — Looking up a Figma feature you've never seen

1. **First stop:** `helper/analysis/figma-design-deep-index.md` — 175 articles grouped by breadcrumb section, with one-line summaries.
2. **For "is this in scope?":** `helper/analysis/feature-inventory-deep.md` — every feature with FN / VO / DEF status and a link to its spec file.
3. **For "where do other features connect to this one?":** `helper/analysis/cross-feature-relationships.md`.
4. **For "what's the umbrella article on topic X?":** `helper/analysis/dependency-clusters.md` lists hub articles by in-degree.

### Workflow 7 — Designing a multi-step user flow

1. **`helper/analysis/workflows.md`** documents canonical multi-step flows from the corpus (e.g. masks, bulk rename, auto-layout setup, vector network creation).
2. Cross-reference per-feature specs for the individual steps.

### Quick-reference — which file answers which question

| Question | File |
|---|---|
| "What features exist in Figma Design?" | `helper/analysis/feature-inventory-deep.md` |
| "What's in article X?" | `helper/analysis/figma-design-deep-index.md` |
| "How does feature Y behave?" | `helper/extracted/features/<cat>/<Y>.md` |
| "Where does UI element Z live, what states?" | `helper/extracted/ui-schema/regions/*.md` + `chrome.md` |
| "Which sections show for selection type S?" | `helper/extracted/ui-schema/state-matrix.md` |
| "What's in the color picker?" | `helper/extracted/ui-schema/regions/color-picker.md` |
| "Right-click menu for context C?" | `helper/extracted/ui-schema/regions/context-menu.md` |
| "What's the toast for unsupported buttons?" | `helper/extracted/features/ui-shell/unsupported-feature-toast.md` + `helper/extracted/ui-schema/unsupported-toast.md` |
| "How do features interact?" | `helper/analysis/cross-feature-relationships.md` |
| "What multi-step flows exist?" | `helper/analysis/workflows.md` |
| "Which articles are hubs?" | `helper/analysis/dependency-clusters.md` |
| "Where's the source article for X?" | bottom of every spec under `helper/extracted/features/` |
| "How does the engine work?" | `app-docs/architecture.md` |
| "What's the current wave?" | `execution-map.md` |
| "What does the customer want?" | `feature-checklist.md` |

## 8. Decision log

### Decided / resolved

- **Scope:** broader than original Tier 2. Source of truth = `feature-checklist.md` + `execution-map.md`. Full possible scope documented in `helper/extracted/features/`.
- **Out of scope:** see VO + DEF status in `feature-inventory-deep.md`.
- **Build order:** vertical slices, per-wave per `execution-map.md`.
- **UI fidelity source:** corpus + extracted specs, not live Figma inspection.
- **Tech stack:** Vite + React + TS (under `mock/`).
- **No-op UI click behavior:** route through `unsupported-feature-toast.md` (toast with feature name).
- **Logger taxonomy:** semantic event candidates per spec under `helper/extracted/features/<cat>/<feature>.md` — consolidated as features are implemented.

### Open / wave-level

- **Per-wave functional scope** — decided in `execution-map.md` as waves are planned.
- **Per-wave UI fidelity passes** — decided per feature when implementing.

## 9. Review cadence (current)

- Per wave (per `execution-map.md`): user reviews wave output, approves or sends back.
- Per feature within a wave: implement engine + UI + logger together; commit when feature is end-to-end.
- Mid-wave questions: raised immediately, no silent assumptions.
- Reference docs (`helper/00-02`): kept current (artifact map + workflow guide). Update when corpus or analysis changes.
