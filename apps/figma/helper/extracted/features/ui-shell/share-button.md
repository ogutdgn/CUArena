# Share button

- **Category:** ui-shell
- **One-line summary:** Top-right Share button in the right-panel header opens the Share modal (file permissions and invitation flow).

## Triggers
- Click the **Share** button in the right-panel header (top of right sidebar).

## Preconditions
- Editor view active.

## Inputs
- Pointer click.

## Behavior — real Figma
1. Opens a modal with: people/email invite field, current member list with permission dropdowns (can edit / can view / can comment), team-link selector, copy-link button, advanced settings (link access).
2. Send invites via email; toggle public link on/off.

## Behavior — mock
- The Share button is `visual-only` for the mock.
- Click triggers `unsupported-feature-toast.md` with feature label `"Share"`.

## Outputs
- **Scene graph changes:** none.
- **UI state:** toast renders ("Share is not yet supported").
- **Logger:** `unsupported_feature_clicked { feature_key: "share_button" }`.

## UI feedback
- Toast appears.

## Side effects
- None.

## Related UI schema entries
- `regions/right-properties.md` → header row → Share button
- `chrome.md` → Share

## Semantic event(s) candidate
- `unsupported_feature_clicked { feature_key: "share_button", feature_label: "Share" }`

## Source articles
- `navigating-ui3` (Share button location)

## Notes / gaps
- Real Figma's Share modal is documented across multiple articles; if mock scope expands later, swap this spec for a real `open_share_modal` flow.
