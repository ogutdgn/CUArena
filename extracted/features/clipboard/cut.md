# Cut

- **Category:** clipboard
- **One-line summary:** Copy the current selection to the clipboard, then delete the original from the scene graph.

## Triggers
- Keyboard: `Cmd X` (Mac) / `Ctrl X` (Windows).
- Right-click → Cut.
- Main menu → Edit → Cut.

## Preconditions
- Selection is non-empty.
- Canvas has focus (not in a text input).

## Inputs
- Just the trigger.

## Behavior
1. Serialize the selection into the clipboard (same as Copy).
2. Delete the selected layers from the scene graph.
3. Selection becomes empty.

## Outputs
- **Scene graph changes:** selected layers removed.
- **Clipboard state:** holds the cut selection.
- **Selection changes:** cleared.

## UI feedback
- Canvas: layers disappear.
- Left panel: rows removed.
- Right panel: switches to no-selection view.

## Side effects
- Undo stack: one entry; undo restores the cut layers at their original positions AND the clipboard still holds the cut copy.

## Related UI schema entries
- `regions/floating-overlays.md` → right-click-context-menu (Cut entry — functional)

## Semantic event(s) candidate
- `cut { layer_ids: [...], trigger: "shortcut" | "context_menu" | "main_menu" }`

## Source articles
- `copy-and-paste-objects`

## Notes / gaps
- Behavior when cutting layers that are children of a frame with auto layout: real Figma reflows siblings. Auto layout is visual-only for us, so no reflow needed.
