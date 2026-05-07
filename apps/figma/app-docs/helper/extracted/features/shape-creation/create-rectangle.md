# Create rectangle

- **Category:** shape-creation
- **One-line summary:** Place a rectangle layer on the canvas by dragging with the Rectangle tool.

## Triggers
- Keyboard: `R` — activates Rectangle tool.
- Toolbar: Shape-tools dropdown → Rectangle (default sub-tool of the dropdown).

## Preconditions
- Tool is set to Rectangle.
- Pointer is over canvas area.

## Inputs
- Pointer-down coordinates (canvas space).
- Pointer-move deltas while drag is active (to size the rectangle).
- Pointer-up coordinates.
- Modifiers:
  - `Shift` held during drag — constrain to square (equal W and H).
  - `Alt/Option` held — draw from center instead of corner.
  - Both — both behaviors.
- Click without drag (or very small drag) — insert default-size rectangle (common editor convention: ~100×100 or 1×1 per platform).

## Behavior
1. On tool activation: cursor becomes insertion crosshair.
2. On pointer-down: record start coordinates; begin live-preview rectangle outline.
3. On pointer-move: update the rectangle's W and H to match current pointer position relative to start, respecting modifiers.
4. On pointer-up: commit — create a new rectangle layer with the resulting X/Y/W/H. Parent = current page OR the frame/section under the pointer-up position if nested.
5. Selection becomes the new rectangle. Tool reverts to Move tool (standard "place and select" pattern, per docs).

## Outputs
- **Scene graph changes:** one new rectangle layer created. Default properties:
  - `type: "rectangle"`
  - `x`, `y`, `w`, `h` from drag extents
  - `fill: [{ type: "solid", color: default }]` (default often light gray or a library default — `plan/03` decision)
  - `stroke: []`
  - `cornerRadius: 0`
- **Selection changes:** selection = `[new_rectangle_id]`.

## UI feedback
- Cursor: insertion crosshair → arrow (after commit).
- Canvas: live-preview outline while dragging; W×H label near cursor.
- Left panel: new layer row added at top of layer list.
- Right panel: switches to single-shape selection view.
- Toolbar: Rectangle button's active highlight drops after commit.

## Side effects
- Undo stack: adds a "create rectangle" entry; `undo` removes the layer.
- Focus: canvas retains focus.

## Related UI schema entries
- `regions/toolbar.md` → shape-tools-dropdown
- `regions/canvas-overlays.md` → insertion-crosshair, selection-bounding-box
- `state-matrix.md` → Single shape row

## Semantic event(s) candidate
- `create_rectangle { x, y, w, h, parent_id | null, modifiers: { shift, alt }, trigger: "shortcut_R" | "toolbar" }`

## Source articles
- `basic-shape-tools-in-figma-design`
- `access-design-tools-from-the-toolbar`
- `frames-in-figma-design` (frame vs rectangle context)

## Notes / gaps
- Default fill color not specified; `plan/03` decision (sensible default: neutral light gray).
- Click-without-drag insert size not specified; pick ~100×100 default.
