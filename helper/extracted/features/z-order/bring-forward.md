# Bring forward (one step up)

- **Category:** z-order
- **One-line summary:** Move selected layer(s) one position up in their parent's child stacking order.

## Triggers
- Selection non-empty + shortcut:
  - Mac: `⌘ ]`
  - Windows: `Ctrl ]`
- Right-click → **Bring forward**.

## Preconditions
- One or more layers selected.
- At least one selected layer is not already at the top of its parent's children list.

## Inputs
- Keyboard shortcut OR menu choice.

## Behavior
1. For each selected layer, swap its position with the layer above it (one step toward the top).
2. If a layer is already topmost in its parent, it doesn't move.
3. Multi-select spanning multiple parents: independent per-parent.

## Outputs
- **Scene graph changes:** `parent.children` array reordered.
- **Selection changes:** none.

## UI feedback
- Panel rows shift one position up.
- Canvas re-renders.

## Side effects
- Undo stack: one entry per command.

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu

## Semantic event(s) candidate
- `bring_forward { layer_ids, trigger: "shortcut" | "context_menu" }`

## Source articles
- `use-figma-products-with-a-keyboard` (full Figma shortcut sheet)

## Notes / gaps
- Same shortcut works on Windows and Mac modulo modifier mapping.
