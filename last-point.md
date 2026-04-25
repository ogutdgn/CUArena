# Last Point — Handoff Note

**Purpose:** This file is read by the next chat session so it can resume seamlessly without re-discovering context. Read this first, then `CLAUDE.md`, then the `plan/` + `extracted/` directories.

**Date of last activity:** 2026-04-25.

---

## How we work together (sticky)

The user prefers:

1. **Step-by-step collaboration, not big outputs.** Before writing a long doc, propose an outline; get approval; then write. Before writing a section, confirm its scope.
2. **One section at a time, Q&A style.** For `plan/03-engine-architecture.md`: walk through each outline section one-by-one, Q&A, confirm every decision, THEN the doc is written. NOT "write a full draft, ask for edits." NOT "batch write".
3. **Realistic answers, not people-pleasing.** Challenge the user's claims if needed, give real cost estimates, retract if wrong. Do not glaze over risks or trade-offs.
4. **Turkish in conversation, English in docs.** The user writes Turkish; planning docs + extracted specs are in English to match existing `helper/analysis/` style.
5. **Scope discipline.** Tier 2 scope is locked; do not pull in out-of-scope features. Visual-only UI elements are rendered but non-functional.
6. **Analyze before deciding** (memory rule, 2026-04-25). When given decision authority, mine the project's extracted specs and OpenPencil reference code FIRST. Do not default to generic "best practice" picks. The user explicitly called this out twice in this session — it cost an architectural retraction.
7. **Memory directory** at `C:\Users\ogutd\.claude\projects\C--Users-ogutd-OneDrive-Desktop-new-coding-figma-mock\memory\` — consult `MEMORY.md` for user profile + working-style notes that apply across sessions.
8. **Concise responses.** Short focused answers; skip enumerations and nice-to-haves unless asked.

---

## Where we are

### ✅ Completed planning work

- `plan/00-overview.md` — strategy, scope, guiding principles, decision log
- `plan/01-ui-schema-extraction.md` — Agent B spec
- `plan/02-feature-research.md` — Agent A spec with closed feature list (65 features, 12 categories)
- `extracted/ui-schema/` — 9 files, 1460 lines (UI schema, all regions)
- `extracted/features/` — 66 files (65 specs + index), 3560 lines (12 categories)

### ✅ Completed plan/03 walk-through (Q&A only — doc not yet written)

- §1 — Purpose
- §2 — Architecture at a glance (Command pattern + state separation)
- §3 — Scene graph data model (full taxonomy + storage shape + 5 micro-decisions)
- §4 — Operation model + logger event schema (4 sub-sections §4a-§4d)
- §5 — Input pipeline (4 sub-sections §5a-§5d)

### ⏳ Currently next

- §6 — State partitioning (scene graph vs viewport / selection / mode / tool / clipboard)
  - Will further address cross-cutting concern #5 (viewport vs scene-graph state boundary; partially started in §4a's `undoable` flag)

### ⏳ Remaining plan/03 sections (not yet started)

- §7 — Logger architecture (raw stream + semantic registry + storage + export)
- §8 — Undo / redo (will resolve 4 deferred questions from §4d)
- §9 — Visual-only UI click behavior policy
- §10 — Tech stack (framework, build tool, state mgmt, canvas rendering)
- §11 — Font + icon strategy
- §12 — Theme / token strategy
- §13 — Project layout
- §14 — Performance / scale
- §15 — Open questions

### ⏳ After plan/03

- `plan/04-build-phases.md` — Tier 2 vertical slice ordering. Blocked on plan/03.

---

## plan/03 §1-§5 LOCKED DECISIONS (detailed)

These are settled. Do NOT re-open unless the user asks.

### §1 — Purpose

This document decides how the engine works internally: data shape, op model, input flow, state partition, logger, undo, tech stack, layout, performance — everything required before code begins.

### §2 — Architecture at a glance

**Core loop (locked):**

```
user input → tool resolves op → op applies to scene graph
                                       ↓
                             emits semantic event (logger)
                                       ↓
                             pushes inverse closure (undo)
                                       ↓
                                  view re-renders
