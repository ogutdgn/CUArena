# Set auto-layout alignment (3x3 grid)

- **Category:** auto-layout
- **One-line summary:** Choose where children are aligned within the auto-layout frame using a 9-cell (3×3) grid picker.

## Triggers
- Auto-layout frame selected → Auto layout section → alignment grid → click a cell.

## Preconditions
- Auto-layout frame with at least one child.

## Inputs
- Click on one of 9 cells (corners + edge midpoints + center).

## Behavior
1. The chosen cell determines the children's start position along both axes.
2. For vertical flow: top/middle/bottom × left/center/right.
3. For horizontal flow: same matrix.
4. With **Auto** gap, this also controls how the space distributes (top vs middle vs bottom).

## Outputs
- **Scene graph changes:** `auto_layout.alignment: { primary: "min" | "center" | "max", counter: "min" | "center" | "max" }`.
- **Selection changes:** none.

## UI feedback
- Active cell highlights; canvas reflows.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → auto-layout-section → alignment-grid

## Semantic event(s) candidate
- `set_auto_layout_alignment { layer_id, from, to, trigger }`

## Source articles
- `guide-to-auto-layout`
- `use-the-horizontal-and-vertical-flows-in-auto-layout`
