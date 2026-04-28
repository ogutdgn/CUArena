# Use paint tool (fill closed regions)

- **Category:** vector
- **One-line summary:** Add or remove a fill in any closed region of a vector network individually.

## Triggers
- Vector edit mode + secondary toolbar **Paint** OR shortcut `⇧ B`.
- Hover over a closed region → click to add fill (or remove if one already applies).

## Preconditions
- Vector edit mode active.
- Vector network has at least one closed region.

## Inputs
- Pointer hover (highlights region with diagonal stripes).
- Click → toggle fill.

## Behavior
1. Hovering a closed region shows a stripe pattern indicating the region.
2. Cursor shows a `+` (can add fill) or `-` (can remove fill).
3. Click adds/removes the fill at that region.
4. Default fill color = grey; modify via Fill section in the right sidebar afterward.

## Outputs
- **Scene graph changes:** vector network's per-region fill list updated.
- **Selection changes:** none.

## UI feedback
- Stripe pattern over hovered region.
- Cursor with droplet + plus/minus.

## Side effects
- Undo stack: one entry per click.

## Related UI schema entries
- `regions/toolbar.md` → secondary toolbar (vector edit) → paint

## Semantic event(s) candidate
- `add_region_fill { layer_id, region_id, color, trigger }`
- `remove_region_fill { layer_id, region_id, trigger }`

## Source articles
- `edit-vector-layers`

## Notes / gaps
- "Region id" is engine-specific; could be a path index or a computed area index.
