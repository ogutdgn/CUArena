# Send backward (one step down)

- **Category:** z-order
- **One-line summary:** Move selected layer(s) one position down in their parent's child stacking order.

## Triggers
- Selection non-empty + shortcut:
  - Mac: `⌘ [`
  - Windows: `Ctrl [`
- Right-click → **Send backward**.

## Preconditions
- One or more layers selected.
- At least one selected layer is not already at the bottom of its parent's children.

## Inputs
- Keyboard shortcut OR menu choice.

## Behavior
1. For each selected layer, swap with the layer below it (one step toward bottom).
2. Layer at index 0 of its parent doesn't move.
3. Multi-select spanning multiple parents: independent per-parent.

## Outputs
- **Scene graph changes:** `parent.children` array reordered.
- **Selection changes:** none.

## UI feedback
- Panel rows shift one position down.
- Canvas re-renders.

## Side effects
- Undo stack: one entry per command.

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu

## Semantic event(s) candidate
- `send_backward { layer_ids, trigger: "shortcut" | "context_menu" }`

## Source articles
- `use-figma-products-with-a-keyboard`

## Notes / gaps
- Mirror of `bring-forward.md`.
