# Set pattern fill

- **Category:** fills
- **One-line summary:** Use another object on the same canvas (single layer, group, or frame) as the fill source — repeating tiles, with live updates when the source changes.

## Triggers
- Color picker open → fill-type icons → **Pattern** → click **Select source** → pick a layer on the canvas.

## Preconditions
- Picker open with a fill targeted.
- The file contains at least one layer/group/frame to use as a source.

## Inputs
- Click **Select source** → pointer click on a canvas layer.
- After source is set: pattern options for tile type, scale, spacing, alignment, opacity.

## Behavior
1. Fill type → `pattern`. Source = layer/group/frame id reference.
2. Pattern is **dynamic**: editing the source layer's appearance updates every consumer's pattern fill live (per `use-patterns-as-a-fill-or-stroke`).
3. Tile parameters (type, scale, spacing, alignment, opacity) are configured in the picker.

## Outputs
- **Scene graph changes:** fill type → `pattern`, `source_node_id`, tile config.
- **Selection changes:** none.

## UI feedback
- Picker shows source preview + tile config UI.
- Canvas layer renders with the patterned fill.

## Side effects
- Undo stack: one entry per setup.
- Live propagation: source-layer edits cause downstream re-renders on consumers.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → pattern-controls

## Semantic event(s) candidate
- `set_fill_type { fill_index, to_type: "pattern", from_type, trigger: "picker_type" }`
- `set_pattern_source { layer_ids, fill_index, source_node_id, trigger: "canvas_click" }`
- `set_pattern_tile { layer_ids, fill_index, property: "type" | "scale" | "spacing" | "alignment" | "opacity", from, to }`

## Source articles
- `use-patterns-as-a-fill-or-stroke`
- `guide-to-fills`

## Notes / gaps
- Tile-type enum (e.g. square, hex, brick, etc.) and alignment options are mentioned at high level; the exact list is not enumerated in this article.
- Patterns also work as stroke fills.
