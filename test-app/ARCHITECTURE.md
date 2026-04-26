# Test-app architecture

Source of truth for engineering decisions. Grounded in:
- `extracted/ui-schema/*` (9 files)
- `extracted/features/*` (65 feature specs)
- `plan/00-overview.md` (Tier 2 scope, visual-only inventory)
- `last-point.md` (locked decisions)
- Two deep-dive analysis reports in `.analysis/` (UI assembly, engine + logger + slices)

## 1. Stack

| Concern | Choice |
|---|---|
| Framework | React 18 + TypeScript |
| Build | Vite 5 |
| Store | Zustand + Immer |
| Canvas | SVG (shapes/vectors/handles) + HTML overlays (text edit, panels) |
| Font | `@fontsource/inter` (bundled) |
| Icons | `lucide-react` (placeholder; per-feature replacement later) |
| Tests | Vitest (deferred to slice 1) |

Why SVG: pen tool / vector edit / text editing / hit-testing / corner-radius all decisively easier than Canvas2D at <1k node mock scale.

## 2. State buckets

Six independent state regions. Each has different mutation gates and undo behaviour.

| Bucket | Mutation gate | Undo restores | Page-switch | Reload |
|---|---|---|---|---|
| **Scene graph** (Document → Pages → Layers) | undoable ops only | yes | persists | persists |
| **Viewport** (per-page pan/zoom) | `set_viewport` (non-undoable) | untouched | saved/restored per page | persists |
| **Selection** (per-page) | `set_selection` (non-undoable) + recorded as side-channel on every undoable op | restored from undo entry's snapshot | per-page restore | persists |
| **Mode** (active tool, productMode, editMode, focusContextId) | `set_tool`/`set_edit_mode`/`set_focus_context` | untouched | focusContext per page; tool stays | reset |
| **Clipboard** | `set_clipboard` | untouched (persists across undo) | persists | lost |
| **UI ephemeral** (hover, dropdowns, drag preview, toasts) | direct writes | untouched | reset | lost |
| **Logger** (raw + semantic) | append-only | append `undo` event; originals stay | logged as `switch_page` | exported then cleared |

## 3. Op set (16 atomic ops)

All scene-graph mutation goes through the op pipeline. UI never writes scene state directly.

| Op | Undoable | Inverse | Used by |
|---|---|---|---|
| `create_node` | yes | snapshot → `delete_nodes` | every shape/frame/section/text/vector/image creation, paste, duplicate |
| `delete_nodes` | yes | snapshot → `create_node` per | delete, cut, delete-from-panel |
| `set_property` | yes | symmetric `before/after` | rename, fills, strokes, effects, opacity, corner radius, constraints, visibility, flip |
| `set_transform` | yes | symmetric | move, resize, rotate |
| `scale_uniform` | yes | snapshot of nested mutations | scale tool only |
| `reparent` | yes | symmetric | reorder cross-parent, group/ungroup, frame/section wrap |
| `reorder_z` | yes | symmetric | same-parent z-order |
| `mutate_text_runs` | yes | symmetric | text editing (coalesced) |
| `mutate_vector_network` | yes | symmetric | pen, vector edits |
| `set_selection` | **no** | symmetric (for replay) | selection changes |
| `set_focus_context` | **no** | symmetric | enter/exit group |
| `set_viewport` | **no** | n/a | pan, zoom |
| `set_tool` | **no** | n/a | tool activation |
| `set_edit_mode` | **no** | n/a | text-edit, vector-edit, pen-creation |
| `create_page` / `delete_page` | yes | symmetric | page lifecycle |
| `switch_page` | **no** | n/a | page switch |
| `set_clipboard` | **no** | n/a | copy, cut |

## 4. Transaction / undo model

Coalescing combines micro-mutations from one user gesture into ONE undo entry.

```
open()  → snapshot selection + focusContext, buffer ops
commit()→ apply buffered ops as one merged undo entry; merge set_transform chains via before/after snapshot
abort() → discard ops, revert preview
```

