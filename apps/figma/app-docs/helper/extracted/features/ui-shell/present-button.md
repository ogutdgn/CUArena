# Present button (play triangle)

- **Category:** ui-shell
- **One-line summary:** Right-panel header play-triangle button — opens prototype presentation in a new tab.

## Triggers
- Click the play-triangle icon in the right panel header.
- Shortcut: `Ctrl/⌘ ⌥ \` or per Figma keyboard sheet (covered by `use-figma-products-with-a-keyboard`).

## Preconditions
- Editor view active.

## Inputs
- Pointer click.

## Behavior — real Figma
- Opens Presentation view in a new browser tab — see `play-your-prototypes`.

## Behavior — mock
- `visual-only`. Click → `unsupported-feature-toast.md` with feature label `"Presentation view"`.

## Outputs
- **Scene graph changes:** none.
- **UI state:** toast renders.
- **Logger:** `unsupported_feature_clicked`.

## UI feedback
- Toast.

## Side effects
- None.

## Related UI schema entries
- `regions/right-properties.md` → header → present-button

## Semantic event(s) candidate
- `unsupported_feature_clicked { feature_key: "present_button", feature_label: "Presentation view" }`

## Source articles
- `play-your-prototypes`
- `navigating-ui3`

## Notes / gaps
- Prototype tab itself is also `visual-only` per existing scope.
