# Tidy up (smart selection)

- **Category:** alignment
- **One-line summary:** Auto-arrange selected layers into rows / columns / a grid with uniform spacing — distributes + aligns in one move.

## Triggers
- Multi-select → Alignment row → "Tidy up" icon (visible when selection qualifies).
- Right-click → **Tidy up**.

## Preconditions
- 2+ layers selected.
- Layers must overlap on at least one axis to qualify for one-dimensional tidy; for two-dimensional tidy, layout must approximate a grid.

## Inputs
- Pointer click OR menu.

## Behavior
1. Engine detects whether the selection is 1D (vertical row, horizontal column) or 2D (grid).
2. **One-dimensional**: aligns objects on the perpendicular axis and equalizes spacing on the primary axis.
   - Uses the **most common spacing** in the selection (mode) as the result.
3. **Two-dimensional**: arranges layers into a grid aligned with the top-left corner of the selection's bbox; vertical and horizontal spacing computed independently.
4. Resulting spacing visible in the position-section spacing fields; tweakable via smart-selection pink handles.

## Outputs
- **Scene graph changes:** layers' X/Y positions updated.
- **Selection changes:** smart-selection state activates (pink handles); selection itself unchanged.

## UI feedback
- Canvas: layers snap into tidy positions; pink smart-selection handles render.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → position-section → alignment-row → tidy-up
- `regions/canvas-overlays.md` → smart-selection-pink-handles

## Semantic event(s) candidate
- `tidy_up { layer_ids, dimension: "1d_horizontal" | "1d_vertical" | "2d", computed_spacing, trigger }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`
- `arrange-layers-with-smart-selection`

## Notes / gaps
- If `Snap to pixel grid` enabled, Figma allows up to 1px rounding tolerance in the displayed spacing.
- Smart selection (the pink handles) is its own affordance — see `arrange-layers-with-smart-selection`.
