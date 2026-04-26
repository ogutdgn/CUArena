# Where we left off... (April 26, 2026 — updated session 2)

## 1) Current branch and latest shipped changes
- Active working branch: `ogutdgn/vibe-fixes` (not yet pushed at time of writing).
- Latest commits on this branch (newest first):
  - `fddc95b` — `fix(layout): prevent grid row expansion by adding min-height: 0 to panel flex containers` *(also includes scale tool)*
  - `feat(scale): implement scale tool with proportional stroke/radius/font scaling on commit` *(part of above commit)*
  - Previous commits from first vibe-fixes merge: pen anchor-drag fixes, VectorEditOverlay/pen conflict fix.

## 2) What is now fixed (session 2 additions)

1. **Pen anchor-drag Immer freeze crash**
- Root cause: `creation.segments.slice()` passes same object references to `op.after`; Immer freezes those objects inside `useStore.setState`; next `onPointerMove` tries to mutate frozen objects → `TypeError: Cannot assign to read only property 'handleTo'`.
- Fix pattern: replace `inSeg.handleTo = {...}` with `creation.segments[inSegIdx] = {...creation.segments[inSegIdx], handleTo: {...}}` — creates new object, assigns by array index (the new array from `.slice()` is NOT frozen).
- Files changed: `test-app/src/tools/pen.ts`

2. **VectorEditOverlay intercepts pen tool pointer events**
- Root cause: `editMode` stays `"vector"` when switching to pen via `K` shortcut; `VectorEditOverlay` renders and calls `e.stopPropagation()` in `startDrag`, blocking pen tool from receiving events.
- Fix: (a) In `setTool()` in `keymap.ts`, dispatch `set_edit_mode → none` when switching to pen. (b) In `VectorEditOverlay`, add `activeTool === "pen"` to early-return guard.
- Files changed: `test-app/src/util/keymap.ts`, `test-app/src/ui/overlays/VectorEditOverlay.tsx`

3. **Scale tool implemented** (was `noopTool`)
- `K` key now activates a real scale tool.
- Handle drag: same resize math as move tool (live w/h feedback via `set_transform`).
- On commit (pointer up): proportionally scales stroke weights, corner radii, font sizes via `set_property` ops in the same transaction (undo-able together).
- Scale factor uses geometric mean of `sx`/`sy` for property scaling.
- Known V1 gap: children of frames/groups are NOT recursively scaled yet.
- Files changed: `test-app/src/tools/scale.ts` (new), `test-app/src/tools/index.ts`

4. **CSS Grid layout bug — toolbar and sidebar pushed off-screen on selection**
- Root cause: `<aside>` elements (LeftPanel, RightPanel) lacked `min-height: 0`. CSS Grid's `1fr` row expanded to fit the flex children's content height (which grows when selection shows all the property panels), pushing the `1fr` row to 861px instead of the 633px viewport.
- Fix: add `minHeight: 0, overflow: "hidden"` to both `<aside>` elements, and `minHeight: 0` to their `flex: 1` scroll containers.
- Verified in browser: toolbar visible at bottom after selection; canvas container correctly 633px (= viewport height).
- Files changed: `test-app/src/ui/chrome/RightPanel.tsx`, `test-app/src/ui/chrome/LeftPanel.tsx`

## 3) What is still missing (updated P0–P2)

## P0 (highest impact)
1. Constraint reflow during parent frame resize
- Spec: `extracted/features/properties/set-constraints.md`
- Current: constraints can be set in panel, but no child reflow logic during parent frame resize.
- Scale tool children scaling (recursive, for frames/groups) is the same P0 pass.

## P1 (high)
1. Right-panel sidebar field parity vs actual Figma — **NEW**
- The sidebar fields have NOT been compared against actual Figma behavior across all states:
  - No selection → page properties (color, variables)
  - Single layer of each type (rectangle, ellipse, text, vector, frame, group, section, image, etc.)
  - Multi-select
  - Frame-child with constraints
  - Vector edit mode
  - Text edit mode
- Different modes produce different sidebar field sets in Figma; our mock may be missing fields, showing extra fields, or firing wrong events.
- Tracked as **Slice F**: `plan/slice-f-sidebar-parity.md`

2. Pen/vector parity still incomplete
- Handle-type toggle toolbar flow (corner/mirror-angle/mirror-length) is partial.
- Shift angle constraints and Alt asymmetric handle behavior not implemented.
- Close/open path ergonomics still limited.

3. Text range model incomplete
- No first-class caret/range state.
- `runs` are not fully managed as editable formatting ranges.

4. Layers panel same-parent-only reorder
- `reorderLayerInPanel` returns early when parent differs; no cross-parent reparent.

## P2 (medium)
1. Creation parent resolution inconsistency — several tools hardcode `parentId = activePageId`.
2. Select-all recursion — top-level only; doesn't include nested unlocked descendants.
3. Image placement toolbar button — visual-only, not wired.

## 4) Recommended next execution queue

### Slice B (P0): Constraint reflow + scale children
1. Implement child constraint reflow when parent frame is resized.
2. Add recursive children scaling to scale tool commit path.

Acceptance checks:
- Children reflow per constraint mode (left/right/center/stretch/scale) when parent frame is resized.
- Scale tool drag also rescales all descendants proportionally.
- Undo/redo is deterministic.

### Slice F (P1): Right-panel sidebar parity review
The sidebar fields shown in the right panel change based on selection state, layer type, and tool/edit mode. We haven't verified our implementation against actual Figma. Need to compare by a human, and provide screenshots/findings to the agent to implement fixes.

Acceptance checks:
- A human compares each sidebar state (no selection, each layer type, multi-select, vector edit mode, text edit mode) against real Figma and documents the gaps.
- Agent receives the gap list and fixes missing/wrong sections, field visibility conditions, and mis-wired events.
- TypeScript typechecks pass after changes.

### Slice C (P1): Pen/vector completion
1. Add explicit handle-type toggle flow in vector edit mode.
2. Shift angle constraints; Alt asymmetric handle.
3. Close/open path parity improvements.

### Slice D (P1): Text range parity
1. Explicit caret/range state in text edit mode.
2. Range-aware typography updates; mixed-value reflection.

### Slice E (P1/P2): Layers + creation consistency
1. Cross-parent drag reparent in layers panel.
2. Unify creation parent resolution.
3. Fix `select-all` recursion.

## 5) Practical note for next implementer
- Always read `extracted/features/<category>/<feature>.md` before changing behavior.
- For sidebar parity work, use `analysis/panel-states.md` as a reference; final comparison must be done against actual Figma.
- TypeScript typechecks pass with `npx tsc --noEmit` (pre-existing unrelated errors in `move.ts` and `line.ts` are known and not blocking).
