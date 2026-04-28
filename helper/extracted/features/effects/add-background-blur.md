# Add background blur

- **Category:** effects
- **One-line summary:** Blur the content **behind** a layer (rather than the layer itself) — useful for frosted-glass effects.

## Triggers
- Right sidebar **Effects** section → `+` → **Background blur**.

## Preconditions
- A layer selected.
- Layer should have some transparency (via fill opacity / layer opacity) to make the blur visible.

## Inputs
- Blur radius (px).

## Behavior
1. Pixels behind the layer's geometry are blurred by the radius.
2. Effect requires partial transparency to be visible.

## Outputs
- **Scene graph changes:** `effects` gains `{ type: "background_blur", radius }`.

## UI feedback
- Canvas re-renders.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/right-properties.md` → effects-section

## Semantic event(s) candidate
- `add_effect { layer_ids, type: "background_blur", default_params, trigger }`

## Source articles
- `apply-effects-to-layers`
