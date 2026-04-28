# Create ellipse

- **Category:** shape-creation
- **One-line summary:** Place an ellipse (or circle) layer by dragging with the Ellipse tool.

## Triggers
- Keyboard: `O` — activates Ellipse tool.
- Toolbar: Shape-tools dropdown → Ellipse.

## Preconditions
- Tool set to Ellipse.
- Pointer over canvas.

## Inputs
- Pointer-down + pointer-move + pointer-up.
- Modifiers: `Shift` (constrain to circle), `Alt` (draw from center).

## Behavior
1. Tool activation: cursor becomes crosshair.
2. Pointer-down: record start (corner of bounding box).
3. Pointer-move: live-preview ellipse inscribed in the drag rectangle; W×H label shows size.
4. Pointer-up: commit ellipse with bounding `x/y/w/h`.
5. Selection = new ellipse. Tool reverts to Move.
6. Arc handles become available on the new selection (see `regions/canvas-overlays.md` → arc-handles-ellipse).

## Outputs
- **Scene graph changes:** one new ellipse.
  - `type: "ellipse"`
  - `x`, `y`, `w`, `h`.
  - `fill: [{ type: "solid", color: default }]`
  - Arc-specific: `arcStartAngle: 0`, `arcEndAngle: 360`, `innerRadius: 0`.
- **Selection changes:** selection = new ellipse.

## UI feedback
- Crosshair during placement; live preview.
- New layer in Layers panel.
- Right panel: single-shape view. Arc handles on the ellipse itself.

## Side effects
- Undo stack: adds "create ellipse" entry.

## Related UI schema entries
- `regions/toolbar.md` → shape-tools-dropdown
- `regions/canvas-overlays.md` → arc-handles-ellipse

## Semantic event(s) candidate
- `create_ellipse { x, y, w, h, parent_id | null, modifiers: { shift, alt }, trigger: "shortcut_O" | "toolbar" }`

## Source articles
- `basic-shape-tools-in-figma-design`
- `arc-tool-create-arcs-semi-circles-and-rings`

## Notes / gaps
- None.
