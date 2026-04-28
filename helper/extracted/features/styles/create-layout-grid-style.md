# Create layout grid style

- **Category:** styles
- **One-line summary:** Save a frame's layout-guide / grid configuration as a reusable named style.

## Triggers
- Right sidebar Layout guide section → style-picker icon → `+`.

## Preconditions
- A frame with layout guides defined.

## Inputs
- Name, description.

## Behavior
1. Style stores grid type (rows, columns, square grid), color, count, gutter, margin, alignment.
2. Applying the style to a frame replaces its layout guides.

## Outputs
- **Persistent state:** new layout grid style.

## UI feedback
- Style chip on Layout guide section.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → layout-guide-section

## Semantic event(s) candidate
- `create_layout_grid_style { name, guide_config, source_frame_id }`
- `apply_layout_grid_style { frame_ids, style_id, trigger }`

## Source articles
- `create-color-text-effect-and-layout-guide-styles`
- `create-layout-guides`
