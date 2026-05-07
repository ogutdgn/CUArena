# Set text case

- **Category:** text
- **One-line summary:** Non-destructively transform letter case: Original, UPPERCASE, lowercase, Capitalize (Title Case), Small Caps.

## Triggers
- Open Type-settings → **Basics** tab → Letter case selector. (Also visible on Details tab per corpus.)

## Preconditions
- A text layer is selected OR a character range is selected.

## Inputs
- Click one of: `Original`, `UPPER`, `lower`, `Title` (Capitalize), `Small Caps`.

## Behavior
1. Transformation is **non-destructive** — the underlying `content` is unchanged; only the rendered case differs.
2. Applies to layer or range.
3. Small Caps uses font-provided small-cap glyphs when available; otherwise faux-typography fallback.

## Outputs
- **Scene graph changes:** `textCase: "original" | "upper" | "lower" | "title" | "small_caps"` on layer or run.
- **Selection changes:** none.

## UI feedback
- Selector shows current value.
- Canvas re-renders with transformed case.

## Side effects
- Undo stack: one entry per change.
- Inverse: switching back to `original` restores rendered case.

## Related UI schema entries
- `regions/right-properties.md` → typography-section → type-settings-popover → letter-case-selector

## Semantic event(s) candidate
- `set_text_property { layer_id, range | null, property: "text_case", from, to, trigger: "click_button" }`

## Source articles
- `explore-text-properties`

## Notes / gaps
- Case-sensitive forms and capital spacing toggles for some fonts: `visual-only`.
- Small Caps fallback rendering: keep simple — use built-in small-cap glyph if the font has it, else fall back to scaled uppercase.