Per-gesture rules (full table in `.analysis/engine-report.md` §4.2):
- Drag-move/resize/rotate/scale → open on pointerdown, commit on pointerup
- Color picker scrub → open on picker open, commit on picker close
- Slider scrub → open on pointerdown of thumb, commit on pointerup
- Text typing burst → 500ms inactivity window or caret-jump → commit
- Pen path-build → first pointerdown → close-path / Esc / Enter / tool-change → commit ONE entry

Undo stack depth: 1000 entries (configurable).

## 5. Logger

**Raw events** (window/document capture, ring buffer 10k):
- pointer{down/move/up}, click, dblclick, contextmenu (window capture)
- wheel (canvas root, 16ms coalesced)
- keydown/keyup, paste/copy/cut, drag{enter/over/drop}
- focus/blur, resize/visibilitychange
- pointermove throttled to 60fps; raw `paste` records byte size only (no content)

**Semantic events** — closed registry, schemaVersion 1. Every event:
```ts
{ schemaVersion: 1, sessionId, eventId, timestamp, pageId, rawEventIdRange }
```

Cross-cutting decisions (resolved):
- **Drag vs Alt-drag → SPLIT** (`move_layer { trigger:"drag" }` vs `duplicate { trigger:"alt_drag" }`)
- **Delete-from-canvas vs panel → UNIFIED** with `trigger ∈ {keyboard_canvas, keyboard_panel, context_menu_canvas, context_menu_panel, main_menu}`
- `selection_change` umbrella always emitted alongside method-specific event
- `viewport_change` debounced 100ms; raw scroll/pinch still go to raw stream
- `noop_click { element_id }` for every visual-only button click

Storage: in-memory + JSON download. IndexedDB deferred to Slice 13.

## 6. Visual-only UI

Per `plan/00 §3` and the deep-dive UI inventory: **~110 stable button_ids** across toolbar, left rail, file menu, main menu, right panel header, sub-header, no-selection sections, selection sections, color picker (gradient/pattern tabs), context menu, action bar.

Click behaviour:
- Emit `noop_click { element_id }` semantic event
- Show small tooltip "X — not implemented in this mock" (deferred styling)
- Visual-only dropdowns: full no-op (no chevron rotation animation) — re-evaluate if it feels broken

## 7. Theme

- Dark default (locked).
- CSS variables. Tokens in `src/theme/tokens.ts`, exposed as CSS custom properties via `:root`.
- Confirmed defaults from gap analysis:
  - Selection blue: `#0D99FF`
  - Canvas bg: `#1E1E1E` dark / `#F5F5F5` light
  - Left panel default: 240px (min 200, max 480)
  - Right panel default: 240px (min 200, max 400)
  - Left rail (when shown): 48px

## 8. Folder structure

