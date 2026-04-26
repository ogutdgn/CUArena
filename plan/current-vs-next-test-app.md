# Test-App Current vs Next Report (April 26, 2026 — updated post ogutdgn/vibe-fixes session 2)

## Scope baseline used for this report
- `plan/00-overview.md` (Tier 2 functional scope and visual-only scope)
- `extracted/features/index.md` (65 functional feature specs across 12 categories)
- `extracted/features/vector/use-pen-tool.md`, `extracted/features/vector/close-open-vector-path.md`
- `extracted/features/text/edit-text.md`, `extracted/features/text/select-text-range.md`
- Current `test-app/src/*` implementation snapshot
- `plan/where-we-left-off-2026-04-26.md` (post-merge state)

## TL;DR
- The app now covers most core CRUD/canvas flows: selection, creation tools, move/resize/rotate, pages, layers, undo/redo, and logger export.
- Recent work on `ogutdgn/vibe-fixes` (session 2) shipped four additional fixes:
  - **Pen anchor-drag Immer freeze bug fixed**: `creation.segments` objects were frozen by Immer after dispatch; mutating them in-place crashed. Fixed by index-based object replacement (`creation.segments[i] = {...}` pattern).
  - **VectorEditOverlay / pen tool conflict fixed**: `editMode` was staying `"vector"` when switching to pen, causing VectorEditOverlay to intercept pointer events. Fixed by resetting editMode to `"none"` on pen tool switch, and guarding the overlay with `activeTool === "pen"`.
  - **Scale tool implemented**: `K` key now activates a real scale tool that scales w/h live (handle drag), then scales stroke weights, corner radii, and font sizes proportionally on commit. Previously was `noopTool`.
  - **Layout bug fixed**: right panel and left panel `<aside>` elements lacked `min-height: 0`, causing the CSS Grid `1fr` row to expand beyond viewport height. Toolbar and sidebar were pushed off-screen when a layer was selected.
- Biggest remaining gaps: constraint reflow, full text-range/runs behavior, remaining pen modifiers, right-panel property field fidelity vs actual Figma, and deeper sidebar mode-switch parity.

## Current feature coverage vs expected

| Category | Spec Count | Current Status | Notes |
|---|---:|---|---|
| canvas-navigation | 5 | Mostly complete | Pan, wheel zoom, zoom-to-fit/100/selection implemented. |
| selection | 6 | Partial | Click/shift-click/drag-box/deselect/select-all implemented; `select-all` currently walks top-level page children only. |
| shape-creation | 7 | Partial | Rectangle/line/arrow/ellipse/polygon/star + image import implemented; preview fill now matches final defaults; toolbar image button still visual-only and several creation tools still force page parent. |
| region-tools | 3 | Partial | Frame/Section/Slice creation works; no frame presets/wrap-selection flow yet. |
| transform | 5 | Mostly complete | Move/resize/rotate/flip implemented; Scale tool now functional (strokes/radii/fonts scale on commit); constraint reflow still missing. |
| clipboard | 5 | Partial | Copy/cut/paste/duplicate/delete implemented incl. alt-drag duplicate; placement semantics are simplified. |
| properties | 7 | Partial | Fill/stroke/effects/opacity/corner radius/visibility controls exist; right-panel field set/behavior not compared against actual Figma yet (see Slice F). |
| layers | 7 | Partial | Group/ungroup/enter/exit/rename/reorder works; drag reorder is same-parent only (no cross-parent reparent via layers tree). |
| pages | 4 | Mostly complete | Create/switch/rename/delete page implemented and wired to left panel. |
| text | 5 | Partial | Create/edit/commit and basic typography controls implemented; text-range model and rich run-level behavior are not complete. |
| vector | 9 | Partial | Pen/pencil creation + vector point add/move/delete/edit mode implemented; pen session stability fixed; anchor-drag Immer freeze fixed; VectorEditOverlay/pen conflict fixed; handle-type toggles, full close/open parity, and Shift/Alt pen modifiers still incomplete. |
| history | 2 | Complete | Undo/redo transaction flow is in place and wired across main commands. |
| ui-layout | — | Fixed | Grid row expansion bug (toolbar/sidebar off-screen on selection) fixed via `min-height: 0` on panel flex containers. |

## Key parity gaps vs design docs

