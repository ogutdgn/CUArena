# Manage comment thread (reply / resolve / mark unread)

- **Category:** comments
- **One-line summary:** Reply to a comment, mark thread as resolved, mark as unread, or delete.

## Triggers
- Open thread → reply input + thread menu.

## Preconditions
- Existing comment thread.

## Inputs
- Reply text, resolve button, menu choice (mark-unread, delete, copy link).

## Behavior
- **Reply**: appends to thread.
- **Resolve**: marks thread resolved; pin styling changes; resolved threads can be filtered out.
- **Mark unread**: re-flags as needing attention.
- **Delete**: removes the thread (typically restricted to the author).

## Outputs
- **Persistent state:** thread updated.

## UI feedback
- Thread panel updates.

## Side effects
- Email / in-app notifications per user prefs.

## Related UI schema entries
- `regions/floating-overlays.md` → comment-thread

## Semantic event(s) candidate
- `reply_comment { thread_id, message }`
- `resolve_comment { thread_id, to_state }`
- `mark_comment_unread { thread_id }`
- `delete_comment { thread_id, message_id? }`

## Source articles
- `add-comments-to-files`
- `guide-to-comments-in-figma`
- `view-and-manage-comments`
- `move-or-edit-comments`
- `manage-email-notifications-for-comments-on-files`
