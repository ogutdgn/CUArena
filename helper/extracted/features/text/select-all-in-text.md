# Select-all inside text

- **Category:** text
- **One-line summary:** Inside text edit mode, `Cmd/Ctrl A` selects all text content (not all layers).

## Triggers
- Text edit mode active + `⌘ A` / `Ctrl A`.

## Preconditions
- Text edit mode active on a text layer.

## Inputs
- Keyboard shortcut.

## Behavior
- Selects the full text content (all characters in the layer).
- Without text edit mode: same shortcut selects all layers in current scope (page or current frame) — see `selection/select-all.md`.

## Outputs
- **Scene graph changes:** none.
- **Selection changes:** text range = entire text content.

## UI feedback
- Selection highlight on full text.

## Side effects
- Unaffected.

## Related UI schema entries
- `regions/canvas-overlays.md` → text-selection-highlight

## Semantic event(s) candidate
- `select_all_text { layer_id, trigger: "shortcut" }`

## Source articles
- `guide-to-text-in-figma-design`

## Notes / gaps
- Cross-cuts with the global `selection/select-all.md`. The active mode (text edit vs canvas) determines which interpretation fires.
