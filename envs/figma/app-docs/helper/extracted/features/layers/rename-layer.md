# Rename layer

- **Category:** layers
- **One-line summary:** Change the display name of a layer (or bulk-rename multiple layers).

## Triggers
- Keyboard: `Cmd R` / `Ctrl R` — opens Rename modal (bulk-capable).
- Double-click a layer name in the Layers panel → inline edit input appears.
- Right-click → Rename.

## Preconditions
- Selection is non-empty.

## Inputs
- Typed new name.
- For bulk-rename modal: Match field, Rename-to field, Number tokens, Start-from inputs, etc.

## Behavior

**Inline rename (panel):**
1. Double-click row label: label becomes editable input with current name pre-selected.
2. Type new name.
3. Press Enter to commit. Press Esc to cancel.

**Rename modal (`Cmd R`):**
1. Open Rename modal anchored above canvas (see `regions/floating-overlays.md` → rename-modal).
2. Fill fields + tokens.
3. Click Rename → all selected layers updated accordingly.

## Outputs
- **Scene graph changes:** selected layers' `name` updated.
- **Selection changes:** none.

## UI feedback
- Left panel: row label updates.
- Modal: live Preview list shows the new names.

## Side effects
- Undo stack: one entry per commit (single rename or bulk rename = one entry).

## Related UI schema entries
- `regions/left-navigation.md` → layers-tree
- `regions/floating-overlays.md` → rename-modal

## Semantic event(s) candidate
- `rename_layer { layer_ids, from_names, to_names, method: "inline" | "modal", trigger: "double_click_panel" | "shortcut_cmd_r" | "context_menu" }`

## Source articles
- `edit-objects-on-the-canvas-in-bulk`

## Notes / gaps
- Regex match in Match field is `visual-only` in the first pass (plan/00 §3-ish — advanced; flag for plan/03 decision). Basic plain-text rename is functional.
- Slash-separated names create hierarchy in the Assets panel — Assets panel is `visual-only` for us; renaming with slashes still works, just doesn't feed the assets view.
