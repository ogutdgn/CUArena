# Align vertical centers

- **Category:** alignment
- **One-line summary:** Align selected layers' vertical centers to the parent's vertical center (single) or selection's group center (multi).

## Triggers
- Alignment row → "align vertical centers" icon.
- Shortcut: `Alt V`.

## Preconditions
- One or more layers selected.

## Inputs
- Pointer click OR shortcut.
- Optional `Shift` + click for group-align.

## Behavior
- **Single:** layer center Y = parent center Y.
- **Multi:** layers' centers Y = selection bbox center Y.
- **Multi + Shift:** align as a group to parent center Y.

## Outputs
- **Scene graph changes:** layers' Y positions updated.

## UI feedback
- Canvas snap.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → position-section → alignment-row

## Semantic event(s) candidate
- `align_vertical_center { layer_ids, anchor, trigger }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`
