# Toggle frame "Clip content"

- **Category:** frames
- **One-line summary:** Toggle whether content extending beyond a frame's bounds is clipped (default) or shown overflowing.

## Triggers
- Right sidebar **Layout** section → **Clip content** toggle (visible only when a frame is selected).

## Preconditions
- A frame is selected.

## Inputs
- Pointer click on the toggle.

## Behavior
1. When **on** (default): children rendered outside the frame's bounds are clipped at the frame edge.
2. When **off**: children render outside the bounds (overflow visible).
3. Affects rendering only — children's geometry is unchanged.

## Outputs
- **Scene graph changes:** frame's `clip_content` flag toggled.
- **Selection changes:** none.

## UI feedback
- Canvas re-renders.
- Toggle reflects state.

## Side effects
- Undo stack: one entry per toggle.
- Affects hit-testing: clipped content is still selectable (visible via Layers panel) per Figma convention; clarify with engine — not pinned by docs.

## Related UI schema entries
- `regions/right-properties.md` → layout-section → clip-content toggle

## Semantic event(s) candidate
- `toggle_clip_content { frame_id, to_state, trigger: "panel_toggle" }`

## Source articles
- `frames-in-figma-design`
- `parent-child-and-sibling-relationships`

## Notes / gaps
- Clip-content interaction with effects (e.g. drop shadow): a shadow on a clipped child may be clipped at the frame edge, depending on frame's effect-clip settings — not enumerated here.
