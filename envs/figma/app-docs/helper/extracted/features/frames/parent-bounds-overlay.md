# Parent bounds overlay (dashed outline)

- **Category:** frames
- **One-line summary:** When a child of a frame is selected (or while a drag is moving a layer that has a frame parent), a dashed outline renders showing the parent frame's bounds.

## Triggers
- Child of a frame becomes selected.
- Layer is being dragged on the canvas; the candidate parent frame highlights.
- Layer is being created inside a frame.

## Preconditions
- A scoped operation involves a frame parent.

## Inputs
- N/A — this is a feedback overlay, not an input target.

## Behavior
1. Whenever the active operation has a "current parent frame", that frame renders a dashed bounding outline.
2. Outline is non-interactive (clicks pass through to canvas).
3. The overlay disappears when scope returns to the page root or when no candidate parent applies.

## Outputs
- N/A.

## UI feedback
- Dashed line on the parent frame's outer edge, distinct color from the selection box (e.g. lighter or different stroke style).

## Side effects
- N/A.

## Related UI schema entries
- `regions/canvas-overlays.md` → parent-bounds-overlay

## Semantic event(s) candidate
- N/A (feedback only).

## Source articles
- Implemented per commit `20a05a4 feat(canvas): add dashed parent-bounds overlay for frame context`.
- Concept consistent with `frames-in-figma-design` and `parent-child-and-sibling-relationships`, but the visual treatment (dashed) is a mock-specific affordance not directly described in the corpus.

## Notes / gaps
- Visual style (dash length, color) is implementer's choice. Real Figma uses a subtle bounding indicator on selected children's parent — gray/neutral.
