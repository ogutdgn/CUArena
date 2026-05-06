# Create effect style

- **Category:** styles
- **One-line summary:** Save a layer's effects (drop shadow, inner shadow, blur, etc.) as a reusable named effect style.

## Triggers
- Right sidebar Effects section → style-picker icon → `+`.

## Preconditions
- Layer with one or more effects.

## Inputs
- Name, description.

## Behavior
1. All effects on the layer are bundled into the style.
2. Applying the style to another layer replaces its effects with the style's set.

## Outputs
- **Persistent state:** new effect style.

## UI feedback
- Style chip on Effects section.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → effects-section → style-picker

## Semantic event(s) candidate
- `create_effect_style { name, effects, source_layer_id }`
- `apply_effect_style { layer_ids, style_id, trigger }`

## Source articles
- `create-color-text-effect-and-layout-guide-styles`
- `apply-styles-to-layers-and-objects`
