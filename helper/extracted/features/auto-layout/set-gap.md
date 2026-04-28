# Set auto-layout gap (spacing between)

- **Category:** auto-layout
- **One-line summary:** Distance between adjacent children in an auto-layout frame.

## Triggers
- Auto-layout frame selected → Auto layout section → gap input.

## Preconditions
- Auto-layout frame.

## Inputs
- Numeric `px` value, OR keyword `Auto` (vertical/horizontal flows only).

## Behavior
1. **px value**: explicit gap between children.
2. **Auto**: distributes children with maximum equal space — equivalent to `space-between` in CSS terms.
3. **Grid flow**: gap becomes column-gap and row-gap, configurable separately.

## Outputs
- **Scene graph changes:** `auto_layout.gap` (or column_gap / row_gap for grid) updated.
- **Selection changes:** none.

## UI feedback
- Gap input updates; canvas reflows.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/right-properties.md` → auto-layout-section → gap-input

## Semantic event(s) candidate
- `set_auto_layout_gap { layer_id, axis: "primary" | "column" | "row", from, to, trigger }`

## Source articles
- `guide-to-auto-layout`
