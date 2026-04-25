# Zoom to 100%

- **Category:** canvas-navigation
- **One-line summary:** Reset the viewport zoom to 100% (1:1 pixel mapping).

## Triggers
- Keyboard: `Shift 0` (and sometimes reported as `Cmd/Ctrl 0`; both imply "reset zoom").
- Zoom/view-options dropdown: typing `100` and Enter in the zoom-% input field.

## Preconditions
- None.

## Inputs
- None beyond the trigger.

## Behavior
1. Set `viewport.zoom` to 1.0 (100%).
2. Keep the current viewport center fixed (the pre-reset center world-space point stays centered).
3. Zoom-% display updates.

## Outputs
- **Scene graph changes:** none.
- **Viewport state changes:** `zoom` set to 1.0.

## UI feedback
- Canvas rescales to 1:1.
- Zoom-% display shows "100%".
- No toast.

## Side effects
- Undo stack: no entry.

## Related UI schema entries
- `regions/right-properties.md` → zoom-percentage-display
- `regions/right-properties.md` → zoom-and-view-options-dropdown

## Semantic event(s) candidate
- `zoom_to_100 { trigger: "keyboard" | "input_field" }`

## Source articles
- `adjust-your-zoom-and-view-options`
- `navigating-ui3`

## Notes / gaps
- Whether the reset preserves viewport center vs resets to origin not explicitly documented; "preserve center" is the common editor convention.
