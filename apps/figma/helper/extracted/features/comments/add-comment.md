# Add comment

- **Category:** comments
- **One-line summary:** Drop a comment pin on the canvas (or attach to a layer / prototype hotspot) with a thread.

## Triggers
- Toolbar Comments group (`C` shortcut for Comment, `Shift T` Annotation, `Shift M` Measurement).
- Click on the canvas with the comment tool active to drop a pin.

## Preconditions
- File access (any seat type can comment, depending on file permissions).

## Inputs
- Pointer click → text-input field on the pin.
- Type message; mention with `@`; attach images / files.

## Behavior
1. Pin placed at click location.
2. Comment thread opens for typing.
3. Posted comment appears in the file's comments list and is broadcast to subscribers.
4. Replies, reactions, mark-as-resolved supported.

## Outputs
- **Persistent state:** comment thread added.
- **Scene graph changes:** comments are not part of the scene graph; stored separately.

## UI feedback
- Pin renders on canvas; thread panel opens.

## Side effects
- Notifications sent to mentioned users.

## Related UI schema entries
- `regions/canvas-overlays.md` → comment-pin
- `regions/floating-overlays.md` → comment-thread

## Semantic event(s) candidate
- `add_comment { thread_id, position, content, mentions, attachment_ids?, trigger }`

## Source articles
- `add-comments-to-files`
- `guide-to-comments-in-figma`
- `view-and-manage-comments`
- `move-or-edit-comments`
- `comment-on-prototypes`
- `manage-email-notifications-for-comments-on-files`
