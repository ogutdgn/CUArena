# Create frame

- **Category:** region-tools
- **One-line summary:** Create a frame container on the canvas — the primary building block for holding design elements.

## Triggers
- Keyboard: `F` — activates Frame tool.
- Toolbar: Region-tools dropdown → Frame.
- Selection + `Opt/Alt Cmd/Ctrl G` — "Frame selection" wraps existing selection in a new frame (separate behavior path).
- Right-click → "Frame selection" on existing selection.

## Preconditions
- Tool set to Frame (for drag-creation path) OR an existing selection (for wrap path).
- Pointer over canvas.

## Inputs
- **Drag path:** Pointer-down + pointer-move + pointer-up. Modifiers: `Shift` (square), `Alt` (center-drag).
- **Preset path:** Frame tool active + click → Figma opens preset list in right sidebar (Phone / Tablet / Desktop / etc.); clicking a preset places a preset-sized frame.
- **Wrap path:** Existing selection + shortcut — wraps that selection in a new frame sized to its bounds.

## Behavior

**Drag path:**
1. Tool activation: crosshair cursor.
2. Right sidebar shows the frame-preset list (if no drag started yet).
3. Pointer-down → pointer-up: create a frame with `x/y/w/h` from drag.

**Preset path:**
1. Tool activation: right sidebar preset list visible.
2. User clicks a preset: a frame with that preset's dimensions is placed at the viewport center (or cursor, depending on flow).

**Wrap path:**
1. Existing selection + trigger.
2. Compute bounding box of selection.
3. Create a new frame at that bounding box, reparenting the selection as children.

Selection after all paths = the new frame.

## Outputs
- **Scene graph changes:** one new frame layer.
  - `type: "frame"`
  - `x`, `y`, `w`, `h`
  - `fill: [{ type: "solid", color: white }]` (default frame fill is white)
  - `clipContent: true` (default)
  - `children: []` (empty) OR the wrapped selection (wrap path)
- **Selection changes:** selection = new frame.

## UI feedback
- Crosshair during drag. Live preview.
- Right panel: frame-preset list visible when the tool is active without drag.
- New layer in Layers panel; frame names default like "Frame 1", "Frame 2", etc. (or preset name like "iPhone 14 Pro" for preset path).
- Right panel switches to Frame-selection view (Layout, Position, Fill, etc., with Layout guide section visible).

## Side effects
- Undo stack: adds "create frame" entry.
- For wrap path: undo restores the selection to its original parents and removes the new frame.

## Related UI schema entries
- `regions/toolbar.md` → region-tools-dropdown (Frame entry)
- `regions/canvas-overlays.md` → insertion-crosshair, selection-bounding-box
- `regions/right-properties.md` → layout-section (Frame-only fields: Clip content, Layout guide)
- `state-matrix.md` → Frame row

## Semantic event(s) candidate
- `create_frame { x, y, w, h, parent_id | null, preset | null, source: "drag" | "preset_click" | "wrap_selection", modifiers: { shift, alt }, trigger: "shortcut_F" | "toolbar" | "wrap_shortcut" | "context_menu" }`
- "Wrap selection" may be a distinct event if CUA trajectories care; `plan/03` decides whether to split.

## Source articles
- `frames-in-figma-design`
- `access-design-tools-from-the-toolbar`

## Notes / gaps
- Frame-preset list contents (names + dimensions) not enumerated here; pick a canonical set (iPhone sizes, iPad, common web breakpoints, 16:9 cover) at build time.
- Naming scheme for auto-generated frame names is "Frame N" by convention.
