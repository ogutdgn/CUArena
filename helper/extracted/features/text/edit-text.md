# Edit text (enter mode + typing + caret navigation)

- **Category:** text
- **One-line summary:** Enter text-edit mode on a text layer, type / delete characters, move the caret.

## Triggers
- Double-click an existing text layer on canvas.
- Keyboard: `Enter` with a text layer selected.
- Creation: `create-text.md` automatically enters edit mode.

## Preconditions
- Selection is a text layer OR double-click target is a text layer.
- Not currently editing a different text layer (that would commit the prior edit first).

## Inputs
- Key events while in edit mode:
  - Printable characters → insert at caret.
  - Arrow keys → move caret (with modifiers: Cmd/Ctrl + arrow for word/line jump; Shift for range extension).
  - Backspace / Delete → remove character(s).
  - Home / End → caret to line start / end.
  - Cmd/Ctrl Home / End → caret to document start / end.
  - Enter → insert newline.
  - Tab → insert tab (or may commit depending on context).
- Click within text → caret moves to clicked position.
- Double-click within text → select word.
- Triple-click → select line or paragraph.

## Behavior

**Enter mode:**
1. Caret becomes visible at initial position (layer origin for new; clicked character for double-click).
2. Text-edit mode overlays; canvas otherwise locked for other interactions.

**Typing:**
1. Each keystroke updates the layer's `content` at caret position.
2. Caret advances.
3. If layer is auto-width, width grows with text; if bounded, content wraps.

**Navigation:**
1. Caret moves per key logic.
2. For multi-line text, arrow up / down navigate between visual lines (accounting for wrapping).

## Outputs
- **Scene graph changes:** text layer's `content` mutated on each meaningful commit point (every keystroke or debounced batch — engine decision).
- **Selection changes:** selection stays = the text layer.
- **Mode state change:** in text-edit mode.

## UI feedback
- Canvas: blinking caret; selected range (if any) shown with highlighted background on the characters.
- Typography section in right panel applies to current caret position / selection range.

## Side effects
- Undo stack: keystrokes typically coalesced into one undo entry per "typing burst" or per commit. `plan/03` decides granularity.

## Related UI schema entries
- `regions/right-properties.md` → typography-section

## Semantic event(s) candidate
- `enter_text_edit_mode { layer_id, entry_point: "double_click" | "enter_key" | "create" }`
- `type_characters { layer_id, inserted: "text", position: caret_index_before, cursor_after: caret_index_after }`
- `move_caret { layer_id, from_index, to_index, method: "arrow_key" | "click" | "cmd_arrow" | "home_end" }`
- `delete_character { layer_id, direction: "backspace" | "delete", deleted: "text", position }`

## Source articles
- `explore-text-properties`
- `edit-main-components` (text editing inside components — visual-only context for us)

## Notes / gaps
- IME / composition events for CJK, emoji input: `visual-only` (plan/00 §3 — advanced text features), but basic IME should not break; test at build time.
- Rich-text formatting within a text layer (per-character font / color): plan/00 §2 lists "full Text editing (caret, selection, wrapping, font weight / size / color)" so per-character formatting is functional. Rich-text details in `set-text-properties.md`.
- Undo granularity for typing: pick typing-burst coalescing (e.g., 500ms of continuous typing = one undo entry).
