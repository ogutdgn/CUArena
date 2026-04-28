# Export button

- **Category:** ui-shell
- **One-line summary:** Right sidebar **Export** section button to export the selection (or page) — visual-only in mock scope.

## Triggers
- Right sidebar **Export** section → click **Export** button.
- Shortcut: `⌘ ⇧ E` (Mac) / `Ctrl Shift E` (Win) — opens advanced export modal.

## Preconditions
- An export config is set (or default).

## Inputs
- Pointer click.

## Behavior — real Figma
- Renders selected layers/pages to file(s) per export config (PNG/JPG/SVG/PDF, scale, suffix).
- Opens a save dialog or downloads directly.
- For multi-frame exports, emits a zip.

## Behavior — mock
- `visual-only` — clicking the button triggers `unsupported-feature-toast.md` with feature label `"Export"`.

## Outputs
- **Scene graph changes:** none.
- **UI state:** toast renders.
- **Logger:** `unsupported_feature_clicked { feature_key: "export_button" }`.

## UI feedback
- Toast.

## Side effects
- None.

## Related UI schema entries
- `regions/right-properties.md` → export-section
- `regions/floating-overlays.md` → bulk-export-modal (visual-only)

## Semantic event(s) candidate
- `unsupported_feature_clicked { feature_key: "export_button", feature_label: "Export" }`

## Source articles
- `export-formats-and-settings`
- `export-from-figma-design`

## Notes / gaps
- Real Figma's export pipeline is complex (per-layer config, batch export, advanced settings). Out of mock scope.
