# Frame presets

- **Category:** frames
- **One-line summary:** When the Frame tool is active or a frame is selected, choose a preset (Phone/Tablet/Desktop/etc.) to apply standard dimensions.

## Triggers
- **Frame tool active** (`F` / `A` / toolbar): right sidebar shows a preset list.
- **Frame selected**: right sidebar **Frame** dropdown in Layout section exposes the preset list.

## Preconditions
- Frame tool active OR a frame is selected.

## Inputs
- Pointer click on a preset.

## Behavior
1. Preset categories (per `frames-in-figma-design`):
   - **Phone**
   - **Tablet**
   - **Desktop**
   - **Presentation**
   - **Watch**
   - **Paper**
   - **Social Media**
   - **Figma Community**
   - **Archive**
2. Each category expands to specific named presets with W × H values (e.g. iPhone 14 Pro 393 × 852, etc. — exact list not enumerated by the article; common Figma presets apply).
3. Click → if Frame tool active and no frame selected: place a frame of those dimensions at the viewport center (or click-on-canvas point).
4. Click → if a frame is selected: change selected frame's W/H to the preset (children respond per constraints — see `frame-resize-with-children.md`).
5. Frame name defaults to the preset name (e.g. "iPhone 14 Pro").

## Outputs
- **Scene graph changes:** frame's W/H updated (or new frame created with preset dimensions).
- **Selection changes:** if creating, selection = new frame.

## UI feedback
- Right panel shows the preset list.
- Canvas: new frame placed, or selected frame resizes.

## Side effects
- Undo stack: one entry per preset application.

## Related UI schema entries
- `regions/right-properties.md` → frame-presets list (visible when Frame tool active or frame selected)
- `regions/right-properties.md` → layout-section → frame-preset dropdown

## Semantic event(s) candidate
- `apply_frame_preset { frame_id?, preset_name, dimensions, source: "tool_active_panel" | "selected_frame_dropdown" }`

## Source articles
- `frames-in-figma-design`

## Notes / gaps
- Exact preset entries inside each category not enumerated in this article. Implementer should pick a canonical set (e.g. iPhone sizes, iPad, common breakpoints, 16:9 cover, A4, US-Letter, common social-post sizes).