```
test-app/
├── ARCHITECTURE.md         (this file)
├── package.json
├── tsconfig.json
├── vite.config.ts
├── index.html
├── src/
│   ├── main.tsx            entry
│   ├── App.tsx             top-level layout
│   ├── types/
│   │   ├── scene.ts        Document, Page, Layer union, paint/stroke/effect
│   │   ├── ops.ts          16-op union
│   │   └── events.ts       semantic event registry
│   ├── engine/
│   │   ├── store.ts        zustand store (6 buckets)
│   │   ├── ops.ts          apply + inverse per op
│   │   ├── transactions.ts open/commit/abort
│   │   ├── undo.ts         history stack
│   │   ├── dispatch.ts     central entrypoint: dispatch(op) → apply + push undo + emit raw->semantic
│   │   └── selectors.ts    derived state (active page, selected layers, hit-testing)
│   ├── logger/
│   │   ├── buffer.ts       ring buffer
│   │   ├── raw.ts          DOM event capture install/remove
│   │   ├── semantic.ts     emit() + registry
│   │   └── export.ts       download JSON
│   ├── tools/
│   │   ├── index.ts        active tool registry
│   │   ├── move.ts         move/select/drag/resize/rotate
│   │   ├── rectangle.ts    drag-create
│   │   └── hand.ts         pan
│   ├── ui/
│   │   ├── chrome/
│   │   │   ├── Toolbar.tsx
│   │   │   ├── LeftPanel.tsx
│   │   │   ├── RightPanel.tsx
│   │   │   └── ModeSwitcher.tsx
│   │   ├── canvas/
│   │   │   ├── CanvasView.tsx     SVG root + viewport transform
│   │   │   ├── NodeRenderer.tsx   per-type SVG renderer
│   │   │   └── Marquee.tsx
│   │   ├── overlays/
│   │   │   ├── SelectionOverlay.tsx  bbox + handles
│   │   │   └── InsertionCrosshair.tsx
│   │   └── panels/
│   │       ├── LayersTree.tsx
│   │       ├── PageSection.tsx
│   │       ├── PositionSection.tsx
│   │       └── LoggerPanel.tsx     dev panel: live events + Export JSON
│   ├── theme/
│   │   ├── tokens.ts
│   │   └── global.css
│   ├── icons/
│   │   └── (re-exports from lucide-react with stable names)
│   └── util/
│       ├── id.ts           uuid
│       ├── keymap.ts       keyboard shortcut routing
│       └── geometry.ts     bbox, hit-test
└── public/
```

## 9. Slice 0 — what's in this build

Per `.analysis/engine-report.md §8`:

**Functional** (engine + UI + logger triple-checked):
- Move tool (click-select, shift-click, drag-box-select, drag-move, drag-resize, delete via keyboard)
- Rectangle tool (drag-create + click-default-size)
- Hand tool (drag-pan)
- Wheel zoom
- Copy/cut/paste/duplicate (Cmd D + Alt-drag)
- Undo/redo

**Visual-only** (rendered, click → `noop_click`):
- All other toolbar buttons (move-tools sub-tools, region tools, ellipse/polygon/star/line/arrow, image, text, pen, pencil, comment, actions menu, mode switcher Draw/Dev)
- Left rail icons (Variables, Assets, Find, Notifications)
- File menu, main menu, pages selector add-page
- Right panel: Page section (read-only), all selection sections except Position (W/H/rotation read-only stub)
- Help dock, keyboard shortcuts panel

**Acceptance** — three CUA trajectories decidable from log alone:
- A. drag-move: one `move_layer { trigger:"drag" }`, no `duplicate`, scene-graph node count unchanged
- B. copy+paste: `copy` then `paste` events, node count +1, selection shifts to new layer
- C. alt-drag duplicate: one `duplicate { trigger:"alt_drag" }`, no `move_layer` for those ids, node count +1

## 10. Open risks (deferred)

Carried from `.analysis/engine-report.md §10`:
- Vector network single-region vs multi-region (slice 8 decision)
- Default fill on close-path (recommend: empty)
- Cut tool functional vs visual-only (recommend: visual-only)
- Smart-duplicate offset memory (recommend: fixed offset; smart later)
- Selection on page switch (recommend: restore per-page)
- Typing-burst window 500ms (tunable)
- Pen tool per-click events (recommend: emit for trajectory granularity)

## 11. Slice ordering after Slice 0

Per `.analysis/engine-report.md §9`:

1. Shape tool family (ellipse/line/arrow/polygon/star) — M
2. Properties pass 1 (fill/stroke/opacity/corner-radius/visibility) — M
3. Frames + groups + reorder — M
4. Pages + slice-tool + rename — S
5. Text basics — L
6. Rotate/scale/flip + constraints — M
7. Image placement — S
8. Vector + pen + edit-mode — L
9. Pencil — S
10. Effects (drop shadow + blur) — S
11. Panel completion + bulk rename + cross-parent reparent + zoom-to-* — M
12. Visual-only completion + actions menu + comment stub — S
13. Logger export + sessions + replay — M
14. Snap guides + smart guides — M
15. Polish + edge cases — M
