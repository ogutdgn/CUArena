# Avatar stack

- **Category:** ui-shell
- **One-line summary:** Top-of-right-panel collaborator avatars (multiplayer presence indicators).

## Triggers
- Click an avatar — typically jumps the viewport to follow that collaborator's cursor (in real Figma).

## Preconditions
- Editor view active.

## Inputs
- Pointer click on an avatar.

## Behavior — real Figma
- Click → "follow" mode: viewport tracks that user's cursor + camera; second click stops following.
- Hover → tooltip with name.

## Behavior — mock
- `visual-only`. Click → `unsupported-feature-toast.md` with feature label `"Multiplayer follow"`.
- The mock can render dummy avatars (e.g. one self avatar) without functional follow.

## Outputs
- **Scene graph changes:** none.
- **UI state:** toast renders on click.

## UI feedback
- Avatars rendered as colored circles with initials/photos.

## Side effects
- None.

## Related UI schema entries
- `regions/right-properties.md` → header → avatar-stack
- `chrome.md` → avatar-stack

## Semantic event(s) candidate
- `unsupported_feature_clicked { feature_key: "avatar_stack_click", feature_label: "Multiplayer follow" }`

## Source articles
- `present-to-collaborators-using-spotlight`
- `use-cursor-chat-in-figma-design`

## Notes / gaps
- Multiplayer presence is out of mock scope; render placeholder avatars.
