# Frame children z-order

- **Category:** frames
- **One-line summary:** Within a frame, children render in z-order; the layer panel shows them in reverse paint order (top of panel = top of stack = drawn last).

## Triggers
- N/A — rendering contract.

## Preconditions
- N/A.

## Inputs
- N/A — z-order is changed via discrete events: `z-order/bring-to-front.md`, `z-order/bring-forward.md`, `z-order/send-backward.md`, `z-order/send-to-back.md`, or by dragging in the Layers panel.

## Behavior
1. Each frame stores its children as an ordered list.
2. Render order: index 0 in the list = drawn first (bottom of stack); last index = drawn last (top of stack).
3. Layers panel: same children rendered top-down, with the **last list index at the top of the panel** (so the top of the panel = visually-on-top layer).
4. Reorder operations are scoped to the parent — a child's z-index only changes within its parent.

## Outputs
- N/A directly. Reorder is performed via dedicated events.

## UI feedback
- Layers panel reflects current order.
- Canvas re-renders.

## Side effects
- N/A directly.

## Related UI schema entries
- `regions/left-navigation.md` → layers-tree

## Semantic event(s) candidate
- See `z-order/*` for discrete events.

## Source articles
- `view-layers-and-pages-in-the-left-sidebar`
- `parent-child-and-sibling-relationships`

## Notes / gaps
- Z-order across frames doesn't apply — children of frame A and children of frame B don't share a z-stack; only the frames themselves are siblings on the page.
