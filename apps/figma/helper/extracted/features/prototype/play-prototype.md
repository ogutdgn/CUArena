# Play prototype (Presentation view)

- **Category:** prototype
- **One-line summary:** Open the prototype in presentation view; viewer can interact with it per the configured connections.

## Triggers
- Right panel header → play triangle button.
- Shortcut from Figma keyboard sheet (`Cmd ⌥ \\` per Figma; confirm in `use-figma-products-with-a-keyboard`).

## Preconditions
- File has at least one prototype flow start point.

## Inputs
- Pointer click on play.

## Behavior
1. Opens a new browser tab / overlay with presentation view.
2. Plays from the active flow's start.
3. Includes navigation chrome (close, restart, share link).
4. Mobile preview / device frame option (per `set-prototype-device-and-background-settings`).
5. Offline presenter mode and other variants per `present-prototypes-offline`, `view-prototypes-on-a-mobile-device`.

## Outputs
- **UI state:** new presentation view opened.

## UI feedback
- Browser navigation.

## Side effects
- N/A.

## Related UI schema entries
- `regions/right-properties.md` → header → present-button
- (presentation view is its own UI surface — `regions/floating-overlays.md` → presentation-view)

## Semantic event(s) candidate
- `play_prototype { flow_id?, mode: "browser" | "mobile" | "offline", trigger: "play_button" | "shortcut" }`

## Source articles
- `play-your-prototypes`
- `present-prototypes-offline`
- `view-prototypes-on-a-mobile-device`
- `set-prototype-device-and-background-settings`
- `accessible-prototypes-in-figma`
- `use-animated-gifs-in-prototypes`
- `use-videos-in-prototypes`