```

**State separation (locked):**
- Scene graph = the ONLY undoable state
- Viewport, selection, active mode, active tool, clipboard, current page = NOT on undo stack

**Pattern justification:** Walked through 4 alternatives (direct mutation, command pattern, pure reducer, event sourcing). Command pattern + hybrid state chosen because: logger guarantee comes free (single dispatch site), undo is natural by-product (inverse closure), avoids structural-sharing perf cost of pure reducer at 60fps drag, OpenPencil pattern is proven.

### §3 — Scene graph data model

#### §3a — Storage shape (locked)

**Decision: Monolithic flat `SceneNode` interface + Zod runtime validator + per-type behavior modules with registry dispatch.**

```typescript
interface SceneNode {
  // common (every node)
  id: string
  type: NodeType   // 'rectangle' | 'ellipse' | 'frame' | ...
  parentId: string | null
  childIds: string[]   // empty for leaf, populated for containers
  name: string
  x, y, width, height: number
  rotation: number
  visible: boolean
  opacity: number
  locked: boolean
  fills: Fill[]
  strokes: Stroke[]
  effects: Effect[]
  // type-specific (all optional, type tag narrows)
  cornerRadius?: number | { tl, tr, bl, br }
  arcStartAngle?, arcEndAngle?, innerRadius?: number
  p1?, p2?: Point
  endCap?: 'none' | 'arrow'
  sides?, points?, pointInnerRatio?: number
  text?: string
  styleRuns?: StyleRun[]
  fontFamily?, fontSize?, fontWeight?, lineHeight?, letterSpacing?: any
  vectorNetwork?: VectorNetwork
  clipsContent?: boolean
  title?: string
}
```

**Why monolithic** (chosen over discriminated union after research):
- Most code paths operate on common fields (move, resize, opacity, fill, render selection box) — no narrowing tax
- Per-type branching isolated to behavior modules
- Closure-based undo with state capture is trivial on uniform shape
- OpenPencil prod evidence: `packages/core/src/scene-graph/index.ts:303-430` uses ~130-field flat interface
- Adding new types = optional field + behavior module (one new file), no switch-statement sprawl
- TypeScript safety loss mitigated by Zod runtime validation + type guards (`isText`, `isVector`)

**Validator pattern (locked):**

Zod chosen over hand-written. Schema = single source of truth, TypeScript types derived via `z.infer`. Validation invoked at boundaries (NOT on hot path):
- `createNode()` — every new node
- `paste()` / `loadFile()` — untrusted data
- `undo()` / `redo()` restore — sanity check
- `updateNode()` — DEV MODE only (assertion-style; eliminated in prod build)

`updateNode` during a 60fps drag MUST NOT validate (perf).

**Behavior dispatch (locked):**

```typescript
// nodes/rectangle.ts
export const RectangleBehavior = { render, hitTest, getBounds, defaultProps }

