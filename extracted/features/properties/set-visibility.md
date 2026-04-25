# Set visibility (layer-level)

- **Category:** properties
- **One-line summary:** Show / hide a layer on canvas.

## Triggers
- Layers panel row hover → eye icon → click to toggle.
- Right-sidebar Appearance section: eye icon at the section header.
- Keyboard: `Cmd Shift H` / `Ctrl Shift H` — toggle visibility on current selection.
- Right-click → Show / Hide.

## Preconditions
- Selection is non-empty (for shortcut / panel paths).

## Inputs
- Just the trigger.

## Behavior
1. Toggle each selected layer's `visible` flag.
2. Layers with `visible: false` do not render on canvas and appear grayed-out in the Layers panel.
3. Selection is unchanged; even a hidden layer remains selectable in the Layers panel.

## Outputs
- **Scene graph changes:** selected layers' `visible` flag toggled.

## UI feedback
- Canvas: hidden layers disappear.
- Left panel: rows become grayed-out; eye icon shows closed-eye glyph for hidden layers and remains visible even without hover.
- Right panel: Appearance eye updates.

## Side effects
- Undo stack: one entry per toggle.

## Related UI schema entries
- `regions/left-navigation.md` → layers-tree (eye icon)
- `regions/right-properties.md` → appearance-section (visibility eye)

## Semantic event(s) candidate
- `set_layer_visibility { layer_ids, to_visible, trigger: "layers_panel_eye" | "appearance_eye" | "shortcut" | "context_menu" }`

## Source articles
- `toggle-visibility-to-hide-layers`

## Notes / gaps
- None.
