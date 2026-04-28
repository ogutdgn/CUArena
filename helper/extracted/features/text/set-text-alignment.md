# Set text alignment (horizontal & vertical)

- **Category:** text
- **One-line summary:** Set horizontal alignment (left / center / right / justify) and vertical alignment (top / middle / bottom) of text within its layer.

## Triggers
- Right sidebar **Typography** section → horizontal-alignment row (4 icons) and vertical-alignment row (3 icons).
- Keyboard shortcuts (per Figma keyboard sheet): horizontal align mirrors auto-layout shortcuts in some contexts; check `use-figma-products-with-a-keyboard`.

## Preconditions
- Text selected.

## Inputs
- Click an alignment icon.

## Behavior
1. **Horizontal**: left / center / right / justify (last spreads words).
2. **Vertical**: top / middle / bottom — applies only when text has explicit height (auto-height or fixed sizing modes).
3. Justify is only valid for paragraphs (block text); single-line text-runs are unaffected.

## Outputs
- **Scene graph changes:** text layer's `text_align_horizontal` and `text_align_vertical` updated.
- **Selection changes:** none.

## UI feedback
- Active icon highlights; canvas redraws.

## Side effects
- Undo stack: one entry per change.

## Related UI schema entries
- `regions/right-properties.md` → typography-section → alignment-rows

## Semantic event(s) candidate
- `set_text_align_horizontal { layer_ids, from, to, trigger }`
- `set_text_align_vertical { layer_ids, from, to, trigger }`

## Source articles
- `explore-text-properties`

## Notes / gaps
- Vertical alignment requires a frame-bounded text or auto-height/fixed sizing mode; for auto-grow text, vertical alignment is no-op.
