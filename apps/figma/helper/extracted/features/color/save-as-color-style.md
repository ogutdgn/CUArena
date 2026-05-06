# Save current color as a color style

- **Category:** color
- **One-line summary:** Promote the picker's current color into a named color style available for reuse across the file.

## Triggers
- Color picker open — click the `+` (or "Create style") button in the picker's libraries / styles area.
- Eyedropper "create style/variable" flow (`⌘ ⇧` + Enter) — see `use-eyedropper.md`.

## Preconditions
- Picker open with a non-default color set.
- (Optional) Edit access to the file (any-plan).

## Inputs
- Pointer click on `+` or "Create style".
- Modal: type a style **Name** and optional **Description**.
- Modal: choose **Style** vs **Variable** (eyedropper flow surfaces both; picker `+` offers Style by default per `update-fills-using-the-color-picker` item 2).

## Behavior
1. Click `+` opens a small modal/inline form.
2. User names the style and confirms.
3. A new color style is added to the file's local styles list.
4. The currently-selected target property is bound to that style (its swatch shows the style chip).

## Outputs
- **Scene graph changes:** target's fill/stroke/effect color is now bound to a style id.
- **Persistent file state:** new entry under file's local styles.

## UI feedback
- Modal closes; picker shows the style chip on the swatch.
- Right sidebar **Local styles** section (when nothing selected) gains the new style.

## Side effects
- Undo stack: one entry covering both the style creation and the binding.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → libraries-panel, create-style-modal
- `regions/right-properties.md` → page-section → local-styles-and-variables

## Semantic event(s) candidate
- `create_color_style { name, color, description?, source: "picker_plus" | "eyedropper_create" }`
- `apply_color_style { layer_ids, target, fill_index?, style_id }`

## Source articles
- `apply-styles-to-layers-and-objects`
- `create-color-text-effect-and-layout-guide-styles`
- `manage-and-share-styles`
- `update-fills-using-the-color-picker`

## Notes / gaps
- Corpus does not pin the exact modal layout for the picker `+` flow vs the eyedropper flow; treat them as two surfaces of the same underlying create-style operation.
