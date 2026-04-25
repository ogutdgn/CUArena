# Create polygon

- **Category:** shape-creation
- **One-line summary:** Place a regular polygon by dragging with the Polygon tool.

## Triggers
- Toolbar: Shape-tools dropdown → Polygon. No default keyboard shortcut.

## Preconditions
- Tool set to Polygon.
- Pointer over canvas.

## Inputs
- Pointer-down + pointer-move + pointer-up.
- Modifiers: `Shift` (constrain to regular aspect), `Alt` (draw from center).

## Behavior
1. Tool activation: crosshair cursor.
2. Pointer-down: start point (bounding box corner).
3. Pointer-move: live-preview polygon inscribed in drag rectangle. Default side count = 3 (triangle).
4. Pointer-up: commit polygon with sides = 3, bounding `x/y/w/h`.
5. Selection = new polygon. Tool reverts to Move.
6. After creation, side count can be increased via the right panel (Appearance / count control) or a canvas handle.

## Outputs
- **Scene graph changes:** one new polygon.
  - `type: "polygon"`
  - `x`, `y`, `w`, `h`.
  - `sides: 3` (default triangle)
  - `fill: [{ type: "solid", color: default }]`
- **Selection changes:** selection = new polygon.

## UI feedback
- Live preview during drag.
- New layer in panel.
- Right panel shows a side-count control (not covered precisely in corpus but visible in shape-appearance contexts).

## Side effects
- Undo stack: adds "create polygon" entry.

## Related UI schema entries
- `regions/toolbar.md` → shape-tools-dropdown

## Semantic event(s) candidate
- `create_polygon { x, y, w, h, sides, parent_id | null, modifiers: { shift, alt }, trigger: "toolbar" }`

## Source articles
- `basic-shape-tools-in-figma-design`

## Notes / gaps
- Where the side-count control lives in the right panel not explicitly documented; put it under Appearance.
