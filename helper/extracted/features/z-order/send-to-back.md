# Send to back

- **Category:** z-order
- **One-line summary:** Move selected layer(s) to the bottommost position within their parent's child list.

## Triggers
- Selection non-empty + shortcut:
  - Mac: `⌥ ⌘ [`
  - Windows: `Ctrl Alt [`
- Right-click → **Send to back**.

## Preconditions
- One or more layers selected.

## Inputs
- Keyboard shortcut OR menu choice.

## Behavior
1. For each selected layer, set its index in its parent's children to position 0 (drawn first; bottom of stack).
2. Multi-select spanning multiple parents: independent per-parent.
3. Order among the selected siblings is preserved.

## Outputs
- **Scene graph changes:** `parent.children` array reordered.
- **Selection changes:** none.

## UI feedback
- Layers panel: rows move to bottom of their parent group.
- Canvas re-renders.

## Side effects
- Undo stack: one entry per command.

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu

## Semantic event(s) candidate
- `send_to_back { layer_ids, from_indices, to_indices, trigger: "shortcut" | "context_menu" }`

## Source articles
- `use-figma-products-with-a-keyboard`

## Notes / gaps
- Mirror of `bring-to-front.md`.
