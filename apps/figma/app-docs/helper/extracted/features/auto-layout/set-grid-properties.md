# Set grid auto-layout properties

- **Category:** auto-layout
- **One-line summary:** When direction = grid, configure rows, columns, cell sizing, and per-child cell span.

## Triggers
- Auto-layout frame with direction = grid + Auto layout section properties.

## Preconditions
- Auto-layout frame with grid direction (currently in open beta).

## Inputs
- Number of rows, number of columns.
- Per-row / per-column sizing (Fixed px, Fill, Hug).
- Per-child: row-span, column-span.

## Behavior
1. Grid arranges children into a 2D matrix of cells.
2. Children can span multiple rows or columns (configurable per child).
3. Rows and columns can grow / shrink independently with their own sizing rules.
4. Unlike wrap, items don't auto-flow to next row — they're explicitly placed.

## Outputs
- **Scene graph changes:** `auto_layout.grid: { rows: [...], columns: [...] }` config; per-child `cell_span: { row, col }`.
- **Selection changes:** none.

## UI feedback
- Layout panel exposes grid-specific controls; canvas reflows.

## Side effects
- Undo stack: per-change entries.

## Related UI schema entries
- `regions/right-properties.md` → auto-layout-section → grid-controls

## Semantic event(s) candidate
- `set_grid_rows { layer_id, from, to }`
- `set_grid_columns { layer_id, from, to }`
- `set_grid_cell_size { layer_id, axis, index, from, to }`
- `set_grid_cell_span { child_id, row_span, col_span }`

## Source articles
- `use-the-grid-auto-layout-flow`
- `combine-vertical-horizontal-and-grid-auto-layout-flows`

## Notes / gaps
- Open beta; some properties may evolve. Implementer can defer grid behind a feature flag.
