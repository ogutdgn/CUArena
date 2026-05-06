# Enable wrap (horizontal flow)

- **Category:** auto-layout
- **One-line summary:** When auto-layout direction is horizontal, enable wrapping so overflowing children flow to the next line.

## Triggers
- Auto-layout frame, direction = horizontal → Auto layout section → **Wrap** toggle.

## Preconditions
- Auto-layout frame with horizontal direction.

## Inputs
- Toggle click.

## Behavior
1. With wrap on, children that would exceed the row's width move to a new row.
2. Row gap is configurable separately from the in-row gap.
3. Wrap is not available for vertical or grid flows.

## Outputs
- **Scene graph changes:** `auto_layout.wrap` flag toggled.
- **Selection changes:** none.

## UI feedback
- Toggle reflects state; canvas reflows children to multiple rows.

## Side effects
- Undo stack: one entry per toggle.

## Related UI schema entries
- `regions/right-properties.md` → auto-layout-section → wrap-toggle

## Semantic event(s) candidate
- `set_auto_layout_wrap { layer_id, to_state, trigger }`

## Source articles
- `guide-to-auto-layout`
- `use-the-horizontal-and-vertical-flows-in-auto-layout`
