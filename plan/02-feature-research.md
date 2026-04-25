# Plan 02 — Feature Research (Agent A)

## 1. Purpose

Agent A reads the Figma documentation corpus and produces a per-feature behavior spec for every Tier 2 feature. The output tells the build phase *what each feature does*, *how the user triggers it*, *what changes in the scene graph*, *what UI feedback appears*, and *what semantic event(s) the logger should emit*.

Agent A does **not** write code, does **not** design the engine, does **not** design UI. It is a researcher: it reads and structures.

## 2. Inputs

Agent A reads from:

1. **`helper/figma_docs/articles/Figma Design/`** — 175 articles with `content.md` per article.
2. **`helper/analysis/feature-inventory.md`** — pre-synthesized exhaustive feature list. Primary navigation aid; Agent A still reads source articles for depth.
3. **`helper/analysis/workflows.md`** — multi-step flows. Useful when a feature is part of a larger workflow (e.g., "create frame from selection").
4. **`plan/00-overview.md §2`** — the functional scope filter. Only features listed there get a spec file. Visual-only elements from §3 do **not** get feature specs (they are covered by Agent B's UI schema and get no-op click behavior decided in `plan/03`).
5. **`extracted/ui-schema/`** (Agent B's output, optional) — used for UI cross-references in the `Related UI` field. Not a blocker: if a spec needs to reference a UI element and Agent B's output covers it, Agent A links. If not, Agent A describes the UI element inline and that reference can be updated later.
6. **`CLAUDE.md`** — project overview context.

Agent A does not read articles from Dev Mode, Figma Draw, or Projects products — out of scope for the mock.

## 3. Output — structure

```
extracted/features/
├── canvas-navigation/
├── selection/
├── shape-creation/
├── region-tools/
├── transform/
├── clipboard/
├── properties/
├── layers/
├── pages/
├── text/
├── vector/
├── history/
└── index.md
```

One markdown file per feature (`kebab-case.md`), grouped by category folder. `index.md` at top level lists every feature with a one-line summary and its category.

## 4. Output — per-feature spec template

```
# <Feature name>

- **Category:** <folder name>
- **One-line summary:** <what this feature lets the user do>

## Triggers (all equivalent paths)
- Keyboard shortcut: <keys or N/A>
- Toolbar: <button / dropdown entry or N/A>
- Right-click / context menu: <entry or N/A>
- Main menu: <path or N/A>
- Right sidebar: <button / section or N/A>
- Other (layer panel, on-canvas handle, etc.): <description or N/A>

## Preconditions
- <what must be true for the trigger to produce this behavior>
- <e.g., "selection must be non-empty", "cursor must be over canvas", "not currently in text edit mode">

## Inputs (what the user provides during the action)
- <e.g., "click coordinates on canvas", "drag path from pointer-down to pointer-up", "typed character", "dragged value in W input field">

## Behavior (step-by-step)
1. <what happens on trigger>
2. <intermediate state>
3. <commit state>

## Outputs (scene-graph or state changes)
- Nodes created: <type, default properties>
- Nodes modified: <which properties>
- Nodes deleted: <criteria>
- Selection changes: <yes/no, how>
- Non-scene state changes: <clipboard, mode, focus, undo stack, page>

## UI feedback
- Cursor: <change or no change>
- Canvas overlays: <bounding box, handles, guides appearing or disappearing>
- Panels: <which right-sidebar sections appear/update; left-panel updates>
- Toolbar: <tool highlight change>
- Transient feedback: <toast, cursor ghost, etc.>

## Side effects
- Undo stack: <adds entry? what's reversed?>
- Clipboard: <written, cleared, untouched>
- Focus: <moves to canvas, input, panel>

## Related UI schema entries
- <path or heading references into extracted/ui-schema/>

## Semantic event(s) candidate
- <proposed event name(s) and payload fields — Agent A proposes; plan/03 finalizes the taxonomy>
- <e.g., `create_rectangle { x, y, w, h, parent_id }` — trigger-agnostic>
- <or distinct events per trigger if trajectory semantics require: `drag_move_layer` vs `keyboard_move_layer`>

## Source articles
- <article slug>: <one-line why it's relevant>
- <article slug>: <one-line why it's relevant>

## Notes / gaps
- <anything ambiguous, contradictory across articles, or not covered>
```

Fields that do not apply are omitted, not left blank. `Semantic event(s) candidate` is intentionally a proposal — Agent A is not the final authority on the logger taxonomy; `plan/03` consolidates proposals from every feature file into a registry and resolves naming conflicts.

## 5. Closed feature list

Agent A produces one file per feature below. No new feature files outside this list without a scope decision.

### canvas-navigation (5)
- pan-canvas
- zoom-in-out
- zoom-to-fit
- zoom-to-100
- zoom-to-selection

### selection (6)
- click-select
- shift-click-add-to-selection
- shift-click-remove-from-selection
- drag-box-select
- select-all
- deselect

### shape-creation (7)
- create-rectangle
- create-line
- create-arrow
- create-ellipse
- create-polygon
- create-star
- place-image (user drops/picks an image, image layer is created)

### region-tools (3)
- create-frame
- create-section
- use-slice-tool — *flag: slice is coupled to export, which is visual-only. Agent A documents behavior as described in docs; actual export is a no-op. See gaps.*

### transform (5)
- move-layer (drag + arrow keys + right-sidebar X/Y)
- resize-layer (bounding-box handles + right-sidebar W/H)
- rotate-layer (corner rotation handle + right-sidebar rotation)
- scale-with-scale-tool (K)
- flip (horizontal + vertical — one file covering both)

### clipboard (5)
- copy
- cut
- paste (including paste-here at cursor position)
- duplicate (Cmd/Ctrl+D)
- delete

### properties (7)
- set-fill (add, remove, reorder, change color, change opacity, change blend mode)
- set-stroke (add, remove, change color, change weight, change alignment, change dash)
- set-effects (drop shadow, blur — add/remove/edit)
- set-opacity (layer-level)
- set-corner-radius (uniform + independent per corner)
- set-constraints (horizontal + vertical constraint dropdowns)
- set-visibility (eye icon toggle)

### layers (7)
- group-selection (Cmd/Ctrl+G)
- ungroup (Cmd/Ctrl+Shift+G)
- enter-group (double-click or Enter)
- exit-group (Esc or Shift+Enter)
- reorder-layer (drag in panel, Cmd+] / Cmd+[, bring-forward/send-back)
- rename-layer (Cmd/Ctrl+R or double-click label)
- delete-layer-from-panel

### pages (4)
- create-page
- switch-page
- rename-page
- delete-page

### text (5)
- create-text (T tool, click to place, click-drag to place with bounded width)
- edit-text (enter text editing mode + typing + caret navigation)
- select-text-range (within a text layer)
- set-text-properties (font family, weight, size, line-height, letter-spacing, color via right-panel Typography + Fill)
- commit-text (Esc or click outside)

### vector (9)
- use-pen-tool (create vector network — click for corner point, click-drag for curved point, close by hovering start or press Enter)
- use-pencil-tool (create freehand stroke — drag to draw; stroke simplification)
- enter-vector-edit-mode (Enter on selected vector)
- exit-vector-edit-mode (Enter / Esc / Done)
- add-vector-point (click on existing path segment in edit mode)
- move-vector-point (drag a point in edit mode)
- delete-vector-point (select point + Delete)
- toggle-vector-handle (convert between corner / mirror-angle / mirror-length / no-handle)
- close-open-vector-path (hover starting point, click — or in edit mode)

### history (2)
- undo
- redo

**Total: ~60 feature files.**

Granularity rule applied throughout: **one feature = one distinct user-facing action, irrespective of trigger.** Multiple triggers for the same action live in the `Triggers` field, not as separate files. If a trigger produces a semantically different trajectory that matters to the logger (e.g., drag-move vs keyboard-move), Agent A proposes two candidate events inside a single feature file; `plan/03` decides whether they split.

## 6. Batching strategy

- **Run order:** Agent B first (UI schema), Agent A second. Agent A uses Agent B's output as optional cross-reference in the `Related UI schema entries` field.
- **Batch per category:** one fresh Agent A invocation per category folder (12 invocations total). Fresh agent per batch for context isolation — no prior-batch state leaking between invocations.
- **Category order (easy → hard, builds context for later batches):**
  1. canvas-navigation (simplest, no selection model needed)
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
  12. vector (hardest, largest, most docs to digest)
- After all 12 batches: I write `extracted/features/index.md` from the generated files (meta-pass, not an Agent A run).

## 7. Agent A brief (per-category dispatch)

Each batch dispatch includes:

1. **Role statement** — "You are a feature researcher. You do not write code or design."
2. **Category + feature list** — the closed list from §5 for that category.
3. **Inputs** — paths from §2. Include `extracted/ui-schema/` as optional cross-reference.
4. **Output template** — §4 verbatim.
5. **Scope filter** — `plan/00 §2` functional scope. Every feature in this plan's §5 list is in scope by definition; Agent A does not re-decide scope.
6. **Granularity rule** — §5's "one feature = one action, multi-trigger stays in Triggers field".
7. **Semantic event naming guidance** — snake_case, verb_noun, e.g. `create_rectangle`, `drag_move_layer`. Proposal only, not final.
8. **Gap handling** — "If docs don't cover a field, write `not covered in corpus` and list in the `Notes / gaps` section."
9. **Quality checklist** — §8 self-check before finishing.
10. **Stop condition** — "When every feature in the batch has a spec file, output a completion summary and stop."

## 8. Quality gates

A batch is accepted only if:

1. Every feature in the batch's list exists as a file under the correct category folder.
2. Every file follows the §4 template (all applicable fields filled, omitted fields noted).
3. Every file cites at least one source article.
4. Every file lists at least one semantic event candidate.
5. Semantic event names are snake_case and follow the `verb_noun` pattern (minor variations allowed).
6. No feature file references a concept out of `plan/00 §2` scope (no feature silently pulls in auto layout, components, variables, etc.).
7. `Notes / gaps` is present in every file (may say "none").

I (primary agent) run these gates on each batch's output before launching the next batch.

## 9. Relationship to Agent B

- **Agent B must finish first.** Agent A's `Related UI schema entries` field links into Agent B's output. Running Agent A before Agent B means those links are all unfillable.
- Agent A still works if Agent B's output is incomplete or has gaps — Agent A writes an inline description of the UI element in that case, and flags it for post-hoc linking once Agent B's gap is filled.
- The two agents do not communicate. I am the only integrator.

## 10. Relationship to `plan/03` (engine architecture)

- Feature specs feed directly into `plan/03`:
  - `Outputs` sections inform the engine's operation model (what ops the engine must support).
  - `Inputs` sections inform input handling (what raw events feed which operations).
  - `Semantic event(s) candidate` sections are consolidated into the final logger taxonomy in `plan/03`. Naming conflicts are resolved; duplicates collapsed; trajectory-distinctions (drag vs keyboard) decided.
- `plan/03` is blocked on `extracted/features/` being complete (at least the core categories) — we do not write the engine architecture before we know what operations it must host.

## 11. Risks and known limits

- **Workflow articles cross multiple features.** A single article can describe "create frame + convert to section + mark ready for dev" in one flow. Agent A is instructed to extract the feature-relevant slice and cite the article; minor duplication of quoted text across files is acceptable.
- **Inconsistent event-name proposals.** Agent A across 12 batches may propose `move_layer` in one and `layer_move` in another. I consolidate these in `plan/03`.
- **Feature granularity disputes.** The §5 list freezes granularity. If Agent A identifies a feature that seems to need splitting (e.g., paste vs paste-here-at-cursor), it flags it in `Notes / gaps` and proposes a split — but does **not** create new files. We decide together whether to expand the §5 list.
- **Trigger completeness.** Agent A can miss a trigger (e.g., forgets the context menu entry). Mitigation: cross-checking against `helper/analysis/feature-inventory.md` which is exhaustive on triggers.
- **"Gaps" on behavioral detail.** Some features have vague docs (e.g., exact pencil-stroke simplification algorithm). Agent A is allowed to write `algorithmic detail not specified — engine decision` rather than invent. `plan/03` handles the engine decision.

## 12. Decisions

- ✅ **Order:** Agent B first, then Agent A.
- ✅ **Batching:** fresh Agent A per category (12 invocations).
- ✅ **Granularity:** one feature = one user-facing action; multi-trigger in `Triggers` field.
- ✅ **Output format:** markdown, one file per feature, folder per category.
- ✅ **Closed feature list:** §5 (expandable only with a scope decision).
- ✅ **Semantic event naming style:** snake_case verb_noun; Agent A proposes, `plan/03` finalizes.
- Open: none at dispatch time.

## 13. Exit criteria

This plan is done when:

- User approves the §5 feature list as-is or with edits.
- User approves the §4 template.
- User approves the category order in §6.
- All decisions in §12 are ✅.

Dispatching Agent A happens after Agent B finishes and its output passes `plan/01`'s quality gates.
