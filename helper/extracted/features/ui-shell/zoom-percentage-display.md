# Zoom percentage display + dropdown

- **Category:** ui-shell
- **One-line summary:** Top-of-right-panel zoom % indicator with a dropdown of zoom & view options.

## Triggers
- Click the zoom %.
- Click the chevron next to the zoom %.

## Preconditions
- Editor view active.

## Inputs
- Pointer click → opens dropdown.
- (Some docs imply you can type into the % field directly to set a custom zoom — confirm with `adjust-your-zoom-and-view-options`.)

## Behavior
1. Clicking opens a dropdown of zoom & view options. Functional entries:
   - **Zoom in / out / to fit / to selection / Custom %** — see `canvas-navigation/*.md`.
2. Visual-only entries (per existing `regions/right-properties.md` schema):
   - **Pixel preview** (Disabled / 1x / 2x)
   - **Pixel grid**
   - **Snap to pixel grid**
   - **Layout guides**
   - **Multiplayer cursors**
   - **Outlines** (Show outlines / Include hidden / Include object bounds — `view-layer-outlines.md` makes outlines functional)
   - **Property labels**
3. Visual-only entries route to `unsupported-feature-toast.md`.

## Outputs
- **Scene graph changes:** none.
- **UI state:** dropdown open; per-entry the entry's effect.

## UI feedback
- Dropdown anchored to zoom %.

## Side effects
- Undo stack: most entries are view-only and unaffected. Functional entries that change scene-graph (none in this dropdown) follow their own undo rules.

## Related UI schema entries
- `regions/right-properties.md` → zoom-percentage-display + zoom-and-view-options-dropdown

## Semantic event(s) candidate
- `open_zoom_view_options_dropdown { trigger: "click_zoom_percent" | "click_chevron" }`
- Per-entry: `zoom_to_fit`, `zoom_to_selection`, `zoom_to_100`, `zoom_to_custom_percent { value }`, `unsupported_feature_clicked { feature_key }` for visual-only entries.

## Source articles
- `adjust-your-zoom-and-view-options`
- `navigating-ui3`

## Notes / gaps
- Custom % typing: per the existing schema "some docs imply typing in the % field is supported; exact trigger not confirmed". Treat as supported (keyboard-only entry on the field).
