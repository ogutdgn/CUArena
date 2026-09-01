# Lock aspect ratio

- **Category:** transform
- **One-line summary:** Constrain a layer's W:H ratio so that resizing in one dimension automatically scales the other proportionally.

## Triggers
- Right sidebar **Layout / Auto layout** section → click the lock-aspect-ratio icon.
- Modifier-on-drag:
  - **`Shift`** while resizing from canvas → temporarily locks aspect ratio for the duration of the drag.
  - **`⌃ Control`** while resizing on canvas with lock already on → temporarily disables lock.

## Preconditions
- A layer selected.

## Inputs
- Click on the lock icon, OR keyboard modifier during a resize.

## Behavior
1. Lock toggle stored on the layer.
2. With lock on:
   - Typing W → H updates proportionally; or vice versa.
   - Dragging a resize handle scales 2D proportionally.
3. With lock off:
   - W and H change independently.
4. Min/max dimensions: if min/max set on a layer with lock on, the other dimension's min/max is set proportionally (for layers with auto-layout-coupled min/max).
5. Lock is unavailable on instance children (per article).

## Outputs
- **Scene graph changes:** layer's `lock_aspect_ratio` flag set.
- **Selection changes:** none.

## UI feedback
- Lock icon shows locked vs unlocked state.
- Live resize obeys lock during drag.

## Side effects
- Undo stack: one entry per toggle.

## Related UI schema entries
- `regions/right-properties.md` → layout-section → lock-aspect toggle

## Semantic event(s) candidate
- `set_lock_aspect_ratio { layer_ids, to_state, trigger: "panel_icon" }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`

## Notes / gaps
- Cross-references `transform/scale-with-scale-tool.md` for K-key proportional scale.
