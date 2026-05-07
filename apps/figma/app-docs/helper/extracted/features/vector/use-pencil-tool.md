# Use Pencil tool (freehand)

- **Category:** vector
- **One-line summary:** Freehand-draw a stroke; Figma applies smoothing to produce a vector network.

## Triggers
- Toolbar: Creation-tools dropdown → Pencil. No default keyboard shortcut in UI3 Figma Design (corpus doesn't list one).

## Preconditions
- Tool set to Pencil.
- Pointer over canvas.

## Inputs
- Pointer-down + pointer-move (freehand path trace) + pointer-up.

## Behavior
1. Tool activation: crosshair + pencil-icon cursor.
2. Pointer-down: begin a new freehand stroke at that point.
3. During pointer-move: accumulate raw points of the pointer trajectory.
4. On pointer-up: simplify the accumulated path (curve-fitting to reduce point count while preserving shape), producing a vector network.
5. Commit as a new vector layer.

## Outputs
- **Scene graph changes:** one new vector layer from the simplified path.
  - `type: "vector"`
  - `points: [...]` from simplification
  - `stroke: [{ type: "solid", color: default, weight: default }]`
  - `fill: []`
  - `closed: false`
- **Selection changes:** selection = new vector.
- **Mode state change:** after commit, tool reverts to Move (standard place-and-select behavior).

## UI feedback
- Cursor: pencil glyph.
- Canvas: live stroke rendering as the user drags.
- On release: stroke smooths; simplified path visible.

## Side effects
- Undo stack: one entry per pencil stroke.

## Related UI schema entries
- `regions/toolbar.md` → creation-tools-dropdown (Pencil)

## Semantic event(s) candidate
- `create_vector_with_pencil { layer_id, raw_points_count, simplified_points_count, trigger: "toolbar" }`

## Source articles
- `access-design-tools-from-the-toolbar`

## Notes / gaps
- Smoothing tolerance / algorithm not specified. Use a Douglas-Peucker or spline-fit approximation; tune at build time.
- Figma Draw's Pencil is a more advanced version of this tool with brush styles. That is out of scope per plan/00 §3.
