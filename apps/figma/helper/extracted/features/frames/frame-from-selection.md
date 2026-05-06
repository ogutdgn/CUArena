# Frame from selection

- **Category:** frames
- **One-line summary:** Wrap one or more selected layers in a new frame sized to their bounding box; selected layers become children of the new frame.

## Triggers
- Selection non-empty + shortcut:
  - Mac: `⌥ Option` `⌘ Command` `G`
  - Windows: `Ctrl` `Alt` `G`
- Right-click on selection → **Frame selection**.

## Preconditions
- One or more layers selected.

## Inputs
- Keyboard shortcut OR right-click menu.

## Behavior
1. Compute axis-aligned bounding box of the selection.
2. Create a new frame at that bounding box (X/Y/W/H = bbox).
3. Reparent every selected layer as a child of the new frame; preserve their on-canvas positions (children's local coordinates updated).
4. Selection becomes the new frame.

## Outputs
- **Scene graph changes:** new frame created; selected layers' parent changes to the frame; their X/Y converts to local coords inside the frame.
- **Selection changes:** selection = new frame.

## UI feedback
- Layers panel: new frame row appears; previously-selected layers nest under it.
- Canvas: new frame outline appears around the wrapped content.
- Right panel switches to Frame-selection view (Layout, Position, Fill, etc.).

## Side effects
- Undo stack: one entry covering the create + reparent.
- Default frame name: per existing conventions ("Frame N").

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu (Frame selection)
- `regions/right-properties.md` → layout-section (Frame-only fields)

## Semantic event(s) candidate
- `frame_selection { layer_ids: [...], new_frame_id, bbox, trigger: "shortcut" | "context_menu" }`

## Source articles
- `frames-in-figma-design`
- `the-difference-between-frames-and-groups`

## Notes / gaps
- If the selection spans multiple parents, the new frame is created at the common ancestor scope; coords adjusted accordingly. Corpus does not pin exact behavior — implementer's call.
- If the selection includes a top-level frame, behavior of "wrap a frame in a frame" is allowed (nested frames).
