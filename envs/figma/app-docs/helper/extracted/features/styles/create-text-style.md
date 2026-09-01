# Create text style

- **Category:** styles
- **One-line summary:** Save a text run's typography settings as a reusable named style.

## Triggers
- Right sidebar Typography section → style-picker icon → `+`.
- Or right-click on text → **Create style**.

## Preconditions
- A text layer or run with the desired typography.

## Inputs
- Name (supports `/` for nesting), description.

## Behavior
1. Style stores font family, weight, size, line-height, letter-spacing, paragraph spacing, decoration, case, OpenType features, etc.
2. Local style appears under right sidebar Local Styles section (when nothing is selected).
3. Applying the style to a layer binds its typography to the style id.

## Outputs
- **Persistent state:** new text style.
- **Scene graph changes:** source text optionally bound to the new style.

## UI feedback
- Style chip appears.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → typography-section → style-picker
- `regions/right-properties.md` → page-section → local-styles-and-variables

## Semantic event(s) candidate
- `create_text_style { name, properties, source_layer_id, trigger }`
- `apply_text_style { layer_ids, range?, style_id, trigger }`

## Source articles
- `create-and-apply-text-styles`
- `apply-styles-to-layers-and-objects`
- `manage-and-share-styles`
- `create-color-text-effect-and-layout-guide-styles`
