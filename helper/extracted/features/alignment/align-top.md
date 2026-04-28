# Align top

- **Category:** alignment
- **One-line summary:** Align selected layers to the topmost Y edge.

## Triggers
- Alignment row → "align top" icon.
- Shortcut: `Alt W`.

## Preconditions
- One or more layers selected.

## Inputs
- Pointer click OR shortcut.
- Optional `Shift` + click for group-align.

## Behavior
- **Single:** layer top = parent top.
- **Multi:** layers' tops = topmost layer's top.
- **Multi + Shift:** align as a group to parent top.

## Outputs
- **Scene graph changes:** layers' Y positions updated.

## UI feedback
- Canvas snap.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → position-section → alignment-row

## Semantic event(s) candidate
- `align_top { layer_ids, anchor, trigger }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`
