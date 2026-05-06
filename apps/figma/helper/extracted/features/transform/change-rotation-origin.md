# Change rotation origin

- **Category:** transform
- **One-line summary:** Move the pivot point used by rotation operations from the layer's geometric center to a custom location.

## Triggers
- Selection non-empty + shortcut:
  - Mac: `⌥ R`
  - Windows: `Alt R`
- Reveals a rotation-origin target on the canvas.
- Drag the target to reposition the rotation origin.

## Preconditions
- One or more layers selected.

## Inputs
- Shortcut to reveal target.
- Pointer drag on the target.

## Behavior
1. By default, rotation origin = layer's geometric center.
2. After custom origin is set, all subsequent rotations (via canvas rotate handle, panel input, or drag) pivot around the new origin.
3. The custom origin is per-layer (not session global).

## Outputs
- **Scene graph changes:** layer's `rotation_origin: {x, y}` updated (or back to default if reset).
- **Selection changes:** none.

## UI feedback
- Rotation-origin target visible after shortcut.
- Subsequent rotations pivot around the visible origin.

## Side effects
- Undo stack: one entry per origin change.

## Related UI schema entries
- `regions/canvas-overlays.md` → rotation-origin-target

## Semantic event(s) candidate
- `set_rotation_origin { layer_ids, from_origin, to_origin, trigger: "shortcut_then_drag" }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`

## Notes / gaps
- Whether the origin persists after deselect or resets to center on next selection is not pinned in the corpus excerpt. Persistence is more useful — assume per-layer persistent storage.
