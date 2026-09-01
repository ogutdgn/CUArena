# Cursor chat

- **Category:** ui-shell
- **One-line summary:** Send ephemeral chat bubbles tied to your cursor position so collaborators see what you're saying in real time.

## Triggers
- Shortcut: `/` (forward slash) — opens cursor chat input.

## Preconditions
- Multiplayer session (multiple users in file) for receiver-side visibility.

## Inputs
- Type message; Enter to send; Esc to cancel.

## Behavior
1. Message bubble follows cursor.
2. Bubble fades after a few seconds.
3. Recipients see bubble near sender's cursor.

## Outputs
- **UI state:** ephemeral chat bubble.

## UI feedback
- Bubble visible briefly.

## Side effects
- N/A.

## Related UI schema entries
- `regions/canvas-overlays.md` → cursor-chat-bubble

## Semantic event(s) candidate
- `cursor_chat { message, trigger: "shortcut_slash" }`

## Source articles
- `use-cursor-chat-in-figma-design`

## Notes / gaps
- Mock scope: `visual-only` (no multiplayer). Pressing `/` triggers `unsupported-feature-toast.md`.
