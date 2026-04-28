# Select font family

- **Category:** text
- **One-line summary:** Open the font-family picker and choose a typeface for the selected text layer or text range.

## Triggers
- Right sidebar **Typography** section → click on the font name field → font picker opens.

## Preconditions
- A text layer (or text range) is selected.

## Inputs
- Pointer click on font field.
- Type to filter the list.
- Click a font to apply.

## Behavior
1. Picker lists web fonts, locally-installed fonts, and shared/team fonts.
2. Typing filters the list (substring match).
3. Selecting a font applies it to the selection.
4. Multi-text-layer selection: applies the chosen font to all selected.

## Outputs
- **Scene graph changes:** text run(s) `font_family` updated.
- **Selection changes:** none.

## UI feedback
- Picker overlay; canvas updates live as user hovers options (real Figma previews on hover).

## Side effects
- Undo stack: one entry per font commit.

## Related UI schema entries
- `regions/right-properties.md` → typography-section → font-family picker
- `regions/floating-overlays.md` → font-picker

## Semantic event(s) candidate
- `set_font_family { layer_ids, range?, from_font, to_font, trigger: "picker_click" }`

## Source articles
- `browse-and-apply-fonts`
- `add-a-font-to-figma`
- `explore-text-properties`

## Notes / gaps
- Mock app fonts: scope to a small canonical set (e.g. Inter, Roboto, common system fonts) unless full OS-font enumeration is implemented.
