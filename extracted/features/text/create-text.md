# Create text

- **Category:** text
- **One-line summary:** Place a new text layer on the canvas, either auto-sized or bounded-width.

## Triggers
- Keyboard: `T` — activates Text tool.
- Toolbar: Text button.

## Preconditions
- Tool set to Text.
- Pointer over canvas.

## Inputs
- Pointer-down + optional drag + pointer-up.
- **Click once:** creates an auto-width text layer (grows horizontally with content). Default resizing mode "Auto width".
- **Click and drag:** creates a bounded-width text layer (fixed width = drag width, height grows with content). Default resizing mode "Auto height".

## Behavior
1. Tool activation: cursor becomes text-placement crosshair.
2. On pointer-down-up (no drag): create text layer anchored at cursor; layer automatically enters text-edit mode with caret positioned at the layer origin.
3. On drag: create bounded-width text layer; also enters text-edit mode.
4. Default content: empty. A placeholder caret blinks awaiting input.

## Outputs
- **Scene graph changes:** one new text layer.
  - `type: "text"`
  - `x`, `y`
  - `w`: 0 (auto-width) or drag-width (bounded)
  - `h`: 0 (grows with content)
  - `content: ""`
  - `resizingMode: "auto_width" | "auto_height"`
  - `fontFamily: default` (e.g., Inter)
  - `fontSize: default` (e.g., 16)
  - `fontWeight: default` (e.g., 400)
  - `fill: [{ type: "solid", color: black }]`
- **Selection changes:** selection = new text layer.
- **Mode state change:** enters text-edit mode (see `edit-text.md`).

## UI feedback
- Cursor: text-placement glyph → caret after placement.
- Canvas: caret visible at layer origin; typing updates content live.
- Left panel: new text row with T icon.
- Right panel: single-text view with Typography section visible (see `regions/right-properties.md`).

## Side effects
- Undo stack: one entry for the creation.
- Focus: moves to text input / caret.

## Related UI schema entries
- `regions/toolbar.md` → text-tool
- `regions/right-properties.md` → typography-section
- `regions/canvas-overlays.md` → insertion-crosshair

## Semantic event(s) candidate
- `create_text { x, y, w, h, resizing_mode: "auto_width" | "auto_height", parent_id | null, trigger: "shortcut_T" | "toolbar" }`

## Source articles
- `explore-text-properties`
- `access-design-tools-from-the-toolbar`
- `adjust-text-dimensions-and-resizing`

## Notes / gaps
- Default font (Inter) and default size (16) common editor defaults; not numerically confirmed in corpus for this exact version. Pick at build time.
- If user exits without typing (Esc without content), real Figma deletes the empty layer. Implement this cleanup in `commit-text.md`.
