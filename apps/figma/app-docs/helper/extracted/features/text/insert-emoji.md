# Insert emoji and smart symbols

- **Category:** text
- **One-line summary:** Insert an emoji into text via colon-shortcode or auto-replace common ASCII patterns to smart symbols.

## Triggers
- Inside text edit mode, type `:` + emoji name (e.g. `:smile`) → autocomplete dropdown → select.
- Type ASCII pattern that matches a smart symbol — e.g. `--` becomes em-dash, `(c)` becomes ©, `...` becomes ellipsis, etc. Auto-replaces on commit (space or newline).

## Preconditions
- Text edit mode active on a text layer.

## Inputs
- Keyboard typing.

## Behavior
1. Colon-prefix triggers an emoji autocomplete suggester.
2. Smart symbols auto-replace on word-boundary typing.

## Outputs
- **Scene graph changes:** text content updated with the inserted character(s).
- **Selection changes:** caret advances.

## UI feedback
- Autocomplete dropdown anchored to caret.
- Replacement happens inline.

## Side effects
- Undo stack: each insert is one undo entry; the smart-symbol auto-replace can be undone in two steps (one to revert the symbol to ASCII, one to remove characters).

## Related UI schema entries
- `regions/floating-overlays.md` → emoji-autocomplete

## Semantic event(s) candidate
- `insert_emoji { layer_id, position, emoji_unicode, source: "colon_autocomplete" | "smart_symbol", trigger }`

## Source articles
- `add-emojis-and-smart-symbols-to-text`