// central registry
const behaviors: Record<NodeType, NodeBehavior> = { rectangle: ..., ellipse: ..., ... }
behaviors[node.type].render(node, ctx)
```

This solves OpenPencil's documented pain (30+ scattered switch statements).

#### §3b-§3f — Five micro-decisions (locked)

| # | Question | Decision | Why |
|---|---|---|---|
| 1 | Image: own type or rectangle+image fill? | **Rectangle + image fill** | Figma + OpenPencil both do this. Image fill works on any shape (ellipse, polygon, vector) → keeps geometry generic. Layer panel rule: if `fills[0].type === 'image'` → display "Image" label/icon. |
| 2 | Arrow: own type or line+endCap? | **Line + `strokes[0].endCap`** | Identical 2-point geometry. User can toggle endCap to switch line↔arrow naturally (no type change). OpenPencil has no arrow type. Logger event still distinguishes (`create_arrow` vs `create_line`) at the semantic layer. |
| 3 | Group bounds: stored or computed? | **Hybrid — position stored, w/h computed** | Position stored (drag of group needs explicit x/y). Width/height computed from union of childIds bounds (auto-correct on child change, no cache invalidation bugs). Frame and Section keep stored bounds (user-resizable); only Group computes. |
| 4 | Slice: real node or overlay? | **Real node, type='slice', `fills`/`strokes`/`effects` forbidden in Zod schema** | Render: invisible by default; dashed outline only when slice tool active OR hover/selected. Hit-test: only selectable when slice tool active (Figma behavior). Z-order present but visually no-op. |
| 5 | Locked field behavior? | **Field exists, default false, NO behavior** | Lock UI toggle is plan/00 §3 visual-only (no-op). Therefore `locked: true` never set by user. Field present for forward-compat (future tier, .fig import). Locked nodes still selectable, draggable, editable. |

#### §3 — Cross-cutting (locked from research)

- **Coordinates: parent-relative.** Absolute computed by chain-multiplying matrices up to root (OpenPencil pattern, `coordinate.ts:5-22`).
- **Z-order: `childIds` array order.** No explicit `zIndex` field.
- **Identity: ID-based references.** `parentId` and `childIds` are string IDs, not nested objects. Flat node map: `Map<id, SceneNode>`.
- **Text representation: flat string + sparse `styleRuns: [{start, length, style}]`** for per-range overrides.
- **Vector representation: vertices + segments (with bezier tangent handles) + regions.** Full network supports branching.

### §4 — Operation model + logger event schema

#### §4a — Op shape (locked)

**Two outputs from one commit point:**
- **Closure pair** for undo: `{forward: () => apply(after), inverse: () => apply(before)}`
- **Structured record** for logger: `OpRecord` (see §4b shape)

**Capture timing:** at gesture-end (commit). Drag does NOT push to undo per mousemove; only `graph.update` runs during drag, undo entry assembled on pointer-up. OpenPencil pattern, `editor/undo.ts:32-57`.

**Capture content:** only changed fields, op-specific shape. Examples:
- `move_layer`: `Map<id, {x, y}>`
- `resize_layer`: `Map<id, {x, y, width, height}>`
- `set_fill_color`: `Map<id, {fills: Fill[]}>`
- `paste`: full node snapshots
- `delete`: full node snapshots (for undelete)

**View-state ops:** Same `OpRecord` shape with `undoable: false` flag. `commitOp()` skips undo push but still emits to logger. Single code path, single mental model.

#### §4b — Logger event schema (locked)

```typescript
interface LoggerEvent {
  // identity
  type: string                    // 'move_layer', ...
  ts: number                      // ms epoch
  seq: number                     // monotonic, tie-break for same ts
  schema_version: 1               // bump only on breaking change

  // context
  trigger: TriggerKind            // nested object — see below
  active_page_id: string
  active_tool: ToolName
  mode?: 'text_edit' | 'vector_edit'   // omit when in default design mode

  // action
  layer_ids?: string[]
  new_layer_ids?: string[]
  params?: Record<string, any>

