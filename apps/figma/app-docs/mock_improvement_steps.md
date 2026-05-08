# Mock Improvement Steps

Running list of improvement steps for the Figma mock — **bug fixes**, **UI improvements**, and **feature updates** — surfaced by Codex audits, hands-on exploration, or user-driven scope.

## Conventions

Each entry starts with a status marker and (for bug fixes) a priority:
- `✅ Fixed` / `🟢 Shipped` — closed; **Status** line names the commit that resolved it.
- `🔴 Open` — actionable, not yet fixed.
- `🟡 In progress` — fix in flight (planning / draft / under review).
- `⚪ Wontfix / Deferred` — explicitly deferred; **Status** line records why.

Bug-fix priorities (Codex audit convention):
- **P1** — wrong final document state, undo corruption, runtime crash.
- **P2** — log-stream contract break, missed semantic event, recoverable misbehavior.
- **P3** — forensic/log quality, minor UX or doc rot.

UI improvements and feature updates do not use P-priorities — they're scoped by user request and ordered for safe-first execution.

When an entry ships, update the **Status** line with the commit short SHA and date; do not delete the section (the history is the value). Item numbering is continuous across all three sections (a single sequence preserves stable `#N` references in commits and `delivery-1_updates.md`).

---

## Bug fixes

### 2026-05-07 — User-reported transform polish

#### 22. 🟡 P2 — Flip/rotate selection outline and frame label diverge from the layer transform

**Status:** Fixed in working tree (commit pending).

Files:
- `apps/figma/mock/src/ui/overlays/SelectionOverlay.tsx`
- `apps/figma/mock/src/ui/overlays/ConnectionArrows.tsx`
- `apps/figma/mock/src/ui/canvas/NodeRenderer.tsx`
- `apps/figma/mock/src/engine/coordinates.ts`

**What I expected:** Position panel rotate / flip controls update the selected layer and its visible selection outline together. Child layer outlines and prototype connector handles should follow their parent frame/group/section transform. A flipped frame should keep its "Frame N" chrome label readable, not mirrored by the frame's shape transform.

**What happened:** The layer itself can rotate/flip, but child outlines and prototype plus handles still come from coordinate helpers that only add ancestor `x/y`; they ignore ancestor rotation/flip. Frame labels are also fragile because the "label transform" is inline in `GroupEl` instead of a separately tested transform that explicitly omits flip scale.

**Root cause verified in code:** `SelectionOverlay`, `HoverOutline`, `ParentBoundsOverlay`, line overlays, and prototype handles need visual/rendered-world geometry, but `coordinates.ts` had an explicit limitation: ancestor rotation/scale were not included in `localPointToWorld`. `ConnectionArrows.buildBounds` repeated the same offset-only walk. `NodeRenderer` already tries to render frame labels outside `commonTransform`, but the transform string is not covered by regression tests, making future flip changes easy to break.

**Suggested fix direction:**
- Keep `selectionBbox()` unchanged for drag/resize math and handles until resize becomes transform-aware.
- Make visual geometry helpers use the rendered transform chain, including ancestor rotation/flip.
- Render the single selected non-line/arrow outline as an oriented polygon; keep multi-selection as the existing axis-aligned bbox.
- Position prototype connector handles from transformed frame edge midpoints.
- Extract and test the frame label transform so it never includes `scale(...)`.

### 2026-05-07 — Mock Foundation / Logic Review (Codex audit)

Scope: `apps/figma/mock` foundation and logical correctness review. Focus areas were scene graph mutation, coordinate spaces, undo/redo, semantic logging, outcome document integrity, and architecture consistency.

Verification performed:
- Read Figma app guide and mock logging/architecture docs.
- Reviewed core mock files around `engine/ops.ts`, `engine/dispatch.ts`, `engine/hierarchyCommands.ts`, `engine/alignmentCommands.ts`, `engine/propertyCommands.ts`, logger files, canvas/tools, and prototype UI.
- Ran `npm run typecheck` from `apps/figma/mock`; it passed.

#### 1. ✅ P1 — Reparent keeps stale local coordinates

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

#### 2. ✅ P1 — Cross-parent align/distribute uses local coordinates

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

#### 3. ✅ P2 — Undo snapshots are captured after mutation

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

#### 4. ✅ P2 — Stroke/effect changes are missing semantic events

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

#### 5. ✅ P2 — Prototype document changes bypass ops/undo

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

#### 6. ✅ P3 — Raw event ranges include the previous boundary

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

### 2026-05-07 — Hands-on task runs (manual exploration)

Scope: bugs surfaced while running the 50 delivery-1 tasks by hand, in the order task_01 → task_24 → task_14 → task_09 → task_07. Symptoms reported by the user; reproductions verified before they get filed below.

#### 7. ✅ P2 — Corner-radius slider value is off (possibly % vs px mismatch)

**Status:** Fixed in `b6d6079` (2026-05-07). Investigation showed the data path was px end-to-end (NumericInput → setCornerRadius → set_property → SVG `rx={cr}`); the symptom matched the missing Figma-style drag-scrub on the input label. Added a leftmost drag-scrub strip to NumericInput that updates the displayed value live and fires a single onCommit on pointer-up, so undo history and semantic-event counts aren't inflated by intermediate moves.

