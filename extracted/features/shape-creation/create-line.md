# Create line

- **Category:** shape-creation
- **One-line summary:** Draw a straight line segment by dragging with the Line tool.

## Triggers
- Keyboard: `L` — activates Line tool.
- Toolbar: Shape-tools dropdown → Line.

## Preconditions
- Tool set to Line.
- Pointer over canvas.

## Inputs
- Pointer-down + pointer-move + pointer-up.
- Modifiers:
  - `Shift` — constrain to 0°/15°/30°/45°/... angle increments.
  - `Alt/Option` — draw from center (both endpoints equidistant from start point).

## Behavior
1. On tool activation: cursor becomes crosshair.
2. On pointer-down: record start point (first endpoint).
3. On pointer-move: live-preview line from start to current pointer; angle snaps if `Shift` held.
4. On pointer-up: create line layer with the two endpoints. If drag distance is near-zero, create a 1-unit line (or no-op — `plan/03` decision).
5. Selection = new line. Tool reverts to Move.

## Outputs
- **Scene graph changes:** one new line layer.
  - `type: "line"`
  - Two endpoints: `p1 = start`, `p2 = end`
  - `stroke: [{ type: "solid", color: default, weight: 1 }]`
  - No fill (line is stroke-only).
- **Selection changes:** selection = new line.

## UI feedback
- Crosshair while placing; live line preview during drag.
- New layer appears in Layers panel.
- Right panel switches to single-shape view with Stroke section (no Fill for pure lines).

## Side effects
- Undo stack: adds "create line" entry.

## Related UI schema entries
- `regions/toolbar.md` → shape-tools-dropdown
- `regions/canvas-overlays.md` → insertion-crosshair

## Semantic event(s) candidate
- `create_line { p1: {x, y}, p2: {x, y}, parent_id | null, modifiers: { shift, alt }, trigger: "shortcut_L" | "toolbar" }`

## Source articles
- `basic-shape-tools-in-figma-design`
- `access-design-tools-from-the-toolbar`

## Notes / gaps
- Default stroke color + weight not specified; `plan/03` decision.
- Whether line is stored as a vector path (2-point) or a special "line" primitive not documented — engine decision.
