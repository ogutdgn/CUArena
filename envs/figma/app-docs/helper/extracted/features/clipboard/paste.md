# Paste

- **Category:** clipboard
- **One-line summary:** Insert clipboard contents into the scene graph at a context-appropriate position.

## Triggers
- Keyboard: `Cmd V` (Mac) / `Ctrl V` (Windows).
- Right-click → Paste (plain).
- Right-click → Paste here (pastes at cursor coordinates instead of clipboard's original position).
- Main menu → Edit → Paste.

## Preconditions
- Clipboard is non-empty (app clipboard or system clipboard containing a Figma payload OR an image / text payload).

## Inputs
- Trigger.
- Cursor position (relevant for "Paste here").

## Behavior

**Regular paste (Cmd/Ctrl V):**
1. Inspect clipboard source:
   - App clipboard / Figma-HTML → deserialize layers.
   - Raw image payload → create a new image layer.
   - Raw text payload → create a new text layer OR paste into active text edit (context-dependent).
2. Determine placement:
   - If one or more frames are selected when pasting: paste into each selected frame at relative coordinates (or center). Real Figma supports the "multi-paste-into-frames" workflow.
   - Otherwise: paste at the clipboard's original world coordinates if pasting into the same file, OR at viewport center if pasting into a different page / file.
3. Selection becomes the newly-pasted layers.

**Paste here (context menu):**
1. Same as above but placement is anchored at the pointer position where the context menu was opened.

**Paste into active text edit:**
1. If the user is in text-edit mode and the clipboard contains text, insert text at the caret.

## Outputs
- **Scene graph changes:** new layer(s) inserted matching clipboard contents.
- **Selection changes:** selection = new layer(s).

## UI feedback
- Canvas: new layers appear at chosen position.
- Left panel: new rows added.
- Right panel: switches to selection-aware view.

## Side effects
- Undo stack: one entry.
- Clipboard state: unchanged (paste does not consume the clipboard).
- Focus: if new text layer was created and placed in edit mode, text caret is active.

## Related UI schema entries
- `regions/floating-overlays.md` → right-click-context-menu (Paste + Paste here entries)

## Semantic event(s) candidate
- `paste { source_clipboard: "app" | "system_figma_html" | "system_image" | "system_text", placement: "original_coords" | "cursor" | "viewport_center" | "into_frame", target_parent_id | null, cursor: {x, y} | null, new_layer_ids: [...], trigger: "shortcut" | "context_menu_paste" | "context_menu_paste_here" | "main_menu" }`
- "Paste here" is captured as a distinct placement value (`"cursor"`) in the same event — CUA can still distinguish trajectories by payload.

## Source articles
- `copy-and-paste-objects`
- `copy-assets-between-design-tools`

## Notes / gaps
- Multi-paste-into-frames: if 3 frames are selected and user pastes, each frame gets a copy. Real Figma behavior. Must be captured.
- Paste-replace (`Cmd Shift R` or menu): replaces selected layers with clipboard — not in plan/00 §2 explicitly; treat as visual-only or flag.
