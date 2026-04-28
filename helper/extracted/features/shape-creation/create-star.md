# Create star

- **Category:** shape-creation
- **One-line summary:** Place a star shape by dragging with the Star tool.

## Triggers
- Toolbar: Shape-tools dropdown → Star. No default keyboard shortcut.

## Preconditions
- Tool set to Star.
- Pointer over canvas.

## Inputs
- Pointer-down + pointer-move + pointer-up.
- Modifiers: `Shift` (constrain aspect), `Alt` (draw from center).

## Behavior
1. Tool activation: crosshair.
2. Pointer-down: start.
3. Pointer-move: live-preview star inscribed in drag rectangle. Default points = 5, inner ratio = ~0.5.
4. Pointer-up: commit star with bounds + default point count and inner ratio.
5. Selection = new star. Tool reverts to Move.
6. After creation, point count + inner ratio editable via right panel.

## Outputs
- **Scene graph changes:** one new star.
  - `type: "star"`
  - `x`, `y`, `w`, `h`.
  - `points: 5`, `innerRatio: 0.5` (defaults)
  - `fill: [{ type: "solid", color: default }]`
- **Selection changes:** selection = new star.

## UI feedback
- Live preview during drag.
- Right panel: single-shape view with point-count + inner-ratio controls.

## Side effects
- Undo stack: adds "create star" entry.

## Related UI schema entries
- `regions/toolbar.md` → shape-tools-dropdown

## Semantic event(s) candidate
- `create_star { x, y, w, h, points, inner_ratio, parent_id | null, modifiers: { shift, alt }, trigger: "toolbar" }`

## Source articles
- `basic-shape-tools-in-figma-design`

## Notes / gaps
- Default point count (5) and inner ratio (0.5) not numerically confirmed in corpus; sensible defaults assumed.
