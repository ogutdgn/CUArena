# Toggle layer visibility

- **Category:** layers
- **One-line summary:** Show / hide a layer (or all children of a frame/group) without removing it.

## Triggers
- Selection + shortcut:
  - Mac: `⌘ ⇧ H`
  - Windows: `Ctrl Shift H`
- Layers panel: hover row → eye icon → click to toggle.
- Right sidebar **Appearance** section → eye icon.
- Drag across multiple rows' eye icons in the panel = batch toggle.

## Preconditions
- Selection OR pointer on a row.

## Inputs
- Shortcut, panel-icon click, or sidebar-icon click.

## Behavior
1. Layer's `visible` flag toggles.
2. Hidden layer disappears from canvas; row text greys out.
3. Hidden layers cannot be selected via canvas click; still selectable from the panel and via "show outlines" view (`Cmd ⇧ O` / `Ctrl Shift O`).
4. Hiding a frame/group hides all children visually; child `visible` flags unchanged.

## Outputs
- **Scene graph changes:** layer's `visible` flag toggled.
- **Selection changes:** none.

## UI feedback
- Eye icon switches between open / closed.
- Layer row dims when hidden.
- Canvas re-renders.

## Side effects
- Undo stack: one entry per toggle.

## Related UI schema entries
- `regions/left-navigation.md` → layers-tree → eye icon
- `regions/right-properties.md` → appearance-section → eye icon

## Semantic event(s) candidate
- `toggle_layer_visibility { layer_ids, to_visible, trigger: "shortcut" | "panel_eye" | "appearance_eye" }`

## Source articles
- `toggle-visibility-to-hide-layers`

## Notes / gaps
- Cross-cuts with the existing `properties/set-visibility.md`. Treat this as the canonical layer-level visibility spec; `set-visibility.md` may be retired or kept as a thin alias.
