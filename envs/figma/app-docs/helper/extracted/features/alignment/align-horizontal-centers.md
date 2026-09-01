# Align horizontal centers

- **Category:** alignment
- **One-line summary:** Align selected layers' horizontal centers to the parent's horizontal center (single) or to the selection's group center (multi).

## Triggers
- Right sidebar **Position / Alignment row** → "align horizontal centers" icon.
- Shortcut: `Alt H`.

## Preconditions
- One or more layers selected.

## Inputs
- Pointer click OR shortcut.
- Optional `Shift` + click — align as a group to parent.

## Behavior
- **Single:** layer center on X = parent center on X.
- **Multi:** all layers' centers on X equal the selection's bbox center on X.
- **Multi + Shift:** align as a group to the parent's center on X.

## Outputs
- **Scene graph changes:** affected layers' X positions updated.
- **Selection changes:** none.

## UI feedback
- Canvas snap.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → position-section → alignment-row

## Semantic event(s) candidate
- `align_horizontal_center { layer_ids, anchor: "parent" | "selection_group", trigger }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`
