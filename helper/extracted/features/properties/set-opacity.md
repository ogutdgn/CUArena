# Set opacity (layer)

- **Category:** properties
- **One-line summary:** Change the overall opacity of selected layer(s).

## Triggers
- Right-sidebar Appearance section: opacity input.
- Keyboard: type `0`-`9` while a layer is selected and not in text-edit — sets opacity to that tenth (e.g. `5` = 50%, `0` = 100%).

## Preconditions
- Selection is non-empty.

## Inputs
- Typed numeric value (0-100).
- Or single-digit keyboard shortcut.

## Behavior
1. Set selected layers' `opacity` to `value / 100`.
2. Apply live.

## Outputs
- **Scene graph changes:** selected layers' `opacity` updated.

## UI feedback
- Canvas: layers fade accordingly.
- Panel: value reflects.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/right-properties.md` → appearance-section (opacity input)

## Semantic event(s) candidate
- `set_layer_opacity { layer_ids, from, to, trigger: "panel_input" | "keyboard_digit" }`

## Source articles
- `apply-effects-to-layers` (opacity is part of Appearance)
- `adjust-alignment-rotation-position-and-dimensions`

## Notes / gaps
- Opacity is layer-level; per-fill-opacity is handled by `set-fill.md`.
- Rapid key presses (`5` then `0`) within a short window combine to `50%` in real Figma; otherwise each digit = that tenth. `plan/03` decides timing.
