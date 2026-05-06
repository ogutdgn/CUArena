# Select a frame vs select its children

- **Category:** frames
- **One-line summary:** Clicking a frame selects the frame; entering scope (double-click / Enter / cmd-click) selects children. Tab / Shift Tab / Shift Enter navigate within the scope.

## Triggers
- **Single click on frame interior:** selects the frame.
- **Double-click on frame:** enters scope; selects first child or the child clicked on (per `enter-frame.md`).
- **`Enter` key with frame selected:** selects a child.
- **`Tab`:** with a child selected, jumps to the next sibling.
- **`Shift Tab`:** previous sibling.
- **`Shift Enter`:** parent (exits one scope level).
- **`Cmd / Ctrl click`:** "deep select" — bypass scope rules; select the deepest hit-tested layer at the cursor.
- **Marquee / drag-box select** while scope = page selects only top-level layers; while scope = inside a frame selects only that frame's children (matches commit `4c6eb77`).

## Preconditions
- A frame exists with at least one child.

## Inputs
- Pointer click / double-click / Cmd-click.
- Keys: `Enter`, `Shift Enter`, `Tab`, `Shift Tab`.

## Behavior
1. Hit-test resolves to the topmost hit layer's parent chain.
2. Selection lands at the deepest "scope-allowed" ancestor — i.e. the child of the current scope frame.
3. Cmd-click bypasses scope and jumps to the leaf.
4. Tab/Shift Tab traverse siblings of the currently-selected layer.

## Outputs
- **Scene graph changes:** none.
- **Selection changes:** updated per the above rules.
- **Editor state:** scope may change (entered/exited as a side effect).

## UI feedback
- Selection bounding box on the selected layer.
- Layers panel highlights the selected row.
- Parent-bounds dashed overlay on the active scope's frame.

## Side effects
- Undo stack: unaffected.

## Related UI schema entries
- `regions/canvas-overlays.md` → selection-bounding-box, parent-bounds-overlay
- `regions/left-navigation.md` → layers-tree

## Semantic event(s) candidate
- `select_layer { layer_ids, modifiers: { cmd, shift }, trigger: "click" | "double_click" | "enter" | "tab" | "shift_tab" | "shift_enter" | "marquee" }`

## Source articles
- `frames-in-figma-design`
- `select-layers-and-objects`
- `parent-child-and-sibling-relationships`

## Notes / gaps
- Cmd-click "deep select" is documented in `select-layers-and-objects` (cross-check that article for full keyboard / modifier matrix).