1. Pen parity is improved but not fully Figma-like yet. *(anchor-drag Immer freeze fixed; session/VectorEditOverlay conflict fixed)*
- `use-pen-tool.md` expects Shift angle constraints and Alt handle asymmetry; these are still not implemented.
- Continuation resumes from selected open vector end; multi-endpoint continuation and broader ergonomics still need work.
- Handle-type toggle toolbar flow (corner/mirror-angle/mirror-length) remains partial.

2. Text parity is still below spec for range-level editing.
- `edit-text.md` and `select-text-range.md` expect robust caret/range behavior and range formatting semantics.
- Current implementation commits plain content + coarse properties; `runs` are not fully managed as first-class editable formatting ranges.

3. Scale tool is now functional but children are not recursively scaled. *(scale tool implemented in session 2)*
- `scale-with-scale-tool.md` requires children of frames/groups to also scale proportionally.
- Current implementation scales the selected layer's dimensions + strokes/radii/fonts; child layers are a known V1 gap.

4. Constraints are writable but not meaningfully enforced during parent resize.
- UI and property writes exist (`ConstraintsControl`), but parent-frame resize reflow logic is not implemented.

5. Layers-panel reorder does not yet support cross-parent reparent by drag target.
- Spec expects reorder/reparent flows in tree interactions.
- Current `reorderLayerInPanel` returns early when parent differs.

6. Right-panel property fields have NOT been compared against actual Figma. *(new gap identified)*
- The sidebar fields shown for different layer types, selection states, and tool modes have not been validated against real Figma behavior.
- Different operations (select vs. edit mode vs. frame context vs. multi-select) produce different sidebar states in Figma; our current implementation may be missing fields, showing wrong fields, or behaving differently.
- This is tracked as Slice F below.

7. Several advanced property controls remain simplified.
- Missing/reduced fidelity: per-corner radius editing, advanced stroke alignment/dash handling UI, full fill stack semantics (reorder/complex paints), richer effect matrix.

## Architecture observations (current)

1. Core architecture is now stable enough for iteration.
- Scene graph + op pipeline + semantic logger + overlay-driven interaction model are coherent.
- `min-height: 0` fix on panel flex containers resolved the CSS Grid row expansion bug.

2. Creation-parent resolution is inconsistent across tools.
- Some commands use contextual parent resolution (`resolveCreationParentId`), while several tools still hardcode `parentId = activePageId`.
- This causes behavior drift for grouped/frame-focused authoring.

3. Event schema is ahead of actual behavior in a few areas.
- `scale_layer` event is now wired; some other names in the union (`scale_layer` children) remain partially instrumented.
- This is good for forward compatibility but can hide coverage gaps unless tracked explicitly.

4. Test harness depth is currently low.
- No automated tests are present in this app.
- TypeScript typechecks pass (confirmed via `npx tsc --noEmit`; pre-existing errors in move.ts/line.ts are unrelated).

## Recommended next build queue (priority order)

1. **[P0] Constraint reflow during parent frame resize.**
- Implement child reflow logic for `horizontal`/`vertical` constraint modes.
- Scale tool children scaling (recursive) can be added in the same pass.

2. **[P1] Right-panel sidebar field parity review vs actual Figma.** *(Slice F — new)*
- Compare every sidebar state (no selection, single layer types, multi-select, edit modes) against real Figma.
- A human must compare each sidebar state against real Figma and provide the gap list to the agent.

3. **[P1] Complete Pen parity slice.**
- Add Shift angle constraints.
- Add Alt asymmetric handle behavior.
- Support continuation from both open endpoints with clearer endpoint hit UX.

4. Complete text-range slice.
- Introduce explicit edit-state model for caret/range.
- Make `runs` a real editable target (not passive storage).
- Support range-aware typography updates and mixed-value reflection.

5. Complete layer-tree structural operations.
- Enable cross-parent drag reparent in layers panel.
- Improve `select-all` recursion for nested trees.

6. Complete property-depth slice.
- Per-corner radius inputs.
- Stroke alignment/dash UI + behavior.
- Fill stack reorder and richer paint handling.

7. Add hardening gates before further feature expansion.
- Add focused regression tests around creation persistence, transform commits, and vector/text commit flows.
- Add a lightweight feature coverage checklist that maps each extracted feature file to a code owner and status.
