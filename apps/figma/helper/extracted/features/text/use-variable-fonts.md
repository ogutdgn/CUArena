# Use variable fonts

- **Category:** text
- **One-line summary:** Adjust variable-axis sliders (weight, width, slant, optical size, etc.) for fonts that expose a variable axis.

## Triggers
- Type-settings panel → **Variable** tab (visible only when the font is a variable font).
- Drag axis sliders or type values.

## Preconditions
- Text selected.
- Font is a variable font.

## Inputs
- Slider drag or numeric input per axis.

## Behavior
1. Variable fonts expose multiple continuous axes (per font author).
2. Common axes: weight (`wght`), width (`wdth`), slant (`slnt`), italic (`ital`), optical size (`opsz`).
3. Adjusting an axis updates the font rendering live.

## Outputs
- **Scene graph changes:** text run(s) `font_variation_settings` updated.
- **Selection changes:** none.

## UI feedback
- Sliders + numeric values; canvas redraws live.

## Side effects
- Undo stack: per-axis change entry.

## Related UI schema entries
- `regions/floating-overlays.md` → type-settings panel → variable tab

## Semantic event(s) candidate
- `set_font_variation { layer_ids, range?, axis_tag, from_value, to_value, trigger }`

## Source articles
- `use-variable-fonts`
- `explore-text-properties`
