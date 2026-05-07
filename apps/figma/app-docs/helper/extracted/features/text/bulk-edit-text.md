# Bulk edit text

- **Category:** text
- **One-line summary:** Apply text-property changes to multiple selected text layers at once via the right sidebar.

## Triggers
- Multi-select 2+ text layers.
- Edit any typography property in the right sidebar.

## Preconditions
- 2+ text layers selected.

## Inputs
- Standard typography inputs (font / weight / size / line-height / etc.).

## Behavior
1. Mixed values display as "Mixed" in the affected fields.
2. Editing a field replaces that property on all selected layers.
3. Editing a field that's already uniform: shows the value; entering a new value applies to all.

## Outputs
- **Scene graph changes:** all selected text layers' affected property updated.
- **Selection changes:** none.

## UI feedback
- Fields show "Mixed" or uniform value.

## Side effects
- Undo stack: one entry per bulk change.

## Related UI schema entries
- `regions/right-properties.md` → typography-section (multi-select state)

## Semantic event(s) candidate
- Standard set_*_text events with `layer_ids: [multiple]` — the multi-select aspect is implicit in the event.

## Source articles
- `edit-objects-on-the-canvas-in-bulk`
- `explore-text-properties`
