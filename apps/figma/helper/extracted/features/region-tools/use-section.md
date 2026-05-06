# Use section (canvas section)

- **Category:** region-tools
- **One-line summary:** Group frames on the canvas under a labeled section to organize work; sections can be marked "Ready for dev".

## Triggers
- Toolbar Region tools → **Section** OR shortcut `Shift S`.
- Drag-select to define section bounds; or wrap selection.

## Preconditions
- Editor view active.

## Inputs
- Pointer drag for bounds OR right-click selection → **Section**.

## Behavior
1. Section is a special container; behaves like a frame for organizational purposes but doesn't apply layout.
2. Section auto-resizes to enclose contained frames.
3. Section label shown above the section bounds.
4. Section can be marked "Ready for dev" (Dev Mode handoff feature) — see `optimize-design-files-for-developer-handoff`.

## Outputs
- **Scene graph changes:** new section node created.
- **Selection changes:** selection = section.

## UI feedback
- Section bounds with label.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/toolbar.md` → region-tools dropdown → section
- `regions/canvas-overlays.md` → section-bounds-and-label

## Semantic event(s) candidate
- `create_section { x, y, w, h, contained_frame_ids?, trigger: "shortcut" | "toolbar" | "wrap" }`

## Source articles
- `organize-your-canvas-with-sections`
- `use-sections-in-prototyping`
- `optimize-design-files-for-developer-handoff`