  // state delta (for undoable ops)
  before?: any
  after?: any
  undoable: boolean
}
```

**Trigger field is a nested object**, not a flat enum:
```typescript
{ kind: 'drag' }
{ kind: 'drag', modifiers: ['alt'] }                  // duplicate-by-drag
{ kind: 'drag', modifiers: ['shift'] }                // axis-constrain
{ kind: 'click', source: 'canvas' }
{ kind: 'click', source: 'layers_panel' }
{ kind: 'shortcut', combo: 'cmd+d' }
{ kind: 'panel', region: 'right_properties', control: 'fill_swatch' }
{ kind: 'menu', source: 'context' | 'main' }
{ kind: 'scrub', control: 'opacity_slider' }
{ kind: 'type' }
{ kind: 'system', reason: 'auto_empty_text' }
```

`kind` enum is small (~8 values). Detail under `kind` is flexible.

**Naming convention:** `verb_noun` snake_case throughout. `layer_ids` plural even for single-layer ops (consistency).

**`before`/`after` optional**, op type decides shape. Schema does not enforce (helper per op type populates).

**`schema_version: 1`** — bump only on breaking change (rename/removal/type change). Adding field is non-breaking.

#### §4c — Batching / coalescing (locked)

| Op type | Logger emits | Undo entry |
|---|---|---|
| Drag (move/resize/rotate/scale) | 1 event @ commit (no intermediate semantic) | 1 entry @ commit |
| Typing | 1 event/keystroke | 1 entry/burst (~500ms inactivity) |
| Property scrub (slider/numeric) | 1 event @ commit (release/blur) | 1 entry @ commit |
| Pen tool | 1 `pen_add_point`/click + 1 `create_vector_with_pen` @ commit | 1 entry (compound) |
| Pencil tool | 1 event @ commit (simplified path) | 1 entry @ commit |
| Multi-step compound (shape draw = create+resize) | 1 event @ commitBatch | 1 entry (compound) |
| Cancel (Esc, tool switch mid-gesture) | 1 `*_cancelled` event | 0 (revert temp state) |

**Key principle:** Trajectory data lives in raw event stream; semantic stream emits only at commit. Exception: typing (per-keystroke logger reflects intent) and pen (per-point reflects discrete clicks).

**Multi-step API:** `beginBatch(label)` ... internal ops ... `commitBatch()` — collapses to single logger event AND single undo entry.

**Coalescing parameters:** in `engineConfig` (test-overridable). Default: typing burst window 500ms.

#### §4d — Open question resolutions for §4 scope (locked)

| Question | Decision |
|---|---|
| Smart duplicate offset default | `{dx: 10, dy: 10}` for first Cmd+D; subsequent Cmd+D uses last manual offset |
| Snap guide event emission | NO. Snap is visual feedback. Final snapped position is in op `after`. Raw events show trajectory. |
| Page create/delete undoable | YES. `create_page` undo deletes; `delete_page` undo restores page + content + active state. (`switch_page` remains non-undoable — it's navigation.) |
| `switch_page` event includes viewport before/after | YES. Each page has its own viewport memory; CUA can verify restore via `before_viewport` + `after_viewport` in event params. |

### §4 — Open questions DEFERRED to §8 (Undo/redo)

These belong in §8 walk-through, not §4:

1. Text caret position restoration on undo (caret state in undo stack?)
2. Selection preservation across undo (is selection part of undo stack at all?)
3. Compound operations (group-then-move = 1 entry or 2?)
4. Layer ID stability on undo→redo (restore same ID or generate new?)

### §5 — Input pipeline (raw → tool → op)

Layered dispatch model: **InputCapture → Mode (if any) → Tool → Default handler**. Both real users and CUA tests feed events through the same dispatch path.

#### §5a — Raw event capture (locked)

| Sub-decision | Decision |
|---|---|
| 1. DOM listening level | Hybrid: canvas element (pointer/wheel/drop/contextmenu), window (keyboard/clipboard) |
| 2. Event API | PointerEvent (NOT MouseEvent — modern, unifies mouse/touch/pen, friendlier to synthetic) |
| 3. Event types | pointerdown/move/up/cancel, wheel, keydown/up, paste/copy/cut, drop/dragover, contextmenu |
| 4. Coordinate normalization | Done at capture; every event carries BOTH `clientX/Y` (raw, browser-relative) AND `canvasX/Y` (after pan/zoom transform applied) |
| 5. Raw stream policy | All events recorded, NO throttle, hover events (buttons=0) included. ~5MB/hour storage budget — non-issue. |
| 6. preventDefault | Selective: contextmenu, wheel-on-canvas, drop, our shortcut combos. Browser defaults preserved for typing in real text inputs and unused combos. |

**Normalized `InputEvent` shape** — single interface fed to engine, framework-agnostic:

```typescript
interface InputEvent {
  type: 'pointerdown' | 'pointermove' | 'pointerup' | 'pointercancel'
      | 'wheel' | 'keydown' | 'keyup'
      | 'paste' | 'copy' | 'cut'
      | 'drop' | 'contextmenu'
  ts: number
  pointerId?: number
  clientX?: number; clientY?: number
  canvasX?: number; canvasY?: number     // post-transform
  buttons?: number
  deltaX?: number; deltaY?: number       // wheel
  key?: string; code?: string            // keyboard
  payload?: { type: string, data: any }  // clipboard / drop
  modifiers: { shift, ctrl, alt, meta }  // ALWAYS present, browser-sourced
}
```

`modifiers` mandatory on every event — read directly from browser's `e.shiftKey/ctrlKey/altKey/metaKey`. Engine never tracks modifier state internally (avoids stuck-modifier bug from missed keyup).

#### §5b — Tool state machine (locked)

| Sub-decision | Decision |
|---|---|
| 1. Tool dispatch | Per-tool handler module + registry (parallels §3 behavior registry). Each tool exports a `ToolHandler` with onPointerDown/Move/Up/KeyDown + lifecycle hooks (onActivate/onDeactivate). |
| 2. Mode interceptor layer | Layered dispatch: Mode → Tool → Default. CONSUMED/NOT_CONSUMED return flag controls whether event falls through (analogous to `e.stopPropagation()`). |
| 3. State location | Single centralized `engineState` object (activeTool, activeMode, pointerState, dragState, selectedIds, viewport, activePageId, scopeContainerId, toolOverride). NO state scattered across tool modules or input handler. |
| 4. Transition discipline | `setTool(newTool)` follows strict order: cancel mid-gesture → onDeactivate(old) → clear toolState → set activeTool → onActivate(new) → emit `tool_switch` logger event. Same pattern for `enterMode/exitMode`. |
| 5. FSM library | NO. Simple field + lifecycle hook pattern sufficient for ~15 tools + 2-3 modes. XState would be overkill. |

```typescript
// tools/move-tool.ts
export const MoveTool: ToolHandler = {
  name: 'move',
  onPointerDown(e, ctx) { ... },
  onPointerMove(e, ctx) { ... },
  onPointerUp(e, ctx) { ... },
  onKeyDown(e, ctx) { ... },
  onActivate(ctx) { ... },
  onDeactivate(ctx) { ... },
}

