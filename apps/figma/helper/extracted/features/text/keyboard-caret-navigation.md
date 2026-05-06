# Keyboard caret navigation

- **Category:** text
- **One-line summary:** Inside text edit mode, navigate the caret and select ranges with arrow keys, modifiers, Home/End.

## Triggers
- Text edit mode active.
- Keyboard input.

## Preconditions
- Active text edit on a layer.

## Inputs
- Arrow keys (`←`, `→`, `↑`, `↓`).
- Modifiers:
  - **`⌥ Option` / `Alt`** + arrow → word-jump (left/right) or paragraph-jump (up/down).
  - **`⌘ Command` / `Ctrl`** + arrow → line-start/end (left/right) or document-start/end (up/down).
  - **`⇧ Shift`** combined with any → select range from current caret to new position.
- `Home` / `End` → line start/end.
- `Cmd/Ctrl + Home / End` → document start/end.

## Behavior
- Caret moves; selection range updates if Shift is held.
- Standard OS text-edit conventions.

## Outputs
- **Scene graph changes:** none (selection-only).
- **Selection changes:** caret position / range updated.

## UI feedback
- Caret repositions; selection highlighted.

## Side effects
- Undo stack: unaffected (selection-only).

## Related UI schema entries
- `regions/canvas-overlays.md` → text-edit-caret

## Semantic event(s) candidate
- `move_text_caret { layer_id, from_position, to_position, mode: "char" | "word" | "line" | "doc", with_shift: bool, trigger }`

## Source articles
- `guide-to-text-in-figma-design`
- `use-figma-products-with-a-keyboard`

## Notes / gaps
- Word-jump boundary rules are OS-driven; mock can use standard whitespace-based segmentation.
