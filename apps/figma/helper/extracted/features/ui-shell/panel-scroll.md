# Panel scroll behavior

- **Category:** ui-shell
- **One-line summary:** Both the left navigation panel and the right properties panel scroll vertically when their contents exceed the viewport height; scroll is independent per-panel.

## Triggers
- Pointer wheel inside a panel.
- Touchpad two-finger scroll inside a panel.
- Drag the scrollbar (if visible).
- Keyboard `Page Up` / `Page Down` (when panel has focus).

## Preconditions
- Panel content height exceeds the panel's visible height.

## Inputs
- Wheel / touch / scrollbar drag.

## Behavior
1. **Left panel** (Layers tree, Pages list, Find/Replace, Assets):
   - Pages selector and the layers tree share the same scroll container OR have separate sub-scrolls (Figma uses a unified scroll with the page selector pinned at the top).
   - Auto-scroll on drag near the top/bottom edges (per `reparent-via-layer-panel.md`).
2. **Right panel** (selection-driven sections):
   - Sections (Layout, Position, Appearance, Fill, Stroke, Effects, Export) stack vertically.
   - When the total height exceeds the panel viewport, the panel scrolls.
   - Header (zoom, tabs, sub-header) may stay pinned at the top (per real Figma; specific behavior not pinned in the corpus).
3. **Color picker** (floating overlay) and **bulk-rename modal** etc. — each scrolls independently if oversized.

## Outputs
- **Scene graph changes:** none.
- **UI state:** scroll position per panel.

## UI feedback
- Scrollbar visible during scroll (auto-hide on idle in OS-style).
- Smooth scrolling.

## Side effects
- Undo stack: unaffected.

## Related UI schema entries
- `regions/left-navigation.md`
- `regions/right-properties.md`
- `regions/floating-overlays.md` → color-picker (scrollable)

## Semantic event(s) candidate
- `scroll_panel { panel: "left" | "right" | "color_picker" | ..., from_offset, to_offset, trigger: "wheel" | "drag_scrollbar" | "key_page_down" | ... }`
- For CUA, scroll events are typically not interesting unless they're user-driven gestures with a target outcome (e.g. "scroll to reveal section X").

## Source articles
- `navigating-ui3`
- `view-layers-and-pages-in-the-left-sidebar`
- `design-prototype-and-explore-layer-properties-in-the-right-sidebar`

## Notes / gaps
- Whether the right-panel header is sticky during scroll: real Figma keeps the tabs pinned. Implementer follows.
- Auto-scroll thresholds during drag-and-drop are not pinned numerically by the corpus.
