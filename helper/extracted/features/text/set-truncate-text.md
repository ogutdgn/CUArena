# Set truncate text

- **Category:** text
- **One-line summary:** Toggle truncation: hide overflow text and append `...`. Set max number of lines.

## Triggers
- Open Type-settings → **Basics** tab → Truncate text toggle and Max lines field.

## Preconditions
- A text layer is selected.
- Text resizing is Auto-height OR Auto-width OR (for layers in auto-layout frames) vertical resizing is Hug contents.

## Inputs
- Click truncate-text toggle (boolean).
- Numeric Max lines value (integer ≥ 1), only available when truncate is ON.

## Behavior
1. Truncate ON + content exceeds available height (or max-lines): visible text is clipped at the last fitting line, with an ellipsis `...` appended at the visible cutoff.
2. Truncate OFF: content overflows freely (Fixed size) or grows the layer (Auto-height).
3. Max-lines caps at integer; content beyond that line is hidden.

## Outputs
- **Scene graph changes:** `truncateText: bool`, `maxLines: int | null` on layer.
- **Selection changes:** none.

## UI feedback
- Toggle / field reflect state.
- Canvas re-renders with `...` shown when truncated.

## Side effects
- Undo stack: one entry per change.

## Related UI schema entries
- `regions/right-properties.md` → typography-section → type-settings-popover → truncate-toggle
- `regions/right-properties.md` → typography-section → type-settings-popover → max-lines-field

## Semantic event(s) candidate
- `set_text_property { layer_id, range: null, property: "truncate" | "max_lines", from, to, trigger: "click_button" | "type" }`

## Source articles
- `explore-text-properties`

## Notes / gaps
- Combined behavior of truncate + auto-height: layer height grows up to max-lines, then truncates.
- Ellipsis character: `…` (U+2026) per typical convention; corpus shows `...` — pick the single-glyph form.
