# Paste properties (between layers)

- **Category:** fills
- **One-line summary:** Copy a layer's properties (fills, strokes, effects, layout, etc.) and paste them onto another layer's matching property slots without copying the geometry/content.

## Triggers
- Source layer selected → right-click → **Copy properties** OR shortcut `⌥⌘C` (Mac) / `Ctrl+Alt+C` (Win).
- Target layer(s) selected → right-click → **Paste properties** OR shortcut `⌥⌘V` (Mac) / `Ctrl+Alt+V` (Win).

## Preconditions
- A source layer was previously copied via the copy-properties command.

## Inputs
- Keyboard shortcut OR right-click menu choice.

## Behavior
1. **Copy properties** captures the source layer's design properties (fills, strokes, effects, opacity, blend mode, corner radius, typography for text, image-fill modes/adjustments, etc.) into a special clipboard slot.
2. **Paste properties** writes those properties onto each currently-selected target layer.
3. Geometry (X, Y, W, H, rotation) and identity (name, id, parent) are NOT pasted.
4. Layer-type-mismatch handling: properties are filtered to ones the target type supports (e.g. typography won't paste onto a non-text target).

## Outputs
- **Scene graph changes:** target layer(s) gain the source's design properties (filtered by type).
- **Selection changes:** none.
- **Clipboard:** properties clipboard slot is set on copy; standard clipboard untouched.

## UI feedback
- Canvas: targets re-render with the new properties.

## Side effects
- Undo stack: one entry per paste-properties.

## Related UI schema entries
- `regions/floating-overlays.md` → context-menu → copy/paste-properties

## Semantic event(s) candidate
- `copy_properties { source_layer_id, captured_properties: [...] }`
- `paste_properties { target_layer_ids: [...], applied_properties: [...] }`

## Source articles
- `copy-and-paste-properties-between-layers`

## Notes / gaps
- Documented under fills/ because the user-listed fill flow most often uses paste-properties to bulk-apply colors. The same operation is cross-cutting (also covers strokes, effects, etc.).
- Exact list of "design properties" pasted vs not is detailed in the source article.
