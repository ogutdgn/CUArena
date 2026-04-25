# Feature Specs Index

**Purpose:** Top-level index of every feature spec under `extracted/features/`. Produced after all 12 category batches complete.

Each feature follows the template from `plan/02-feature-research.md §4` — Name, Category, One-line summary, Triggers, Preconditions, Inputs, Behavior, Outputs, UI feedback, Side effects, Related UI schema entries, Semantic event(s) candidate, Source articles, Notes / gaps.

All features in this index are in `plan/00 §2` functional scope. Visual-only UI elements are NOT listed here — they are covered by the UI schema (`extracted/ui-schema/`) and get no-op click behavior decided in `plan/03`.

---

## Feature list by category

### canvas-navigation (5)
- [pan-canvas](canvas-navigation/pan-canvas.md) — translate the viewport without changing selection
- [zoom-in-out](canvas-navigation/zoom-in-out.md) — continuous / discrete zoom
- [zoom-to-fit](canvas-navigation/zoom-to-fit.md) — fit all content on page
- [zoom-to-100](canvas-navigation/zoom-to-100.md) — 1:1 zoom
- [zoom-to-selection](canvas-navigation/zoom-to-selection.md) — fit current selection

### selection (6)
- [click-select](selection/click-select.md) — single-layer select via click
- [shift-click-add-to-selection](selection/shift-click-add-to-selection.md)
- [shift-click-remove-from-selection](selection/shift-click-remove-from-selection.md)
- [drag-box-select](selection/drag-box-select.md) — marquee / rubber-band
- [select-all](selection/select-all.md) — Cmd/Ctrl A
- [deselect](selection/deselect.md) — Esc / click empty

### shape-creation (7)
- [create-rectangle](shape-creation/create-rectangle.md)
- [create-line](shape-creation/create-line.md)
- [create-arrow](shape-creation/create-arrow.md)
- [create-ellipse](shape-creation/create-ellipse.md)
- [create-polygon](shape-creation/create-polygon.md)
- [create-star](shape-creation/create-star.md)
- [place-image](shape-creation/place-image.md) — file picker / drag-drop / paste

### region-tools (3)
- [create-frame](region-tools/create-frame.md)
- [create-section](region-tools/create-section.md)
- [use-slice-tool](region-tools/use-slice-tool.md) — slice functional, export visual-only

### transform (5)
- [move-layer](transform/move-layer.md)
- [resize-layer](transform/resize-layer.md)
- [rotate-layer](transform/rotate-layer.md)
- [scale-with-scale-tool](transform/scale-with-scale-tool.md) — distinct from resize
- [flip](transform/flip.md) — horizontal + vertical

### clipboard (5)
- [copy](clipboard/copy.md)
- [cut](clipboard/cut.md)
- [paste](clipboard/paste.md)
- [duplicate](clipboard/duplicate.md) — Cmd D + Alt-drag
- [delete](clipboard/delete.md)

### properties (7)
- [set-fill](properties/set-fill.md) — grouped meta-feature
- [set-stroke](properties/set-stroke.md) — grouped meta-feature
- [set-effects](properties/set-effects.md) — drop shadow + blur functional; others visual-only
- [set-opacity](properties/set-opacity.md) — layer-level
- [set-corner-radius](properties/set-corner-radius.md) — uniform + per-corner
- [set-constraints](properties/set-constraints.md)
- [set-visibility](properties/set-visibility.md)

### layers (7)
- [group-selection](layers/group-selection.md)
- [ungroup](layers/ungroup.md)
- [enter-group](layers/enter-group.md) — scope nested clicks to container
- [exit-group](layers/exit-group.md)
- [reorder-layer](layers/reorder-layer.md) — z-order + reparent
- [rename-layer](layers/rename-layer.md) — inline + bulk modal
- [delete-layer-from-panel](layers/delete-layer-from-panel.md) — distinguished trigger vs canvas delete

### pages (4)
- [create-page](pages/create-page.md)
- [switch-page](pages/switch-page.md)
- [rename-page](pages/rename-page.md)
- [delete-page](pages/delete-page.md)

### text (5)
- [create-text](text/create-text.md)
- [edit-text](text/edit-text.md) — enter mode + typing + caret nav
- [select-text-range](text/select-text-range.md)
- [set-text-properties](text/set-text-properties.md)
- [commit-text](text/commit-text.md)

### vector (9)
- [use-pen-tool](vector/use-pen-tool.md) — create vector network
- [use-pencil-tool](vector/use-pencil-tool.md) — freehand + simplification
- [enter-vector-edit-mode](vector/enter-vector-edit-mode.md)
- [exit-vector-edit-mode](vector/exit-vector-edit-mode.md)
- [add-vector-point](vector/add-vector-point.md)
- [move-vector-point](vector/move-vector-point.md)
- [delete-vector-point](vector/delete-vector-point.md)
- [toggle-vector-handle](vector/toggle-vector-handle.md)
- [close-open-vector-path](vector/close-open-vector-path.md)

### history (2)
- [undo](history/undo.md)
- [redo](history/redo.md)

---

## Totals

**65 feature files across 12 categories.**

| Category | Count |
|---|---|
| canvas-navigation | 5 |
| selection | 6 |
| shape-creation | 7 |
| region-tools | 3 |
| transform | 5 |
| clipboard | 5 |
| properties | 7 |
| layers | 7 |
| pages | 4 |
| text | 5 |
| vector | 9 |
| history | 2 |
| **total** | **65** |

---

## Known cross-cutting concerns

Items that span multiple feature files and need centralized decision in `plan/03`:

1. **Undo granularity / coalescing** — typing bursts, color-picker scrubbing, drag operations. Currently each feature's "Side effects → Undo stack" section handles this at a per-op level; `plan/03` consolidates.

2. **Multi-trigger semantic events** — most features emit one event name with a `trigger` field. `plan/03` finalizes the enum for `trigger` values and decides which trigger pairs should split into distinct events (vs remain in one event for CUA distinguishability).

3. **Drag vs Alt-drag** — critical for CUA trajectory testing. `move-layer` and `duplicate` share the pointer drag input but differ by modifier. Confirm both emit distinct events.

4. **Delete from canvas vs from panel** — currently a single `delete` event with a `trigger` distinguishing source. `plan/03` confirms whether to keep unified or split.

5. **Viewport state vs scene-graph state** — canvas-navigation features affect viewport only; this drives a clear engine-model boundary that `plan/03` will define explicitly.

6. **Coalesced undo during continuous input** — rotation drag, resize drag, color-picker scrubbing, typing — each emits a single undo entry per user gesture. Engine infrastructure for this lives in `plan/03`.

7. **Visual-only click behavior** — not part of feature specs (those are functional); covered by `plan/00 §8` open decision and resolved in `plan/03`.

---

## Relationship to downstream plans

- **`plan/03-engine-architecture.md`** reads every feature file:
  - `Outputs` sections → engine operation model (what ops exist, what each mutates)
  - `Inputs` sections → raw-event → operation mapping
  - `Semantic event(s) candidate` sections → consolidated logger taxonomy + registry
  - Cross-cutting concerns above → engine-wide design decisions

- **`plan/04-build-phases.md`** reads categories for slice ordering:
  - Slice 0 (vertical slice, pipeline validation) likely covers: canvas-navigation + selection + shape-creation (rectangle only) + transform (move) + clipboard (copy/paste/delete) + history (undo/redo) — the minimum to prove drag-vs-copy-paste trajectory distinction.
  - Subsequent slices expand to full Tier 2 per `plan/04` ordering.
