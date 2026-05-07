# Bugs Found

Running list of bugs and structural risks found in the Figma mock app.

## Conventions

Each bug section starts with a status marker and priority:
- `✅ Fixed` — closed; **Status** line names the commit that resolved it.
- `🔴 Open` — actionable, not yet fixed.
- `🟡 In progress` — fix in flight (planning / draft / under review).
- `⚪ Wontfix / Deferred` — explicitly deferred; **Status** line records why.

Priorities (per Codex audit convention):
- **P1** — wrong final document state, undo corruption, runtime crash.
- **P2** — log-stream contract break, missed semantic event, recoverable misbehavior.
- **P3** — forensic/log quality, minor UX or doc rot.

When a bug ships, update the **Status** line with the commit short SHA and date; do not delete the bug section (the history is the value).

---

## 2026-05-07 — Mock Foundation / Logic Review (Codex audit)

Scope: `apps/figma/mock` foundation and logical correctness review. Focus areas were scene graph mutation, coordinate spaces, undo/redo, semantic logging, outcome document integrity, and architecture consistency.

Verification performed:
- Read Figma app guide and mock logging/architecture docs.
- Reviewed core mock files around `engine/ops.ts`, `engine/dispatch.ts`, `engine/hierarchyCommands.ts`, `engine/alignmentCommands.ts`, `engine/propertyCommands.ts`, logger files, canvas/tools, and prototype UI.
- Ran `npm run typecheck` from `apps/figma/mock`; it passed.

### 1. ✅ P1 — Reparent keeps stale local coordinates

**Status:** Fixed in `07657e9` (2026-05-07).

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

### 2. ✅ P1 — Cross-parent align/distribute uses local coordinates

**Status:** Fixed in `1897504` (2026-05-07).

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

### 3. ✅ P2 — Undo snapshots are captured after mutation

**Status:** Fixed in `e2fd631` (2026-05-07).

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

### 4. ✅ P2 — Stroke/effect changes are missing semantic events

**Status:** Fixed in `998d429` (2026-05-07).

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

### 5. ✅ P2 — Prototype document changes bypass ops/undo

**Status:** Fixed in `41fd1c8` (2026-05-07).

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

### 6. ✅ P3 — Raw event ranges include the previous boundary

**Status:** Fixed in `c080a6a` (2026-05-07).

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

---

## 2026-05-07 — Hands-on task runs (manual exploration)

Scope: bugs surfaced while running the 50 delivery-1 tasks by hand, in the order task_01 → task_24 → task_14 → task_09 → task_07. Symptoms reported by the user; reproductions verified before they get filed below.

### 7. ✅ P2 — Corner-radius slider value is off (possibly % vs px mismatch)

**Status:** Fixed in `b6d6079` (2026-05-07). Investigation showed the data path was px end-to-end (NumericInput → setCornerRadius → set_property → SVG `rx={cr}`); the symptom matched the missing Figma-style drag-scrub on the input label. Added a leftmost drag-scrub strip to NumericInput that updates the displayed value live and fires a single onCommit on pointer-up, so undo history and semantic-event counts aren't inflated by intermediate moves.

**Found while doing:** task_24 (centered modal — scrubbed corner radius to ~16).

**File(s) (best guess):** `apps/figma/mock/src/ui/panels/DesignPanel.tsx` (or wherever the corner-radius input lives) and `apps/figma/mock/src/engine/propertyCommands.ts:setCornerRadius`.

**What I expected:** The corner-radius input/slider applies the entered value as a px integer to `cornerRadius`, and the visible rounding matches that pixel value. (Figma uses px directly; not a % of width.)

**What happened (reported):** Adjusting radius in the design panel didn't behave correctly — the visible rounding seemed proportionally off, possibly because the value is being treated as a percentage of width/height or scaled somewhere. The output may not match the input integer.

**Verify before fix:**
- Pin down whether the displayed input value is the same number that lands in `outcome.document` `cornerRadius`.
- Check whether the renderer applies it as px (correct) vs as a fraction of size.
- If a % path exists, decide whether to remove it or expose it explicitly.

### 8. ✅ P2 — Alignment buttons need an explicit parent selection

**Status:** Fixed in `5981591` (2026-05-07). New `getSingleSelectionAlignmentContainer` helper resolves the alignment target when a single layer sits inside a non-page frame/group/section; shared between the engine guard and the AlignmentRow disabled state so they cannot drift. Single-child alignment uses the parent's world rect for bounds and converts back to parent-local before dispatching set_transform; existing 2+ layer behavior is unchanged.

**Found while doing:** task_24 (centering a modal rect inside an outer frame — currently must marquee both rect AND frame for alignment to do anything).

**File(s) (best guess):** `apps/figma/mock/src/engine/alignmentCommands.ts` and the right-panel align/distribute buttons.

**What I expected (Figma parity):** When a single child of a frame is selected, the right-sidebar Align Horizontal Centers / Align Vertical Centers buttons align the child to the parent frame automatically — no need to marquee both.

**What happened:** Selecting just the child does nothing for alignment; we must select the frame too. This is non-Figma-like and adds friction for the modal-in-frame flow that task_24 specifically asks for.

