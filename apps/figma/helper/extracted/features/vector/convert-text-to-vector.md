# Convert text to vector

- **Category:** vector
- **One-line summary:** Convert a text layer's glyphs into vector paths so the typography can be customized as shapes (logos, wordmarks).

## Triggers
- Right-click on text layer → **Outline text** (or equivalent).
- Shortcut: `⇧ ⌘ O` (per `convert-text-to-vector-paths`; collides with show-outlines — cross-check `use-figma-products-with-a-keyboard`).

## Preconditions
- Text layer selected.

## Inputs
- Menu choice or shortcut.

## Behavior
1. Each glyph is converted into a vector path.
2. The text's typography (font, size, weight, line-height) is destroyed — the result is a vector layer with the glyph outlines rendered at the size/weight at the time of conversion.
3. Editing text content is no longer possible after conversion.

## Outputs
- **Scene graph changes:** text node replaced by a vector node containing each glyph as a sub-path.
- **Selection changes:** selection = new vector layer.

## UI feedback
- Layer panel: text icon replaced by vector icon.
- Canvas: visual unchanged at the moment of conversion.

## Side effects
- Undo stack: one entry. Cannot return to text without undo.

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu

## Semantic event(s) candidate
- `convert_text_to_vector { layer_ids, new_layer_ids, trigger }`

## Source articles
- `convert-text-to-vector-paths`

## Notes / gaps
- Like `flatten-to-vector.md`, this is destructive — version history is the only restore path beyond undo.
