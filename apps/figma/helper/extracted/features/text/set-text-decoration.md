# Set text decoration

- **Category:** text
- **One-line summary:** Apply or remove underline / strikethrough on a text layer or selected range.

## Triggers
- In Type-settings popover (Basics tab) → click the underline or strikethrough icon.
- Keyboard shortcut for underline:
  - Mac: `Option` `U`
  - Windows: `Ctrl` `U`
- Underline (style-context) bold/italic/underline shortcut also applies: `Cmd/Ctrl U` (style-context, see `apply-text-style.md`).

## Preconditions
- A text layer is selected OR a character range is selected.

## Inputs
- Click on the underline icon → toggles underline.
- Click on the strikethrough icon → toggles strikethrough.

## Behavior
1. Toggles the boolean for the selected target (whole layer or range).
2. Underline has additional sub-properties under a chevron: style (solid/dotted/wavy), thickness, offset, skip-ink, color. [Sub-options: `visual-only` per `set-text-properties.md` notes.]

## Outputs
- **Scene graph changes:** `textDecoration: { underline: bool, strikethrough: bool }` on layer or run.
- **Selection changes:** none.

## UI feedback
- Icon shows active state.
- Canvas re-renders with line drawn.

## Side effects
- Undo stack: one entry per toggle.

## Related UI schema entries
- `regions/right-properties.md` → typography-section → type-settings-popover → decoration-buttons

## Semantic event(s) candidate
- `set_text_property { layer_id, range | null, property: "underline" | "strikethrough", from: bool, to: bool, trigger: "click_button" | "shortcut" }`

## Source articles
- `explore-text-properties`

## Notes / gaps
- Underline sub-options (style, thickness, offset, skip-ink, color) are documented in corpus but treated as advanced — keep simple boolean for the mock.
- Note: links auto-underline by default (see `insert-link-in-text.md`); using `Cmd/Ctrl U` on a link toggles its underline.
