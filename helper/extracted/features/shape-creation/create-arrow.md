# Create arrow

- **Category:** shape-creation
- **One-line summary:** Draw a directional arrow (line with arrowhead) by dragging with the Arrow tool.

## Triggers
- Keyboard: `Shift L` — activates Arrow tool (per docs; may vary by rollout).
- Toolbar: Shape-tools dropdown → Arrow.

## Preconditions
- Tool set to Arrow.
- Pointer over canvas.

## Inputs
- Pointer-down + pointer-move + pointer-up.
- Modifiers: same as line (`Shift` for angle constraint, `Alt` for centered draw).

## Behavior
1. Tool activation: cursor becomes crosshair.
2. Pointer-down: start point.
3. Pointer-move: live-preview arrow (line + arrowhead at pointer end).
4. Pointer-up: create arrow layer with `p1 = start`, `p2 = end`; arrowhead at `p2`.
5. Selection = new arrow. Tool reverts to Move.

## Outputs
- **Scene graph changes:** one new arrow layer.
  - `type: "arrow"` (or line with `endCap: "arrow"`)
  - Two endpoints.
  - `stroke` with end-cap marker.
- **Selection changes:** selection = new arrow.

## UI feedback
- Same as create-line, plus the arrowhead is part of the live preview.
- Right panel: stroke section shows end-cap option with "arrow" preselected.

## Side effects
- Undo stack: adds "create arrow" entry.

## Related UI schema entries
- `regions/toolbar.md` → shape-tools-dropdown

## Semantic event(s) candidate
- `create_arrow { p1: {x, y}, p2: {x, y}, parent_id | null, modifiers: { shift, alt }, trigger: "shortcut_shift_L" | "toolbar" }`

## Source articles
- `basic-shape-tools-in-figma-design`
- `access-design-tools-from-the-toolbar`

## Notes / gaps
- Whether "arrow" is its own primitive or a line with an end-cap is an engine decision.
