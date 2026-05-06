# Set text properties

- **Category:** text
- **One-line summary:** Apply typography changes — font family, weight, size, line height, letter spacing, alignment, color — to a text layer or a selected character range.

## Triggers
- Right-sidebar Typography section while a text layer is selected OR a range is selected in text-edit.
- Right-sidebar Fill section for text color (fill applies to text glyphs).

## Preconditions
- Text layer is selected OR a range is selected in edit mode.
- (For range edits: must be in text-edit with `selectedRange` non-empty.)

## Inputs
- Font family picker: dropdown or type-ahead.
- Weight / style dropdown: regular / medium / bold / italic etc.
- Size input: numeric pt or px.
- Line height: number or percent.
- Letter spacing: number.
- Horizontal alignment: left / center / right / justify.
- Vertical alignment: top / middle / bottom.
- Fill color (from Fill section).

## Behavior

**Layer-level change (no range selected):**
1. Property applies to every character in the layer.

**Range-level change (range selected in edit mode):**
1. Property applies only to characters in the range.
2. Layer's `content` gains or updates per-character formatting runs.

## Outputs
- **Scene graph changes:** text layer's formatting updated. May be expressed as `runs: [{ range: [a, b], props: {...} }]` or as a single layer-level props block if uniform.
- **Selection changes:** none.

## UI feedback
- Canvas: text re-renders instantly.
- Panel: values reflect current state.

## Side effects
- Undo stack: one entry per committed change.

## Related UI schema entries
- `regions/right-properties.md` → typography-section
- `regions/right-properties.md` → fill-section (for text color)

## Semantic event(s) candidate
- `set_text_property { layer_id, range | null, property: "font_family" | "font_weight" | "font_size" | "line_height" | "letter_spacing" | "h_align" | "v_align" | "color", from, to, trigger }`

## Source articles
- `explore-text-properties`
- `browse-and-apply-fonts`
- `adjust-text-dimensions-and-resizing`

## Notes / gaps
- Font list depends on installed fonts; corpus doesn't enumerate. In the mock, pick a small curated default list (Inter, Roboto, system fonts).
- OpenType features, variable-axis sliders, text decorations (underline / strikethrough), case transforms — `visual-only` (plan/00 §3 — advanced text features). Basic ones (weight / size / color / alignment) functional.
- "Mixed" state when range spans heterogeneous formatting: display "Mixed" in the input; applying a value unifies the range.
