# Set font size

- **Category:** text
- **One-line summary:** Type or scrub the font-size input to change text point size.

## Triggers
- Right sidebar **Typography** section → font-size input → type a value or scrub the icon.

## Preconditions
- Text selected.

## Inputs
- Numeric input.
- Drag-scrub (Figma supports scrubbing on numeric icons).

## Behavior
1. Input commits on Enter / blur (or live during scrub).
2. Multi-text-layer selection applies to all.
3. Mixed text-range font sizes display as "Mixed"; entering a value sets all to that value.

## Outputs
- **Scene graph changes:** text run(s) `font_size` updated.
- **Selection changes:** none.

## UI feedback
- Canvas redraws live.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/right-properties.md` → typography-section → font-size input

## Semantic event(s) candidate
- `set_font_size { layer_ids, range?, from_size, to_size, trigger }`

## Source articles
- `explore-text-properties`
