# Convert shape to vector network (enter vector edit on a shape)

- **Category:** vector
- **One-line summary:** Pressing Enter on a primitive shape (rectangle, ellipse, polygon, star) enters vector edit mode on it; the shape is exposed as an editable vector network with its native vertices.

## Triggers
- Select a shape layer → press `Enter` (or `Return`).
- Right-click → **Edit object** (or equivalent).

## Preconditions
- Selected layer is a primitive shape OR a vector layer.

## Inputs
- `Enter` key.

## Behavior
1. Editor switches to vector edit mode.
2. The shape's native points become editable:
   - Rectangle → 4 corner points.
   - Ellipse → 4 cardinal points (top/right/bottom/left); curve handles connect them.
   - Polygon (N) → N corner points.
   - Star (N points) → 2N points (alternating outer/inner).
3. Editing points (move, add, delete) makes the layer no longer a "primitive" — it becomes a custom vector network. Properties unique to the primitive (e.g. polygon point count, star inner-ratio, ellipse arc handles) may be lost or preserved per implementation.
4. The user's referenced workflow ("Vector Shapes - Circle into 3M circle") corresponds to entering vector edit on an ellipse and adding additional points along its perimeter.

## Outputs
- **Scene graph changes:** layer type may transition from `ellipse` / `polygon` / etc. to `vector` after first edit (or stay as the primitive type with an internal vector representation, per engine choice).
- **Selection changes:** sub-selection of vector points; layer-level selection unchanged.

## UI feedback
- Toolbar swaps to vector-edit secondary toolbar (Move / Pen / Bend / Lasso / Cut / Paint / Variable width / Shape builder).
- Selection box hidden; vector points + handles visible instead.

## Side effects
- Undo stack: per-edit entries; entering edit mode itself unaffected.

## Related UI schema entries
- `regions/toolbar.md` → secondary toolbar (vector edit)
- `regions/canvas-overlays.md` → vector-points-and-handles

## Semantic event(s) candidate
- `enter_vector_edit_mode { layer_id, trigger: "enter_key" | "context_menu" }`
- (Subsequent point edits use `add_vector_point.md`, `move_vector_point.md`, etc.)

## Source articles
- `edit-vector-layers`
- `vector-networks`
- `shape-tools`

## Notes / gaps
- Real Figma transitions a primitive to a "vector network" representation transparently when you make non-primitive edits; the layer's type label updates accordingly.
