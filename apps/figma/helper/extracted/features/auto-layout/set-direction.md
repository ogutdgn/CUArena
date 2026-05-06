# Set auto layout direction

- **Category:** auto-layout
- **One-line summary:** Choose whether the auto-layout frame arranges children vertically, horizontally, or in a grid.

## Triggers
- Auto-layout frame selected + Right sidebar Auto layout section → direction icons (vertical / horizontal / grid).

## Preconditions
- Frame has auto-layout enabled.

## Inputs
- Click direction icon.

## Behavior
- **Vertical**: children stack along Y; reorder updates Y order.
- **Horizontal**: children flow along X.
- **Grid (open beta)**: children arranged in columns and rows; can span multiple cells.
- **Wrap** option becomes available when **Horizontal** is selected (pushes overflowing items to next row).

## Outputs
- **Scene graph changes:** frame's `auto_layout.direction` set to `"vertical" | "horizontal" | "grid"`.
- **Selection changes:** none.

## UI feedback
- Layout panel reflects the selected direction; canvas re-arranges children.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → auto-layout-section → direction-icons

## Semantic event(s) candidate
- `set_auto_layout_direction { layer_id, from_direction, to_direction, trigger }`

## Source articles
- `guide-to-auto-layout`
- `use-the-horizontal-and-vertical-flows-in-auto-layout`
- `use-the-grid-auto-layout-flow`
- `combine-vertical-horizontal-and-grid-auto-layout-flows`
