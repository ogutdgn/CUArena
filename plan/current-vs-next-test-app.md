# Test-App Current vs Next Report (April 26, 2026)

## Scope baseline used for this report
- `plan/00-overview.md` (Tier 2 functional scope and visual-only scope)
- `extracted/features/index.md` (65 functional feature specs across 12 categories)
- `extracted/features/vector/use-pen-tool.md`, `extracted/features/vector/close-open-vector-path.md`
- `extracted/features/text/edit-text.md`, `extracted/features/text/select-text-range.md`
- Current `test-app/src/*` implementation snapshot

## TL;DR
- The app now covers most core CRUD/canvas flows: selection, creation tools, move/resize/rotate, pages, layers, undo/redo, and logger export.
- This branch already includes two meaningful quality fixes:
  - Text editing now uses an uncontrolled `contentEditable` flow to preserve caret behavior (stops prepend-style typing artifacts).
  - Pen tool now supports continuation flow by resuming from the selected open vector endpoint.
- Biggest remaining gaps are parity gaps, not foundation gaps: Scale-tool semantics, full text-range/runs behavior, full Pen modifiers/endpoint continuation behavior, and deeper property fidelity.

## Current feature coverage vs expected

| Category | Spec Count | Current Status | Notes |
|---|---:|---|---|
| canvas-navigation | 5 | Mostly complete | Pan, wheel zoom, zoom-to-fit/100/selection implemented. |
| selection | 6 | Partial | Click/shift-click/drag-box/deselect/select-all implemented; `select-all` currently walks top-level page children only. |
| shape-creation | 7 | Partial | Rectangle/line/arrow/ellipse/polygon/star + image import implemented; toolbar image button still visual-only and several creation tools still force page parent. |
| region-tools | 3 | Partial | Frame/Section/Slice creation works; no frame presets/wrap-selection flow yet. |
| transform | 5 | Partial | Move/resize/rotate/flip implemented; `scale` tool is stubbed (`noopTool`) and true scale semantics are missing. |
| clipboard | 5 | Partial | Copy/cut/paste/duplicate/delete implemented incl. alt-drag duplicate; placement semantics are simplified. |
| properties | 7 | Partial | Fill/stroke/effects/opacity/corner radius/visibility controls exist; advanced stroke/fill/radius/constraints behavior remains incomplete. |
| layers | 7 | Partial | Group/ungroup/enter/exit/rename/reorder works; drag reorder is same-parent only (no cross-parent reparent via layers tree). |
| pages | 4 | Mostly complete | Create/switch/rename/delete page implemented and wired to left panel. |
| text | 5 | Partial | Create/edit/commit and basic typography controls implemented; text-range model and rich run-level behavior are not complete. |
| vector | 9 | Partial | Pen/pencil creation + vector point add/move/delete/edit mode implemented; handle-type toggles, full close/open parity, and full pen modifier behavior are incomplete. |
| history | 2 | Complete | Undo/redo transaction flow is in place and wired across main commands. |

## Key parity gaps vs design docs

1. Pen parity is improved but not fully Figma-like yet.
- `use-pen-tool.md` expects Shift angle constraints and Alt handle asymmetry; current pen flow does not fully implement both.
- Continuation currently resumes from selected open vector end; continuation from either endpoint and broader continuity ergonomics still need work.

2. Text parity is still below spec for range-level editing.
- `edit-text.md` and `select-text-range.md` expect robust caret/range behavior and range formatting semantics.
- Current implementation commits plain content + coarse properties; `runs` are not fully managed as first-class editable formatting ranges.

3. Scale tool behavior is missing.
- `scale-with-scale-tool.md` explicitly distinguishes scale semantics from resize semantics.
- UI exposes Scale (`K`), but tool registry maps it to a no-op.

4. Constraints are writable but not meaningfully enforced during parent resize.
- UI and property writes exist (`ConstraintsControl`), but parent-frame resize reflow logic is not implemented.

5. Layers-panel reorder does not yet support cross-parent reparent by drag target.
- Spec expects reorder/reparent flows in tree interactions.
- Current `reorderLayerInPanel` returns early when parent differs.

6. Several advanced property controls remain simplified.
- Missing/reduced fidelity: per-corner radius editing, advanced stroke alignment/dash handling UI, full fill stack semantics (reorder/complex paints), richer effect matrix.

## Architecture observations (current)

1. Core architecture is now stable enough for iteration.
- Scene graph + op pipeline + semantic logger + overlay-driven interaction model are coherent.
- Recent tree/index consistency fixes reduced prior divergence between `document.pages` and `nodesById` behavior.

2. Creation-parent resolution is inconsistent across tools.
- Some commands use contextual parent resolution (`resolveCreationParentId`), while several tools still hardcode `parentId = activePageId`.
- This causes behavior drift for grouped/frame-focused authoring.

3. Event schema is ahead of actual behavior in a few areas.
- Event union includes names for flows not fully implemented (`scale_layer`, etc.).
- This is good for forward compatibility but can hide instrumentation coverage gaps unless tracked explicitly.

4. Test harness depth is currently low.
- No automated tests are present in this app, and local typecheck was not run here because `npm` is unavailable in this execution environment.

## Recommended next build queue (priority order)

1. Complete transform parity slice.
- Implement real Scale tool semantics (`K`) including stroke/text/radius/children scaling.
- Implement constraint reflow behavior during parent frame resize.

2. Complete Pen parity slice.
- Add Shift angle constraints.
- Add Alt asymmetric handle behavior.
- Support continuation from both open endpoints with clearer endpoint hit UX.

3. Complete text-range slice.
- Introduce explicit edit-state model for caret/range.
- Make `runs` a real editable target (not passive storage).
- Support range-aware typography updates and mixed-value reflection.

4. Complete layer-tree structural operations.
- Enable cross-parent drag reparent in layers panel.
- Improve `select-all` recursion for nested trees.

5. Complete property-depth slice.
- Per-corner radius inputs.
- Stroke alignment/dash UI + behavior.
- Fill stack reorder and richer paint handling.

6. Add hardening gates before further feature expansion.
- Add focused regression tests around creation persistence, transform commits, and vector/text commit flows.
- Add a lightweight feature coverage checklist that maps each extracted feature file to a code owner and status.
