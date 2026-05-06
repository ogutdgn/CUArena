# Lock / unlock layer

- **Category:** layers
- **One-line summary:** Lock a layer so it cannot be moved or edited on the canvas; unlocking restores normal interaction.

## Triggers
- Selection non-empty + shortcut:
  - Mac: `⌘ ⇧ L`
  - Windows: `Ctrl Shift L`
- Right-click on a layer (canvas or panel) → **Lock** / **Unlock**.
- Layers panel: hover row → padlock icon → click to toggle.
- Drag across multiple rows' padlock icons in the panel = batch lock/unlock.

## Preconditions
- Selection (for shortcut) OR pointer on a row (for panel).

## Inputs
- Keyboard shortcut OR menu choice OR panel-icon click.

## Behavior
1. **Lock**: layer's `locked` flag becomes true.
   - Layer cannot be moved or transformed via canvas drag.
   - Layer cannot be selected by clicking on canvas.
   - Layer can still be selected from the panel and properties can still be adjusted.
   - Locked layers can also be selected via right-click → **Select layer** → choose from list.
2. **Lock parent → cascades**: if a frame or group is locked, all children are effectively locked too. Children cannot be unlocked individually until parent unlocks.
3. **Unlock**: clears the flag.

## Outputs
- **Scene graph changes:** layer's `locked` flag toggled.
- **Selection changes:** none directly.

## UI feedback
- Padlock icon on the layer's row in the panel.
- Cursor changes when hovering a locked layer (no-edit indicator).

## Side effects
- Undo stack: one entry per lock/unlock command (or one per drag-batch).

## Related UI schema entries
- `regions/left-navigation.md` → layers-tree → padlock affordance
- `regions/floating-overlays.md` → context-menu

## Semantic event(s) candidate
- `set_layer_lock { layer_ids, to_locked, trigger: "shortcut" | "context_menu" | "panel_padlock" }`

## Source articles
- `lock-and-unlock-layers`

## Notes / gaps
- Real Figma allows batch lock/unlock by dragging across the panel padlock column — supported behavior.
