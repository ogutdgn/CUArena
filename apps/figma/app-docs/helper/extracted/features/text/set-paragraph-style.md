# Set paragraph style (lists)

- **Category:** text
- **One-line summary:** Turn a paragraph into a bulleted or numbered list, or remove list styling.

## Triggers
- Type-settings popover → Basics tab → List style selector (`No list`, `Bulleted`, `Numbered`).
- Auto-create on typing: `- ` or `* ` followed by Space → bulleted list. `1. ` or `1) ` → numbered list.
- Keyboard shortcuts:
  - Bulleted list: `Cmd/Ctrl Shift 8`. Also Mac `Option 8`; Windows `Alt 0149`.
  - Numbered list: `Cmd/Ctrl Shift 7`.
- Indent in/out:
  - Increase: `Tab` or `Cmd/Ctrl ]`.
  - Decrease: `Shift Tab` (implied) / Backspace at start / Enter on empty list item.

## Preconditions
- In text-edit mode on a text layer (auto-create paths) OR text layer / paragraph selected.

## Inputs
- Selector pick, or shortcut, or auto-trigger characters.

## Behavior
1. Selected paragraphs become list items (or revert to plain).
2. Bullets are uniform across indent levels (cannot be customized).
3. Numbered counters cycle: number → alphabetical → roman with each indent level.
4. Up to 5 indent levels supported.
5. List spacing setting controls vertical gap between items (px); default 0.
6. List item color follows preceding character; first item color sets bullet color.

## Outputs
- **Scene graph changes:** per-paragraph `listStyle: "none" | "bulleted" | "numbered"`, `listIndent: int (0-4)`. Layer may also store `listSpacing: number (px)`.
- **Selection changes:** none.

## UI feedback
- Canvas re-renders with bullets / numbers.
- Selector updates.

## Side effects
- Undo stack: one entry per change. Auto-create + Cmd/Ctrl Z removes the auto-styling.

## Related UI schema entries
- `regions/right-properties.md` → typography-section → type-settings-popover → list-style-selector

## Semantic event(s) candidate
- `set_paragraph_style { layer_id, paragraph_indices, from: style, to: style, trigger: "shortcut" | "auto_replace" | "selector" }`
- `change_list_indent { layer_id, paragraph_indices, from: int, to: int, trigger: "tab" | "shift_tab" | "shortcut" }`

## Source articles
- `create-bulleted-and-numbered-lists`
- `explore-text-properties`

## Notes / gaps
- Hanging lists toggle (decoration on the indentation): `visual-only`.
- Custom bullet glyphs: not supported per corpus.
