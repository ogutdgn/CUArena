# Color Picker (floating overlay)

**Region role:** Modal-less floating overlay anchored to a fill / stroke / effect / page-bg / gradient-stop / selection-colors swatch. Encapsulates all color editing.

**Anatomy, top → bottom (per `update-fills-using-the-color-picker`):**
1. **Fill type row** — icons for Solid / Gradient / Pattern / Image / Video.
2. **Style+ button** — `+` to save current color as a Style or Variable.
3. **Blend mode dropdown** — applies a per-fill / per-stroke / per-effect blend mode.
4. **Check color contrast button** — opens accessibility panel.
5. **Saturation/Value square** — 2D color palette; click + drag.
6. **Eyedropper icon** — toggle eyedropper for sampling on canvas.
7. **Hue slider** — 1D vertical slider on the side of the SV square.
8. **Opacity slider** — 1D slider for alpha.
9. **Color model dropdown** — select Hex / RGB / HSL / HSB / CSS.
10. **Channel inputs** — fields appropriate to the active model:
    - Hex: single field accepting `#RRGGBB` / `RRGGBB` / `RGB` shorthand.
    - RGB: three integer fields 0-255.
    - HSL / HSB: three fields 0-360° / 0-100% / 0-100%.
    - CSS: free-text `rgb()`, `rgba()`, `hsl()`, `hsla()`, `red`, `#fff`, etc.
11. **Document colors** — swatches of every color used in the current file.
12. **Library colors** — swatches of color styles + color variables from enabled libraries.
13. **(For gradient fills only)** — gradient stops slider + `+`/`-` + Flip / Rotate buttons.

**Global behavior:**
- Non-modal: clicks outside close the picker (commit). Drags inside don't close.
- One picker open at a time; opening another closes the first.
- Picker session = unit of undo (one undo entry covers all edits within a single open-close cycle).
- Picker scrolls vertically if content exceeds height.
- Width fixed; vertical orientation.
- Closing happens on: click outside, Esc, click another swatch.

**Canonical reference images:**
- `helper/figma_docs/articles/Figma Design/update-fills-using-the-color-picker/images/img_*.png`
- `helper/figma_docs/articles/Figma Design/sample-colors-with-the-eyedropper-tool/images/img_*.png`

---

## 1. Fill type row

### fill-type-icons
- **Scope flag:** functional-in-scope (Solid + Gradient + Image; Pattern functional; Video out-of-scope or VO)
- **Default appearance:** 5 small icons in a row.
- **States:**
  - Hover — tooltip with name.
  - Active — pressed-style indicator.
- **Behavior:** clicking a type switches the fill's `type`; existing type-specific config is discarded.
- **Reference:** `update-fills-using-the-color-picker/images/img_03.png`
- **Source articles:** `guide-to-fills`, `update-fills-using-the-color-picker`

---

## 2. Style+ button

### create-style-from-picker
- **Scope flag:** functional-in-scope (color style basics)
- **Default appearance:** `+` icon next to the active type.
- **Behavior:** opens an inline modal with Name + Description + Style/Variable tabs. Submit creates style and binds the swatch.
- **Reference:** `update-fills-using-the-color-picker/images/img_03.png`
- **Source articles:** `update-fills-using-the-color-picker`, `apply-styles-to-layers-and-objects`

---

## 3. Blend mode dropdown

### blend-mode-dropdown
- **Scope flag:** functional-in-scope
- **Default appearance:** Text "Blend" + chevron.
- **Behavior:** opens enum dropdown of all blend modes (Normal, Darken, Multiply, Color burn, Lighten, Screen, Color dodge, Overlay, Soft light, Hard light, Difference, Exclusion, Hue, Saturation, Color, Luminosity).
- **Source articles:** `apply-blend-modes-to-layers-fills-and-effects`

---

## 4. Check color contrast button

### color-contrast-button
- **Scope flag:** visual-only (accessibility check is informational)
- **Default appearance:** small icon in header row.
- **Behavior:** expands an accessibility view showing foreground/background contrast ratio + WCAG AA/AAA badges. Clickable badge auto-corrects to nearest compliant color.
- **Source articles:** `update-fills-using-the-color-picker` (Accessibility section)

---

## 5. Saturation/Value square (color palette)

### sv-square
- **Scope flag:** functional-in-scope
- **Default appearance:** 2D square gradient — saturation X axis, value/brightness Y axis. Selected position rendered as small ring.
- **Behavior:** pointer-down + drag updates color live. Click without drag = jump-to-position.
- **Reference:** `update-fills-using-the-color-picker/images/img_03.png`

