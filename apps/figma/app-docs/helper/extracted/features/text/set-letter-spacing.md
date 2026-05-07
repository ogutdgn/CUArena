# Set letter spacing

- **Category:** text
- **One-line summary:** Adjust horizontal spacing between letters (tracking) — px or %.

## Triggers
- Right sidebar **Typography** section → letter-spacing input.

## Preconditions
- Text selected.

## Inputs
- Numeric, `px` or `%`. Negative values tighten.

## Behavior
- Spacing is applied uniformly across the selection.

## Outputs
- **Scene graph changes:** text run(s) `letter_spacing` updated.
- **Selection changes:** none.

## UI feedback
- Canvas redraws live.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/right-properties.md` → typography-section → letter-spacing

## Semantic event(s) candidate
- `set_letter_spacing { layer_ids, range?, from, to, unit, trigger }`

## Source articles
- `explore-text-properties`
