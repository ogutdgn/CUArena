# Open color picker

- **Category:** color
- **One-line summary:** Open the floating Color Picker overlay anchored to a fill / stroke / effect / page-bg swatch.

## Triggers
- Click on the fill swatch in the right sidebar **Fill** section.
- Click on the stroke swatch in **Stroke** section.
- Click on a color swatch inside an effect row (drop shadow, inner shadow).
- Click on the **Page** background color swatch (when nothing is selected).
- Click on a swatch in the **Selection colors** section (mixed selection).
- Click a gradient color stop in an open gradient configuration (re-opens picker for that stop).

## Preconditions
- The triggering swatch is rendered (i.e. the relevant section is visible — see `state-matrix.md`).

## Inputs
- Pointer click on a swatch.

## Behavior
1. Picker overlay opens anchored to the swatch (typically to the left of the swatch, vertical orientation).
2. Picker is **non-modal** — clicks on canvas or panel outside the picker close it (commit).
3. Picker contents reflect the current value of the swatched property (color, opacity, fill type, etc.).
4. Closing the picker = commit to undo stack (one entry per picker session, regardless of how many sub-edits inside).

## Outputs
- **Scene graph changes:** none on open — only on subsequent edits.
- **Selection changes:** none.
- **UI state:** picker overlay opens, anchored to swatch.

## UI feedback
- Picker overlay appears with current color/value preselected.
- The triggering swatch may show a subtle "active" state.

## Side effects
- Undo stack: not affected on open. A picker session that produces edits creates one undo entry on close.
- Clipboard: untouched.

## Related UI schema entries
- `regions/right-properties.md` → fill-section, stroke-section, page-section, effects-section
- `regions/floating-overlays.md` → color-picker

## Semantic event(s) candidate
- `open_color_picker { target: "fill" | "stroke" | "effect" | "page_bg" | "selection_colors" | "gradient_stop", layer_ids?: [...], fill_index?: number, trigger: "swatch_click" }`

## Source articles
- `update-fills-using-the-color-picker`
- `guide-to-fills`
- `view-and-adjust-colors-in-a-mixed-selection`

## Notes / gaps
- Real Figma also re-opens the picker when typing in a hex input that's part of the swatch row — flag whether the mock treats the hex input as a separate trigger or part of the picker session. The corpus does not explicitly distinguish; treat as separate triggers (see `set-color-hex.md`).
- Anchoring side (left vs right of swatch) is not pinned by docs — corpus shows pickers to the left of the right sidebar.
