# Use icon fonts

- **Category:** text
- **One-line summary:** Use a font that maps glyphs to icon codepoints (Material Icons, Font Awesome, etc.) by typing the codepoint or pasting the icon character.

## Triggers
- Set font family to an icon font.
- Type the codepoint character (or paste).

## Preconditions
- Icon font is available (installed locally / in shared fonts).

## Inputs
- Typing or pasting Unicode codepoints / character names.

## Behavior
- Selected font's glyph for the typed character is rendered.
- No transformation — icon fonts behave like any font; the only thing different is the visual mapping.

## Outputs
- **Scene graph changes:** text content updated.

## UI feedback
- Canvas shows the icon glyph.

## Side effects
- Standard text-edit undo.

## Related UI schema entries
- `regions/right-properties.md` → typography-section → font-picker

## Semantic event(s) candidate
- N/A — uses standard text-edit and set-font-family events.

## Source articles
- `use-icon-fonts`

## Notes / gaps
- The article confirms icon fonts work like any font; codepoint reference is font-specific (Material Icons documented codepoints, etc.).
