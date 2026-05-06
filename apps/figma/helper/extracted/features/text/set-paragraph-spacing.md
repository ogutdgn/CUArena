# Set paragraph spacing

- **Category:** text
- **One-line summary:** Set vertical distance between paragraphs (above each new paragraph break) — px.

## Triggers
- Type-settings panel (`…` in Typography section) → **Paragraph spacing** field.

## Preconditions
- Text selected.

## Inputs
- Numeric `px` value.

## Behavior
- Applied between paragraphs (newline-separated runs).

## Outputs
- **Scene graph changes:** text layer's `paragraph_spacing` updated.
- **Selection changes:** none.

## UI feedback
- Canvas redraws live.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/floating-overlays.md` → type-settings panel

## Semantic event(s) candidate
- `set_paragraph_spacing { layer_ids, from, to, trigger }`

## Source articles
- `explore-text-properties`
