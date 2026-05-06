# Select text range

- **Category:** text
- **One-line summary:** Select a range of characters within a text layer (for formatting, copy, delete).

## Triggers
- Click-drag inside a text layer in edit mode.
- Shift + click → extends selection from caret to click point.
- Shift + arrow keys → extends selection per arrow logic.
- Double-click → selects word containing caret.
- Triple-click → selects line or paragraph.
- `Cmd/Ctrl A` while in text-edit → selects all text within the layer (not all layers).

## Preconditions
- User is currently in text-edit mode on a text layer.

## Inputs
- Pointer or keyboard as listed.

## Behavior
1. Compute range `[start, end]` as character indices.
2. Display selection: highlighted background on selected characters.
3. Caret is typically at the anchor end (or the most-recently-moved end).
4. Formatting controls (in Typography section) apply to the range.

## Outputs
- **Scene graph changes:** none directly.
- **Mode state change:** range selection active; `selectedRange = [start, end]` on the text layer's edit state.

## UI feedback
- Highlighted range on canvas.
- Typography values reflect the range's formatting (may show "Mixed" if formatting varies within the range).

## Side effects
- Undo stack: no entry for pure selection.

## Related UI schema entries
- `regions/right-properties.md` → typography-section

## Semantic event(s) candidate
- `select_text_range { layer_id, from_range, to_range, method: "drag" | "shift_click" | "shift_arrow" | "double_click" | "triple_click" | "cmd_a" }`

## Source articles
- `explore-text-properties`

## Notes / gaps
- Bidirectional text selection (RTL) is `visual-only` per plan/00 §3. LTR selection functional.
