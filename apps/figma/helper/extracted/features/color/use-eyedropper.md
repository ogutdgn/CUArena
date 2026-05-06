# Use eyedropper to sample a color

- **Category:** color
- **One-line summary:** Sample any color visible on the canvas (or, on macOS Desktop, anywhere on screen) and apply it to the targeted property.

## Triggers
- With a layer selected: shortcut `I` (Mac/Win) or `⌃ Control C` (Mac) toggles the eyedropper for the layer's primary fill.
- From inside the color picker: click the **Eyedropper** icon in the picker, or press `I`.
- Works for any color-bearing property: fill, stroke, effect color, page bg, gradient stop, selection-colors swatch.

## Preconditions
- A layer is selected (when invoking via shortcut) OR a color picker is open.

## Inputs
- Pointer hover over canvas — shows a magnified preview with the color value at the cursor.
- Click — apply the color.
- Optional `Tab` while sampling — switch between Hex / RGB / HSL / HSB display.
- Optional `⇧ Shift` while clicking — apply a color variable / style if the hovered pixel has one.
- Optional `⌘ Command ⇧ Shift` (Mac) / `⌃ Control ⇧ Shift` (Win) + Enter or click — open a "create style or variable" modal seeded with the sampled color.
- Esc cancels.

## Behavior
1. Eyedropper toggles on; cursor becomes the eyedropper.
2. As the user hovers over a pixel, a preview tooltip shows the color value (and the variable / style name if one applies).
3. Click commits the sampled color to the selected target property.
4. With Shift modifier: applies the source variable/style binding (not just the resolved color).
5. macOS Figma Desktop additionally allows sampling outside the Figma window (requires Screen Recording permission).

## Outputs
- **Scene graph changes:** target property color updated to the sampled value (or its variable / style binding if Shift).
- **Selection changes:** none.
- **Clipboard:** if no layer was selected, clicking copies the color value (and optionally style/variable name with Shift) to the OS clipboard.

## UI feedback
- Eyedropper cursor active.
- Magnified preview / tooltip near cursor with hex value.
- Press-Tab affordance shown when applicable.

## Side effects
- Undo stack: one entry per click commit.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → eyedropper-button
- `regions/canvas-overlays.md` → eyedropper-cursor + sample-tooltip

## Semantic event(s) candidate
- `sample_color { sampled_value, applied_to: "fill" | "stroke" | "effect" | "page_bg" | "clipboard", layer_ids?, fill_index?, modifiers: { shift }, trigger: "shortcut_I" | "picker_button" | "shortcut_Ctrl_C" }`
- `create_color_style_from_eyedropper { ... trigger: "shortcut_Cmd_Shift" }` — when used to seed a style / variable.

## Source articles
- `sample-colors-with-the-eyedropper-tool`

## Notes / gaps
- Outside-window sampling is Mac-Desktop-only; for the mock, scope sampling to canvas only.
- Tooltip rendering position relative to the cursor not pinned by the corpus.