**Suggested fix direction:**
- In `alignSelection` / `distributeSelection`, when `layers.length === 1` and the layer has a non-page parent, treat the parent's world rect as the alignment bounds (instead of computing bounds from the single layer, which is a no-op).
- Mind the new world-space code from #2 — the parent's world rect comes from `worldRectOfLayer(s, parentLayer)` for frame/group, or page bounds when parent is the page.
- Distribute (≥3 layers) probably stays the same since it is inherently multi-layer.

### 9. ✅ P2 — Verifier expects `create_vector` event that mock never emits

**Status:** Fixed in `b87f10b` (2026-05-07). All 6 affected verifiers (07/08/19/39/42/49) now check `create_vector_with_pen` since every prompt asks for the pen tool. task_08 / task_39 minimums lowered to 1 because their prompts duplicate a single pen vector to reach the final shape count (geometry rubric still enforces ≥2 / ≥3 final vectors). Mock event emission unchanged — pen vs pencil attribution preserved in the log.

**Found while doing:** task_07 (mountain range, two pen-tool paths). Document state is correct; the gap is purely on the action-log contract.

**File(s):**
- Mock: `apps/figma/mock/src/tools/pen.ts` (and any pencil tool file) — currently emits `create_vector_with_pen` and `create_vector_with_pencil`.
- Verifier: `apps/figma/delivery-1/task_07/verifier.py` — expects `EventTypeCountAtLeast("create_vector", 2)`.

**What happens:** Verifier `Event` rubric does an exact-match check on the event name `create_vector`. Mock emits `create_vector_with_pen` / `create_vector_with_pencil` instead, so the check returns 0 for any pen/pencil-built run. The Event rubric tops out at ~0.165 / 0.33 and the final pre-efficiency score caps around 0.835 — a perfect run cannot reach 1.0.

**Fix direction (decided):** Verifier-side. The log MUST keep tool attribution (`_with_pen` vs `_with_pencil`) for forensic value, so we will not collapse to a generic `create_vector` event. Each task's verifier matches the tool the task prompt specifies — pen tasks check `create_vector_with_pen`, pencil tasks check `create_vector_with_pencil`. Mock event emission stays as-is.

**Scope (6 tasks across `delivery-1/`):**
| Task | Tool the prompt asks for | Current verifier event | Should be |
|---|---|---|---|
| task_07 (mountain range) | pen | `create_vector` | `create_vector_with_pen` |
| task_08 (water waves)    | pen (Bezier)  | `create_vector` | `create_vector_with_pen` |
| task_19 (padlock — pen U-shackle) | pen | `create_vector` | `create_vector_with_pen` |
| task_39 (wifi arcs) | pen | `create_vector` | `create_vector_with_pen` |
| task_42 (bell pen-arc accent?) | pen | `create_vector` | `create_vector_with_pen` (verify in prompt before flipping) |
| task_49 (S-curve ribbon) | pen | `create_vector` | `create_vector_with_pen` |

Each prompt should be re-read to confirm pen vs pencil before flipping; if any task is genuinely pencil, point its verifier at `create_vector_with_pencil`.

### 10. ✅ P2 — Tidy up is a non-functional placeholder

**Status:** Fixed in `887853c` (2026-05-07). `tidySelection` added to alignmentCommands.ts following the helper spec: 1D vs 2D detection (2D classified before 1D-overlap check so grids with slight row overlap aren't collapsed), gap mode with mean fallback, column-aware positioning so variable-width grids line up, no-op when already tidy. `tidy_up` semantic event added to the schema. AlignmentRow's disabled-placeholder button is now wired to the real action.

**Found while doing:** task_09 (12-color 4×3 swatch grid — prompt says "use Tidy up to lock the grid arrangement"; the button is disabled and titled "Tidy up — not implemented").

**Files:**
- `apps/figma/mock/src/ui/panels/AlignmentRow.tsx:44` — button rendered with `disabled visualOnly`, no real handler.
- `apps/figma/mock/src/engine/alignmentCommands.ts` — has `alignSelection` / `distributeSelection` but no `tidySelection`.

**Helper spec exists:** `apps/figma/app-docs/helper/extracted/features/alignment/tidy-up.md`. Summary:
- 2+ layers required.
- Detect 1D (single row/column) vs 2D (grid) layout.
- 1D: align on perpendicular axis + equalize primary-axis spacing using the **mode** (most common spacing) as the target gap.
- 2D: arrange layers in a grid using the selection's bbox top-left as anchor; vertical + horizontal spacing computed independently.
- Should emit a single semantic event `tidy_up { layer_ids, dimension: "1d_horizontal" | "1d_vertical" | "2d", computed_spacing, trigger }`.
- One undo entry.
- Outputs scene-graph X/Y mutation (no resize, no parent change).

**Suggested fix direction:**
- Add `tidySelection(trigger)` to `engine/alignmentCommands.ts`. Reuse world-space helpers (#2 fix) so a tidy that crosses parents still lands correctly.
- Detect dimension from world-space bounds: count distinct rows / columns within a tolerance.
- Add `tidy_up` to `types/events.ts` SemanticEvent union.
- Wire the button in `AlignmentRow.tsx` (drop `disabled visualOnly`, add real `onClick`).
- task_09 verifier doesn't require the event, but task prompt does — implementing this aligns user-visible behavior with the prompt and unblocks any future verifier that adds `tidy_up` checks.
