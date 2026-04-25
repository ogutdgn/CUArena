# Pan canvas

- **Category:** canvas-navigation
- **One-line summary:** Move the viewport across the canvas without changing the selection or the scene graph.

## Triggers
- Keyboard + mouse: hold `Space`, then click-drag anywhere on the canvas (temporarily activates Hand tool; releasing Space returns to previous tool).
- Trackpad: two-finger slide.
- Keyboard only: arrow keys (`Shift + arrow` = larger step; step size scaled to zoom).
- Toolbar: pick Hand tool (`H`) from Move-tools dropdown, then click-drag on canvas.
- Middle-mouse button: drag (behavior implied by standard editor conventions; not explicitly documented in corpus).

## Preconditions
- Pointer is over the canvas.
- No modal overlay is capturing input.
- Text-edit mode is not active (Space types a space character instead).

## Inputs
- Pointer position delta (dx, dy) from pointer-down to pointer-up during drag.
- OR arrow key + optional Shift modifier.

## Behavior
1. On `Space` down (or Hand tool selected): cursor changes to open-hand glyph.
2. On pointer-down: cursor changes to closed-hand glyph; viewport anchor captured.
3. On pointer-move: viewport x/y translates by pointer delta (no zoom change; 1:1 screen-to-world).
4. On pointer-up: closed-hand reverts to open-hand (if Space still held) or to previous tool cursor.
5. On `Space` up: returns to prior tool.

Arrow-key variant:
1. On arrow-key press (canvas focused): viewport offsets by a fixed nudge.
2. `Shift + arrow` scales the nudge up; nudge magnitude scales with current zoom so a fixed screen-space distance moves per press.

## Outputs
- **Scene graph changes:** none.
- **Viewport state changes:** viewport `x` + `y` translated. Zoom unchanged.
- **Selection changes:** none.

## UI feedback
- Cursor: open-hand while Space held (or Hand tool active), closed-hand while dragging.
- Canvas content scrolls smoothly; any canvas overlays (selection box, guides) move with their anchor objects.
- No panel updates.
- No toast.

## Side effects
- Undo stack: no entry (view state is not undoable).
- Clipboard: untouched.
- Focus: unchanged.

## Related UI schema entries
- `regions/toolbar.md` → move-tools-dropdown (Hand sub-tool)
- `regions/canvas-overlays.md` → canvas-zoom-and-pan

## Semantic event(s) candidate
- `pan_canvas { dx, dy, trigger: "space_drag" | "hand_tool_drag" | "trackpad" | "arrow_key" | "middle_mouse" }`
- Multi-trigger stays in one event; `trigger` field distinguishes trajectory for CUA test assertions.

## Source articles
- `navigating-ui3`: describes pan as part of UI3 basics.
- `access-design-tools-from-the-toolbar`: Hand tool reference.
- `adjust-your-zoom-and-view-options`: view-options dropdown + zoom mention implies canvas-navigation surface.

## Notes / gaps
- Arrow-key nudge magnitude across zoom levels not numerically specified; pick a sensible default at build time (e.g. 10 CSS-pixels base, 100 with Shift).
- Middle-mouse pan behavior not explicitly documented; treat as optional.
