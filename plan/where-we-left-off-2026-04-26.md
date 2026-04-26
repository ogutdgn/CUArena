# Where we left off... (April 26, 2026)

## 1) Current branch and latest shipped changes
- Active working branch: `codex/caygar/vibe-fixes` (pushed to `origin/caygar/vibe-fixes`).
- Latest commits on this branch:
  - `790c7e5` — `fix(preview): match shape drag fill colors to final created layers`
  - `c3d9b5d` — `fix(pen): auto-finish active pen session when changing tools`
  - `ef3013b` — `fix(pen): stabilize anchor-edit sessions and append preview behavior`

## 2) What is now fixed
1. Shape creation preview fill parity
- During drag-create, preview now uses the same fill family as final created layer defaults (instead of hollow/blue-tint preview mismatch).
- Includes rectangle/ellipse/polygon/star/frame/section; slice remains dashed; line/arrow remain stroke-only.

2. Pen session reliability
- Pen no longer gets stuck across tool switches.
- Existing-anchor pen sessions are more stable (explicit append-vs-edit state, preview guardrails).

## 3) User complaints and workflow constraints captured in `last-point.md`
The strongest recurring complaints in `last-point.md` are process/quality constraints that should drive implementation order:
1. Analyze before deciding: always ground behavior in `extracted/features/*` (and OpenPencil reference when needed), not ad-hoc choices.
2. Scope discipline: prioritize Tier-2 functional parity gaps; avoid drifting into out-of-scope functionality.
3. Realistic delivery: avoid broad “done” claims when parity gaps remain.

These constraints are now reflected in the prioritized next queue below.

## 4) What is still missing (mapped to `extracted/features/*`)

## P0 (highest impact)
1. Pen anchor-drag curve generation is still unreliable
- Specs: `extracted/features/vector/use-pen-tool.md`, `extracted/features/vector/toggle-vector-handle.md`
- User repro: click to place points, then click-drag an anchor; only bbox/existing lines are visible and no live curve/curve commit is observed.
- Required acceptance:
  - With Pen active, click-dragging an existing anchor always shows live handle + curve preview.
  - Releasing pointer commits visible bezier curvature on affected segments.
  - Close-path click behavior still works (click without drag on start anchor).

2. Scale tool is still a stub
- Spec: `extracted/features/transform/scale-with-scale-tool.md`
- Current: tool registry maps `scale` to `noopTool`.
- Impact: major transform parity gap (K tool visible but non-functional).

3. Constraints are writable but not behaviorally enforced
- Spec: `extracted/features/properties/set-constraints.md`
- Current: constraints can be set in panel, but no child reflow logic during parent frame resize.
- Impact: core frame/layout behavior divergence from docs.

## P1 (high)
1. Pen/vector parity is improved but still incomplete
- Specs: `extracted/features/vector/use-pen-tool.md`, `toggle-vector-handle.md`, `close-open-vector-path.md`
- Current gaps:
  - Handle-type parity is partial (no full corner/mirror-angle/mirror-length toolbar flow).
  - Close/open path parity still limited to implemented interaction paths.
  - Continuation ergonomics still below expected fidelity.

2. Text range model is incomplete
- Specs: `extracted/features/text/select-text-range.md`, `set-text-properties.md`
- Current: text edit is contentEditable-first and caret-end initialization works, but no first-class range state/range formatting model.
- Impact: mixed-range typography behaviors are missing.

3. Layers panel drag reorder is same-parent only
- Spec: `extracted/features/layers/reorder-layer.md`
- Current: drag-drop early-returns when `dragged.parentId !== target.parentId`.
- Impact: no cross-parent panel reparenting flow.

## P2 (medium)
1. Creation parent resolution inconsistency
- Specs: shape/region creation flows under `extracted/features/shape-creation/*` and `region-tools/*`
- Current: multiple creation tools still hardcode `parentId = activePageId` instead of contextual parent placement.

2. Select-all recursion gap
- Spec: `extracted/features/selection/select-all.md`
- Current: selection walk is top-level only in current command path.

3. Image placement entrypoint mismatch
- Spec: `extracted/features/shape-creation/place-image.md`
- Current: drag-drop/shortcut path works, toolbar image item remains visual-only.

## 5) Recommended next execution queue

### Slice A0 (P0): Pen anchor-drag hotfix
1. Harden anchor hit detection for pen handle drags (avoid silent miss paths).
2. Separate click-to-close from drag-intent so handle drags never resolve as close-click.
3. Ensure live curve previews are always visible during handle drag.

Acceptance checks:
- Existing-anchor drag reliably produces preview curves and committed bezier curves.
- Start-anchor click without drag still closes path.
- Start-anchor drag creates handles instead of accidentally closing.
- Console shows `[pen-debug]` lifecycle logs for anchor hit, handle drag vectors, and close-vs-drag resolution while validating this bug.

### Slice A (P0): Transform parity
1. Implement real Scale tool behavior (`K`) in tool registry + move/resize math path.
2. Distinguish resize vs scale semantics per spec (strokes/text/radii/children scaling in Scale mode).
3. Add semantic events for scale commits.

Acceptance checks:
- `K` tool can drag handles and visibly scales strokes/text/radii/children.
- Resize tool remains resize-only.
- Undo/redo returns exact pre-scale geometry and styles.

### Slice B (P0): Constraint reflow
1. On parent frame resize, apply child constraint rules (`left/right/center/stretch/scale`, `top/bottom/center/stretch/scale`).
2. Ensure constraint logic does not run outside frame-child context.

Acceptance checks:
- Child layers reflow according to horizontal/vertical modes when parent frame is resized.
- Undo/redo preserves deterministic reflow results.

### Slice C (P1): Pen/vector completion
1. Add explicit handle-type toggle flow in vector edit mode.
2. Complete close/open path interactions in edit mode parity paths.
3. Polish endpoint continuation UX consistency.

Acceptance checks:
- Handle type changes are visible, persistent, and undoable.
- Close/open path interactions match feature docs paths.

### Slice D (P1): Text range parity
1. Add text edit state for selection range (`start/end`) and mixed-style detection.
2. Apply typography controls to active range (not whole layer only).

Acceptance checks:
- Shift+arrow and drag-selection maintain range.
- Range formatting updates only selected characters and supports mixed values.

### Slice E (P1/P2): Layers + creation consistency
1. Enable cross-parent layer drag reparent from layers panel.
2. Unify creation parent resolution across bbox/line/pen/text creation paths.
3. Fix `select-all` recursion over nested containers.

Acceptance checks:
- Panel drag can move items between containers.
- New objects land in expected focused/contextual parent consistently.
- Select-all includes nested unlocked descendants.

## 6) Practical note for next implementer
Before changing behavior, read the corresponding `extracted/features/<category>/<feature>.md` file first and encode acceptance checks directly from that spec. This addresses the exact quality/process complaint called out in `last-point.md` (analyze-before-deciding).
