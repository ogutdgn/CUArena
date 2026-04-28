# Minimize UI (hide panels)

- **Category:** ui-shell
- **One-line summary:** Toggle visibility of the left + right panels and toolbar to free up canvas space.

## Triggers
- Shortcut: `⇧ \` (Shift Backslash) on both Mac and Windows.
- Top-corner Minimize-UI icon in the left navigation panel.

## Preconditions
- Editor view active.

## Inputs
- Keyboard shortcut OR icon click.

## Behavior
1. Toggle hides the left navigation panel, right properties panel, and (optionally) the bottom toolbar.
2. Selecting a canvas object while minimized **temporarily** re-expands the right panel for that selection (per `regions/right-properties.md`).
3. Re-press the shortcut to restore the persistent minimized state.

## Outputs
- **Scene graph changes:** none.
- **UI state:** panel visibility flags toggled.

## UI feedback
- Panels slide / fade in/out.
- Canvas takes the full window width when minimized.

## Side effects
- Undo stack: unaffected (UI state).

## Related UI schema entries
- `regions/left-navigation.md` → minimize-ui-button
- `regions/right-properties.md` → temporary-expand-on-selection rule

## Semantic event(s) candidate
- `toggle_minimize_ui { to_state, trigger: "shortcut" | "icon" }`

## Source articles
- `navigating-ui3`
- `view-layers-and-pages-in-the-left-sidebar`

## Notes / gaps
- Whether the toolbar is hidden together with the panels in minimized mode is not pinned by the article snippet — Figma hides toolbar too in minimized UI. Implementer follows.
