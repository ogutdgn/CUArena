# Enter group / frame

- **Category:** layers
- **One-line summary:** Enter a group / frame so that clicks select its children directly instead of the group itself.

## Triggers
- Double-click a group / frame on canvas.
- Keyboard: `Enter` while a group / frame is selected.
- Double-click a row in the Layers panel (may expand rather than enter — ambiguous in docs).

## Preconditions
- Selection or pointer target is a group / frame / section.

## Inputs
- Just the trigger.

## Behavior
1. Set the "active parent context" to the target group / frame.
2. Subsequent clicks on the canvas hit-test children of this container first; clicks outside the container select within its parent context.
3. If the double-click occurred on a specific child, that child becomes the new selection.
4. `Esc` or click-outside exits the container context (see `exit-group.md`).

## Outputs
- **Scene graph changes:** none.
- **Selection changes:** may change to the specific child that was double-clicked, or to the first child if entered via keyboard.
- **Mode state change:** "current context" moves one level deeper.

## UI feedback
- Canvas: the parent context is visually marked (dashed parent-bounds overlay, breadcrumb or similar — corpus doesn't fully detail).
- Left panel: the corresponding tree branch is expanded; row highlighted.

## Side effects
- Undo stack: no entry (context is not undoable).

## Related UI schema entries
- `regions/canvas-overlays.md` → dashed-parent-bounds

## Semantic event(s) candidate
- `enter_group { container_layer_id, entered_child_id | null, trigger: "double_click_canvas" | "enter_key" | "double_click_panel" }`

## Source articles
- `parent-child-and-sibling-relationships`
- `select-layers-and-objects`

## Notes / gaps
- Visual marking of the active context (breadcrumb? subtle shading? dashed parent bounds only?) not fully specified in corpus. Implement the dashed parent-bounds overlay as the minimum signal.
- "Enter group" vs "enter frame" vs "enter section" likely share the same semantic; covered here.
