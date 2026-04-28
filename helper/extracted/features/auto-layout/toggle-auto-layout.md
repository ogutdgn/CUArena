# Toggle auto layout on / off

- **Category:** auto-layout
- **One-line summary:** Apply auto-layout to a frame (or to selected layers, wrapping them in an auto-layout frame), or remove it.

## Triggers
- Selection (frame OR layers to be wrapped) + shortcut `⇧ A`.
- Right sidebar **Layout** section → click **Add auto layout** button.
- Right-click → **Add auto layout** / **Remove auto layout**.

## Preconditions
- Single layer or selection that can be wrapped.

## Inputs
- Shortcut OR menu / button click.

## Behavior
1. **On a frame:** auto layout settings are added; Figma infers an initial flow (vertical / horizontal / grid) based on child layout.
2. **On non-frame layers:** wraps them in a new auto-layout frame and applies an inferred flow.
3. **Remove**: clears auto-layout settings from the frame; children keep their current absolute positions.
4. After enabling, the right sidebar's Layout section header changes from "Layout" to "Auto layout" and exposes auto-layout-specific properties (direction, padding, gap, alignment, resizing, etc.).

## Outputs
- **Scene graph changes:** frame's `auto_layout` config object created or removed; children's per-position absolute coords may be reset.
- **Selection changes:** if wrapping non-frame layers, selection = new auto-layout frame.

## UI feedback
- Layout panel switches to auto-layout view.
- Canvas re-arranges children per the inferred flow.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → layout-section / auto-layout-section

## Semantic event(s) candidate
- `toggle_auto_layout { layer_ids, to_state, inferred_direction?, trigger: "shortcut" | "panel_button" | "context_menu" }`

## Source articles
- `guide-to-auto-layout`
- `toggle-on-auto-layout-in-designs`