**Found while doing:** task_24 (centered modal — scrubbed corner radius to ~16).

**File(s) (best guess):** `apps/figma/mock/src/ui/panels/DesignPanel.tsx` (or wherever the corner-radius input lives) and `apps/figma/mock/src/engine/propertyCommands.ts:setCornerRadius`.

**What I expected:** The corner-radius input/slider applies the entered value as a px integer to `cornerRadius`, and the visible rounding matches that pixel value. (Figma uses px directly; not a % of width.)

**What happened (reported):** Adjusting radius in the design panel didn't behave correctly — the visible rounding seemed proportionally off, possibly because the value is being treated as a percentage of width/height or scaled somewhere. The output may not match the input integer.

**Verify before fix:**
- Pin down whether the displayed input value is the same number that lands in `outcome.document` `cornerRadius`.
- Check whether the renderer applies it as px (correct) vs as a fraction of size.
- If a % path exists, decide whether to remove it or expose it explicitly.

#### 8. ✅ P2 — Alignment buttons need an explicit parent selection

**Status:** Fixed in `5981591` (2026-05-07). New `getSingleSelectionAlignmentContainer` helper resolves the alignment target when a single layer sits inside a non-page frame/group/section; shared between the engine guard and the AlignmentRow disabled state so they cannot drift. Single-child alignment uses the parent's world rect for bounds and converts back to parent-local before dispatching set_transform; existing 2+ layer behavior is unchanged.

**Found while doing:** task_24 (centering a modal rect inside an outer frame — currently must marquee both rect AND frame for alignment to do anything).

**File(s) (best guess):** `apps/figma/mock/src/engine/alignmentCommands.ts` and the right-panel align/distribute buttons.

**What I expected (Figma parity):** When a single child of a frame is selected, the right-sidebar Align Horizontal Centers / Align Vertical Centers buttons align the child to the parent frame automatically — no need to marquee both.

**What happened:** Selecting just the child does nothing for alignment; we must select the frame too. This is non-Figma-like and adds friction for the modal-in-frame flow that task_24 specifically asks for.

**Suggested fix direction:**
- In `alignSelection` / `distributeSelection`, when `layers.length === 1` and the layer has a non-page parent, treat the parent's world rect as the alignment bounds (instead of computing bounds from the single layer, which is a no-op).
- Mind the new world-space code from #2 — the parent's world rect comes from `worldRectOfLayer(s, parentLayer)` for frame/group, or page bounds when parent is the page.
- Distribute (≥3 layers) probably stays the same since it is inherently multi-layer.

#### 9. ✅ P2 — Verifier expects `create_vector` event that mock never emits

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

#### 10. ✅ P2 — Tidy up is a non-functional placeholder

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

### 2026-05-07 — User-driven round (figma/ui-feature-bug)

Scope: hands-on bugs the user surfaced while running the mock, captured for the round on the `figma/ui-feature-bug` branch. Each entry's root-cause hypothesis is verified in code below; live repro is implied where the symptom needs runtime confirmation.

#### 11. ✅ P1 — Canvas layer drag is laggy and jumps left/right

**Status:** Fixed in `9856e93` (2026-05-07). Frame-list and candidate sibling rects are now snapshotted once at drag start; the per-pointermove `applyFrameNestingByOverlap` walk is throttled via `requestAnimationFrame` so it fires at most once per paint frame, with a forced sync flush on pointer-up so the final classification still lands.

**File(s):**
- `apps/figma/mock/src/tools/move.ts` (`onPointerMove` / `active_layer_drag` branch, `applyFrameNestingByOverlap`)
- `apps/figma/mock/src/engine/snap.ts` (snap candidate iteration)

**What I expected:** Smooth 60fps canvas drag. Snap recomputed per frame is fine; reparent decisions only fire at low frequency or at pointer-up.

