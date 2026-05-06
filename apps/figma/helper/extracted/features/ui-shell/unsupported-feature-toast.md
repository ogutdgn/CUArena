# Unsupported feature toast

- **Category:** ui-shell
- **One-line summary:** Robust click handling — when the user clicks a UI element that isn't yet implemented, surface a toast saying "{feature_name} is not yet supported" rather than silently doing nothing.

## Triggers
- Pointer click on any UI element flagged `visual-only` or `not yet implemented`.
- Keyboard shortcut for an unsupported command (when shortcut binding exists but engine has no handler).
- Dropdown menu choice for an unsupported entry.

## Preconditions
- Mock-app rendering is active.
- Element has been registered in the unsupported-features registry with a human-readable feature name.

## Inputs
- The click event itself plus the element's identity (registry key).

## Behavior
1. Mock app maintains a registry mapping element IDs → human-readable feature names.
2. When an unsupported element is clicked, the engine emits an `unsupported_feature_clicked` semantic event AND triggers a toast via the toast service.
3. Toast text format: `"{Feature name} is not yet supported"` (or localized equivalent).
4. Toast auto-dismisses after a fixed duration (default ~3-5s); can be dismissed earlier by click.
5. If the same unsupported feature is clicked again rapidly, additional toasts are coalesced (one toast at a time).
6. Underlying state is unchanged — the click is captured, no scene-graph mutation happens.

## Outputs
- **Scene graph changes:** none.
- **Selection changes:** none.
- **UI state:** toast renders.
- **Logger:** semantic event emitted.

## UI feedback
- Toast appears (typically at the bottom of the canvas, per Figma's toast convention).

## Side effects
- Undo stack: unaffected.

## Related UI schema entries
- `regions/floating-overlays.md` → toast-notifications
- `regions/floating-overlays.md` → unsupported-toast (subtype)

## Semantic event(s) candidate
- `unsupported_feature_clicked { feature_key, feature_label, source: "toolbar" | "panel" | "menu" | "shortcut" | ..., trigger }`

## Source articles
- N/A — this is a mock-specific robustness spec, not a Figma feature. Implements the user requirement: "Robust buttons logic for all features on the screen (pop up '{feature_name} unsupported' error message if not yet implemented)".

## Notes / gaps
- The registry entries should pair element IDs with concrete labels (e.g. `"share_button"` → `"Share"`, `"present_button"` → `"Presentation view"`). The exhaustive list comes from `chrome.md` + `regions/*.md` `visual-only` flags.
- The toast is also useful for testing harness assertions: a CUA can assert "user clicked X and the response was 'X unsupported'" rather than guessing nothing happened.
