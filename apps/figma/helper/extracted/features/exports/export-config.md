# Export config (per layer / page)

- **Category:** exports
- **One-line summary:** Configure per-layer export entries — scale, suffix, format (PNG/JPG/SVG/PDF) — and trigger export.

## Triggers
- Right sidebar **Export** section → `+` to add export entry.

## Preconditions
- A layer or page is selected.

## Inputs
- Per-entry: scale (1x/2x/3x/0.5x/custom), suffix string (e.g. `@2x`), format dropdown.
- Optional: contents-only / full bounds.

## Behavior
1. Each entry yields one export file when triggered.
2. Multiple entries → multiple files (or zip for batch).
3. Advanced settings: optimize for developer handoff, preserve layer hierarchy.

## Outputs
- **Persistent state:** export config stored on the layer/page.
- **UI state on export trigger:** download initiated.

## UI feedback
- Export rows in panel; preview link.

## Side effects
- File system: downloaded files (out-of-scope for mock — see `ui-shell/export-button.md`).

## Related UI schema entries
- `regions/right-properties.md` → export-section

## Semantic event(s) candidate
- `add_export_entry { layer_ids, scale, suffix, format }`
- `remove_export_entry { layer_ids, entry_index }`
- `trigger_export { layer_ids }`

## Source articles
- `export-formats-and-settings`
- `export-from-figma-design`
- `optimize-design-files-for-developer-handoff`

## Notes / gaps
- Mock scope: section is `visual-only` per existing extracted ui-schema; clicking Export triggers `unsupported-feature-toast.md`. Export config can still be edited (stored on layers) — only the trigger is no-op.
