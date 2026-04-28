# Toggle fill visibility

- **Category:** fills
- **One-line summary:** Toggle a fill row's visibility (eye icon) without removing it.

## Triggers
- Right sidebar **Fill** section, fill row → click eye icon (open vs closed).

## Preconditions
- Selection non-empty.
- Fill row exists.

## Inputs
- Pointer click on eye icon.

## Behavior
1. Eye icon toggles between "open eye" (visible) and "closed eye" (hidden).
2. The fill's `visible` flag flips.
3. Layer re-renders without the hidden fill.
4. Hidden fill stays in the array — eye is non-destructive.

## Outputs
- **Scene graph changes:** the fill's `visible` flag toggled.
- **Selection changes:** none.

## UI feedback
- Eye icon updates.
- Canvas re-renders.

## Side effects
- Undo stack: one entry per toggle.

## Related UI schema entries
- `regions/right-properties.md` → fill-section → fill-row eye icon

## Semantic event(s) candidate
- `toggle_fill_visibility { layer_ids: [...], fill_index, to_visible, trigger: "panel_eye" }`

## Source articles
- `guide-to-fills`

## Notes / gaps
- "Show in exports" is a separate per-fill checkbox documented in panel inventory; that one is `visual-only` per existing scope (export not implemented). The eye icon is the visibility-on-canvas toggle.