// tools/registry.ts
const tools: Record<ToolName, ToolHandler> = { move: MoveTool, rectangle: ..., pen: ..., ... }

// dispatch
function dispatchInput(event: InputEvent) {
  const mode = modes[engineState.activeMode]
  if (mode) {
    const result = mode.handle(event, ctx)
    if (result === CONSUMED) return
  }
  const tool = tools[getCurrentTool()]   // override-aware
  tool[handlerFor(event.type)]?.(event, ctx)
}
```

#### §5c — Mode states (locked)

**Two true modes**, plus two NON-mode mechanisms that are sometimes confused with modes:

| Concept | What | Implementation |
|---|---|---|
| **Mode (true)** | Changes input dispatch rules | `text_edit`, `vector_edit` — exclusive `engineState.activeMode` field |
| **Scope context** | Limits hit-test scope, dispatch unchanged | `engineState.scopeContainerId: string \| null` — NOT a mode |
| **Tool override** | Suspends active tool, substitutes another | `engineState.toolOverride: ToolName \| null` — NOT a mode |

**Critical conceptual point** (clarified after user question): "editing a layer" ≠ "entering mode". Layer-level operations (move, resize, set fill, rename, delete, group, etc.) all happen in **default `design` mode** — no mode entry needed. Modes are ONLY for editing a layer's INTERNAL structure (text characters, vector points). Most editing in our scope is mode-free.

| Mode | Enter triggers | While active | Mode state | Exit triggers | onDeactivate cleanup |
|---|---|---|---|---|---|
| `text_edit` | double-click on text layer; Enter on selected text; auto on `create_text` finish | Keyboard → typing/caret-nav (R, V, T are characters NOT shortcuts); pointer → caret/range; click outside → exit+commit; Cmd-shortcuts still active (text scope) | `editingLayerId, caretPosition, selectionRange?` | Esc; click outside text layer; tool change | Auto-delete empty text (`delete` event with `system/auto_empty_text` trigger); emit `commit_text`; clear caret/selection state |
| `vector_edit` | double-click on vector layer; Enter on selected vector; auto on `create_vector_with_pen/pencil` finish | Pointer → point/handle/segment manipulation; arrows → nudge selected points; Delete → remove points; V → toggle handle type; sub-toolbar visible (Bend, Cut) | `editingLayerId, selectedPointIndices, bendActive?` | Esc; click on non-vector layer; tool change | Clear selectedPointIndices (vector edits commit instantly, no extra cleanup) |

**Group scope** (NOT a mode): `scopeContainerId` set when user "enters" a frame/group (double-click). Hit-test recursive only inside that container. Selection limited to children. Visual: parent dimmed, container outlined. **Coexists with modes** — you can be inside a group AND in text_edit at the same time. Exit: Esc / click outside container bounds / switch tool.

**Hand pan** (NOT a mode, tool override): Space keydown → `toolOverride = 'hand'`. Dispatch checks override before activeTool. Space keyup → clear override. Disabled inside text_edit (space is a typed character there). Engine tracks `spaceHeld: boolean` (one of the rare exceptions to "no internal modifier state" rule, because space ISN'T a modifier in browser event terms).

#### §5d — Synthetic input handling for CUA (locked)

| Sub-decision | Decision |
|---|---|
| 1. Input entry points | TWO paths feeding the same dispatch: (a) DOM events → capture layer normalizes → `dispatchInput()`. (b) CUA test calls `engine.dispatchInput(event: InputEvent)` directly, bypassing DOM. Both paths converge — zero behavior divergence. |
| 2. Clock | Injectable `Clock` interface (`{ now(): number }`). Production uses `realClock` (`Date.now()`). Tests use `TestClock` with `advance(ms)`. Engine NEVER calls `Date.now()` directly — coalescing windows (e.g., 500ms typing burst) become deterministic. |
| 3. Validation | Zod schema on `InputEvent` (discriminated union per type). Validated in DEV mode only inside `dispatchInput()`. CUA driver bugs throw immediately instead of silent fail. Eliminated in prod build. |
| 4. Dispatch model | **Synchronous**. `dispatchInput()` returns when all consequences (graph update, undo push, logger emit) are complete. CUA can immediately query state after dispatch. Async only for genuinely async operations (clipboard read, image load) — those return Promises but happen outside input pipeline. |
| 5. State observability | Read-only accessors for CUA mid-test queries: `engine.state.getSelection() / getNode(id) / getActivePage() / getViewport() / getActiveTool() / getActiveMode() / getScopeContainer() / getUndoStackDepth() / getLogStream()`. Mutation only via `dispatchInput()`. |
| 6. Modifier state | Engine does NOT track shift/ctrl/alt/meta internally. Every `InputEvent` carries `modifiers: { shift, ctrl, alt, meta }` from browser source. Eliminates stuck-modifier bugs entirely. **Exception:** space-hold for hand-pan tracked as `spaceHeld` field (space is not a browser modifier). |

**Key architectural property:** Real user input and CUA synthetic input are **indistinguishable to the engine** past the entry point. CUA tests exercise the SAME tool/mode/op code paths as real users — no test-only shortcut paths to maintain.

---

## Cross-cutting concerns from `extracted/features/index.md` — status

| # | Concern | Status |
|---|---|---|
| 1 | Undo granularity / coalescing | ✅ Resolved §4c |
| 2 | Multi-trigger semantic events | ✅ Resolved §4b (structured trigger object) |
| 3 | Drag vs Alt-drag (move vs duplicate) | ✅ Resolved §4 (split into `move_layer` and `duplicate_by_drag`) |
| 4 | Delete from canvas vs from panel | ✅ Resolved §4 (unified `delete` event with trigger discriminator) |
| 5 | Viewport state vs scene-graph state | ⏳ Partial — §4a established `undoable` flag; §5b located viewport in `engineState` (not graph); §6 will explicitly partition state buckets |
| 6 | Coalesced undo during continuous input | ✅ Resolved §4c |
| 7 | Visual-only click behavior | ⏳ §9 (Visual-only UI click behavior) |

---

## Other locked top-level decisions

- **Scope:** Tier 2 — see `plan/00 §2`.
- **Out-of-scope but UI rendered:** `plan/00 §3`.
- **Out-of-scope and not rendered:** `plan/00 §3a`.
- **Theme:** dark default, light via ThemeProvider. Token values TBD.
- **Mode switcher composition:** Draw / Design / Dev Mode (NOT Design / Prototype / Dev).
- **Chrome placement:** Avatar stack + Share + Present triangle in right-panel header (UI3).
- **Agent approach:** Sandbox blocks Agent A/B writes. Primary agent writes directly. Pre-create directories before any future agent dispatch.

---

## Open / not-yet-decided

- Tech stack (framework, build tool, state management) → §10
- Canvas rendering approach (Canvas 2D / SVG / WebGL / canvaskit-wasm) → §10
- Project package layout → §13
- Log storage + export format → §7
- Logger taxonomy registry vs closed set → §7
- Visual-only UI click behavior → §9
- Fonts (Inter Google Fonts vs bundled) → §11
- Icons (Lucide placeholder vs Figma kit extraction) → §11

---

## Repo state reference

```
figma-mock/
├── CLAUDE.md                 ← project overview (source of truth for scope)
├── last-point.md             ← THIS FILE
├── helper/                   ← read-only (analysis + raw docs)
│   ├── figma_docs/           (216 articles + 1087 images)
│   └── analysis/             (ui-map, panel-states, feature-inventory, workflows, dependency-clusters)
├── open-source-example/      ← OpenPencil reference, read-only
├── plan/                     ← planning phase output
│   ├── 00-overview.md        ✅
│   ├── 01-ui-schema-extraction.md  ✅
│   ├── 02-feature-research.md      ✅
│   ├── 03-engine-architecture.md   ⏳ §1-§5 walked, §6-§15 pending
│   └── 04-build-phases.md          ⏳ blocked on plan/03
└── extracted/
    ├── ui-schema/            ✅ 9 files, 1460 lines
    └── features/             ✅ 66 files (65 specs + index), 3560 lines
