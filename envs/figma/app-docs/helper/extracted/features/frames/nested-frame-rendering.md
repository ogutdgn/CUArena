# Nested frame rendering

- **Category:** frames
- **One-line summary:** A frame can contain other frames (and groups, shapes, text, etc.) to arbitrary depth; rendering applies clipping, transform, and opacity stacking per parent.

## Triggers
- Any frame creation that places it inside another frame (drag inside, frame-from-selection on existing nested layers, drop-into-frame).

## Preconditions
- The file's scene graph supports nesting (it does, by spec).

## Inputs
- N/A — this spec is a rendering / behavior contract, not a discrete user action.

## Behavior
1. **Containment:** child frames render inside their parent's coordinate space; their X/Y/W/H are local to the parent.
2. **Clip Content:** each parent frame applies clipping based on its own `clip_content` flag (independent per frame).
3. **Stacking:** within each parent, children render in z-order (top of the layer panel = drawn last).
4. **Transform:** transforming a parent (move/rotate/scale) cascades to children.
5. **Layer panel:** nested frames are bolded only at the top level (per `frames-in-figma-design`: "Figma bolds top-level frames in the layers panel and shows the name of any top-level frames on the canvas.")
6. **Selection:** entering one nested frame scopes hit-testing one level deeper (recursive — see `enter-frame.md`).

## Outputs
- This is a rendering contract; no scene-graph mutations are caused by this spec alone.

## UI feedback
- Top-level frame names render on the canvas above each top-level frame.
- Layers panel: nested frames indent under their parent.

## Side effects
- N/A.

## Related UI schema entries
- `regions/canvas-overlays.md` → frame-name-label, parent-bounds-overlay
- `regions/left-navigation.md` → layers-tree

## Semantic event(s) candidate
- N/A — no discrete event; covered by reparent / create / move events.

## Source articles
- `frames-in-figma-design`
- `parent-child-and-sibling-relationships`

## Notes / gaps
- "How deep can nesting go" is not numerically constrained by docs; treat as unbounded.
- Frame name rendered above frame is only for top-level frames per the article.
