# Create section

- **Category:** region-tools
- **One-line summary:** Create a section — a container for organizing frames and content at a higher level than frames themselves.

## Triggers
- Keyboard: `Shift S` — activates Section tool.
- Toolbar: Region-tools dropdown → Section.
- Selection + right-click → "Wrap in new section" — wraps the current selection in a new section.

## Preconditions
- Tool set to Section (drag path) OR an existing selection (wrap path).

## Inputs
- Drag path: pointer-down + pointer-move + pointer-up.
- Wrap path: existing selection.

## Behavior

**Drag path:**
1. Tool activation: crosshair.
2. Pointer-down + drag: live preview of section bounds.
3. Pointer-up: create section at drag bounds.

**Wrap path:**
1. Selection + trigger.
2. Compute bounding box.
3. Create a section at that bounding box, reparenting the selection as children.

Selection after = new section.

## Outputs
- **Scene graph changes:** one new section layer.
  - `type: "section"`
  - `x`, `y`, `w`, `h`
  - `fill` default: light gray / neutral (sections typically render with a distinct background visually separating them from frames)
  - `children: []` OR the wrapped selection
  - `devStatus: null` (Ready-for-dev flag — visual-only concept for us)
- **Selection changes:** selection = new section.

## UI feedback
- Crosshair during drag.
- Section's title bar appears at the top of the section region (section title text rendered above the section, editable on double-click).
- New layer in Layers panel with the Section icon.
- Right panel: Section-selection view (minimal — Position, Layout W/H, Appearance, no Fill / Stroke / Effects — per `state-matrix.md`).

## Side effects
- Undo stack: adds "create section" entry.

## Related UI schema entries
- `regions/toolbar.md` → region-tools-dropdown (Section entry)
- `regions/canvas-overlays.md` → insertion-crosshair
- `state-matrix.md` → Section row

## Semantic event(s) candidate
- `create_section { x, y, w, h, parent_id | null, source: "drag" | "wrap_selection", trigger: "shortcut_shift_S" | "toolbar" | "context_menu" }`

## Source articles
- `frames-in-figma-design`
- `access-design-tools-from-the-toolbar`
- workflow reference in `workflows.md`: "Create a frame from existing objects and convert to a section ready for dev"

## Notes / gaps
- Section default fill color not specified; use a subtle neutral (different from frame's white) at build time.
- "Mark as ready for dev" toggle is `visual-only` in our mock.
- Section vs group vs frame distinction: sections can contain frames; frames are the primary content container; sections are purely organizational. This is a scene-graph model decision, handled in `plan/03`.