**What happened (root cause verified):** [move.ts:538](apps/figma/mock/src/tools/move.ts#L538) calls `applyFrameNestingByOverlap` on **every** pointermove event. That function walks the entire scene-graph to collect all frames (line 822-824), then for each moving root walks every frame computing `worldRectOfLayer` + overlap ratio + ancestor checks (line 826-902). On large pages this is O(layers × frames) per frame. When the overlap ratio crosses 0.5, the layer reparents mid-drag, which re-anchors world coordinates (the mover is now in a new parent space) and the next frame snaps relative to the new parent — visible as left/right jumps. Pointer events fire at 60–120Hz; the work overruns the frame budget.

**Suggested fix direction:**
- Throttle `applyFrameNestingByOverlap` to ~60ms (rAF) or run it only when the moving bbox's parent-overlap classification changes (track last classification, only reparent on transition).
- Memoize the frame list per drag (rebuild only if document mutates, which during drag it doesn't apart from this op).
- Memoize candidate sibling rects (line 478-493) per drag — they don't change while dragging.
- Verify snap line buffering doesn't allocate per move; `computeSnap` already returns arrays each call (low risk).

#### 12. ✅ P2 — Frame auto-parent on creation does not nest the new shape

**Status:** Fixed in `e7acfb8` (2026-05-07). `resolveCreationParentId` now falls back to a depth-first walk for the topmost-z-order visible/unlocked frame|section|group whose world rect contains the cursor when no focus context applies. All creation tools route through this resolver, so the fix propagates uniformly.

**File(s):**
- `apps/figma/mock/src/tools/creationBbox.ts` (drag-create resolver — needs verification)
- `apps/figma/mock/src/engine/coordinates.ts` `resolveCreationParentId` (lines 71-84)
- `apps/figma/mock/src/tools/pen.ts`, `pencil.ts`, `line.ts` (each call `resolveCreationParentId` at creation)

**What I expected:** Drawing a shape (rectangle, ellipse, polygon, star, line, arrow, vector via pen/pencil) **inside an existing frame** auto-parents the new layer into that frame, matching real Figma. No need to draw outside the frame and drag back in.

**What happened (root cause verified):** `resolveCreationParentId` at [coordinates.ts:71-84](apps/figma/mock/src/engine/coordinates.ts#L71-L84) only resolves a frame parent **when there is an active focus context** (`focusContextByPage[pageId]`). Without entering the frame (double-click), `focusId == null` → returns the page id. So a shape drawn while pointer is inside an unfocused frame goes to the page, not the frame.

**Suggested fix direction:**
- Make `resolveCreationParentId` look up the deepest visible frame (or section) whose world-rect contains the cursor when focus context is null. Same overlap logic as `applyFrameNestingByOverlap` (item #11), but at creation time → only one walk per click. Negligible cost.
- Walk in z-order top-down so the topmost overlapping container wins.
- Skip locked / hidden frames.
- Apply uniformly to all creation tools (rectangle, ellipse, polygon, star, frame, line, arrow, pen, pencil) — they all funnel through `resolveCreationParentId`.

#### 13. ✅ P2 — Pen-created vector shows wrong selection bounds

**Status:** Fixed in `398b79c` (2026-05-07). New `computeVectorNetworkBounds` helper takes Bezier handle endpoints into the bbox math (conservative versus full cubic-extrema), and pen `syncStore` now uses it so curves whose handles extend past the vertex hull get the correct selection rect. Vector-edit-mode resize (#13 follow-up) does not yet re-normalize bounds — flagged as a known follow-up.

**File(s):**
- `apps/figma/mock/src/tools/pen.ts` `syncStore` (lines 161-256) — bbox tracking during creation.
- `apps/figma/mock/src/engine/selectors.ts` `selectionBbox` (lines 27-42).
- `apps/figma/mock/src/ui/overlays/SelectionOverlay.tsx` + `VectorEditOverlay.tsx`.
- `apps/figma/mock/src/ui/canvas/NodeRenderer.tsx` (vector rendering).

**What I expected:** A pen-drawn vector layer's selection bbox tightly hugs the network's vertices. The displayed (x, y, w, h) on the layer matches `min/max` of vertex positions in world space.

**What happened (needs live repro to disambiguate):** User reports "sınırları doğru göstermiyor" — bounds wrong. `pen.ts` syncStore normalizes vertices to (0,0)..(w,h) and dispatches set_property for x/y/w/h. So during creation bbox should track. Possible causes after creation:
1. Editing handles in `vector` edit mode (post-create) mutates `network` but does not re-normalize the layer's `(x, y, w, h)` → bbox stale.
2. Resize from the SelectionOverlay scales the network with the bbox; if the network has handles whose extent exceeds vertex extent (Bezier handles can stretch outside the polygon hull), the bbox drawn around the layer's `(w, h)` is smaller than the actual visible curve.
3. A single-vertex network normalized with `Math.max(1, w)` floors to 1 — then `ShapeCount` and selection rect look 1×1 instead of empty/invisible.

**Suggested fix direction:**
- Add a `recomputeVectorBounds(layer)` helper that, given a Vector, computes the AABB of the network including Bezier handle reach (de Casteljau evaluation per segment OR the conservative bbox of `vertex ± handle_offset`). Use this everywhere the network mutates (pen syncStore, vector-edit overlay, scale).
- After `mutate_vector_network` op applies, dispatch a follow-up set_property to re-tighten `(x, y, w, h)` (via the same approach as pen syncStore — translate vertices so min is 0).
- Verify with task_07 (mountain range): after drawing a path then selecting it, bbox handles should sit on the visible curve extremes.

#### 14. ✅ P2 — Vector layers lack auto-numbered "Vector N" naming

**Status:** Fixed in `d0f4fcc` (2026-05-07). Both pen and pencil now name new layers `Vector ${countByType(activePage, "vector") + 1}` using the existing helper. Tool attribution stays in the semantic event (`create_vector_with_pen` vs `create_vector_with_pencil`); the layer name no longer leaks "Pencil stroke" into the panel.

**File(s):**
- `apps/figma/mock/src/tools/pen.ts` line 398 — `name: "Vector"` (no ordinal).
- `apps/figma/mock/src/tools/pencil.ts` line 113 — `name: "Pencil stroke"` (different name, no ordinal).

**What I expected:** Real Figma names every newly created layer with a type name + ordinal scoped to the page (e.g. "Vector 1", "Vector 2"). Both pen and pencil tools should produce a layer named **"Vector N"** because the underlying type is `vector` and the user shouldn't see implementation distinctions in the Layers panel. Tool attribution stays in the **semantic event** (`create_vector_with_pen` vs `create_vector_with_pencil`) — that's where forensics belong, not in the layer name.

**What happened:** Pen sets `name: "Vector"` (constant, no ordinal); pencil sets `name: "Pencil stroke"` (different label, no ordinal). Both diverge from how rectangles/ellipses/polygons/etc. are named — see [polygon.ts:12](apps/figma/mock/src/tools/polygon.ts#L12) (`Polygon ${ordinal}` via `countByType(page, "polygon")`).

**Suggested fix direction:**
- Both `pen.ts` `beginNewCreation` (line 384-478) and `pencil.ts` `onPointerUp` (line 110-130) set `name: "Vector " + countByType(page, "vector") + 1`, where `countByType` is the same helper used by `creationBbox.makeCreationBboxTool`. Reuse the existing helper or extract a `countOfType` utility.
- `pen.ts` `beginCreationFromExistingAnchor` (resume an existing vector) leaves the existing name alone.
- Counting by type, not by "all layers", matches Figma's behavior (a fresh polygon among 5 vectors becomes "Polygon 1", not "Layer 6").
- Verifier check: `TextContent` / `LayerName` checks in `delivery-1/` may rely on either name. Search `delivery-1/` for `"Vector"` and `"Pencil stroke"` literals; update verifier checks if any depend on the old name. Log to `delivery-1_updates.md`.

#### 15. 🟡 P1 — Undo silently stops after a few presses (apparent ~5-entry limit)

**Status:** Mitigation shipped in `5b2f7e3` (2026-05-07). ColorPicker exposes onChangeStart/onChangeEnd hooks; PageSection wraps a hue/sat/alpha drag in a single `openTransaction` → many `set_property` ticks → `commitTransaction` so a drag becomes one undo entry. Adds DEV-only `console.debug` at `undo()` and `pushUndoEntry()` so a live repro can distinguish "stack actually empties" from "many micro-entries flood the stack." Other ColorPicker call sites (FillSection, StrokeSection, EffectsSection) keep the old per-tick behavior — wiring them through is a follow-up. Marked 🟡 (in-progress) until live repro confirms the fix or surfaces a different root cause.

**File(s):**
- `apps/figma/mock/src/engine/dispatch.ts` (`UNDO_STACK_MAX = 1000` on line 10 — limit is correct).
- `apps/figma/mock/src/types/ops.ts` (`UNDOABLE_KINDS` set — needs audit).
- `apps/figma/mock/src/util/keymap.ts` lines 197-205 (Cmd/Ctrl+Z keyboard shortcut — fires undo() once per keydown, looks correct).

**What I expected:** Every meaningful document mutation pushes an undo entry. Holding or repeating Cmd/Ctrl+Z walks back through them one-by-one until the stack is empty. Stack max 1000 (per current code) is more than enough.

**What happened (root cause hypothesis — needs live repro):**
- Stack size limit is not the issue (1000 ≫ 5).
- Two plausible root causes:
  1. **Many semantic actions don't produce undoable ops** — e.g. mutating `set_focus_context` / `set_edit_mode` / `set_tool` may NOT be in `UNDOABLE_KINDS`. The user's perceived "5 actions" may include several non-mutation ops which create no undo entries; the stack actually has 5.
  2. **Bundled transactions** — drag-move = 1 transaction = 1 undo entry. The user sees a complex visual change but only 1 entry exists. After 5 transactions of work, undo "runs out."
- Need to audit `UNDOABLE_KINDS` against every Op kind and verify property-panel commits (NumericInput, color picker drag) each produce one transaction per commit (not per intermediate value, and not zero).

**Suggested fix direction:**
- Read [types/ops.ts UNDOABLE_KINDS](apps/figma/mock/src/types/ops.ts) and confirm every op that mutates `document.*` is in the set.
- Property-panel inputs (NumericInput) commit on blur/Enter — ensure that's wrapped in a single transaction so each commit pushes one entry.
- If the issue is "user expected 5 entries but only got 1 because of transaction batching", consider: drag-move is rightfully one entry, but multi-property edits in property panels SHOULD be per-field. Verify behavior matches expectation.
- Add a short developer console log at undo() that prints `undoStack.length` so the user can confirm whether the stack is empty (entries were properly created but consumed) vs the stack never grew (entries weren't created).
- Live repro session needed to disambiguate.

#### 16. ✅ P2 — Hover outline draws at canvas top-left for frame children

**Status:** Fixed in `e62093c` (2026-05-07). `HoverOutline` now reads the world-space rect via `worldRectOfLayer` (matching `selectionBbox`) instead of using local layer coords, so the outline tracks ancestor offsets for nested layers.

**File(s):**
- `apps/figma/mock/src/ui/overlays/HoverOutline.tsx` lines 25-37.

**What I expected:** Hover outline rect rendered tightly around the hovered layer in world space, so the blue thin outline visually wraps the shape regardless of nesting depth.

**What happened (root cause verified):** [HoverOutline.tsx:29-32](apps/figma/mock/src/ui/overlays/HoverOutline.tsx#L29-L32) uses `l.x` and `l.y` directly. Those are **local coordinates** (relative to the parent, e.g. a Frame at world (300, 300) with a child at local (50, 50)). The rect is rendered inside the world-space SVG group. So for a child of a Frame at world (300, 300), the outline draws at (50, 50) instead of (350, 350) — visually it lands at the top-left of the canvas.

**Suggested fix direction:**
- Replace `l.x` / `l.y` / `l.w` / `l.h` with the result of `worldRectOfLayer(useStore.getState(), l)` (already used by `selectionBbox` in `selectors.ts`).
- Keep the same `pointerEvents="none"`, stroke width scaled by `1/zoom`.
- This is a one-file, ~3-line fix; touches no semantic events or store schema.

---

## UI improvements

### 2026-05-07 — Right + Left sidebar polish (figma/ui-feature-bug)

#### 17. 🟢 — Right sidebar (no-selection) Page section incomplete + Share button still active

**Status:** Shipped in `4f43ba6` (2026-05-07). Page section split into swatch + hex input + opacity % + hide-eye toggle (with `Page.backgroundHidden` driving a checker-pattern backdrop on canvas when hidden). Local-styles + Export sections dropped per user request. Share is now `aria-disabled` with `cursor:not-allowed` and no click handler. New events: `set_page_background_opacity`, `toggle_page_background_hidden`. Existing `set_page_background` event keeps its name and gains an optional `trigger`.

**File(s):**
- `apps/figma/mock/src/ui/chrome/RightPanel.tsx` lines 60-77 (no-selection branch), 116-135 (Share button).
- `apps/figma/mock/src/ui/panels/PageSection.tsx` lines 39-90 (Page + Local-styles + Export sections).
- `apps/figma/mock/src/types/scene.ts` `Page` (line 317-326) — needs `backgroundHidden: boolean` added.
- `apps/figma/mock/src/types/events.ts` — new semantic events: `set_page_background_opacity`, `toggle_page_background_hidden`.

**Expected behavior (research-backed):** When nothing is selected, the right sidebar shows:
1. Header (zoom, profile placeholder "A", Present icon, **Share button as inactive** — 50% opacity, neutral grey background, `cursor: not-allowed`, `aria-disabled="true"`, no click handler / no toast).
2. Tabs row (Design active / Prototype).
3. **No** sub-header.
4. **Page section** with:
   - Color swatch (14×14) + **directly editable hex input** (typing a valid hex commits the color).
   - **Opacity input** (default 100%, % suffix) — maps to `page.backgroundColor.a × 100`. Editable; clamp 0–100. Per Figma help docs, clicking 100% opens an inline numeric input.
   - **Eye toggle (Hide icon)** — toggles a new boolean `page.backgroundHidden`. When hidden, the canvas background renders transparent (CSS checker-pattern over the canvas root), and outcome.document keeps the field so verifiers can read it.
5. **Local styles + Export sections: omit entirely** for this round (user choice; both are visual-only `○` per state-matrix).

**Current state:**
- `RightPanel.tsx:64` `<PageSection />` renders Page + Local-styles + Export. Drop the latter two from PageSection or guard them behind a flag.
- `PageSection.tsx:42-73` combines swatch + hex into a single click-to-open-picker button. Needs split: swatch button (opens picker) + standalone hex input + opacity input + hide toggle.
- `RightPanel.tsx:116-135` Share button uses Figma blue `var(--color-selection-blue)` background — currently looks active. Apply inactive treatment.

**New ops + semantic events:**
- `set_property` already covers `page.backgroundColor` mutations (current `setBg` in PageSection.tsx already dispatches one). Reuse for opacity (mutates `backgroundColor.a`) and for `backgroundHidden`.
- New semantic events:
  - `set_page_background_opacity { pageId, before, after, trigger }` — fires when opacity input commits.
  - `toggle_page_background_hidden { pageId, before, after, trigger }` — fires when eye icon clicked.
- Existing `set_page_background` event keeps firing for hex/color-picker changes; add a `trigger` field if missing to distinguish hex-input vs color-picker.

**Verifier impact (delivery-1):** `Page.backgroundColor` is already part of `outcome.document`. Adding `backgroundHidden` extends the outcome shape — verifiers that use it can opt in via a new check primitive (`PageBackgroundHidden`). No existing verifier should break since they don't read the new field. Log to `delivery-1_updates.md` if any check primitives change.

#### 18. 🟢 — Left sidebar lacks "Layers" section header

**Status:** Shipped in `e61028b` (2026-05-07). Added a `LayersHeader` row above `<LayersTree />` styled to match the Pages header. Real Figma omits this label; the deviation is intentional (user-requested) and noted in code.

**File(s):**
- `apps/figma/mock/src/ui/chrome/LeftPanel.tsx` lines 11-36 (root layout).
- `apps/figma/mock/src/ui/panels/LayersTree.tsx` (rendered directly in LeftPanel without a wrapping header).

**Expected behavior:** The left sidebar's Pages section already has a clear "Pages" uppercase header ([LeftPanel.tsx:130-159](apps/figma/mock/src/ui/chrome/LeftPanel.tsx#L130-L159)). The Layers section below it should have a matching **"Layers" header** (uppercase, small caps, same style as Pages header). NO sidebar-close icon (mock-specific deviation from real Figma's minimize-UI button — which lives at the top-right of the file-name row in Figma but the user explicitly said don't add it).

The far-left icon column (`LeftRail`) keeps its current inactive `noopClick` behavior — the user said leave it alone.

**Current state:**
- `LeftPanel.tsx:32` renders `<LayersTree />` directly inside the scroll area with no header.
- No close icon currently rendered. ✓ matches user request.

**Suggested fix direction:**
- Add a `LayersHeader` div above `<LayersTree />` styled identically to the Pages header (`fs-xs`, uppercase, letter-spacing 0.4, font-weight 600, padding 6px 12px 4px).
- No `+` button on the right (Pages has add-page; Layers has no equivalent).
- Optional: collapse-all chevron icon on the right (matches real Figma's collapse-layers-icon) — defer this if it adds scope.

**Real-Figma divergence note:** Real Figma does NOT render an explicit "Layers" label — it just has an implicit collapse-all icon. Adding the label is a mock-specific deviation, deliberately chosen by the user for clarity. Document this in a code comment so future agents don't "fix" it back.

---

## Feature updates

### 2026-05-07 — File rename + Rotation panel + Shape geometry (figma/ui-feature-bug)

#### 19. 🟢 — File rename (Untitled → editable inline)

**Status:** Shipped in `159a6e2` (2026-05-07). Single-click on the file name enters edit mode (Enter/blur commits, Escape cancels, empty trim falls back to "Untitled"). Backed by a new `SetDocumentNameOp` (separate from `set_property` because `DocumentNode` isn't in `nodesById`), added to `UNDOABLE_KINDS`, with apply/inverse handlers. Emits `rename_file` semantic event.

**File(s):**
- `apps/figma/mock/src/ui/chrome/LeftPanel.tsx` lines 38-72 (`FileNameRow`).
- `apps/figma/mock/src/types/scene.ts` `DocumentNode` (line 328-332) — needs a `name` field.
- `apps/figma/mock/src/engine/store.ts` (initial state — `document.name = "Untitled"`).
- `apps/figma/mock/src/types/events.ts` — new semantic event `rename_file`.

**Expected behavior (research-backed):** Per Figma help center, **single-click on the file name** enters edit mode. The name becomes a text input with the existing value pre-selected. **Enter** or **blur** commits. **Escape** cancels. Empty/whitespace-only commits revert to "Untitled" (or to the previous name). No documented length cap; mock should trim and cap at ~255 chars. The chevron next to the name keeps its current behavior (opens the file menu — currently `noopClick`).

**Current state:** `FileNameRow` is a single button with `onClick = noopClick("file-menu.open", ...)` and the literal text "Untitled". No edit affordance.

**Suggested fix direction:**
- Add `name: string` to `DocumentNode`; default `"Untitled"`. Existing log/outcome shape unchanged otherwise — `outcome.document` already serializes the document; the new field rides along.
- Convert `FileNameRow` to the same click-to-edit pattern used by `LeftPanel.tsx PageRow` (lines 226-253) and `LayersTree.tsx`. Local `useState` for `editing`. Single-click on the **name span** → enter edit. Click on the chevron → file-menu noop (existing behavior).
- New command `renameFile(name, trigger)` in a new or existing engine command file, dispatching `set_property` on the document.
- Emit `rename_file { before, after, trigger: "inline_edit" | "file_menu" }` semantic event on commit.
- Add `name` to `outcome.document` serialization in `logger/outcome.ts` if not already covered by the generic walk.

**Verifier impact:** New optional check primitive `FileNameEquals(expected: str)` for tasks that ask the user to rename. Don't add unless a delivery-1 task needs it; otherwise keep dormant.

#### 20. 🟢 — Rotation panel (4 controls in Position section)

**Status:** Shipped in `3918f85` + `7feb73f` (2026-05-07). Position section gains a rotation row with degree input (`((value % 360) + 360) % 360` normalization at commit), Rotate-90° button (new `rotate90Selection` mirroring `flipSelection`, single transaction, one `rotate_layer` event with `panel_button` trigger), and Flip-H / Flip-V buttons reusing `flipSelection` with the new `panel_button` trigger value. Existing keyboard shortcuts (Shift+H/V) and drag-rotate path are unchanged.

**File(s):**
- `apps/figma/mock/src/ui/panels/PositionSection.tsx` (current panel — adds rotation row).
- `apps/figma/mock/src/engine/transformCommands.ts` — already has `flipSelection`; needs `rotate90Selection`.
- `apps/figma/mock/src/engine/propertyCommands.ts` `setTransformField` — needs rotation normalization (mod 360).
- `apps/figma/mock/src/types/events.ts` — `rotate_layer` event already exists (move.ts line 627); reuse it. New events for `flip_layer` (per direction) likely already exist via `flipSelection`; verify.

**Expected behavior:** The Position section should have a Rotation row below the X/Y row, with 4 controls (matching the user's reference screenshot):
1. **Degree input** with `°` suffix. Accepts any numeric value (negative, positive, magnitudes > 360). On commit, normalize to `((value % 360) + 360) % 360` so `-1060 → 20°` (per user's spec). Edits all selected layers' `rotation` field via `set_transform`. Already partially implemented at [PositionSection.tsx:27-29](apps/figma/mock/src/ui/panels/PositionSection.tsx#L27-L29) but lacks normalization.
2. **Rotate 90° clockwise** icon button — adds 90° to each layer's rotation, normalized. Rotation pivot = each layer's own center (NOT the selection bbox center). Single semantic event `rotate_layer { trigger: "panel_rotate_90" }`.
3. **Flip horizontal** icon button — calls `flipSelection("horizontal", "panel_button")`. Pivot = each layer's own center.
4. **Flip vertical** icon button — calls `flipSelection("vertical", "panel_button")`. Pivot = each layer's own center.

**Current state:** PositionSection has X, Y, ∠ (rotation input). Rotation input doesn't normalize. No icon buttons. `flipSelection` exists in `transformCommands.ts` and is wired to keyboard shortcuts (Shift+H / Shift+V) per [keymap.ts:296-307](apps/figma/mock/src/util/keymap.ts#L296-L307); reuse it.

**Suggested fix direction:**
- Add rotation-normalization in `setTransformField` when path === "rotation": `value = ((value % 360) + 360) % 360`.
- Add `rotate90Selection(trigger)` to `engine/transformCommands.ts` modeled after `flipSelection`. Per-layer: `newRot = ((layer.rotation + 90) % 360 + 360) % 360`. Single transaction, one `set_transform` op for all selected layers, one semantic `rotate_layer` event.
- PositionSection: replace the lone rotation row with a row of 4 controls — degree NumericInput (existing) + 3 icon buttons. Use Lucide icons: `RotateCw` (90°), `FlipHorizontal2`, `FlipVertical2`.
- Per-layer-center pivot for both flip and rotate-90 is the existing behavior in `flipSelection`/`set_transform` — verify in `applyOp` for `set_transform` that `(x, y)` is recomputed so each layer's center stays put.

**Verifier impact:** Verifiers checking `rotation` property (e.g. a "draw a square rotated 45°" task) should still work. The rotate-90 button only adds to rotation, doesn't change geometry shape. Flip already exists. No verifier breakage expected.

#### 21. 🟢 — Polygon/star sides count + line/arrow as 2-point geometry

**Status:** Shipped across `7960353` (sub 21a, 21b) and `ec3cb2e` (sub 21c, 21d) (2026-05-07). 21a: Polygon `sides` editable via new ShapeOptionsSection (3..60). 21b: Star `points` (3..60) + `innerRatio` (% in UI, 0..1 stored) editable; StarEl renderer drops the legacy `[0.05, 0.95]` clamp so the panel and canvas agree. 21c: SelectionOverlay renders a line stroke + 2 endpoint markers on top of the bbox for single line/arrow selection (visual only — bbox handles stay until 21f ships proper endpoint-drag resize). 21d: hit-test uses point-to-segment distance for line/arrow with a stroke-weight + zoom-aware threshold so selection feels right at any zoom level. New events: `set_polygon_sides`, `set_star_points`, `set_star_inner_ratio`. **Sub-item 21f (line endpoint-drag resize) deferred** — needs a custom move-tool handle path; tracked as a separate follow-up.

**File(s):**
- `apps/figma/mock/src/types/scene.ts` `Polygon`, `Star`, `Line`, `Arrow` (lines 165-198). Possible `Line.height = 0` invariant.
- `apps/figma/mock/src/tools/polygon.ts`, `star.ts`, `line.ts` (defaults + creation).
- `apps/figma/mock/src/ui/panels/AppearanceSection.tsx` (or new `ShapeOptionsSection`) — `sides` / `points` / `innerRatio` controls.
- `apps/figma/mock/src/ui/canvas/NodeRenderer.tsx` — switch line/arrow rendering from rect-wrapped to stroked SVG `<line>` (or path).
- `apps/figma/mock/src/ui/overlays/SelectionOverlay.tsx` + `move.ts` handle code — line/arrow get a custom 2-point selection (overlay + 2 endpoint handles), not 8-handle bbox.
- `apps/figma/mock/src/engine/selectors.ts` `hitTest` — line/arrow hit-test uses point-to-segment distance, not rect-contains.
- `apps/figma/mock/src/engine/snap.ts`, `engine/alignmentCommands.ts` — sibling rects for lines need verification (current `worldRectOfLayer` returns the bbox; for a 45° line that's a square — semantically wrong for snap/align, but visually acceptable for now; flag as out-of-scope).
- `apps/figma/mock/src/engine/propertyCommands.ts` — new `setPolygonSides`, `setStarPoints`, `setStarInnerRatio` commands.
- `apps/figma/mock/src/types/events.ts` — `set_polygon_sides`, `set_star_points`, `set_star_inner_ratio` semantic events.

**Expected behavior (research-backed):**

**Polygon:**
- `sides` editable, min 3, max 60 (mirroring Star — Figma docs don't cap polygon explicitly but 60 is the practical UI cap). Default 3.
- Renders as a regular polygon inscribed in the bbox (top vertex at `-90°`). Bbox does NOT tightly hug the visible shape — this matches Figma so adding sides keeps the bbox stable.
- New "Count" control in AppearanceSection (or a new `ShapeOptionsSection` shown when selection type is polygon/star).

**Star:**
- `points` editable, min 3, max **60** (Figma hard cap, help-center confirmed).
- `innerRatio` editable as a percentage (UI shows %, store keeps 0..1). Min 0.0, max 1.0. Default 0.5 (mock keeps current default; real Figma uses ~0.382 — `[gap]`, flag in code comment).
- Renders as a star inscribed in the bbox (outer points on inscribed circle/ellipse, inner points on circle of radius `outerR × innerRatio`). Bbox same convention as polygon.
- New "Count" + "Ratio" controls in AppearanceSection.

**Line / Arrow (CRITICAL refactor):**
- Figma's `LineNode` is `(x, y, width, rotation)` with `height = 0`. The current mock stores `{ p1, p2 }` as offsets within an axis-aligned bbox — equivalent geometry but the **rendering** treats lines as rectangles. KEEP the current `Line { p1, p2 }` representation BUT change rendering and selection:
  - **Rendering** (`NodeRenderer.tsx`): draw an SVG `<line>` from world-space p1 to p2 with the stroke applied. NO rectangle. The bbox `(x, y, w, h)` derives from `min/max(p1, p2)` and may be axis-aligned (which is what current line.ts produces).
  - **Selection** (`SelectionOverlay.tsx`): for line/arrow, render a single overlay line on top of the path + 2 endpoint handles (small blue squares at p1, p2) + rotation cursors just outside endpoints. NO 8-handle bbox.
  - **Hit-test** (`selectors.ts hitTest`): for line/arrow, use point-to-segment distance ≤ `(strokeWeight / 2 + 4) / zoom`. Current `contains` uses rect-contains which is too loose (clicks anywhere in the bounding rect register, even far from the visible line).
  - **Resize**: dragging an endpoint handle moves only that endpoint (changes both `p1`/`p2` and consequently `(x, y, w, h)`). Shift constrains to 15° angle increments (matches `constrainShift` already in line.ts).
  - **Stroke**: alignment locked to `center` for lines/arrows (Figma rule). Disable inside/outside in StrokeSection when selection is line/arrow.
  - **Stroke caps** (`endCapStart`/`endCapEnd` for arrows; `Line` may need them too — see below). Render arrowheads as decorative markers on the SVG line endpoints.
- **Width profile + Arrow interaction:** applying a width profile to an arrow strips its arrowhead per Figma rule. Defer this — it's a follow-up. Flag as `[gap-deferred]`.
- **Optional small refactor:** add `endCapStart` / `endCapEnd` to `Line` so the Stroke section can render the start/end cap dropdowns Figma shows for any open path. This makes Line and Arrow uniform internally; the toolbar Arrow tool just defaults `endCapEnd = "arrow"`. Mock currently keeps Arrow as a separate `type: "arrow"` — keep that for now to avoid touching every reference, but consider migrating `Line` to have caps too.

**New ops + semantic events:**
- `set_property` already handles `sides` / `points` / `innerRatio` if AppearanceSection wires them through `setProp`-style commands. Add convenience commands `setPolygonSides(layerId, n)`, `setStarPoints(layerId, n)`, `setStarInnerRatio(layerId, r)` that dispatch `set_property` and emit semantic events.
- Semantic events: `set_polygon_sides { layerId, before, after }`, `set_star_points`, `set_star_inner_ratio`. These extend the existing taxonomy and don't clash with anything.

**Verifier impact (delivery-1):**
- Polygon `PolygonSidesEquals` — already exists per architecture doc. Verifier reads `sides` from outcome — the field already exists in mock's Polygon type. No verifier change.
- Star `StarPointsEquals` — already exists. Same — no change.
- Line/Arrow geometry: any verifier that reads line `(x, y, w, h)` to derive direction may need to read `p1`/`p2` instead. Search delivery-1 for `line` / `arrow` checks. If any task verifies "this line goes diagonally from corner to corner" by checking bbox width and height, it still works (current line.ts already encodes this). If a verifier checks rotation derived from bbox, it might be buggy — verify.
- Hit-test change: any task verifier that relies on click-to-select on a line does NOT exist (verifiers don't simulate clicks). No impact.
- Selection overlay change: visual only, doesn't touch outcome.

**Sequencing:** This item is the biggest in the round. Strongly recommend implementing AFTER all bug fixes and other UI/feature items so any breakage in shape geometry is isolated for review. Within this item, sequence: polygon sides → star points/ratio → line/arrow rendering (smallest engine change) → line/arrow selection → line/arrow hit-test.
