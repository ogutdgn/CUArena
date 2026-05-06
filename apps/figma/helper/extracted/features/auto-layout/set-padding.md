# Set auto-layout padding

- **Category:** auto-layout
- **One-line summary:** Control the empty space between an auto-layout frame's edges and its children.

## Triggers
- Auto-layout frame selected → Auto layout section → padding inputs.

## Preconditions
- Auto-layout frame.

## Inputs
- One value (uniform), two values (vertical / horizontal), or four values (top / right / bottom / left).
- Toggle between modes via a small icon.

## Behavior
1. **Uniform**: single value applies to all four sides.
2. **Vertical / Horizontal split**: separate vertical and horizontal values.
3. **Independent**: separate top / right / bottom / left.
4. Children automatically reposition to respect padding.

## Outputs
- **Scene graph changes:** `auto_layout.padding: { top, right, bottom, left }` updated.
- **Selection changes:** none.

## UI feedback
- Padding inputs update; canvas reflows.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/right-properties.md` → auto-layout-section → padding-inputs

## Semantic event(s) candidate
- `set_auto_layout_padding { layer_id, side: "all" | "top" | "right" | "bottom" | "left", from, to, trigger }`

## Source articles
- `guide-to-auto-layout`
