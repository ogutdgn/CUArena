# Scale with the Scale tool

- **Category:** transform
- **One-line summary:** Uniformly scale objects including strokes, text, corner radii, and nested children using the Scale tool (distinct from raw resize).

## Triggers
- Keyboard: `K` — activates Scale tool.
- Toolbar: Move-tools dropdown → Scale.

## Preconditions
- Selection is non-empty.

## Inputs
- Drag a corner or edge handle of the selection with the Scale tool active.
- Modifiers: `Shift` (preserve aspect — default for Scale tool in many flows), `Alt` (scale from center).

## Behavior
1. Scale tool active: bounding-box handles take on Scale semantics rather than Resize semantics.
2. Pointer-down on handle: record initial scale factor reference.
3. Pointer-move: compute uniform scale factor from handle drag; apply to the selection.
4. Scaling multiplies every affected property proportionally: `w/h`, stroke weight, corner radius, font size (for text children), and children's positions.
5. Pointer-up: commit.

## Outputs
- **Scene graph changes:** for each affected layer, numeric properties scale by the same factor — this is distinct from resize (which changes only `w/h` and leaves stroke, corner radius, and children untouched).
- **Selection changes:** none.

## UI feedback
- Cursor: resize/scale style while over handles.
- Scale factor readout near cursor (or updated W×H label).
- All strokes / text / radii visibly scale in real time.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/toolbar.md` → move-tools-dropdown (Scale sub-tool)
- `regions/canvas-overlays.md` → selection-bounding-box (handles behave differently when Scale tool is active)

## Semantic event(s) candidate
- `scale_layer { layer_ids: [...], scale_factor: {sx, sy}, anchor: {x, y}, modifiers: { shift_uniform, alt_center }, trigger: "scale_tool_drag" }`

## Source articles
- `access-design-tools-from-the-toolbar` (Scale tool entry)
- `adjust-alignment-rotation-position-and-dimensions`

## Notes / gaps
- "Resize" vs "Scale" distinction is fundamental in Figma and must be preserved in the engine model. Resize affects W/H only; Scale affects everything (strokes, text, children, corner radii).
- Multi-selection scale anchor: group center by default.
