# Bugs Found

Running list of bugs and structural risks found during audits of the Figma mock app.

---

## 2026-05-07 - Mock Foundation / Logic Review

Scope: `apps/figma/mock` foundation and logical correctness review. Focus areas were scene graph mutation, coordinate spaces, undo/redo, semantic logging, outcome document integrity, and architecture consistency.

Verification performed:
- Read Figma app guide and mock logging/architecture docs.
- Reviewed core mock files around `engine/ops.ts`, `engine/dispatch.ts`, `engine/hierarchyCommands.ts`, `engine/alignmentCommands.ts`, `engine/propertyCommands.ts`, logger files, canvas/tools, and prototype UI.
- Ran `npm.cmd run typecheck` from `apps/figma/mock`; it passed.

### 1. P1 - Reparent keeps stale local coordinates

Files:
- `apps/figma/mock/src/engine/ops.ts`
- Call sites include `apps/figma/mock/src/engine/hierarchyCommands.ts`

`applyReparent` only removes a layer from its old parent array, inserts it into the new parent array, and updates `parentId`. It does not convert `x/y` from the old parent coordinate space into the new parent coordinate space.

Why this matters:
- `outcome.document` stores layer geometry in parent-space coordinates.
- Moving a top-level object into a frame/group, or moving a child out of a group, should preserve world position by recalculating local `x/y`.
- Current behavior can visually shift layers and corrupt geometry that verifiers read from `outcome.document`.

Impacted flows:
- Grouping selected layers.
- Ungrouping.
- Layers panel drag/drop across parents.
- Any future generic reparent command.

Evidence:
- Drag-to-frame nesting has a special follow-up `set_transform` to compensate after `reparent`, which strongly suggests the generic `reparent` op is missing this invariant.

Suggested fix direction:
- Either make `applyReparent` preserve world position by default, or require `ReparentOp` to carry explicit before/after local transforms.
- Ensure group/ungroup and panel drag do not need separate ad hoc coordinate fixes.
- Add focused tests around top-level -> frame, frame -> page, group -> parent, and nested parent changes.

### 2. P1 - Cross-parent align/distribute uses local coordinates

File:
- `apps/figma/mock/src/engine/alignmentCommands.ts`

`alignSelection` and `distributeSelection` compute selection bounds using raw `l.x/l.y/l.w/l.h`, then write those local values back to layers. This is only correct when every selected layer shares the same parent coordinate space.

Why this matters:
- A top-level layer and a frame child can both be selected.
- Their local coordinates are not comparable.
- Alignment/distribution can place layers incorrectly in world space and produce invalid final geometry in `outcome.document`.

Suggested fix direction:
- Compute bounds in world space using existing coordinate helpers.
- Convert each final world position back to the layer's own parent space before dispatching `set_transform`.
- Add tests for mixed-parent alignment and same-parent alignment to preserve current behavior.

### 3. P2 - Undo snapshots are captured after mutation

File:
- `apps/figma/mock/src/engine/dispatch.ts`

For non-transaction undoable ops, `dispatch` applies the operation first and only then creates the undo entry. It records `selectionBefore` and `focusContextBefore` from the already-mutated state.

Why this matters:
- `applyDeleteNodes` clears stale selection/focus references when deleted nodes are removed.
- Undo can restore the layer tree but not restore the selection/focus state that existed before deletion.
- This conflicts with the architecture contract that scene graph undo restores selection snapshots.

Suggested fix direction:
- Capture selection/focus before applying undoable non-transaction ops.
- Keep `selectionAfter`/`focusContextAfter` from the post-apply state.
- Add regression coverage for delete -> undo restoring both the node and the selected id.

### 4. P2 - Stroke/effect changes are missing semantic events

File:
- `apps/figma/mock/src/engine/propertyCommands.ts`

Several outcome-changing property commands dispatch `set_property` but do not emit semantic events. Examples include:
- `setStrokeWeight`
- `addSolidStroke`
- `addDropShadowEffect`
- `addLayerBlurEffect`
- `removeEffect`
- `setEffectField`
- `setEffectColor`
- `setStrokeColor`

Why this matters:
- Final `outcome` may still be correct.
- The `semantic[]` stream undercounts meaningful user operations.
- Efficiency scoring and forensic debugging become less reliable.
- This violates the stated mock contract that every meaningful operation is represented semantically.

Suggested fix direction:
- Emit either specific semantic events where the schema has them, or a generic `set_property` semantic event with path/before/after.
- Make the property command layer consistent: if a command changes document state, it should dispatch an op and emit semantic intent.
- Add a small audit/test that all property panel commands produce semantic events.

### 5. P2 - Prototype document changes bypass ops/undo

Files:
- `apps/figma/mock/src/ui/panels/PrototypePanel.tsx`
- `apps/figma/mock/src/ui/overlays/ConnectionArrows.tsx`
- `apps/figma/mock/src/ui/overlays/InteractionModal.tsx`

Prototype settings, flows, connections, and scroll behavior mutate `document` with direct `useStore.setState` calls instead of going through `engine/dispatch.ts` and typed ops.

Examples:
- Setting prototype device.
- Adding/removing/renaming flows.
- Creating/deleting/updating prototype connections.
- Setting overflow scrolling and scroll position.

Why this matters:
- These mutations can appear in `outcome.document`, but undo/redo cannot restore them.
- The implementation breaks the foundation rule that document mutations go through ops.
- The UI layer now owns document mutation details, which makes future verifier/log contract changes riskier.

Suggested fix direction:
- Introduce prototype-specific ops or reuse `set_property` with structured paths.
- Move prototype mutations behind engine command functions.
- Preserve semantic events, but let ops own undo/redo and state mutation.

### 6. P3 - Raw event ranges include the previous boundary

File:
- `apps/figma/mock/src/logger/semantic.ts`

`rawEventIdRange` is currently built as `[lastEmittedRawId, rawId]`. That means every semantic event after the first includes the previous semantic event's final raw event as the start of its range.

Why this matters:
- Raw slices overlap by one event.
- Replay/debug tooling that expects "raw events since the last semantic event" gets ambiguous boundaries.
- It is not likely to affect outcome scoring directly, but it weakens forensic quality.

Suggested fix direction:
- Track the first raw event after the previous semantic event, not the previous semantic event's boundary.
- Alternatively document the range as inclusive-overlapping if this is intentional, though the current docs describe it as events since the last semantic event.

