# Align bottom

- **Category:** alignment
- **One-line summary:** Align selected layers to the bottommost Y edge.

## Triggers
- Alignment row → "align bottom" icon.
- Shortcut: `Alt S`.

## Preconditions
- One or more layers selected.

## Inputs
- Pointer click OR shortcut.
- Optional `Shift` + click for group-align.

## Behavior
- **Single:** layer bottom = parent bottom.
- **Multi:** layers' bottoms = bottommost layer's bottom.
- **Multi + Shift:** align as a group to parent bottom.

## Outputs
- **Scene graph changes:** layers' Y positions updated.

## UI feedback
- Canvas snap.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → position-section → alignment-row

## Semantic event(s) candidate
- `align_bottom { layer_ids, anchor, trigger }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`