---

## 6. Eyedropper icon

### eyedropper-icon
- **Scope flag:** functional-in-scope
- **Default appearance:** dropper icon.
- **Behavior:** toggles eyedropper. Cursor changes to dropper. Click on canvas pixel applies it to the picker's target.
- **Modifiers while sampling:** `Tab` — switch model; `Shift` — apply variable/style if found.
- **Source articles:** `sample-colors-with-the-eyedropper-tool`

---

## 7. Hue slider

### hue-slider
- **Scope flag:** functional-in-scope
- **Default appearance:** vertical (or horizontal) hue gradient strip with handle at current hue.
- **Behavior:** drag handle to change hue (S/V preserved).

---

## 8. Opacity slider

### opacity-slider
- **Scope flag:** functional-in-scope
- **Default appearance:** alpha gradient strip with handle.
- **Behavior:** drag changes alpha; numeric % field next to it updates.

---

## 9. Color model dropdown

### color-model-dropdown
- **Scope flag:** functional-in-scope
- **Default appearance:** dropdown showing current model name (HEX / RGB / HSL / HSB / CSS).
- **Behavior:** click → select; channel-input area below changes accordingly.
- **Source articles:** `about-color-models`

---

## 10. Channel inputs

### channel-inputs
- **Scope flag:** functional-in-scope
- **Per model:**
  - **Hex**: `#______` field (3 / 6 / 8 char accepted).
  - **RGB**: R, G, B fields, integer 0-255.
  - **HSL**: H 0-360°, S 0-100%, L 0-100%.
  - **HSB**: H 0-360°, S 0-100%, B 0-100%.
  - **CSS**: free-text input for CSS notation.
- **Behavior:** typing commits on Enter / blur. Live update on every valid keystroke.
- **Source articles:** `update-fills-using-the-color-picker`, `about-color-models`

---

## 11. Document colors

### document-colors-row
- **Scope flag:** functional-in-scope
- **Default appearance:** row of small swatches (de-duplicated colors used in the file).
- **Behavior:** click a swatch to apply it; hover for tooltip with hex + usage count.
- **Source articles:** `update-fills-using-the-color-picker` (item 11)

---

## 12. Library colors

### library-colors-section
- **Scope flag:** functional-in-scope
- **Default appearance:** list of color styles + color variables from each enabled library; grouped by library name. Optional search field at top.
- **Behavior:** click → bind the target to the chosen style/variable. Hover for tooltip.
- **Source articles:** `apply-styles-to-layers-and-objects`, `enable-access-to-libraries-in-your-drafts`, `update-fills-using-the-color-picker`

---

## 13. Gradient stops slider (gradient fills only)

### gradient-stops-slider
- **Scope flag:** functional-in-scope
- **Default appearance:** horizontal slider showing stops along the gradient.
- **Controls:**
  - Click slider to add a stop.
  - Drag a stop to move.
  - Select stop + Delete to remove.
  - `+` / `-` buttons next to "Stops" label.
  - **Flip gradient** button.
  - **Rotate gradient** button.
- **Source articles:** `use-gradients-as-a-fill-or-stroke`

---

## 14. Image fill controls (image fills only)

### image-fill-controls
- **Scope flag:** functional-in-scope
- **Default appearance:** asset preview thumbnail + Upload from computer + (Make an image — visual-only).
- **Controls when image is set:**
  - Fill mode dropdown (Fill / Fit / Crop / Tile)
  - Tile scale slider (Tile only)
  - Rotate 90° button
  - Adjustment sliders (Exposure / Contrast / Saturation / Temperature / Tint / Highlights / Shadows)
- **Source articles:** `add-images-and-videos-to-designs`, `adjust-the-properties-of-an-image`, `crop-an-image`

---

## 15. Pattern fill controls (pattern fills only)

### pattern-fill-controls
- **Scope flag:** functional-in-scope (pattern source picker), DEF for advanced tile options
- **Controls:**
  - **Select source** button → pick layer/group/frame on canvas.
  - Tile type / scale / spacing / alignment / opacity (per article — exact list not enumerated).
- **Source articles:** `use-patterns-as-a-fill-or-stroke`

---

## Notes / gaps

- Picker auto-anchors to the left of the right sidebar by default; corpus does not pin exact positioning. Implementer can re-anchor to fit viewport.
- "Make an image" (Figma AI) entry is `visual-only` — clicking routes to `unsupported-feature-toast.md`.
- Video fill is paid-plan-only; in mock: `visual-only`.
