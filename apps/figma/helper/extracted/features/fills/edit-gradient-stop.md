# Edit gradient stop (add / move / remove / recolor)

- **Category:** fills
- **One-line summary:** Manage the color stops of a gradient — add, move, remove, recolor — via the picker's stop slider or the on-canvas gradient handle.

## Triggers
- **Add stop:** Click anywhere along the gradient color slider in the picker, OR click `+` next to **Stops** in the gradient settings.
- **Move stop:** Click + drag a stop on the picker's slider OR on the on-canvas gradient handle.
- **Remove stop:** Select a stop and press `Delete`, OR click `-` next to it in the gradient settings.
- **Recolor stop:** Select a stop → picker swatches and color inputs apply to that stop.
- **Flip gradient:** click **Flip gradient** button (reverses stop order).
- **Rotate gradient:** click **Rotate gradient** button (cycles 90° rotation).

## Preconditions
- A gradient fill exists (any subtype).

## Inputs
- Pointer click / drag / Delete key.

## Behavior
1. Each stop has `position` (0-100%) and `color` (incl. opacity).
2. Adding a stop interpolates color from neighbors.
3. Removing a stop is allowed only if at least 2 remain.
4. Stops can hold a color **variable** binding — see `color/library-colors-browser.md`. To detach: hover a stop with a variable and click "Detach variable".

## Outputs
- **Scene graph changes:** gradient's `stops` array mutated.
- **Selection changes:** none.

## UI feedback
- Picker stop slider updates; canvas gradient updates live.

## Side effects
- Undo stack: one entry per picker session.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → gradient-controls (stops, flip, rotate)
- `regions/canvas-overlays.md` → gradient-handle

## Semantic event(s) candidate
- `add_gradient_stop { layer_ids, fill_index, position, color, trigger }`
- `move_gradient_stop { layer_ids, fill_index, stop_index, from_position, to_position, trigger }`
- `remove_gradient_stop { layer_ids, fill_index, stop_index, trigger }`
- `set_gradient_stop_color { layer_ids, fill_index, stop_index, from_color, to_color, trigger }`
- `flip_gradient { layer_ids, fill_index }`
- `rotate_gradient { layer_ids, fill_index }`

## Source articles
- `use-gradients-as-a-fill-or-stroke`

## Notes / gaps
- Whether removing a stop when only two remain is silently ignored or shows feedback is not stated.
