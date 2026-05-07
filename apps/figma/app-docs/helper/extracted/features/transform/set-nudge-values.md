# Set small / big nudge values

- **Category:** transform
- **One-line summary:** Configure how far a layer moves with a normal arrow-key (small nudge) and Shift+arrow (big nudge).

## Triggers
- File menu / preferences: **Preferences** → **Nudge amount** (or similar).
- Quick actions menu (`Cmd K`) → "Nudge amount".

## Preconditions
- Editor view active.

## Inputs
- Numeric input for small-nudge (default 1).
- Numeric input for big-nudge (default 10).

## Behavior
1. Both values are points (resolution-independent).
2. Set per-account (across files) per the Figma convention.
3. Affects all subsequent arrow-key nudges in `nudge-with-arrow-keys.md`.

## Outputs
- **Persistent state:** account-level preference updated.

## UI feedback
- Settings screen.

## Side effects
- None on scene graph.

## Related UI schema entries
- `regions/floating-overlays.md` → preferences-modal (visual-only / unsupported in mock)

## Semantic event(s) candidate
- `set_nudge_values { small, big, trigger }`

## Source articles
- `set-small-and-big-nudge-values`

## Notes / gaps
- In mock, may be `visual-only` — accessing Preferences triggers `unsupported-feature-toast.md`.
