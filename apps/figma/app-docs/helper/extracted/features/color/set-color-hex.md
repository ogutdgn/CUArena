# Set color via hex code

- **Category:** color
- **One-line summary:** Type a hex value into the picker (or fill row) hex field; commit changes the color.

## Triggers
- Color picker open, color-model dropdown set to **HEX**, type into the hex field.
- Hex input shown directly in a fill / stroke row (right sidebar) — typing here without opening the picker.

## Preconditions
- The hex field is visible (picker open in HEX mode, or fill row with hex shown).

## Inputs
- Keyboard typing — characters `0-9`, `a-f` / `A-F`. Optional `#` prefix accepted.
- 3-char shorthand (`fff`) and 6-char (`ffffff`) accepted; 8-char (`ffffffff`) for color + alpha.
- Commit on Enter / blur.

## Behavior
1. User types hex characters.
2. Live preview updates as a valid hex is typed (every keystroke that yields a valid color may live-update).
3. Invalid hex is rejected on commit (field reverts to last valid value).
4. Commit on Enter / focus loss writes the color to the underlying fill/stroke/effect color.

## Outputs
- **Scene graph changes:** target color updated for selected layer(s) on the relevant fill / stroke / effect / page-bg.
- **Selection changes:** none.

## UI feedback
- Hex field updates with normalized form (e.g. `fff` → `FFFFFF`).
- Canvas updates live as the value changes.
- Other color-model fields (RGB, HSB, HSL, CSS) update to reflect the new value.

## Side effects
- Undo stack: one entry per commit (typing burst within the same focus session coalesces to one entry).
- Clipboard: untouched.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → hex-input
- `regions/right-properties.md` → fill-section → fill-row hex input

## Semantic event(s) candidate
- `set_color_hex { layer_ids: [...], target: "fill" | "stroke" | "effect" | "page_bg", fill_index?, from_hex, to_hex, trigger: "picker_input" | "panel_input" }`

## Source articles
- `update-fills-using-the-color-picker`
- `about-color-models`

## Notes / gaps
- 8-char hex with alpha: corpus implies hex maps to color only and alpha lives in the opacity field. `about-color-models` documents the available models without committing on alpha-in-hex; behavior left to engine decision.
- Pasting a hex value (Cmd/Ctrl V into the field) is functionally equivalent to typing — same commit flow.
