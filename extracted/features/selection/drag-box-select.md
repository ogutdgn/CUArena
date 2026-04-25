# Drag-box select (marquee)

- **Category:** selection
- **One-line summary:** Click-drag on empty canvas to rubber-band-select all intersecting layers.

## Triggers
- Pointer-down on empty canvas + drag (Move tool active).
- Hold `Shift` during drag to additively add to existing selection instead of replacing.
- Hold `Alt/Option` (reported in some docs) to restrict to fully-enclosed layers rather than intersected ones.

## Preconditions
- Move tool active.
- Pointer-down did NOT land on a layer (otherwise triggers drag-move or drag-select-inside-frame).
- Not in text-edit mode, etc.

## Inputs
- Pointer-down coordinates (start).
- Pointer-move deltas while drag is active.
- Pointer-up coordinates (end).
- Optional modifiers: `Shift` (additive), `Alt` (enclosure-only).

## Behavior
1. On pointer-down in empty space: start marquee; draw translucent selection rectangle from pointer-down to current pointer.
2. On pointer-move: extend the rectangle; compute layers whose bounds intersect it; preview highlight them.
3. On pointer-up: commit the set as the new selection (or add to existing if `Shift`).
4. If drag distance < small threshold (a few pixels), treat as a click on empty canvas → deselect (see `click-select`).

## Outputs
- **Scene graph changes:** none.
- **Selection changes:** set to the intersecting layers (or union, with `Shift`).

## UI feedback
- Canvas: translucent blue rectangle rendered while dragging; preview highlights on intersecting layers.
- On release: rectangle disappears, bounding box of the new selection renders.

## Side effects
- Undo stack: no entry.

## Related UI schema entries
- `regions/canvas-overlays.md` → pixel-cursor-box-select-overlay
- `regions/canvas-overlays.md` → selection-bounding-box / multi-selection-bounding-box

## Semantic event(s) candidate
- `drag_box_select { start: {x, y}, end: {x, y}, layer_ids: [...], modifier: "none" | "shift_additive" | "alt_enclosure" }`

## Source articles
- `select-layers-and-objects`

## Notes / gaps
- Exact intersection vs full-enclosure default not consistently stated; default to "bounds-intersect".
- Drag threshold (to distinguish click-on-empty from marquee) not specified; use ~3px default.
