# Bring to front

- **Category:** z-order
- **One-line summary:** Move selected layer(s) to the topmost position within their parent's child list.

## Triggers
- Selection non-empty + shortcut:
  - Mac: `⌥ ⌘ ]` (Option Command Right Bracket)
  - Windows: `Ctrl Alt ]`
- Right-click → **Bring to front**.
- Right sidebar **More** `…` menu → Bring to front (when applicable).

## Preconditions
- One or more layers selected.

## Inputs
- Keyboard shortcut OR menu choice.

## Behavior
1. For each selected layer, move its index in its parent's children list to the highest position (drawn last; on top in panel).
2. If multi-select spans multiple parents, the operation runs per-parent.
3. Order among the selected siblings is preserved.

## Outputs
- **Scene graph changes:** `parent.children` array reordered for affected parents.
- **Selection changes:** none.

## UI feedback
- Layers panel: rows move to the top of their parent's group.
- Canvas re-renders with updated stacking.

## Side effects
- Undo stack: one entry per command.

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu, more-menu

## Semantic event(s) candidate
- `bring_to_front { layer_ids: [...], from_indices: [...], to_indices: [...], trigger: "shortcut" | "context_menu" }`

## Source articles
- `arrange-layers-with-smart-selection` (mentions order operations as part of layer arrangement)
- Cross-cut with `layers-101-explore-layer-types`

## Notes / gaps
- Standard Figma shortcut on macOS is `⌥ ⌘ ]`; corpus does not list the explicit shortcut in the articles consulted but it's part of the Figma keyboard shortcut sheet (covered by `use-figma-products-with-a-keyboard`).
