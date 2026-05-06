# Change canvas background color (Page bg)

- **Category:** canvas-navigation
- **One-line summary:** Set the page's background color via the **Page** section in the right sidebar (visible when nothing is selected).

## Triggers
- Click empty canvas to clear selection.
- Right sidebar shows **Page** section → click swatch → color picker.

## Preconditions
- No selection.

## Inputs
- Color picker (any of the color/* events).

## Behavior
1. Page background color updated.
2. Affects the canvas area outside frames; frames render on top with their own fills.

## Outputs
- **Scene graph changes:** page's `background_color` updated.

## UI feedback
- Canvas redraws.

## Side effects
- Undo stack: one entry per change.

## Related UI schema entries
- `regions/right-properties.md` → page-section

## Semantic event(s) candidate
- `set_page_background_color { page_id, from_color, to_color, trigger }`

## Source articles
- `change-the-background-color-of-the-canvas`
- `design-prototype-and-explore-layer-properties-in-the-right-sidebar`
