# Align right

- **Category:** alignment
- **One-line summary:** Align selected layers to the rightmost X edge.

## Triggers
- Right sidebar **Position / Alignment row** → "align right" icon.
- Shortcut: `Alt D`.

## Preconditions
- One or more layers selected.

## Inputs
- Pointer click OR shortcut.
- Optional `Shift` + click for group-align to parent.

## Behavior
- **Single:** layer right-edge = parent right edge.
- **Multi:** layers' right edges = rightmost layer's right edge.
- **Multi + Shift:** align as a group to parent right.

## Outputs
- **Scene graph changes:** layers' X positions updated.

## UI feedback
- Canvas snap.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → position-section → alignment-row

## Semantic event(s) candidate
- `align_right { layer_ids, anchor, trigger }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`
