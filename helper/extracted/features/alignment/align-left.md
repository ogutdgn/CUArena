# Align left

- **Category:** alignment
- **One-line summary:** Align selected layers to the leftmost X edge (parent's left edge for single, leftmost layer's edge for multi-select).

## Triggers
- Right sidebar **Position / Alignment row** → click "align left" icon.
- Shortcut: `Alt A` (per `adjust-alignment-rotation-position-and-dimensions`).

## Preconditions
- One or more layers selected.

## Inputs
- Pointer click OR shortcut.
- Optional `Shift` + click — align as a group to the parent frame.

## Behavior
1. **Single selection:** layer aligns to its parent's left edge.
2. **Multi-select:** layers align to the leftmost layer's left edge.
3. **Multi-select + Shift held:** align as a group to the parent frame's left edge (per article: "Hold Shift and click the alignment controls to align multiple objects as a group").
4. If multi-select spans multiple parents, each subset aligns to its own parent.

## Outputs
- **Scene graph changes:** affected layers' X positions updated.
- **Selection changes:** none.

## UI feedback
- Canvas: layers snap to alignment.
- Right panel X field updates.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → position-section → alignment-row

## Semantic event(s) candidate
- `align_left { layer_ids, anchor: "parent" | "selection_group" | "leftmost_layer", trigger: "panel_button" | "shortcut" }`

## Source articles
- `adjust-alignment-rotation-position-and-dimensions`

## Notes / gaps
- Figma Design articles do not list `Cmd ⌥ ←` etc.; only `Alt A` etc. mentioned. Use Alt-letter shortcut row.
