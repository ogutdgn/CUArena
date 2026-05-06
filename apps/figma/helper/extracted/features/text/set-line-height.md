# Set line height

- **Category:** text
- **One-line summary:** Set vertical distance between lines of text — `auto`, px, or %.

## Triggers
- Right sidebar **Typography** section → line-height input.

## Preconditions
- Text selected.

## Inputs
- Numeric value with unit (`px` or `%`) or keyword `auto`.

## Behavior
1. `auto` uses the font's intrinsic line height.
2. `px` is absolute.
3. `%` is relative to the font size.
4. Multi-text-layer selection applies to all.

## Outputs
- **Scene graph changes:** text run(s) `line_height` updated.
- **Selection changes:** none.

## UI feedback
- Canvas redraws live.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/right-properties.md` → typography-section → line-height

## Semantic event(s) candidate
- `set_line_height { layer_ids, range?, from, to, unit: "auto" | "px" | "percent", trigger }`

## Source articles
- `explore-text-properties`