```

---

## Research artifacts produced this session

Two paired research dives via Explore agents — outputs were synthesized into the locked decisions above. If next session needs the raw findings, re-run the agents with the same prompts (saved verbatim below for reproducibility).

**Dive 1 (for §3 — Scene graph data model):**
- Agent A: Read `extracted/ui-schema/state-matrix.md`, `regions/right-properties.md`, `regions/canvas-overlays.md`, all of `extracted/features/properties/`, `transform/`, `text/`, `vector/`, `layers/`, `region-tools/`, `shape-creation/`. Output: complete node taxonomy with field-by-field evidence per type, parent/child invariants, 12 open questions.
- Agent B: Deep-dive on OpenPencil `packages/core/src/scene-graph/`, `editor/undo.ts`, `editor/clipboard.ts`. Output: monolithic shape evidence, closure-based undo pattern, parent-relative coords math, 7 documented pain points.

**Dive 2 (for §4 — Operation model):**
- Agent A: Read all 65 feature specs systematically. Output: ~90-op inventory table, 50+ trigger value enumeration, coalescing-needed feature list (12 entries), naming inconsistencies catalog, 12 open questions.
- Agent B: Deep-dive on OpenPencil `editor/`, especially undo.ts batching mechanics, clipboard.ts paste flow. Output: explicit `beginBatch/commitBatch` pattern, drag-defer-to-pointer-up pattern, paste = single entry pattern, op metadata gap (label-only — confirms our need for separate logger record).

---

## Key cross-references for next session

- `plan/00-overview.md` — scope + decision log (§8 especially)
- `plan/02-feature-research.md §5` — closed feature list
- `extracted/ui-schema/state-matrix.md` — selection × panel layout
- `extracted/features/index.md` — cross-cutting concerns status
- `helper/analysis/ui-map.md` + `panel-states.md` — UI sanity check

---

## Task tracker state (snapshot)

| ID | Status | Subject |
|---|---|---|
| #1 | completed | plan/03 §3 — node taxonomy mikro-kararları (5 tane) |
| #2 | completed | [Açık konu] Continuous input log şişmesi — coalesce stratejisi (resolved §4c) |
| #3 | completed | [Açık konu] Validator kütüphanesi seçimi: Zod vs custom (Zod) |
| #4 | completed | plan/03 §4 — Operation model + logger event schema |
| #5 | completed | plan/03 §5 — Input pipeline (raw → tool → op) |
| #6 | pending | plan/03 §6 — State partitioning |

---

## Session hygiene reminders

- **Do NOT re-launch Agent A or Agent B for past topics** — research outputs already absorbed into locked decisions above.
- **DO launch new research agents for §6+ topics** if a decision needs grounding (analyze-before-deciding rule). §5 was decided without a fresh research dive — extracted/features Inputs sections were already mined in §4 dive, OpenPencil input layer is Vue-coupled and not 1:1 transferable, so engineering judgment was sufficient.
- **Do NOT invent content** — every UI description and feature behavior should trace to a doc/image or extracted spec.
- **Before spawning ANY agent**, pre-create its output directories via Bash `mkdir -p` (sandbox bug from earlier session).
- **Confirm before destructive ops** (delete file, `git reset --hard`, etc.). Default to asking.
- **Ultrareview is user-triggered, cannot launch from primary agent.**
- **§6 — State partitioning is next.** It's a synthesis section (most state buckets already located in §4a/§5b decisions); job is to formalize the bucket map and answer: where does each state piece live, what op categories may touch it, how is it snapshotted, what's its persistence scope (page vs file vs session). No sub-section split decided yet — propose 3-4 sub-sections at start.

---

## First message to send when resuming

"§5 kapandı, last-point güncel. Sırada §6 — State partitioning. Buradaki çoğu kavramı (scene graph, viewport, selection, tool/mode state, clipboard) §4a + §5b'de yerine koymuştuk; §6'nın işi bunları **bucket haritası** olarak formalize etmek + her bucket'ın persistence/snapshot/op-erişim kurallarını tanımlamak. Önce alt-bölüm önerisi getireyim mi (örn. §6a state bucket envanteri, §6b op-bucket erişim matrisi, §6c persistence/snapshot kuralları), yoksa direkt walk-through başlayalım mı?"
