# Set color via CSS string

- **Category:** color
- **One-line summary:** Set color by typing a CSS color string when the color picker's color-model dropdown is set to CSS.

## Triggers
- Color picker open, color-model dropdown set to **CSS**.
- Type a CSS string (e.g. `rgb(255, 0, 0)`, `hsl(0, 100%, 50%)`, `red`) into the CSS field.

## Preconditions
- Picker open with CSS mode active.

## Inputs
- Keyboard typing of CSS color notation.
- Commit on Enter / blur.

## Behavior
1. User selects CSS from color-model dropdown.
2. A single text field accepts CSS notation.
3. On commit, value is parsed and applied; invalid input reverts.
4. Other model fields (HEX, RGB, HSB, HSL) update to mirror.

## Outputs
- **Scene graph changes:** target color updated.
- **Selection changes:** none.

## UI feedback
- Live canvas update.
- All other color-model fields refresh to reflect parsed value.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → color-model-dropdown, css-input

## Semantic event(s) candidate
- `set_color_css { layer_ids: [...], target, fill_index?, from_css, to_css, trigger: "picker_input" }`

## Source articles
- `update-fills-using-the-color-picker`
- `about-color-models`

## Notes / gaps
- Exact subset of CSS notations Figma accepts is not enumerated in the corpus. `update-fills-using-the-color-picker` lists CSS as one of the dropdown options without spelling out which keywords / syntaxes parse. Implementer should support at minimum `rgb()`, `rgba()`, `hsl()`, `hsla()`, `#hex`, named colors.
